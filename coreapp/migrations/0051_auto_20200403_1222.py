# Generated by Django 2.2 on 2020-04-03 06:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coreapp', '0050_auto_20200331_1809'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tax',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, default='Unknown...', max_length=200, null=True)),
                ('description', models.TextField(blank=True, default='some text...', null=True)),
                ('version', models.PositiveIntegerField(blank=True, null=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created date')),
                ('updated', models.DateTimeField(auto_now=True, null=True, verbose_name='Updated date')),
                ('tax_percentage', models.PositiveIntegerField()),
                ('tax_no', models.CharField(max_length=50)),
            ],
            options={
                'ordering': ('name',),
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='projectinvoice',
            name='tax_amount',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='projectinvoice',
            name='total_amount',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='projectinvoice',
            name='transaction_id',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='projectpricing',
            name='free_tire',
            field=models.BooleanField(default=False),
        ),
    ]