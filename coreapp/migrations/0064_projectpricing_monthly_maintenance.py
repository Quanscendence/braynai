# Generated by Django 2.2 on 2020-04-28 17:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coreapp', '0063_endpointalgorithm_no_of_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectpricing',
            name='monthly_maintenance',
            field=models.FloatField(default=39),
        ),
    ]
