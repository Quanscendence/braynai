# Generated by Django 2.2 on 2020-08-01 05:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dataintegration', '0003_auto_20200728_1624'),
    ]

    operations = [
        migrations.AddField(
            model_name='customerapidetails',
            name='sheet_url',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
