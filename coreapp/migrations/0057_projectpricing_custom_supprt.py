# Generated by Django 2.2 on 2020-04-21 14:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coreapp', '0056_auto_20200420_1340'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectpricing',
            name='custom_supprt',
            field=models.FloatField(default=0.0),
        ),
    ]
