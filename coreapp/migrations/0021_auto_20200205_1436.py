# Generated by Django 2.2 on 2020-02-05 09:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coreapp', '0020_auto_20200205_1359'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='project_duration',
            field=models.CharField(blank=True, choices=[('1 Month', '1 Month'), ('3 Month', '3 Month'), ('6 Months', '6 Months'), ('Quarterly', 'Quarterly'), ('Yearly', 'Yearly')], max_length=20, null=True),
        ),
    ]
