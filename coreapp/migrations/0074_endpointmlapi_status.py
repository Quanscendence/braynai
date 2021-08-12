# Generated by Django 2.2 on 2020-07-28 11:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coreapp', '0073_auto_20200728_1624'),
    ]

    operations = [
        migrations.AddField(
            model_name='endpointmlapi',
            name='status',
            field=models.CharField(choices=[('OPEN', 'OPEN'), ('PROCESSED', 'PROCESSED'), ('CANCELLED', 'CANCELLED')], default='OPEN', max_length=7),
        ),
    ]