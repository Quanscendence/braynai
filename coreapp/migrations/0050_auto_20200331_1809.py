# Generated by Django 2.2 on 2020-03-31 12:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coreapp', '0049_auto_20200330_1909'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectbillingmonthcost',
            name='iqs_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='projectinvoice',
            name='invoice_id',
            field=models.CharField(max_length=20),
        ),
    ]