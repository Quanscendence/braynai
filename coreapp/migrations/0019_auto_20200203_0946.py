# Generated by Django 2.2 on 2020-02-03 04:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coreapp', '0018_auto_20200203_0916'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='delete_datetime',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='end_goal',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
