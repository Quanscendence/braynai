# Generated by Django 2.2 on 2020-05-09 13:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coreapp', '0067_auto_20200505_2334'),
    ]

    operations = [
        migrations.AddField(
            model_name='plot',
            name='facet_col',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
