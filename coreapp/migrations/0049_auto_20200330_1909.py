# Generated by Django 2.2 on 2020-03-30 13:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coreapp', '0048_auto_20200330_1906'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectbillingdaycost',
            name='disk_space_cost',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='projectbillingdaycost',
            name='end_point_cost',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='projectbillingdaycost',
            name='iqs_cost',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='projectbillingdaycost',
            name='user_cost',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='projectbillinghourlycost',
            name='disk_space_cost',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='projectbillinghourlycost',
            name='end_point_cost',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='projectbillinghourlycost',
            name='user_cost',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='projectbillingmonthcost',
            name='disk_space_cost',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='projectbillingmonthcost',
            name='end_point_cost',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='projectbillingmonthcost',
            name='iqs_cost',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='projectbillingmonthcost',
            name='user_cost',
            field=models.FloatField(default=0.0),
        ),
    ]