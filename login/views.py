from django.shortcuts import render,redirect
from django.views.generic import TemplateView,CreateView,View,UpdateView,ListView
from login.forms import CustomerForm,ProfileForm,UpdateForm,PasswordResetForm,SignupLinkForm,LoginForm,BasicSignupForm
from login.models import Customer
from django.core.mail import send_mail
from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.db.models import Q
import urllib.request
import urllib.parse
from django.contrib.auth.models import User,Group
import random
from coreapp.models import Project,ProjectUser,UserNotification
from django.contrib.auth import authenticate,login
from django.contrib.auth.mixins import LoginRequiredMixin
from seo_app.models import SiteSeo
from django.http import JsonResponse
###password reset###
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
# Create your views here.
from actstream import action
from braces.views import GroupRequiredMixin
import re
from .tokens import account_activation_token
from django.template.loader import render_to_string


'''function to send sms using text local'''
def sendSMS(numbers,message):
    data =  urllib.parse.urlencode({'apikey': 'PfIdpBsAQu0-MSbkQMgPH9zQXa2KmC26oUVTQwna33', 'numbers': numbers,
        'message' : message, })
    data = data.encode('utf-8')
    request = urllib.request.Request("https://api.textlocal.in/send/?")
    f = urllib.request.urlopen(request, data)
    fr = f.read()
    return(fr)

'''start of customer sign up class '''
class CustomerSignUpView(CreateView):
    model=Customer,User
    def get(self,request):
        '''start of customer sign up get view to display user and customer form '''
        seo=SiteSeo.objects.get(choices='Signup')
        template_name='login/signup.html'
        profile_form=ProfileForm()
        customer_form=CustomerForm()
        context={
            'profile_form':profile_form,
            'customer_form':customer_form,
            'seo':seo

        }
        return render(request,template_name,context)
    def post(self,request):
        '''start of customer sign up post view to receive details from customer and save data '''
        template_name='login/signup.html'
        seo=SiteSeo.objects.get(choices='Signup')
        profile_form=ProfileForm(request.POST)
        customer_form=CustomerForm(request.POST,request.FILES)
        if profile_form.is_valid() and customer_form.is_valid():
            print('valid')
            first_name = profile_form.cleaned_data['first_name']
            last_name = profile_form.cleaned_data['last_name']
            email = profile_form.cleaned_data['email']
            password = profile_form.cleaned_data['password']
            contact_no = request.POST['contact_no']
            address_1 = customer_form.cleaned_data['address_1']

            zipcode = customer_form.cleaned_data['zipcode']
            # type = customer_form.cleaned_data['type']
            type="Company"
            gender = customer_form.cleaned_data['gender']
            dob = customer_form.cleaned_data['dob']
            industry = customer_form.cleaned_data['industry']

            company_name = customer_form.cleaned_data['company_name']
            company_address_1 = customer_form.cleaned_data['company_address_1']

            employee_strength=customer_form.cleaned_data['employee_strength']
            url = customer_form.cleaned_data['url']
            vat_gst_no = customer_form.cleaned_data['vat_gst_no']
            customer_group = Group.objects.get(name='Customer')
            username=email
            subject = 'User Trying to Signup to Brayn.ai'
            plain_message = "A user is trying to signup for Brayn \n\n please find the details below \n \n "
            message = render_to_string('login/account_creation_email.html', {
                    'email': email,
                    'name':first_name+'_'+last_name,
                    'message':plain_message,
                    
                })
            mail.send_mail(subject, plain_message, 'noreply@brayn.ai', ['vishwa@quanscendence.com'], html_message=message)
            if gender and gender == 'Gender':
                msg = "ENTER VALID GENDER"
                context={
                    'profile_form':profile_form,
                    'customer_form':customer_form,
                    'seo':seo,
                    'msg':msg,
                    }
                return render(request,template_name,context)

            
            try:
                user = User.objects.get(username=username)

            except:
                user=False
                print("error")
            if not  user:
                print("inside if")
                #creating user for customer
                try:
                    print("user create")
                    customer_user,created=User.objects.get_or_create(username=username,first_name=first_name,last_name=last_name,email=email)
                    customer_user.set_password(password)
                    customer_user.save()
                    print("user created")
                except:
                    print("except in user creation")
                    pass

                #customer profile is created
                if type=="Individual":
                  
                 
                    try:
                        print("the data passed")
                        image=request.FILES["image"]
                        customer ,created = Customer.objects.get_or_create(user=customer_user,contact_no=contact_no,address_1=address_1,zipcode=zipcode,group=customer_group,type=type,gender=gender,dob=dob,industry=industry,image=image,vat_gst_no=vat_gst_no)
                        print('the dat second pass')
                        customer.image = image
                        customer.save()
                        print("the the image url ",customer.image.url)
                        # action.send(user,verb=str(customer) + "signedup" )
                    except:
                        print("image not uploaded")

                        customer ,created = Customer.objects.get_or_create(user=customer_user,contact_no=contact_no,address_1=address_1,zipcode=zipcode,group=customer_group,type=type,gender=gender,dob=dob,industry=industry,vat_gst_no=vat_gst_no)
                        # action.send(user,verb=str(customer) + "signedup" )
                elif type=="Company":
                    print("the files ",request.FILES)
                    image=request.FILES.get("image",None)
                    logo = request.FILES.get('logo',None)
                    if image and logo:

                        customer ,created = Customer.objects.get_or_create(user=customer_user,contact_no=contact_no,company_name=company_name,company_address_1=company_address_1,employee_strength=employee_strength,url=url,zipcode=zipcode,group=customer_group,type=type,gender=gender,dob=dob,industry=industry,image=image,logo=logo,vat_gst_no=vat_gst_no)
                        customer.image = image
                        customer.logo = logo
                        customer.save()
                        print("the image",customer.image.url,customer.logo.url)
                    elif image:

                        customer ,created = Customer.objects.get_or_create(user=customer_user,contact_no=contact_no,company_name=company_name,company_address_1=company_address_1,employee_strength=employee_strength,url=url,zipcode=zipcode,group=customer_group,type=type,gender=gender,dob=dob,industry=industry,image=image,vat_gst_no=vat_gst_no)
                        customer.image = image
                        customer.save()
                    elif logo:

                        customer ,created = Customer.objects.get_or_create(user=customer_user,contact_no=contact_no,company_name=company_name,company_address_1=company_address_1,employee_strength=employee_strength,url=url,zipcode=zipcode,group=customer_group,type=type,gender=gender,dob=dob,industry=industry,logo=logo,vat_gst_no=vat_gst_no)
                        customer.logo = logo
                        ustomer.save()
                    else:
                        customer ,created = Customer.objects.get_or_create(user=customer_user,contact_no=contact_no,company_name=company_name,company_address_1=company_address_1,employee_strength=employee_strength,url=url,zipcode=zipcode,group=customer_group,type=type,gender=gender,dob=dob,industry=industry,vat_gst_no=vat_gst_no)

                    
                    
                customers=Customer.objects.get(pk=customer.pk)
                pk=str(customer.user.pk)
                
                current_site = get_current_site(request)
                subject = 'Activate Your Brayn Account'
                plain_message = "Thank you for signing up"
                message = render_to_string('login/account_activation_email.html', {
                    'customer': customer,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(customer.user.pk)),
                    'token': account_activation_token.make_token(customer),
                })
                mail.send_mail(subject, plain_message, 'noreply@brayn.ai', [customer.user.email], html_message=message)
                subject = 'User  has Signedup for  Brayn.ai'
                plain_message = "A user is signedup  for Brayn \n \n  please find the details below \n \n "
                message = render_to_string('login/account_creation_email.html', {
                    'email': email,
                    'name':first_name+'_'+last_name,
                    'message':plain_message,
                    
                })
                mail.send_mail(subject, plain_message, 'noreply@brayn.ai', ['vishwa@quanscendence.com'], html_message=message)
                return redirect('/customer/account_activation_sent')
                # return redirect('/customer/login/')
            else:
                msg = "ENTERED EMAIL IS ASSOCIATED WITH ANOTHER ACCOUNT"
                context={
                    'profile_form':profile_form,
                    'customer_form':customer_form,
                    'seo':seo,
                    'msg':msg,
                    }
                return render(request,template_name,context)




                print('user exists')
                #if user already exists, getting the customer profile saved in user
                user=User.objects.get(username=email)
                pk=str(user.pk)


                customer ,created = Customer.objects.get_or_create(user=user,contact_no=phone,address_1=address_1,zipcode=zipcode,group=customer_group,type=type,gender=gender,dob=dob,industry=industry,company_address_1=company_address_1,company_name=company_name,employee_strength=employee_strength,url=url)
                
                # action.send(user,verb=str(customer) + "signedup" )
                context={
                    'profile_form':profile_form,
                    'customer_form':customer_form,
                    'seo':seo
                    }
                current_site = get_current_site(request)
                subject = 'Activate Your Brayn Account'
                plain_message = "Thank you for Signing Up"
                message = render_to_string('login/account_activation_email.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(customer),
                })
                mail.send_mail(subject, plain_message, 'noreply@brayn.ai', [user.email], html_message=message)
                subject = 'User  has Signedup for  Brayn.ai'
                plain_message = "Some user signedup  for Brayn  please find the details below"
                message = render_to_string('login/account_creation_email.html', {
                    'email': email,
                    'name':first_name+'_'+last_name,
                    'message':plain_message,
                    
                })
                mail.send_mail(subject, plain_message, 'noreply@brayn.ai', ['vishwa@quanscendence.com'], html_message=message)
                return redirect('/customer/account_activation_sent')
                # return redirect('/customer/login/') #if form is valid, customer is directed to successful page where otp has to be entered
        else:
            print(profile_form.errors,customer_form.errors)

            print("invalid")
            template_name='login/signup.html'
            context={
                'profile_form':profile_form,
                'customer_form':customer_form,
                'seo':seo
                }
            
            return render(request,template_name,context)

''' ajax call view to send OTP to verify the customer contact no'''
def VerifyCustomerPhone(request):
    print("inside function")
    if request.method == 'POST':
        contact_no =request.POST['contact_no']
        user = request.user
        print("the user is",user)
        customer = Customer.objects.get(user=user)
        print("post",contact_no,"customer",customer.contact_no)
        if contact_no == customer.contact_no:
            user_contact = customer.contact_no
            print(user_contact)
            data={
                'error_msg':"error"
                 }
        elif Customer.objects.filter(contact_no=contact_no).exists():
            data={
                'error_msg':"Contact no is Associated with anothere Account "
            }
        else:

            user=False
            otp=request.POST['random_number']
            resp =  sendSMS('91'+str(contact_no),'Your Login OTP-'+otp)
            data={
                'msg':"Success"
            }





        return JsonResponse(data,safe=False)
    else:
        print("failure")
        return JsonResponse("Failure",safe=False)


'''ajax call view to check whether the email id is already in use'''
def verify_email(request):
    print("inside verify email function")
    if request.method == 'POST':
        email=request.POST['email_id']
        print(email)
        try:
            user=User.objects.get(username=email)
            user_email=user.email
            print(user_email)
            data={
            'msg':"error"  #if email id exists error msg is displayed.
            }
        except:

            data={
            'msg':"Success"
            }

        return JsonResponse(data,safe=False)
    else:
        return JsonResponse("Failure",safe=False)

'''start of login class for the customer to login with username and password'''
class LoginView(CreateView):
   def get(self,request):
       '''get method to display login form'''
       print("login")
       template_name='login/login.html'
       login_form=LoginForm()
       seo=SiteSeo.objects.get(choices='Login')
       context={
           'login_form':login_form,
           'seo':seo

       }
       return render(request,template_name,context)

   def post(self,request):
       '''post method to receive username and password and authenticate the customer'''
       template_name='login/login.html'
       seo=SiteSeo.objects.get(choices='Login')
       login_form=LoginForm(request.POST)
       if login_form.is_valid():
           username=login_form.cleaned_data['username']
           password=login_form.cleaned_data['password']
           try:
               user=User.objects.get(username=username) #check for existing user. if user present authentication is checked.
               print(user)
               login_user=authenticate(username=user.username,password=password)
               print("login successful",login_user)

               if login_user is not None:

                   try:
                       customer = Customer.objects.get(user=user)
                   except:
                       msg_1="Customer Account Does Not Exist" #if authentication is unsuccessful,error msg is displayed'''
                       action.send(request.user,verb="Tried to log in with wrong credentials" )
                       context={
                            'login_form':login_form,
                            'msg_1':msg_1,
                             'seo':seo
                        }
                       customer =None
                       return render(request,template_name,context)
                        
                   if customer and customer.email_confirmed==True:
                       # print("login sucess")
                       login(request,login_user)
                       print("the user loged in ")
                       # action.send(login_user,verb="logged in " )
                       return redirect('/dashboard/')
                   else:
                       msg_1="Please Activate your Account Before Login" #if authentication is unsuccessful,error msg is displayed'''
                       action.send(request.user,verb="Tried to log in with wrong credentials" )
                       context={
                            'login_form':login_form,
                            'msg_1':msg_1,
                             'seo':seo
                        }
                       return render(request,template_name,context)
               else:
                   msg_1="Please Provide Correct Username or Password"
                   action.send(request.user,verb="Tried to log in with wrong credentials" )
                   context={
                       'login_form':login_form,
                       'msg_1':msg_1,
                        'seo':seo
                       }
                   return render(request,template_name,context)
           except:
               print("user not exists")                  # if user does not exists, then error msg is displayed.
               msg="Please Signup before login"

               context={
                       'login_form':login_form,
                       'msg':msg,
                        'seo':seo
                  }
               return render(request,template_name,context)
       else:
           print(login_form.errors)
           context={
               'login_form':login_form,
                'seo':seo
               }
           return render(request,template_name,context)
'''End of login class for the customer to login with username and password'''


'''start of profile update class where customer can edit the profile details'''
class ProfileUpdateView(LoginRequiredMixin,TemplateView):

    def get(self,request,pk):
        '''get method to display profile update form'''
        seo=SiteSeo.objects.get(choices='Update Profile')
        template_name='login/profile_update.html'
        user = User.objects.get(pk=pk)
        projects_delete = Project.objects.filter(Q(admin_user=user) and  Q(delete_datetime__isnull=False) ).count()
        print("project count ",projects_delete)
        if  projects_delete > 0:
            projects_delete = True
        else:
            projects_delete = False
       
        user = User.objects.get(pk=request.user.pk)
        customer = Customer.objects.get(user=user)
        current_site = get_current_site(request)
        site_name = current_site.name
        domain = current_site.domain
        if domain.startswith('127.0.'):
            domain = 'https://'+domain
        else:
            domain = 'https://'+domain
        
        print("user is ",user)
        customer = Customer.objects.get(user=user)
        
        print("user",user)
        print("user_image",customer.type)
        form=UpdateForm(initial={'type':customer.type,'first_name':user.first_name,'last_name':user.last_name,'contact_no':customer.contact_no,'address_1':customer.address_1,'zipcode':customer.zipcode,'company_address_1':customer.company_address_1,'company_name':customer.company_name,'employee_strength':customer.employee_strength,'url':customer.url,'email':customer.user.email,'vat_gst_no':customer.vat_gst_no})

        context={
        'form':form,
        'user':user,
        'customer':customer,
        'seo':seo,
        'projects_delete':projects_delete



        }
        return render(request,template_name,context)

    def post(self,request,pk):
        '''post method is receive the profile updated details and save it according to individual and company type'''
        template_name='login/profile_update.html'
        seo=SiteSeo.objects.get(choices='Update Profile')
        form=UpdateForm(request.POST,request.FILES)
        user = User.objects.get(pk=pk)
        projects_delete = Project.objects.filter(Q(admin_user=user) and  Q(delete_datetime__isnull=False) ).count()
        print("project count ",projects_delete)
        if  projects_delete > 0:
            projects_delete = True
        else:
            projects_delete = False
       
        user = User.objects.get(pk=request.user.pk)
        customer = Customer.objects.get(user=user)

        if form.is_valid():
            email =form.cleaned_data['email']
            profile_type=request.POST.get("type",None)
            first_name=request.POST.get("first_name",None)
            last_name=request.POST.get("last_name",None)
            image = request.FILES.get('image',None)
            logo = request.FILES.get('logo',None)
            company_address_1=request.POST.getlist("company_address_1",None)
            company_address_1 = company_address_1[0]
            company_name=request.POST.getlist("company_name",None)
            company_name = company_name[0]
            employee_strength=request.POST.getlist("employee_strength",None)
            employee_strength = employee_strength[0]
            zipcode=request.POST.getlist("zipcode",None)
            zipcode = zipcode[0]
            vat_gst_no = request.POST.getlist("vat_gst_no",None)
            vat_gst_no = vat_gst_no[0]
            if not zipcode:
                zipcode = None
            print("gfifkwq",request.POST)
            URL=request.POST.getlist("url",None)
            URL =URL[0]
            contact_no=request.POST.get("contact_no",None)

            address_1=request.POST.getlist("address_1",None)
            address_1 = address_1[0]

            user=User.objects.get(pk=pk)
            user_update=User.objects.filter(pk=pk).update(first_name=first_name,last_name=last_name,email=email)
            customer = Customer.objects.get(user=user)

            user=User.objects.get(pk=pk)
            print('user_update',user,employee_strength)
            user_customer=Customer.objects.get(user=user)
            print("user pk",type(user_customer.pk))



            customer_update=Customer.objects.filter(pk=user_customer.pk).update(address_1=address_1,zipcode=zipcode,company_address_1=company_address_1,company_name=company_name,employee_strength=employee_strength,url=URL,contact_no=contact_no,type=profile_type,vat_gst_no=vat_gst_no)
            print("customer updated")
            if profile_type == "Individual":
                if customer.type == "Individual":
                    pass
                else:
                    if "contact_no" in form.changed_data:
                        customer_update=Customer.objects.filter(pk=user_customer.pk).update(address_1=address_1,zipcode=zipcode,contact_no=contact_no,type=profile_type,vat_gst_no=vat_gst_no)
                    else:
                        customer_update=Customer.objects.filter(pk=user_customer.pk).update(address_1=address_1,zipcode=zipcode,type=profile_type,vat_gst_no=vat_gst_no)
                        print("individual customer updated",customer_update)
            elif profile_type == "Company":
                if "contact_no" in form.changed_data:
                    customer_update=Customer.objects.filter(pk=user_customer.pk).update(company_address_1=company_address_1,company_name=company_name,employee_strength=employee_strength,url=URL,zipcode=zipcode,contact_no=contact_no,type=profile_type,vat_gst_no=vat_gst_no)
                else:
                    customer_update=Customer.objects.filter(pk=user_customer.pk).update(company_address_1=company_address_1,company_name=company_name,employee_strength=employee_strength,url=URL,zipcode=zipcode,type=profile_type,vat_gst_no=vat_gst_no)
                    print("company customer updated",customer_update)
            
            if image :
                customer = Customer.objects.get(pk=user_customer.pk)
                customer.image = image
                customer.save()
            if logo :
                customer = Customer.objects.get(pk=user_customer.pk)
                customer.logo = logo
                customer.save()
            user=User.objects.get(pk=pk)
            pk = str(pk)
            return redirect('/customer/updates/'+pk+'/')
        else:
            print(form.errors)
            context={
                'form':form,
                'seo':seo,
                'customer':customer,
                'projects_delete':projects_delete

                }
            return render(request,template_name,context)
'''End of profile update class where customer can edit the profile details'''


''' start of class to reset the password of the customer.'''
class PasswordResetView(CreateView):
    def get(self,request):
        '''get method to display the password reset form'''
        seo=SiteSeo.objects.get(choices='Password Reset')
        template_name='registration/password_reset_form.html'
        reset_form=PasswordResetForm()
        context={
            'reset_form':reset_form,
            'seo':seo
        }
        return render(request,template_name,context)

    def post(self,request):
        '''post method to receive the email id entered by the customer, create token,id to send the password reset link to entered email'''
        template_name='registration/password_reset_form.html'
        seo=SiteSeo.objects.get(choices='Password Reset')
        current_site = get_current_site(request)
        site_name = current_site.name
        domain = current_site.domain
        print('domain',domain)
        reset_form=PasswordResetForm(request.POST)
        if reset_form.is_valid():
            print("email valid")
            email=reset_form.cleaned_data["email"]
            try:
                user=User.objects.get(email=email) # check whether entered email id is available.
                pk=user.pk
                print("email valid")
                subject = 'Password reset link'
                # uid and token are created

                html_message = render_to_string('registration/password_reset_email.html', {'pk': pk,'uid': urlsafe_base64_encode(force_bytes(pk)),
                                                                                                'token': default_token_generator.make_token(user),'domain':domain})
                plain_message = strip_tags(html_message)
                from_email = '<noreply@brayn.ai>'
                to = email
                #sending mail to customer with from, to address and html message which includes the password reset link
                mail.send_mail(subject, plain_message, from_email, [to], html_message=html_message)
                print("email sent")
                return redirect('/password_reset/done/')
            except:
                msg="Please Enter Registered Email Id" # if entered email id is not available,error msg is displayed.
                context={
                    'reset_form':reset_form,
                    'msg':msg
                }
                return render(request,template_name,context)
        else:
            context={
                'reset_form':reset_form,
                'pk':pk,
                'seo':seo
                }
            return render(request,template_name,context)
''' End of class to reset the password of the customer.'''


class SignupUser(View):

    def get(self,request,**kwargs):
        """uid?token?????????."""
        seo=SiteSeo.objects.get(choices='User Signup')
        token = kwargs.get('token')
        uidb64 = kwargs.get('uidb64')
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            print(user)
        except:
            pass
        if user and user.is_active:
            if default_token_generator.check_token(user, token):
                print("token valid")
                user.is_active = True
                user.save()
                print(user)

            template_name='login/project_user_singup.html'
            signup_link_form=SignupLinkForm()
            context={
                    'signup_link_form':signup_link_form,
                    'seo':seo
                   }


            return render(request,template_name,context)


    def post(self,request,uidb64,token):
        template_name='login/project_user_singup.html'
        seo=SiteSeo.objects.get(choices='User Signup')
        signup_link_form=SignupLinkForm(request.POST)
        if signup_link_form.is_valid():
            type=signup_link_form.cleaned_data['type']
            first_name=signup_link_form.cleaned_data['first_name']
            last_name=signup_link_form.cleaned_data['last_name']
            password=signup_link_form.cleaned_data['password']
            gender=signup_link_form.cleaned_data['gender']
            
            dob=signup_link_form.cleaned_data['dob']
            contact_no=signup_link_form.cleaned_data['contact_no']
            address=signup_link_form.cleaned_data['address_1']
            zipcode=signup_link_form.cleaned_data['zipcode']
            industry=signup_link_form.cleaned_data['industry']
            company_name = signup_link_form.cleaned_data['company_name']
            company_address_1 = signup_link_form.cleaned_data['company_address_1']
            employee_strength=signup_link_form.cleaned_data['employee_strength']
            url = signup_link_form.cleaned_data['url']
            customer_group = Group.objects.get(name='Customer')
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            pk=user.pk
            username=user.email
            email=user.email
            account_type="Individual"
            #creating user for customer
            customer_user=User.objects.filter(pk=pk).update(username=username,first_name=first_name,last_name=last_name,email=email)
            user=User.objects.get(pk=pk)
            print(user)
            user.set_password(password)
            user.save()
            #customer profile is created
            if type=="Individual":
                try:
                    image=request.FILES["image"]
                    customer ,created = Customer.objects.get_or_create(user=user,contact_no=contact_no,address_1=address,zipcode=zipcode,group=customer_group,type=type,gender=gender,dob=dob,industry=industry,image=image)
                    customer.image = image
                    customer.save()
                except: print("image not uploaded")
                customer ,created = Customer.objects.get_or_create(user=user,contact_no=contact_no,address_1=address,zipcode=zipcode,group=customer_group,type=type,gender=gender,dob=dob,industry=industry)
            elif type=="Company":
                try:
                    image=request.FILES["image"]
                    customer ,created = Customer.objects.get_or_create(user=user,contact_no=contact_no,company_name=company_name,company_address_1=company_address_1,employee_strength=employee_strength,url=url,zipcode=zipcode,group=customer_group,type=type,gender=gender,dob=dob,industry=industry,image=image)
                except: print("image not uploaded")
                customer ,created = Customer.objects.get_or_create(user=user,contact_no=contact_no,company_name=company_name,company_address_1=company_address_1,employee_strength=employee_strength,url=url,zipcode=zipcode,group=customer_group,type=type,gender=gender,dob=dob,industry=industry)
            user=Customer.objects.get(pk=customer.pk)
            pk=str(user.pk)
            context={
                'signup_link_form':signup_link_form,
                'seo':seo

                }


            return redirect('/customer/login/')


        else:
            print(signup_link_form.errors)

            print("invalid")
            template_name='login/project_user_singup.html'
            context={
                'signup_link_form':signup_link_form,
                'seo':seo

                }
            return render(request,template_name,context)

'''class to redirect the login urls according to the users'''
class LoginPermission(View):
    def get(self,request):
        if request.user.username=='administrator':
            print(request.user.username)
            template_name='admin_dashboard.html'
            return redirect('/administrator/admin-dashboard/')
        else:
            print(request.user.username)
            template_name='login.html'
            return redirect('/customer/login/')

'''class to receive the basic information from customer'''
class BasicSignupView(CreateView):
    def get(self,request):
        template_name='login/basic_signup.html'
        basic_signup=BasicSignupForm()
        seo=SiteSeo.objects.get(choices='Basic Signup')
        context={
            'basic_signup' : basic_signup,
            'seo':seo
        }
        return render(request,template_name,context)
    def post(self,request):
        template_name='login/basic_signup.html'
        seo=SiteSeo.objects.get(choices='Basic Signup')
        basic_signup=BasicSignupForm(request.POST)
        if basic_signup.is_valid():
            print("form valid")
            email = basic_signup.cleaned_data['email'],
            email=''.join(email)
            first_name = basic_signup.cleaned_data['first_name'],
            first_name=''.join(first_name)
            last_name =basic_signup.cleaned_data['last_name'],
            last_name=''.join(last_name)
            contact_no= basic_signup.cleaned_data['contact_no'],
            
            contact_no=''.join(contact_no)



            #sending mail to owner
            html_message = render_to_string('login/mail_content.html', {'first_name': first_name,'last_name': last_name,'email':email,'contact_no':contact_no,})
            subject = 'Basic Signup'
            plain_message = ""
            from_email = '<noreply@brayn.in>'
            to = ['vishwa@quanscendence.com','shrikar@quanscendence.com','vijeth@quanscendence.com']
            mail.send_mail(subject, plain_message, from_email, to, html_message=html_message)
            #sending mail to customer
            subject = 'Basic Signup'
            plain_message = "Thank you for your interest, We will get in touch with you shortly!"
            from_email = '<noreply@brayn.in>'
            to = email
            #sending mail to customer with from, to address and html message which includes the password reset link
            mail.send_mail(subject, plain_message, from_email, [to])
            print("mail sent")
            basic_signup=BasicSignupForm()
            context={
                'msg':"Thank you for your interest, We will get in touch with you shortly!",
                'basic_signup':basic_signup,
                }
            return render(request,template_name,context)

        else:
            print(basic_signup.errors)
            context={
                'basic_signup':basic_signup,
                'seo':seo
            }
            return render(request,template_name,context)


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        customer = Customer.objects.get(user=user)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        customer = None
        user=None

    if user is not None and account_activation_token.check_token(customer, token):
        user.is_active = True
        customer.email_confirmed = True
        user.save()
        customer.save()
        login(request, user)
        
        pk = str(user.pk)
        return redirect('/'+pk+'/')
    else:
        return render(request, 'login/account_activation_invalid.html')


def account_activation_sent(request):

    return render(request,'login/account_activation_sent.html')