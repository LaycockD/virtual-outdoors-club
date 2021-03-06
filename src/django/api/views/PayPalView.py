from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from .error import RespError, Response
from ..models import Reservation
from decimal import Decimal
from ..local_date import local_date
import datetime
import paypalrestsdk


@csrf_exempt
@api_view(['GET'])
@permission_classes((AllowAny, ))
def returnView(request):
    paymentId = request.query_params.get("paymentId", None)
    payerId = request.query_params.get("PayerID", None)

    if not paymentId and not payerId:
        return render(request, 'cancel.html', {'URL': settings.SITE_URL})

    try:
        res = Reservation.objects.get(payment=paymentId)
    except Reservation.DoesNotExist:
        return render(request, 'cancel.html', {'URL': settings.SITE_URL})

    deposit = paypalrestsdk.Payment.find(paymentId)

    if deposit.execute({"payer_id": payerId}):
        res.payment = deposit['transactions'][0]['related_resources'][0]['authorization']['id']
        res.status = "PAID"
    else:
        res.payment = ""
        return RespError(400, {"message": deposit.error})

    res.save()

    return render(request, 'done.html', {'URL': settings.SITE_URL, "id": res.id})


@csrf_exempt
@permission_classes((AllowAny, ))
def cancelView(request):

    return render(request, 'cancel.html', {'URL': settings.SITE_URL})


@api_view(['POST'])
def paypalView(request):

    data = request.data

    if 'id' not in data:
        return RespError(400, "You must specify an id.")

    try:
        res = Reservation.objects.get(id=data['id'])
    except Reservation.DoesNotExist:
        return RespError(400, "There is no reservation with the id of '" + str(data['id']) + "'")

    if res.status == "CANCELLED" or res.status == "RETURNED":
        return RespError(400, "Reservation already returned or cancelled")

    if res.status == "PAID":
        return RespError(400, "Reservation already paid for")

    if res.startDate > (local_date() + datetime.timedelta(days=1)):
        return RespError(400, "The earliest you can pay for a reservation is the day before the start date")

    amount = Decimal()
    itemList = []
    for gear in res.gear.all():
        amount += gear.depositFee
        itemList.append({"sku": gear.code,
                         "name": gear.category.name,
                         "description": gear.description,
                         "quantity": "1",
                         "price": str(gear.depositFee),
                         "currency": "CAD"})

    # TODO Replace with UAOC specif info

    deposit = paypalrestsdk.Payment({
        "intent": "authorize",
        "payer": {
            "payment_method": "paypal"},
        "application_context": {
            "brand_name": "University Of Alberta Outdoors Club",
            "shipping_preference": "NO_SHIPPING"},
        "redirect_urls": {
            "return_url": "http://{}{}".format(request.get_host(), reverse('returnView')),
            "cancel_url": "http://{}{}".format(request.get_host(), reverse('cancelView'))},
        "transactions": [{
            "amount": {
                "total": str(amount),
                "currency": "CAD"},
            "description": "authorization for reservation #" + str(res.id),
            "item_list": {
                "items": itemList}
        }]
    })

    if deposit.create():
        for link in deposit.links:
            if link.rel == "approval_url":
                res.payment = deposit.id
                res.save()
                return Response(str(link.href))
    else:
        return RespError(400, deposit.error)


def process(res, amount):
    deposit = paypalrestsdk.Authorization.find(res.payment)

    if amount == 0:
        if deposit.void():

            return
        else:
            return deposit.error

    capture = deposit.capture({"amount": {"currency": "CAD", "total": str(amount)}, "is_final_capture": True})

    if capture.success():
        return
    else:
        return capture.error
