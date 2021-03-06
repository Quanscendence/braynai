# Generated by Django 2.2 on 2020-01-25 10:32

from django.db import migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('coreapp', '0010_auto_20200125_1235'),
    ]

    operations = [
        migrations.RenameField(
            model_name='projectmetadata',
            old_name='js',
            new_name='columns',
        ),
        migrations.RemoveField(
            model_name='projectmetadata',
            name='connectivity_column',
        ),
        migrations.AddField(
            model_name='projectmetadata',
            name='meta_data',
            field=jsonfield.fields.JSONField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='projectjsonstorage',
            name='columns',
            field=jsonfield.fields.JSONField(blank=True, null=True),
        ),
    ]
