# Generated by Django 2.2 on 2020-01-28 03:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coreapp', '0012_projectfilename'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectfilename',
            name='file_name',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='projectfilename',
            name='name',
            field=models.CharField(blank=True, default='Unknown...', max_length=200, null=True),
        ),
    ]