# Generated by Django 2.2 on 2020-02-11 14:32

from django.db import migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('coreapp', '0026_dataframedisplay'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataframedisplay',
            name='df',
            field=jsonfield.fields.JSONField(default=dict),
        ),
    ]
