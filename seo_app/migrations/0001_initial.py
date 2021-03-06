# Generated by Django 2.2 on 2019-12-19 05:13

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SiteSeo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('choices', models.CharField(choices=[('Home', 'Home'), ('Signup', 'Signup'), ('Login', 'Login'), ('Dashboard', 'Dashboard'), ('Project Creation', 'Project Creation'), ('Project Details', 'Project Details'), ('Single Project Details', 'Single Project Details'), ('Update Profile', 'Update Profile'), ('User Management', 'User Management'), ('Delete Project', 'Delete Project'), ('Restore Project', 'Restore Project'), ('Password Reset', 'Password Reset'), ('User Signup', 'User Signup'), ('Basic Signup', 'Basic Signup'), ('Google Drive Integration', 'Google Drive Integration'), ('DropBox Integration', 'DropBox Integration')], max_length=50)),
                ('seo_title', models.CharField(max_length=100)),
                ('seo_description', models.CharField(max_length=100)),
                ('seo_keyword', models.CharField(max_length=50)),
            ],
        ),
    ]
