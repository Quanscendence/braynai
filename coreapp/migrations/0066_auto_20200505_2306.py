# Generated by Django 2.2 on 2020-05-05 17:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coreapp', '0065_defaultprojectpricing_monthly_maintenance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='defaultprojectpricing',
            name='monthly_maintenance',
            field=models.FloatField(default=49),
        ),
        migrations.AlterField(
            model_name='projectpricing',
            name='monthly_maintenance',
            field=models.FloatField(default=49),
        ),
    ]
