# Generated by Django 2.2 on 2020-02-02 22:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coreapp', '0015_projectendpoint_alignment_object'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='plot',
            name='dashboard_query',
        ),
        migrations.RemoveField(
            model_name='projectdashboard',
            name='title',
        ),
        migrations.RemoveField(
            model_name='projectquery',
            name='js_storage',
        ),
    ]