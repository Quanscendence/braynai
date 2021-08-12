from coreapp.choices import type_choices,GENDER_CHOICES,industry_choices
from login.models import Profile, Customer
from django.contrib.auth.models import User
from django import forms
from captcha.fields import CaptchaField

class ProfileForm(forms.ModelForm):
    '''writing the profile form for profile model to create customer details'''
    first_name = forms.CharField(max_length=500,widget=forms.TextInput(
           attrs={
                'class':"form-control",
                'placeholder':'First Name',
                'style' : 'height: 45px;'
           }
           ))
    last_name = forms.CharField(max_length=500,widget=forms.TextInput(
                  attrs={

                        'class':"form-control",
                       'placeholder':'Last Name',
                       'style' : 'height: 45px;'

                  }
                  ))

    email      = forms.EmailField(max_length=300,widget=forms.TextInput(
           attrs={

                'class':"form-control",
                'required':"required",
                'placeholder':'Email',
                'style' : 'height: 45px;'
           }
           ))
    # username      = forms.CharField(max_length=300,widget=forms.TextInput(
    #        attrs={
    #             'class':"form-control",
    #
    #             'placeholder':'Username'
    #        }
    #        ))
    password      = forms.CharField(max_length=300,widget=forms.PasswordInput(
           attrs={

                'class':"form-control",

                'placeholder':'Password',
                'style' : 'height: 45px;'
           }
           ))
    contact_no = forms.CharField(max_length=14,required=False,widget=forms.TextInput(
                  attrs={


                        'class':"form-control",
                       'placeholder':'Contact No.',
                       "pattern":"[\+()]*(?:\d[\s\-\.()xX]*){10,14}",
                       "oninvalid":"setCustomValidity('Please enter a valid phone number.')",
                       "onchange":"try{setCustomValidity('')}catch(e){}",
                         "id":'phone',
                       "style":"width:100%;height: 45px;",

                  }
                  ))


    class Meta:
        model = User
        fields = ('first_name','last_name','email','password')

class CustomerForm(forms.ModelForm):
    '''writing customer form to receive customer information'''

    # contact_no = forms.CharField(max_length=10,required=False,widget=forms.TextInput(
    #        attrs={
    #             'class':"form-control",
    #
    #             'placeholder':'Contact_no',
    #             "pattern":"[\+()]*(?:\d[\s\-\.()xX]*){10,14}",
    #             "oninvalid":"setCustomValidity('Please enter a valid phone number.')",
    #             "onchange":"try{setCustomValidity('')}catch(e){}",
    #        }
    #        ))
    # alternate_no = forms.CharField(max_length=10,required=False,widget=forms.TextInput(
    #        attrs={
    #             'class':"form-control",
    #
    #             'placeholder':'Alternate Contact no.',
    #             "pattern":"[\+()]*(?:\d[\s\-\.()xX]*){10,14}",
    #             "oninvalid":"setCustomValidity('Please enter a valid phone number.')",
    #             "onchange":"try{setCustomValidity('')}catch(e){}",
    #        }
    #        ))
    address_1 = forms.CharField(max_length=500,required=False,widget=forms.TextInput(
           attrs={
                'class':"form-control",
                'placeholder':'Address'
           }
           ))

    zipcode = forms.CharField(max_length=20,required=True,widget=forms.TextInput(
           attrs={

            'class':"form-control",
                'placeholder':'zipcode'
           }
           ))
    type =forms.ChoiceField(choices=type_choices,required=False,widget=forms.Select(
           attrs={
                    'class':"form-control",

                'placeholder':'type',
           }
           ))
    gender     = forms.ChoiceField(choices=GENDER_CHOICES,required=True,widget=forms.Select(
           attrs={
                'class':"form-control",
                'placeholder':'Gender',
                'style' : 'height: 45px'
           }
           ))
    dob = forms.DateField(required=False,widget=forms.TextInput(attrs={
                'class':"form-control",

            'placeholder':'DOB-ex-1990-06-22',
            'style' : 'height: 45px'

           }
           ))
    industry =forms.ChoiceField(choices=industry_choices,required=False,widget=forms.Select(
          attrs={

                'class':"form-control",
               'placeholder':'Industry',
          }
          ))

    company_address_1 = forms.CharField(max_length=500,required=False,widget=forms.TextInput(
           attrs={
                'class':"form-control",

                'placeholder':'Company Address'
           }
           ))

    company_name = forms.CharField(max_length=500,required=False,widget=forms.TextInput(
               attrs={
                    'class':"form-control",

                    'placeholder':'Company Name'
               }
               ))
    employee_strength = forms.CharField(max_length=50,required=False,widget=forms.NumberInput(
               attrs={
                    'class':"form-control",

                    'placeholder':'Employee Strength'
               }
               ))
    url = forms.CharField(required=False,widget=forms.TextInput(
               attrs={

                    'class':"form-control",
                    'placeholder':'URL'
               }
               ))
    image = forms.ImageField(required=False,widget=forms.FileInput(
               attrs={

                    'class':"form-control uploadlogo",
                    'placeholder':'image'
               }
               ))
    logo = forms.ImageField(required=False,widget=forms.FileInput(
               attrs={

                    'class':"form-control",
                    'placeholder':'image'
               }
               ))
    vat_gst_no = forms.CharField(required=False,widget=forms.TextInput(attrs={
                                                                 'class':'form-control' ,
                                                                 'placeholder':'VAT/GSTIN NO'
                                                                 }))
    class Meta:
        model= Customer
        fields=('type','gender','dob','industry','company_address_1','company_name','url')


class LoginForm(forms.Form):
   '''writing the login form to recieve login details from customer'''
   username=forms.CharField(widget=forms.TextInput(attrs={
                            'class':"form-control login_username",
                           'placeholder':'Email',
   }
   ))
   password=forms.CharField(widget=forms.PasswordInput(attrs={
                            'class':"form-control login_password",
                           'placeholder':'Password',
   }
   ))

class UpdateForm(forms.Form):
      '''update form class to receive the edited profile details of the customer'''
      type =forms.ChoiceField(choices=type_choices,required=False,widget=forms.Select(
             attrs={
                      'class':"form-control",
                      'onchange':"project_type()",
                  'placeholder':'type',
             }
             ))
      email      = forms.EmailField(max_length=300,widget=forms.TextInput(
             attrs={

                  'class':"form-control",

                  'placeholder':'Email',
                  'style' : 'height: 45px;'
             }
             ))
      first_name = forms.CharField(max_length=500,widget=forms.TextInput(
             attrs={
                  'class':"form-control",

                  'placeholder':'First Name'
             }
             ))
      last_name = forms.CharField(max_length=500,widget=forms.TextInput(
                    attrs={

                          'class':"form-control",
                         'placeholder':'Last Name',

                    }
                    ))



      contact_no = forms.DecimalField(required=False,widget=forms.TextInput(
                   attrs ={
                          'type':"tel",
                          'class':'form-control',
                          "name":"contact_no",
                          "pattern":"[\+()]*(?:\d[\s\-\.()xX]*){10,14}",
                          "oninvalid":"setCustomValidity('Please enter a valid phone number.')",
                          }))



      address_1 = forms.CharField(max_length=500,required=False,widget=forms.TextInput(
             attrs={
                  'class':"form-control",
                  'placeholder':'Address Line 1'
             }
             ))

      zipcode = forms.CharField(max_length=20,required=True,widget=forms.TextInput(
             attrs={

              'class':"form-control",
                  'placeholder':'zipcode'
             }
             ))
      company_address_1 = forms.CharField(max_length=500,required=False,widget=forms.TextInput(
             attrs={
                  'class':"form-control",

                  'placeholder':'Company Address Line 1'
             }
             ))

      company_name = forms.CharField(max_length=500,required=False,widget=forms.TextInput(
                 attrs={
                      'class':"form-control",

                      'placeholder':'Company Name'
                 }
                 ))
      employee_strength = forms.CharField(max_length=50,required=False,widget=forms.NumberInput(
                 attrs={
                      'class':"form-control",

                      'placeholder':'Employee Strength'
                 }
                 ))
      url = forms.URLField(required=False,widget=forms.TextInput(
                 attrs={

                      'class':"form-control",
                      'placeholder':'URL'
                 }
                 ))
      image = forms.ImageField(required=False, widget=forms.FileInput(
          attrs={'class':"form-control hidden_input_file",
                 'onchange':"readProfile(this)",
                 'hidden':'true',
                 'placeholder':'URL'
                 }
                 ))

      logo = forms.ImageField(required=False, widget=forms.FileInput(attrs={
                 'class':"form-control hidden_input_file logo_file",
                 'onchange':"readlogo(this)",
                 'hidden':'true',
                 'placeholder':'URL'
                 }
                 ))
      vat_gst_no = forms.CharField(required=False,widget=forms.TextInput(attrs={
                                                                 'class':'form-control' ,
                                                                 'placeholder':'VAT/GSTIN NO'
                                                                 }))


class PasswordResetForm(forms.Form):
    '''Writing password reset form to receive the email id of the customer to which password has to be changed'''
    email=forms.EmailField(max_length=300,widget=forms.TextInput(
           attrs={

                'class':"form-control",
                'placeholder':'Email',
                'style' : 'height: 45%;width:45%;border-radius:8px'

           }
           ))


class SignupLinkForm(forms.Form):
    company_address_1 = forms.CharField(max_length=200,required=False,widget=forms.TextInput(
               attrs={
                    'class':"form-control",

                    'placeholder':'Company Address'
               }
               ))

    company_name = forms.CharField(max_length=200,required=False,widget=forms.TextInput(
                   attrs={
                        'class':"form-control",

                        'placeholder':'Company Name'
                   }
                   ))
    employee_strength = forms.CharField(max_length=50,required=False,widget=forms.NumberInput(
                   attrs={
                        'class':"form-control",

                        'placeholder':'Employee Strength'
                   }
                   ))
    url = forms.URLField(required=False,widget=forms.TextInput(
                   attrs={

                        'class':"form-control",
                        'placeholder':'URL'
                   }
                   ))

    type =forms.ChoiceField(choices=type_choices,required=False,widget=forms.Select(
           attrs={
                    'class':"form-control",

                'placeholder':'type',
           }
           ))
    first_name = forms.CharField(max_length=50,widget=forms.TextInput(
           attrs={
                'class':"form-control",
                'placeholder':'First Name',
                'style' : 'height: 45px;'
           }
           ))
    last_name = forms.CharField(max_length=50,widget=forms.TextInput(
                  attrs={

                        'class':"form-control",
                       'placeholder':'Last Name',
                       'style' : 'height: 45px;'

                  }
                  ))

    # email      = forms.EmailField(max_length=300,widget=forms.TextInput(
    #        attrs={
    #
    #             'class':"form-control",
    #
    #             'placeholder':'Email',
    #             'style' : 'height: 45px;'
    #        }
    #        ))

    password      = forms.CharField(max_length=300,widget=forms.PasswordInput(
           attrs={

                'class':"form-control",

                'placeholder':'Password',
                'style' : 'height: 45px;'
           }
           ))
    contact_no = forms.CharField(max_length=10,required=False,widget=forms.TextInput(
                  attrs={


                        'class':"form-control",
                       'placeholder':'Contact No.',
                       "pattern":"[\+()]*(?:\d[\s\-\.()xX]*){10,14}",
                       "oninvalid":"setCustomValidity('Please enter a valid phone number.')",
                       "onchange":"try{setCustomValidity('')}catch(e){}",

                       "style":"width:48%;height: 45px;",

                  }
                  ))
    address_1 = forms.CharField(max_length=200,required=False,widget=forms.TextInput(
       attrs={
            'class':"form-control",

            'placeholder':'Address '
       }
       ))


    zipcode = forms.DecimalField(max_digits=10,required=False,widget=forms.NumberInput(
           attrs={

            'class':"form-control",
                'placeholder':'zipcode'
           }
           ))
    image = forms.ImageField(required=False,widget=forms.FileInput(
               attrs={

                    'class':"form-control",
                    'placeholder':'image'
               }
               ))
    gender     = forms.ChoiceField(choices=GENDER_CHOICES,required=False,widget=forms.Select(
           attrs={
                'class':"form-control",
                'placeholder':'Gender',
                'style' : 'height: 45px'
           }
           ))
    dob = forms.DateField(required=False,widget=forms.TextInput(attrs={
                'class':"form-control",

            'placeholder':'DOB-ex-1990-06-22',
            'style' : 'height: 45px'

           }
           ))
    industry =forms.ChoiceField(choices=industry_choices,required=False,widget=forms.Select(
          attrs={

                'class':"form-control",
               'placeholder':'Industry',
          }
          ))

class BasicSignupForm(forms.Form):
    '''Form to receive basic details from customer'''
    first_name = forms.CharField(max_length=50,widget=forms.TextInput(
           attrs={
                'class':"form-control",
                'placeholder':'First Name',
                'style' : 'height: 45px;'
           }
           ))
    last_name = forms.CharField(max_length=50,widget=forms.TextInput(
                  attrs={

                        'class':"form-control",
                       'placeholder':'Last Name',
                       'style' : 'height: 45px;'

                  }
                  ))

    email    = forms.EmailField(max_length=300,widget=forms.TextInput(
           attrs={

                'class':"form-control",

                'placeholder':'Email',
                'style' : 'height: 45px;'
           }
           ))
    contact_no = forms.CharField(max_length=10,widget=forms.TextInput(
                  attrs={


                        'class':"form-control",
                       'placeholder':'Contact No.',
                       "pattern":"[\+()]*(?:\d[\s\-\.()xX]*){10,14}",
                       "oninvalid":"setCustomValidity('Please enter a valid phone number.')",
                       "onchange":"try{setCustomValidity('')}catch(e){}",

                       "style":"height: 45px;",

                  }
                  ))
    # reason_to_contact = forms.CharField(max_length=300,widget=forms.TextInput(
    #         attrs={
    #
    #              'class':"form-control",
    #
    #              'placeholder':'Reason to Contact',
    #              'style' : 'height: 45px;'
    #         }
    #         ))
    # captcha = CaptchaField()
