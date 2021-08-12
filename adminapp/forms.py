from django import forms
from coreapp.models import ProjectPricing,Tax
from dal import forward,autocomplete
from coreapp.models import Project
from coreapp.choices import API_REQUEST_CHOICES



class ConversionInputs(forms.Form):
    '''Form class to get conversion inputs like symbol and relevant function for the symbol'''
    character = forms.CharField(widget=forms.TextInput(
    attrs={
         'class':"form-control",
         'placeholder':'Enter the Character',
         }
         ))
    function = forms.CharField(widget=forms.TextInput(
    attrs={
         'class':"form-control",
         'placeholder':'Enter conversion details',
         }
         ))


class ProjectPricingForm(forms.ModelForm):
     user      = forms.FloatField(widget=forms.NumberInput(attrs={
                                                                 'class':'form-control',
                                                                 'min':'0',
                                                                      }))
     end_point = forms.FloatField(widget=forms.NumberInput(attrs={
                                                                      'class':'form-control',
                                                                      'min':'0',
                                                                      }))

     disk_space = forms.FloatField(widget=forms.NumberInput(attrs={
                                                                      'class':'form-control',
                                                                      'min':'0',
                                                                      }))
     iqs = forms.FloatField(widget=forms.NumberInput(attrs={
                                                                 'class':'form-control',
                                                                 'min':'0',
                                                                      }))

     free_tire = forms.CharField(required=False,widget=forms.CheckboxInput(attrs={

                                                                      }))
     monthly_maintenance = forms.FloatField(widget=forms.NumberInput(attrs={
                                                                      'class':'form-control',
                                                                      'min':'0',
                                                                      }))

     class Meta:
          model= ProjectPricing
          exclude =['name','version','created','updated','description','custom_supprt']

class SingleProjectPricing(forms.Form):
     user      = forms.FloatField(widget=forms.NumberInput(attrs={
                                                                 'class':'form-control',
                                                                 'min':'0',
                                                                      }))
     end_point = forms.FloatField(widget=forms.NumberInput(attrs={
                                                                      'class':'form-control',
                                                                      'min':'0',
                                                                      }))

     disk_space = forms.FloatField(widget=forms.NumberInput(attrs={
                                                                      'class':'form-control',
                                                                      'min':'0',
                                                                      }))
     iqs = forms.FloatField(widget=forms.NumberInput(attrs={'class':'form-control',
                                                                        'min':'0',

                                                                      }))
     monthly_maintenance = forms.FloatField(widget=forms.NumberInput(attrs={
                                                                      'class':'form-control',
                                                                      'min':'0',
                                                                      }))

     custom_cost = forms.CharField(required=False,widget=forms.NumberInput(attrs={
                                                                      'class':'form-control',
                                                                      }))
     project    = forms.ModelChoiceField(queryset=Project.objects.all(),widget=autocomplete.ModelSelect2(attrs={
                                                                      'class':'form-control',
                                                                      }))
     free_tire = forms.CharField(required=False,widget=forms.CheckboxInput(attrs={
                                                                      
                                                                      }))


class TaxForm(forms.ModelForm):
     name = forms.CharField(max_length=30,widget=forms.TextInput(attrs={
                                                                      'class':'form-control',
                                                                      }))
     tax_representation = forms.CharField(max_length=30,widget=forms.TextInput(attrs={
                                                                      'class':'form-control',
                                                                      }))
     tax_percentage = forms.IntegerField(widget=forms.NumberInput(attrs={'class':'form-control',
                                                                      }))
     tax_no  = forms.CharField(max_length=30,widget=forms.TextInput(attrs={
                                                                      'class':'form-control',
                                                                      }))
     class Meta:
          model= Tax
          exclude =['version','created','updated','description']



class ApiRequestForm(forms.Form):
  '''form to edit the apr request'''
  status = forms.ChoiceField(choices=API_REQUEST_CHOICES, widget=forms.Select(attrs={'class':'form-control'}))
  api    = forms.CharField(required=False,widget=forms.TextInput(attrs={'class':'form-control'}))
  token    = forms.CharField(required=False,widget=forms.TextInput(attrs={'class':'form-control'}))