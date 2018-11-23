from rest_framework import serializers
from .models import Gear, GearCategory, Reservation, UserVariability, Member, BlackList
from datetime import datetime
from django.db.models import Q


class UserVariabilitySerializer(serializers.ModelSerializer):

    class Meta:
        model = UserVariability
        fields = [
            "variable",
            "value",
        ]


class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = [
            "email"
        ]

    def validate_email(self, value):
        return value.lower()

class BlackListSerializer(serializers.ModelSerializer):

    class Meta:
        model = BlackList
        fields = [
            "email"
        ]


class GearCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = GearCategory
        fields = [
            "name"
        ]


class GearSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(queryset=GearCategory.objects.all(), slug_field='name')

    class Meta:
        model = Gear
        fields = [
            "id",
            "code",
            "category",
            "depositFee",
            "description",
            "condition",
            "version",
        ]


class ReservationGETSerializer(serializers.ModelSerializer):
    gear = GearSerializer(many=True, read_only=True)

    class Meta:
        model = Reservation
        fields = [
            "id",
            "email",
            "licenseName",
            "licenseAddress",
            "startDate",
            "endDate",
            "status",
            "gear",
            "version",
        ]


class ReservationPOSTSerializer(serializers.ModelSerializer):

    class Meta:
        model = Reservation
        fields = [
            "id",
            "email",
            "licenseName",
            "licenseAddress",
            "startDate",
            "endDate",
            "status",
            "gear",
            "version",
        ]

    def validate(self, data):
        DAYSINADVANCETOMAKERESV = "membermaxFuture"  # how far in advance a resv can be made
        MAXRESVDAYS = "membermaxLength"  # Max days a resv can be
        MAXRENTALS = "membermaxRentals"  # Max rentals

        if "email" not in data:
            raise serializers.ValidationError("Requests must have an email")
        try:
            member = Member.objects.get(email=data["email"])
        except Member.DoesNotExist:
            raise serializers.ValidationError("Email for this request not in database!")

        try:    # Check if blacklisted email
            blackListed = BlackList.objects.get(email=data["email"])
            if blackListed:
                raise serializers.ValidationError("You are not allowed to rent gear at this time. If you wish to know why, contact the outdoors club.")
                
        except BlackList.DoesNotExist:
            pass

        if data['startDate'] < datetime.now().date():
            raise serializers.ValidationError("Start date must be in the future.")

        if data['startDate'] > data['endDate']:
            raise serializers.ValidationError("Start date must be before the end date")


        maxTimeInAdvance = UserVariability.objects.get(pk=DAYSINADVANCETOMAKERESV).value

        if (data['startDate'] - datetime.now().date()).days > maxTimeInAdvance:
            raise serializers.ValidationError("Start date cannot be more than " + str(maxTimeInAdvance) + " days in advance")

        maxResvTime = UserVariability.objects.get(pk=MAXRESVDAYS).value
        if (data['endDate'] - data['startDate']).days > maxResvTime:
            raise serializers.ValidationError("Length of reservation must be less than " + str(maxResvTime) + " days")

        maxResvs = UserVariability.objects.get(pk=MAXRENTALS).value

        userReservations = Reservation.objects.filter(email=data["email"]).exclude(status="RETURNED").exclude(status="CANCELLED")
        if 'id' in self.initial_data:
            userReservations = userReservations.exclude(id=self.initial_data["id"])

        if len(userReservations) >= maxResvs:
            raise serializers.ValidationError("You cannot have more than " + str(maxResvs) + " reservations")

        denied = []
        dateFilter = Q(startDate__range=[data['startDate'], data['endDate']]) | \
                     Q(endDate__range=[data['startDate'], data['endDate']]) | \
                     Q(startDate__lte=data['startDate'], endDate__gte=data['endDate'])

        overlappingRes = Reservation.objects.filter(dateFilter).exclude(status="CANCELLED").exclude(status="RETURNED")
        
        if overlappingRes.exists():

            # Remove the self reservation from overlappingRes. Used for patches
            if 'id' in self.initial_data:
                overlappingRes = overlappingRes.exclude(pk=self.initial_data["id"])
                       
            for gear in data['gear']:
                if overlappingRes.filter(gear=gear).exists():
                    denied.append(gear.code)

                if len(denied) != 0:
                    message = ""
                    for item in denied:
                        message += str(item)
                        message += ", "
                    raise serializers.ValidationError("These items are unavailable: " + message[:-2])

        if "version" in data:
            data["version"] += 1
        return data
