# Generated by Django 2.2 on 2020-08-03 05:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('coreapp', '0075_auto_20200728_2143'),
        ('qdesk', '0006_auto_20200229_2024'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticketissue',
            name='project',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='coreapp.Project'),
        ),
    ]