# Generated by Django 2.2 on 2020-04-26 14:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('coreapp', '0059_delete_endpointalgorithm'),
    ]

    operations = [
        migrations.CreateModel(
            name='EndPointAlgorithm',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, default='Unknown...', max_length=200, null=True)),
                ('description', models.TextField(blank=True, default='some text...', null=True)),
                ('version', models.PositiveIntegerField(blank=True, null=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Created date')),
                ('updated', models.DateTimeField(auto_now=True, null=True, verbose_name='Updated date')),
                ('feature', models.CharField(max_length=1000)),
                ('accuracy', models.IntegerField()),
                ('type_of_prediction', models.CharField(choices=[('Classification', 'Classification'), ('Linear', 'Linear')], max_length=100)),
                ('y_factor', models.CharField(blank=True, max_length=100, null=True)),
                ('model_id', models.CharField(max_length=1000)),
                ('end_point', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='coreapp.ProjectEndPoint')),
            ],
            options={
                'ordering': ('name',),
                'abstract': False,
            },
        ),
    ]
