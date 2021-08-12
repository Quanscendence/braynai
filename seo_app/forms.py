from django import forms
from .models import SiteSeo
from .choices import PageChoice




class SiteSeoForm(forms.ModelForm):
#writing a seo form for seo model to receive the data
    class Meta:
        model=SiteSeo
        fields=('choices','seo_title','seo_description','seo_keyword')
