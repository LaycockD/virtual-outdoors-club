# Generated by Django 2.1.2 on 2018-11-26 05:20

from django.conf import settings
import django.core.validators
from django.db import migrations, models
from ..models import UserVariability
import django.db.models.deletion
import simple_history.models


def initialData(apps, schema_editor):
    users = ["member", "executive"]
    variables = ["maxLength", "maxFuture", "maxReservations", "maxGearPerReservation"]
    values = [14, 7, 3, 5]

    for x in range(2):
        for i in range(len(variables)):
            try:
                entry = UserVariability.objects.create(variable=users[x]+variables[i], value=values[i])
                entry.save()
            except:
                pass


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BlackList',
            fields=[
                ('email', models.EmailField(max_length=254, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='CategoryStat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('counter', models.PositiveSmallIntegerField(default=0)),
                ('usage', models.DecimalField(decimal_places=2, max_digits=4)),
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
            name='GearStat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('counter', models.PositiveSmallIntegerField(default=0)),
                ('usage', models.DecimalField(decimal_places=2, max_digits=4)),
                ('gearID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Gear')),
            ],
        ),
        migrations.CreateModel(
            name='HistoricalGear',
            fields=[
                ('id', models.IntegerField(blank=True, db_index=True)),
                ('code', models.CharField(db_index=True, max_length=6)),
                ('depositFee', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0)])),
                ('description', models.CharField(blank=True, max_length=255)),
                ('condition', models.CharField(blank=True, choices=[('RENTABLE', 'Rentable'), ('FLAGGED', 'Flagged'), ('NEEDS_REPAIR', 'Needs Repair'), ('DELETED', 'Deleted')], default='RENTABLE', max_length=20)),
                ('version', models.IntegerField(default=1)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('category', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='api.GearCategory')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical gear',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalReservation',
            fields=[
                ('id', models.IntegerField(blank=True, db_index=True)),
                ('email', models.CharField(max_length=50)),
                ('licenseName', models.CharField(max_length=100)),
                ('licenseAddress', models.CharField(max_length=200)),
                ('approvedBy', models.CharField(max_length=50)),
                ('startDate', models.DateField()),
                ('endDate', models.DateField()),
                ('payment', models.CharField(blank=True, max_length=28)),
                ('status', models.CharField(choices=[('REQUESTED', 'Requested'), ('APPROVED', 'Approved'), ('PAID', 'Paid'), ('TAKEN', 'Taken'), ('RETURNED', 'Returned'), ('CANCELLED', 'Cancelled')], default='REQUESTED', max_length=20)),
                ('version', models.IntegerField(default=1)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical reservation',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('email', models.EmailField(max_length=254, primary_key=True, serialize=False)),
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
                ('payment', models.CharField(blank=True, max_length=28)),
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
                ('variable', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('value', models.IntegerField()),
            ],
        ),
        migrations.AddField(
            model_name='gear',
            name='category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='api.GearCategory'),
        ),
        migrations.AddField(
            model_name='categorystat',
            name='categoryID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.GearCategory'),
        ),

        migrations.RunPython(initialData)
    ]
