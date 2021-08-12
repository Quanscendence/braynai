# Generated by Django 2.2 on 2020-01-28 03:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('coreapp', '0011_auto_20200125_1602'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectFilename',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(blank=True, default='some text...', null=True)),
                ('version', models.PositiveIntegerField(blank=True, null=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created date')),
                ('updated', models.DateTimeField(auto_now=True, null=True, verbose_name='Updated date')),
                ('name', models.CharField(max_length=200)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='coreapp.Project')),
            ],
            options={
                'ordering': ('name',),
                'abstract': False,
            },
        ),
    ]
