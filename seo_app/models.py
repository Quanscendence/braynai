from django.db import models
from .choices import PageChoice


# Create your models here.


class SiteSeo(models.Model):
    '''creating different fields for a SiteSeo model'''
    choices         = models.CharField(max_length=50,choices=PageChoice)
    seo_title       = models.TextField()
    seo_description = models.TextField()
    seo_keyword     = models.TextField()
    def __str__(self):
        return self.choices
