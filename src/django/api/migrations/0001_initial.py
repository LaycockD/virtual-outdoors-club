# Generated by Django 2.1.2 on 2018-10-29 06:29

import django.contrib.postgres.fields.jsonb
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BlackList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
            ],
        ),
        migrations.CreateModel(
            name='Gear',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('code', models.CharField(max_length=6, unique=True)),
                ('depositFee', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0)])),
                ('description', models.CharField(blank=True, max_length=255)),
                ('condition', models.CharField(blank=True, choices=[('RENTABLE', 'Rentable'), ('FLAGGED', 'Flagged'), ('NEEDS_REPAIR', 'Needs Repair'), ('DELETED', 'Deleted')], default='RENTABLE', max_length=20)),
                ('version', models.IntegerField(default=1)),
            ],
        ),
        migrations.CreateModel(
            name='GearCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='PaymentHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('paymentType', models.CharField(choices=[('CASH', 'Cash'), ('PAYPAL', 'Paypal'), ('UNDECIDED', 'Undecided')], default=None, max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('permissionID', models.AutoField(primary_key=True, serialize=False)),
                ('permissionType', models.CharField(choices=[('EDIT_BLACKLIST', 'Edit Blacklist'), ('EDIT_GEAR', 'Edit Gear'), ('EDIT_RESERVATION', 'Edit Reservation'), ('CANCELLED', 'Cancelled'), ('RENTED', 'Rented')], default=None, max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('email', models.CharField(max_length=50)),
                ('licenseName', models.CharField(max_length=100)),
                ('licenseAddress', models.CharField(max_length=200)),
                ('approvedBy', models.CharField(max_length=50)),
                ('startDate', models.DateField()),
                ('endDate', models.DateField()),
                ('payment', django.contrib.postgres.fields.jsonb.JSONField(default=dict)),
                ('status', models.CharField(choices=[('REQUESTED', 'Requested'), ('APPROVED', 'Approved'), ('PAID', 'Paid'), ('TAKEN', 'Taken'), ('RETURNED', 'Returned'), ('CANCELLED', 'Cancelled')], default='REQUESTED', max_length=20)),
                ('version', models.IntegerField(default=1)),
                ('gear', models.ManyToManyField(to='api.Gear')),
            ],
        ),
        migrations.CreateModel(
            name='System',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service', models.CharField(max_length=100)),
                ('enabled', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserVariability',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('variable', models.CharField(max_length=100)),
                ('value', models.IntegerField()),
            ],
        ),
        migrations.AddField(
            model_name='paymenthistory',
            name='reservationID',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.PROTECT, to='api.Reservation'),
        ),
        migrations.AddField(
            model_name='gear',
            name='category',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.PROTECT, to='api.GearCategory'),
        ),
    ]
