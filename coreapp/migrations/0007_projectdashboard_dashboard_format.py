# Generated by Django 2.2 on 2020-01-08 09:20

from django.db import migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('coreapp', '0006_auto_20191229_1758'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectdashboard',
            name='dashboard_format',
            field=jsonfield.fields.JSONField(blank=True, null=True),
        ),
    ]
