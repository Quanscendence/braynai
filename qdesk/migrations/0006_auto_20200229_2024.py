# Generated by Django 2.2.7 on 2020-02-29 14:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('qdesk', '0005_ticketissue_solution_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='priority',
            field=models.CharField(choices=[('High', 'High'), ('Low', 'Low'), ('Medium', 'Medium')], max_length=10),
        ),
        migrations.CreateModel(
            name='TicketTransaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, default='Unknown...', max_length=200, null=True)),
                ('description', models.TextField(blank=True, default='some text...', null=True)),
                ('version', models.PositiveIntegerField(blank=True, null=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created date')),
                ('updated', models.DateTimeField(auto_now=True, null=True, verbose_name='Updated date')),
                ('from_value', models.CharField(blank=True, max_length=50, null=True)),
                ('to_value', models.CharField(blank=True, max_length=50, null=True)),
                ('ticket', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='qdesk.Ticket')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('name',),
                'abstract': False,
            },
        ),
    ]
