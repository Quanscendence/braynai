# Generated by Django 2.2 on 2020-04-03 17:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coreapp', '0051_auto_20200403_1222'),
    ]

    operations = [
        migrations.AddField(
            model_name='tax',
            name='tax_representation',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
    ]
