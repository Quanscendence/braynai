from django import forms
from .choices import type_choices,GENDER_CHOICES,industry_choices,PROJECT_TYPE,permission_choice,dashboard_choices,DATA_UPLOAD_RANGE_CHOICES, \
    PROJECT_DURATION_CHOICES, PROJECT_DASHBOARD_PERMISSION_CHOICES
from coreapp.models import FileUpload, ProjectUser,ProjectDashboard,IndustryChoices, ProjectDashboard, ProjectEndPoint
import os
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from dal import forward,autocomplete



class ProjectForm(forms.Form):
    '''writing project form to receive project details'''
    project_title= forms.CharField(max_length=15,widget=forms.TextInput(attrs={
                             'class':"form-control",
                            'placeholder':'Enter Project Title ',
                            }
                            ))

    # project_type=forms.ChoiceField(choices=PROJECT_TYPE,widget=forms.Select(attrs={
    #                              'class':"form-control",
    #                         'placeholder':'Project type',
    #                         }
    #                         ))
    industry = forms.ModelChoiceField(
                                            queryset=IndustryChoices.objects.all(),
                                            widget=autocomplete.ModelSelect2(
                                                   attrs={
                                                        'class':"form-control ",


                                                   }
                                                   ))
    end_goal =  forms.CharField(widget=forms.TextInput(attrs={
                             'class':"form-control",
                            'placeholder':'Expected Answer ',
                            }
                            ))
    project_duration = forms.ChoiceField(choices=PROJECT_DURATION_CHOICES,widget=forms.Select(attrs={
                             'class':"form-control",
                            }
                            ))
    files  = forms.FileField(required=False,widget=forms.FileInput(attrs={'multiple':True,
                                'class':"form-control input_files",
                                'placeholder':'File 1',
                                'accept':'.csv, .xlsx, .xls,'
                            }
                            ))
    # file_2  = forms.FileField(required=False,widget=forms.FileInput(attrs={
    #                         'class':"form-control",
    #                         'placeholder':'File 2',
    #                         }
    #                         ))
    # file_3  = forms.FileField(required=False,widget=forms.FileInput(attrs={
    #                         'class':"form-control",
    #                         'placeholder':'File 3',
    #                         }
    #                         ))
    # data_title= forms.CharField(max_length=100,widget=forms.TextInput(attrs={
    #
    #                         'placeholder':'Enter DataFrame Title ',
    #                         }
    #                         ))
    data_description= forms.CharField(max_length=100,widget=forms.TextInput(attrs={
                                'class':"form-control",
                            'placeholder':'Enter Data Description',
                            }
                            ))
    # def clean_file_1(self):
    #     file = self.cleaned_data.get("file_1")
    #     ext = os.path.splitext(file.name)[1]  # [0] returns path+filename
    #     valid_extensions = ['.csv', '.doc', '.docx', '.xlsx', '.xls']
    #     if not ext.lower() in valid_extensions:
    #         raise ValidationError(u'Unsupported file extension.')



class Fileform(forms.Form):
    file_1 = forms.FileField(widget=forms.FileInput(attrs={
                                                    "accept":".csv"
                                                    }))
    def clean_file_1(self):
        file = self.cleaned_data.get("file_1")
        ext = os.path.splitext(file.name)[1]  # [0] returns path+filename
        valid_extensions = ['.csv', '.doc', '.docx', '.xlsx', '.xls']
        if not ext.lower() in valid_extensions:
            print('Unsupported file extension.')
            raise ValidationError(u'Unsupported file extension.')




class FileUploadForm(forms.Form):
    '''writing file upload form to receive extra file uploadeds by the customer'''
    files  = forms.FileField(required=False,widget=forms.FileInput(attrs={'multiple':True,
                                'class':"form-control",
                            'placeholder':'File 1',
                            'accept':'.csv'
                            }
                            ))


class ProjectUpdateForm(forms.Form):
    '''Writing project update form to receive edited details of the project'''
    project_title= forms.CharField(max_length=15,widget=forms.TextInput(attrs={
                             'class':"form-control",
                            'placeholder':'Enter Project Title ',
                            }
                            ))
    industry = forms.ModelChoiceField(
                                            queryset=IndustryChoices.objects.all(),
                                            widget=autocomplete.ModelSelect2(
                                                   attrs={
                                                        'class':"form-control ",


                                                   }))

    project_duration = forms.ChoiceField(choices=PROJECT_DURATION_CHOICES,widget=forms.Select(attrs={
                             'class':"form-control",
                            }
                            ))

class AddUsersForm(forms.Form):
    '''writing add users form to add the users for company profile'''
    email=forms.EmailField(max_length=300,widget=forms.TextInput(
               attrs={

                    'class':"form-control",
                    'placeholder':'Email',


               }
               ))
    permissions=forms.ChoiceField(choices=permission_choice,widget=forms.Select(
           attrs={
                    'class':"form-control",

                    'placeholder':'type',

           }
           ))


class AcceptForm(forms.Form):
        accept = forms.CharField(widget=forms.CheckboxInput(
        attrs={
             'class':"form-control",

             'placeholder':'Accept',

        }
        ))


class FormFile(forms.Form):
    file_1  = forms.FileField(required=False,widget=forms.FileInput(attrs={
                                'class':"form-control",
                            'placeholder':'File 1',
                            }
                            ))
    file_2  = forms.FileField(required=False,widget=forms.FileInput(attrs={
                            'class':"form-control",
                            'placeholder':'File 2',
                            }
                            ))
    file_3  = forms.FileField(required=False,widget=forms.FileInput(attrs={
                            'class':"form-control",
                            'placeholder':'File 3',
                            }
                            ))

class ProjectDashboardForm(forms.Form):
    '''form to save the dashboard'''
    name = forms.CharField(required=True,widget=forms.TextInput(attrs={'class':'form-control','onkeyup':'displayProjectName()','id':'project_name','maxlength':20
        }))
    algorithm = forms.CharField(required=False,widget=forms.TextInput(attrs={'class':'form-control',
        }))
    email_users = forms.CharField(required=False,widget=forms.TextInput(attrs={'class':'form-control',
        }))
    report_frequency = forms.ChoiceField(required=False,choices=DATA_UPLOAD_RANGE_CHOICES,widget=forms.Select(attrs={'class':'form-control',}))

    dashboard = forms.ModelChoiceField(required=False,queryset=ProjectDashboard.objects.all(),widget=autocomplete.ModelSelect2(attrs={'onchange':'dashboardAjax()'}))
    user      = forms.ModelMultipleChoiceField(required=False,queryset=ProjectUser.objects.all(),widget=autocomplete.ModelSelect2Multiple(attrs={'style':'display:none;'}))
    dashboard_for = forms.ChoiceField(required=True,choices=PROJECT_DASHBOARD_PERMISSION_CHOICES,widget=forms.Select(attrs={
     'class':'form-control',
     'onchange':'dashboardFor()'
    }))

class ProjectDashboardEditForm(forms.Form):
    '''form to edit the dashboard'''
    name = forms.CharField(required=True,widget=forms.TextInput(attrs={'class':'form-control','onkeyup':'displayProjectName()','id':'project_name','maxlength':20
        }))
    algorithm = forms.CharField(required=False,widget=forms.TextInput(attrs={'class':'form-control',
        }))
    email_users = forms.CharField(required=False,widget=forms.TextInput(attrs={'class':'form-control',
        }))
    report_frequency = forms.ChoiceField(required=False,choices=DATA_UPLOAD_RANGE_CHOICES,widget=forms.Select(attrs={'class':'form-control',}))

    user      = forms.ModelMultipleChoiceField(required=False,queryset=ProjectUser.objects.all(),widget=autocomplete.ModelSelect2Multiple(attrs={}))
    dashboard_for = forms.ChoiceField(required=True,choices=PROJECT_DASHBOARD_PERMISSION_CHOICES,widget=forms.Select(attrs={
     'class':'form-control',
     'onchange':'dashboardFor()'
    }))

class ProjectDashboardsForm(forms.Form):
    project = forms.CharField(required=True,widget=forms.TextInput(attrs={'class':'form-control','onkeyup':'displayProjectName()','id':'project_name','maxlength':20
        }))
    dashboard = forms.ModelChoiceField(required=True,queryset=ProjectDashboard.objects.all(),widget=autocomplete.ModelSelect2(url='coreapp:dashboard-autocomplete',forward=['project'],attrs={'onchange':'dashboardAjax()'}))


class ProjectEndPointForm(forms.Form):
    ''' form class  to create endpoint with frequency'''
    end_point_name = forms.CharField(required=True,max_length=50,widget=forms.TextInput(attrs={'id':'endpoint_name_field',
                                                                                'class':'form-control',
                                                                                'placeholder':'Name' }))
    frequency = forms.ChoiceField(required=True,choices=DATA_UPLOAD_RANGE_CHOICES,widget=forms.Select(attrs={'class':'form-control'}))

class ApidataForm(forms.Form):
    ''' form class  to create endpoint with frequency'''
    api_name = forms.CharField(widget=forms.TextInput(
    attrs={
         'class':"form-control",

         'placeholder':'integration name',
         'maxlength':15,

    }
    ))
    api = forms.CharField(required=False,max_length=500,widget=forms.TextInput(attrs={'id':'endpoint_name_field',
                                                                                'class':'form-control',
                                                                                'placeholder':'URL' }))
    basic_token = forms.CharField(required=False, max_length=50, widget=forms.TextInput(attrs={'id': 'endpoint_name_field',
                                                                                      'class': 'form-control',
                                                                                      'placeholder': 'Token/Secret key'}))
    frequency = forms.ChoiceField(required=False,choices=DATA_UPLOAD_RANGE_CHOICES,widget=forms.Select(attrs={'class':'form-control'}))

class AddonFileForm(forms.Form):
    """docstring for AddonFileForm."""
    files  = forms.FileField(required=False,widget=forms.FileInput(attrs={'multiple':True,
                                'class':"form-control input_files addon_file",
                                'placeholder':'File 1',
                                'id':"id_files",
                                'accept':'.csv, .xlsx, .xls,'
                            }
                            ))
    industry = forms.ModelChoiceField(
                                            queryset=IndustryChoices.objects.all(),
                                            widget=autocomplete.ModelSelect2(
                                                   attrs={
                                                        'class':"form-control ",


                                                   }
                                                   ))
