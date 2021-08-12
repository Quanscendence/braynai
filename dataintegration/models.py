from django.db import models
import jsonfield
from coreapp.choices import INTEGRATION_CHOICES,DATA_UPLOAD_RANGE_CHOICES
from coreapp.models import ProjectType,Project
from login.models import Profile,Customer
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django_cryptography.fields import encrypt
# Create your models here.

################## base #############
class Base(models.Model):
    '''
    A Base case mostly common for all the implementations
    '''
    name        = models.CharField(default="Unknown...", max_length=200,blank=True, null=True)
    description = models.TextField(default="some text...",blank=True, null=True)
    version     = models.PositiveIntegerField(blank=True, null=True)
    created     = models.DateTimeField('Created date', auto_now_add=True,
                                   auto_now=False,
                                   null=True, blank=True)
    updated     = models.DateTimeField('Updated date', auto_now_add=False,auto_now=True,null=True, blank=True)
    class Meta(object):
        abstract=True
        #unique_together = (("name", "version"),)
        ordering=('name',)

    def __str__(self):
        return self.name


'''start of class to save the credentials by the user to connect googledrive'''
class CustomerAPIDetails(Base):
    project = models.ForeignKey(Project,on_delete=models.CASCADE)
    access_token = models.CharField(max_length=200)
    integration_choice = models.CharField(max_length=200,choices=INTEGRATION_CHOICES)
    credentials = models.FileField(upload_to='credentials_file')
    sheet_url  = models.CharField(max_length=500,null=True,blank=True)
    sheet_header = models.PositiveIntegerField(default=1)
    file_id = models.CharField(max_length=200,null=True)
    api = models.URLField(null=True,blank=True)
    token = models.CharField(max_length=1000,null=True,blank=True)
    client_id = models.CharField(max_length=200,null=True)
    client_secret_key =models.CharField(max_length=200,null=True)
    range = models.CharField(max_length=200,choices=DATA_UPLOAD_RANGE_CHOICES,default='')
    token_file = models.CharField(max_length=1000,null=True)


    def __str__(self):
        return self.project.admin_user.first_name
'''end of class to save the credentials by the user to connect googledrive'''
