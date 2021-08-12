from django.db import models
from coreapp.choices import type_choices,industry_choices,GENDER_CHOICES
from django.contrib.auth.models import User,Group
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


class Profile(Base):
    '''Base Models Create Profile for all type of Users '''
    user           = models.OneToOneField(User, on_delete=models.CASCADE)
    contact_no     = models.CharField(max_length=10,null=True)
    address_1      = models.CharField(max_length=500, blank=True, null=True)
    zipcode        = models.CharField(max_length=500, blank=True, null=True)
    
    group          = models.ForeignKey(Group, on_delete=models.CASCADE,null=True)
    email_confirmed = models.BooleanField(default=False)

    
    class Meta:
        abstract=True

class Customer(Profile):
    '''Customer is complete Model inherited From Profile for Customer of DSaaS'''
    type              = models.CharField(max_length=50,choices=type_choices)
    gender            = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    dob               = models.DateField(verbose_name="Date Of Birth", blank=True, null=True)
    image             = models.ImageField(null=True,blank=True)
    logo              = models.ImageField(null=True,blank=True)
    industry          = models.CharField(max_length=500,choices=industry_choices,null=True)
    company_name      = models.CharField(max_length=500,null=True)
    company_address_1 = models.CharField(max_length=500,null=True)
    employee_strength = models.CharField(max_length=500,null=True)
    url               = models.URLField(max_length=100)
    vat_gst_no        = models.CharField(max_length=500,null=True)
    

    def __str__(self):
        return self.user.username
