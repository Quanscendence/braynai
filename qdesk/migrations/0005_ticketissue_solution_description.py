# Generated by Django 2.2.7 on 2020-02-29 11:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qdesk', '0004_ticketissue_ticket_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticketissue',
            name='solution_description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
