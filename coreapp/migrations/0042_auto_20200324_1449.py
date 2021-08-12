# Generated by Django 2.2 on 2020-03-24 09:19

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('coreapp', '0041_projectbillingdaycost_projectbillinghourlycost_projectbillingmonthcost'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectendpoint',
            name='sub_df',
            field=jsonfield.fields.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='projectendpoint',
            name='sub_df_frequency',
            field=models.CharField(choices=[('Daily', 'Daily'), ('Weekly', 'Weekly'), ('15 Days', '15 Days'), ('1 Month', '1 Month'), ('6 Months', '6 Months'), ('Quarterly', 'Quarterly'), ('Yearly', 'Yearly')], max_length=30, null=True),
        ),
    ]
