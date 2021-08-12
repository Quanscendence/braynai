from django import forms
from coreapp.choices import DATA_UPLOAD_RANGE_CHOICES

'''Form to receive the googledrive credentials file and file name '''
class DriveDetailsForm(forms.Form):
    credential = forms.FileField(widget=forms.FileInput(
    attrs={
         'class':"form-control",

         'placeholder':'Accept',

    }
    ))
    file_id = forms.CharField(widget=forms.TextInput(
    attrs={
         'class':"form-control",

         'placeholder':'spreadsheet name',

    }
    ))

'''Form to receive the googlesheet credentials file and file name '''
class SheetDetailsForm(forms.Form):
    sheet_name = forms.CharField(widget=forms.TextInput(
    attrs={
         'class':"form-control",

         'placeholder':'integration name',
         'maxlength':15,

    }
    ))
    credential = forms.FileField(widget=forms.FileInput(
    attrs={
         'class':"form-control",

         'placeholder':'Accept',

    }
    ))
    spreadsheet_id = forms.CharField(widget=forms.TextInput(
    attrs={
         'class':"form-control",

         'placeholder':'spreadsheet name',

    }
    ))
    data_range = forms.ChoiceField(choices=DATA_UPLOAD_RANGE_CHOICES, widget=forms.Select(
        attrs={
         'class':"form-control",

         'placeholder':'data_range',

        }
    ))
    sheet_header = forms.IntegerField(required=False,widget=forms.NumberInput(attrs={'class':'form-control','placeholder':'the data starts from row default 1','min':'1'}))

'''Form to receive the dropbox details '''
class DropboxDetailsForm(forms.Form):
    access_token= forms.CharField(widget=forms.TextInput(
    attrs={
         'class':"form-control",

         'placeholder':'Access Token',

    }
    ))
    path_name= forms.CharField(widget=forms.TextInput(
    attrs={
         'class':"form-control",

         'placeholder':'File path',

    }
    ))
    data_range = forms.ChoiceField(choices=DATA_UPLOAD_RANGE_CHOICES, widget=forms.Select(
    attrs={
         'class':"form-control",

         'placeholder':'data_range',

    }
    ))

class OneDriveDetailsForm(forms.Form):
    client_id= forms.CharField(widget=forms.TextInput(
    attrs={
         'class':"form-control",

         'placeholder':'Client id',

    }
    ))
    client_secret_key= forms.CharField(widget=forms.TextInput(
    attrs={
         'class':"form-control",

         'placeholder':'Client Secret Key',

    }
    ))
    # path_name= forms.CharField(widget=forms.TextInput(
    # attrs={
    #      'class':"form-control",
    #
    #      'placeholder':'File path',
    #
    # }
    # ))


class ApiDataForm(forms.Form):
    ''' class to add the api data integration'''
    api_name = forms.CharField(widget=forms.TextInput(
    attrs={
         'class':"form-control",

         'placeholder':'integration name',
         'maxlength':15,

    }
    ))
    api = forms.CharField(required=True,max_length=1000,widget=forms.TextInput(attrs={'id':'endpoint_name_field',
                                                                                'class':'form-control',
                                                                                'required':'true',
                                                                                'placeholder':'URL' }))
    basic_token = forms.CharField(required=False,max_length=1000,widget=forms.TextInput(attrs={'id':'endpoint_name_field',
                                                                                'class':'form-control',
                                                                                'placeholder':'Token/Secret key' }))

    frequency = forms.ChoiceField(required=True,choices=DATA_UPLOAD_RANGE_CHOICES,widget=forms.Select(attrs={'class':'form-control'}))


'''form for google sheet  with shared url'''

class SheetUrlForm(forms.Form):
    sheet_url_name = forms.CharField(widget=forms.TextInput(
    attrs={
         'class':"form-control",

         'placeholder':'integration name',
         'maxlength':15,

    }
    ))
    url = forms.CharField(widget=forms.TextInput(
    attrs={
         'class':"form-control",

         'placeholder':'spreadsheet URL',

    }
    ))
    header = forms.IntegerField(required=False,widget=forms.NumberInput(attrs={'class':'form-control','placeholder':'the data starts from row default 1','min':'1'}))
    cron_frequency = forms.ChoiceField(choices=DATA_UPLOAD_RANGE_CHOICES, widget=forms.Select(
        attrs={
         'class':"form-control",

         'placeholder':'data_range',

        }
    ))