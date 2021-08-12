from django.contrib import admin
from login.models import User,Profile,Customer
from . import models
# Register your models here.

class CustomerAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'name',
        'description',
        'version',
        'created',
        'updated',
        'user',
        'contact_no',
        'address_1',
        'zipcode',
        'group',
        'gender',
        'dob',
        'image',
        'industry',
        'company_name',
        'company_address_1',
        'employee_strength',
        'url',
    )
    list_filter = (
        'created',
        'updated',
        'user',
        'group',
        'dob',
        'id',
        'name',
        'description',
        'version',
        'created',
        'updated',
        'user',
        'contact_no',
        'address_1',
        'zipcode',
        'group',
        'type',
        'gender',
        'dob',
        'image',
        'industry',
        'company_name',
        'company_address_1',
        'employee_strength',
        'url',
    )
    search_fields = ('name',)
def _register(model, admin_class):
    admin.site.register(model, admin_class)

_register(models.Customer, CustomerAdmin)
