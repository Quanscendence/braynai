from django.shortcuts import render,redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.files.storage import default_storage
from django.views.generic import TemplateView,CreateView,View,UpdateView,ListView
from login.forms import CustomerForm,ProfileForm,UpdateForm,PasswordResetForm,SignupLinkForm,LoginForm
from coreapp.forms import ProjectForm, Fileform,FileUploadForm,ProjectUpdateForm,AddUsersForm,AcceptForm,FormFile,ProjectDashboardForm, ProjectDashboardEditForm, ProjectDashboardsForm,ProjectEndPointForm,ApidataForm,AddonFileForm
from login.models import Customer,Profile
from coreapp.models import ProjectType,Project,FileUpload,ProjectUser, ProjectColumn,ProjectJsonStorage,ProjectDashboard,UserNotification, \
                                            ProjectMetaData,IndustryChoices,ProjectConfiguration, ProjectQuery, DashboardQuery,Plot,ProjectEndPoint, ProjectFileRelationship, \
                                            ProjectSchema,ProjectIndex, ProjectFilename, EndPointAlgorithm, DataFrameDisplay,ProjectJsonStorageMetadata,ProjectBillingPrms, DefaultProjectPricing,ProjectPricing, ProjectInvoice,ProjectBillingMonthCost, \
                                            Tax,EndpointMlApi, EndPointNewColumn
from qdesk.models import Ticket
from qdesk.forms import TicketForm
from django.contrib.auth.models import Group
from dataintegration.models import CustomerAPIDetails
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import urllib.request
import logging
import urllib.parse
import random
import numpy as np
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from django.contrib.auth import authenticate,login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
import pandas as pd
import plotly.offline as opy
import plotly.graph_objs as go
from coreapp.plots import EndPointPlot,QueryPlot
import plotly.express as px
from django.urls import reverse_lazy
from seo_app.models import SiteSeo
from django.contrib.sites.shortcuts import get_current_site
###password reset###
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator

###search###
from itertools import chain
from django.db.models import Q
from functools import reduce, partial
from engine import cleaner,query,optimize
import os
from engine import query as qpl
import csv
from engine.optimize import ProjectJsonAlter
import json
from actstream import action
from actstream.models import Action
from datetime import datetime, timedelta
import ast
from django.http import HttpResponse
from dal import autocomplete
from engine.cleaner import FileReader, FillNan,ColumnCombine,CheckPrimarykey,DeleteColumn,SchmaCheck
from utils import ReadFileLines
from braces.views import GroupRequiredMixin
from utils import ProjectPermissionGroupCreate
import base64
import seaborn as sns
import sys
import requests
# from . import coreapp_global_logger
from mlapp.algorithm.auto_ml import AutoMl
from mlapp.algorithm.linear import Linear
from mlapp.algorithm.cluster import Kmeans
from dataintegration.forms import SheetDetailsForm,SheetUrlForm
from django.views.decorators.clickjacking import xframe_options_exempt
from dateutil.relativedelta import relativedelta
import pytz
import psutil
import gc
logging.getLogger().setLevel(logging.INFO)
utc=pytz.UTC

# view-logging
# vl = coreapp_global_logger.LogMe()

def listgenerator(l):
    
    for i in l:
        yield i


def catrgory_decode(p,col1,col2):
   for i,v in enumerate(col1.unique()):

    if v == p:
      for index,n in enumerate(col2.unique()):

        if i == index:
          return n

def recode(p,col1,col2):
  for i,v in enumerate(col2.unique()):

    if v == p:
      for index,n in enumerate(col1.unique()):

        if i == index:
          return n
#function to find intersection column names of two files
def intersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2]
    return lst3


def total_disk_space(project_ep,project_jsons):
    total=0
    for ep in project_ep:
        total = total +sys.getsizeof(ep.sub_df)
    for json in project_jsons:
        total = total +sys.getsizeof(json.js)
    return total

def df_dtype_casting(df,project):
    df_columns= df.columns.to_list()
    metadata = ProjectMetaData.objects.get(project=project)
    for key, value in metadata.meta_data.items():
        if key in df_columns:
            ##print("key",key)
            if value['dtype'] == 'int':
                df[key] =pd.to_numeric(df[key])
                if key in df_columns:
                    df[key] = pd.to_numeric(df[key])
            elif value['dtype'] == 'float':
                ##print("final key",key,df[key],df[key].dtypes)
                df[key] = pd.to_numeric(df[key])
                if key in df_columns:
                    df[key] = pd.to_numeric(df[key])
            elif value['dtype'] == 'object':
                df[key] = df[key].astype(str)
                if key in df_columns:
                    df[key] = df[key].astype(str)
            elif value['dtype'] == 'bool':
                df[key] = df[key].astype(bool)
                if key in df_columns:
                    df[key] = df[key].astype(bool)
            elif value['dtype'] == 'DateTime':
                df[key] =pd.to_datetime(df[key])
                ##print("the data key",key)
                if key in df_columns:
                    df[key] = pd.to_datetime(df[key])
    return df
def user_permission(project,request):
    '''function to return  the user permission'''
    if Project.objects.filter(pk=project.pk,admin_user=request.user).exists():
        permission="Admin"
    elif ProjectUser.objects.filter(project=project,project_user=request.user).exists():
        user_group = User.objects.get(pk=request.user.pk)

        for g in user_group.groups.all():
            if g.name == str(p_query.project.pk)+"_Read":
                permission="Read"
            elif g.name == str(p_query.project.pk)+"_Write":
                permission="Write"
            elif g.name == str(p_query.project.pk)+"_Delete":
                permission="Delete"
            elif g.name == str(p_query.project.pk)+"_Admin":
                permission="Admin"
    else:
        permission=None
    return permission


class ProjectPermissionMixin(PermissionRequiredMixin):
    model = ProjectUser

    def get_object(self):
        id= self.kwargs.get('id')
        # vl.fullbari("ProjectPermissionMixin::get_object id="+str(id))
        obj = None
        if id is not None:
            obj = get_object_or_404(self,model,id=id)
        return obj



'''function to send sms using text local'''
def sendSMS(numbers,message):
    data =  urllib.parse.urlencode({'apikey': 'PfIdpBsAQu0-MSbkQMgPH9zQXa2KmC26oUVTQwna33', 'numbers': numbers,
        'message' : message, })
    data = data.encode('utf-8')
    request = urllib.request.Request("https://api.textlocal.in/send/?")
    f = urllib.request.urlopen(request, data)
    fr = f.read()
    return(fr)



def identify_user_permission(project,user):
    if Project.objects.filter(pk=project.pk,admin_user=user).exists():
        permission="Admin"
    elif ProjectUser.objects.filter(project=project,project_user=user).exists():
        user_group = User.objects.get(pk=user.pk)

        # # vl.fullbari("ProjectPermissionMixin::identify_user_permission user_groups="+str(vl.one_string(user_group.groups.all())))
        for g in user_group.groups.all():
            if g.name == str(project.pk)+"_Read":
                permission="Read"
            elif g.name == str(project.pk)+"_Write":
                permission="Write"
            elif g.name == str(project.pk)+"_Delete":
                permission="Delete"
            elif g.name == str(project.pk)+"_Admin":
                permission="Admin"

    else:
        permission=None
    return permission




"""site map view"""
def Sitemap(request):
    return HttpResponse(open('sitemap.xml').read(), content_type='text/xml')




'''start of class home to display home page of the website'''
class HomeView(TemplateView):
    def get (self,request):
        template_name='website/index.html'
        seo=SiteSeo.objects.get(choices='Home')
        return render(request,template_name,context={'seo':seo})

'''End of class home to display home page of the website'''

'''start of class About to display about page of the website'''
class AboutView(TemplateView):
    def get (self,request):

        template_name='website/about.html'
        seo=SiteSeo.objects.get(choices='about')
        return render(request,template_name,context={'seo':seo})
'''End of class About to display about page of the website'''


class BlogView(TemplateView):
    '''class blog to display blog page of the website'''
    def get (self,request):
        template_name='website/blog.html'
        seo=SiteSeo.objects.get(choices='blog')
        return render(request,template_name,context={'seo':seo})


class TermsConditionsView(TemplateView):

    def get(self,request):
        template_name = 'website/terms_and_conditions.html'
        return render(request,template_name)


class PrivacyPolicyView(TemplateView):
    '''class terms condition page website'''
    def get (self,request):
        template_name='website/privacy_policy.html'
        return render(request,template_name)



class ServicesView(TemplateView):
    '''class services to display services page of the website'''
    def get (self,request):
        template_name='website/services.html'
        seo=SiteSeo.objects.get(choices='services')
        return render(request,template_name,context={'seo':seo})

class UserActivationSuccessView(View):
    def get(self,request,pk):
        ##print("Inside dashboard")
        template_name= 'dashboard/index.html'
        projects = Project.objects.all()


        seo=SiteSeo.objects.get(choices='Dashboard')
        msg = "YOUR ACCOUNT HAS BEEN ACTIVATED SUCCESSFULLY"
        user=User.objects.get(username=request.user.username)
        all_project = Project.objects.filter(admin_user=user,delete_obj= False)
        projects_delete = Project.objects.filter(Q(admin_user=user) and  Q(delete_datetime__isnull=False)).count()
        ##print("project count ",projects_delete)
        if  projects_delete > 0:
            projects_delete = True
        else:
            projects_delete = False


        # vl.bari("optimizing raw data:", 's')
        #querying customer to display upoaded image on the dashboard
        user_project_pk = []

        user_permission ={}
        for project in projects:
            project_users = ProjectUser.objects.filter(project=project)

            if Project.objects.filter(pk=project.pk,admin_user=request.user).exists():

                permission="Admin"
            elif ProjectUser.objects.filter(project=project,project_user=request.user).exists():
                user_p =ProjectUser.objects.get(project=project,project_user=request.user)
                user_project_pk.append(project.pk)
                user = user_p.project_user

                for g in user.groups.all():
                    if g.name == str(project.pk)+"_Read":
                        permission="Read"
                    elif g.name== str(project.pk)+"_Write":
                        permission="Write"
                    elif g.name == str(project.pk)+"_Delete":
                        permission="Delete"
                    elif g.name == str(project.pk)+"_Admin":
                        permission="Admin"
            else:
                permission="None"
            user_permission[project.pk] = permission
            # ##print("the user permissions are",user_permission)



        customer=Customer.objects.get(user=request.user)
        action.send(customer,verb="Viewed dashboard")
        len_1 = len(all_project)
        if len_1 >0 :
            projects = True
        else:
            projects = False
        context  = {
                'all_project':all_project,
                'user':user,
                'projects':projects,
                'customer':customer,
                'seo':seo,
                'msg':msg,
                'projects_delete':projects_delete,
                'user_permission':user_permission,

                }

        try:
            notification=UserNotification.objects.filter(user=request.user)
            for n in notification:
                notification_count=n.notification_count
                notification_read = n.notification_read
                # ##print(notification_count,notification_read)
                len_1 = len(all_project)
                if len_1 >0 :
                    projects = True
                else:
                    projects = False
                context = {
                                    'all_project':all_project,
                                    'user':user,
                                    'customer':customer,
                                    'projects':projects,
                                    'notification_count':notification_count,
                                    'notification_read':notification_read,
                                    'seo':seo,
                                    'msg':msg,
                                    'projects_delete':projects_delete,
                                    'user_permission':user_permission,

                                    }

            try:
                project_users = ProjectUser.objects.filter(project_user=request.user)
                for user in project_users:
                    # ##print("in project_usermodel",user.project_user.email )
                    len_1 = len(all_project)
                    len_2 = len(project_users)
                    if len_1 >0 or len_2> 0:
                        projects = True
                    else:
                        projects = False
                    context = {
                                        'all_project':all_project,
                                        'user':user,
                                        'projects':projects,
                                        'customer':customer,
                                        'project_user':project_users,
                                        'notification_count':notification_count,
                                        'notification_read':notification_read,
                                        'seo':seo,
                                        'msg':msg,
                                        'projects_delete':projects_delete,
                                        'user_permission':user_permission,
                                        }
            except:
                len_1 = len(all_project)
                if len_1 >0 :
                    projects = True
                else:
                    projects = False
                context = {
                                'all_project':all_project,
                                'user':user,
                                'projects':projects,
                                'customer':customer,
                                'notification_count':notification_count,
                                'notification_read':notification_read,
                                'seo':seo,
                                'projects_delete':projects_delete,
                                'msg':msg,
                                'user_permission':user_permission,
                                }

        except:
            ##print("in except")
            len_1 = len(all_project)
            len_2 = len(user_permission)
            if le_1 >0 or len_2> 0:
                projects = True
            context  = {
                    'all_project':all_project,
                    'user':user,
                    'customer':customer,
                    'seo':seo,
                    'msg':msg,
                    'user_permission':user_permission,
                    'projects_delete':projects_delete


                    }
        # ##print("the user permision is ",project_user,all_project)
        # vl.bari("optimizing raw data:", 'e')
        return render(request,template_name,context)



class DashboardView(LoginRequiredMixin,View):
    ''' Account dashboard class to display the created project card of the customer'''
    login_url = '/customer/login/'
    redirect_field_name = 'redirect_to'
    template_name='dashboard/index.html'

    def get(self,request):
        ##print("Inside dashboard")
        template_name= 'dashboard/index.html'
        projects = Project.objects.all()


        seo=SiteSeo.objects.get(choices='Dashboard')

        user=User.objects.get(username=request.user.username)
        all_project = Project.objects.filter(admin_user=user,delete_obj= False)
        projects_delete = Project.objects.filter(Q(admin_user=user) and  Q(delete_datetime__isnull=False) ).count()
        ##print("project count ",projects_delete)
        if  projects_delete > 0:
            projects_delete = True
        else:
            projects_delete = False


        # vl.bari("optimizing raw data:", 's')
        #querying customer to display upoaded image on the dashboard
        user_project_pk = []

        user_permission ={}
        for project in projects:
            project_users = ProjectUser.objects.filter(project=project)

            if Project.objects.filter(pk=project.pk,admin_user=request.user).exists():

                permission="Admin"
            elif ProjectUser.objects.filter(project=project,project_user=request.user).exists():
                user_p =ProjectUser.objects.get(project=project,project_user=request.user)
                user_project_pk.append(project.pk)
                user = user_p.project_user

                for g in user.groups.all():
                    if g.name == str(project.pk)+"_Read":
                        permission="Read"
                    elif g.name== str(project.pk)+"_Write":
                        permission="Write"
                    elif g.name == str(project.pk)+"_Delete":
                        permission="Delete"
                    elif g.name == str(project.pk)+"_Admin":
                        permission="Admin"
            else:
                permission="None"
            user_permission[project.pk] = permission
            # ##print("the user permissions are",user_permission)



        customer=Customer.objects.get(user=request.user)
        action.send(customer,verb="Viewed dashboard")
        len_1 = len(all_project)
        if len_1 >0 :
            projects = True
        else:
            projects = False
        context  = {
                'all_project':all_project,
                'user':user,
                'projects':projects,
                'customer':customer,
                'seo':seo,
                'projects_delete':projects_delete,
                'user_permission':user_permission,

                }

        try:
            notification=UserNotification.objects.filter(user=request.user)
            for n in notification:
                notification_count=n.notification_count
                notification_read = n.notification_read
                # ###print(notification_count,notification_read)
                len_1 = len(all_project)
                if len_1 >0 :
                    projects = True
                else:
                    projects = False
                context = {
                                    'all_project':all_project,
                                    'user':user,
                                    'customer':customer,
                                    'projects':projects,
                                    'notification_count':notification_count,
                                    'notification_read':notification_read,
                                    'seo':seo,
                                    'projects_delete':projects_delete,
                                    'user_permission':user_permission,

                                    }

            try:
                project_users = ProjectUser.objects.filter(project_user=request.user)
                for user in project_users:
                    # ##print("in project_usermodel",user.project_user.email )
                    len_1 = len(all_project)
                    len_2 = len(project_users)
                    if len_1 >0 or len_2> 0:
                        projects = True
                    else:
                        projects = False
                    context = {
                                        'all_project':all_project,
                                        'user':user,
                                        'projects':projects,
                                        'customer':customer,
                                        'project_user':project_users,
                                        'notification_count':notification_count,
                                        'notification_read':notification_read,
                                        'seo':seo,
                                        'projects_delete':projects_delete,
                                        'user_permission':user_permission,
                                        }
            except:
                len_1 = len(all_project)
                if len_1 >0 :
                    projects = True
                else:
                    projects = False
                context = {
                                'all_project':all_project,
                                'user':user,
                                'projects':projects,
                                'customer':customer,
                                'notification_count':notification_count,
                                'notification_read':notification_read,
                                'seo':seo,
                                'projects_delete':projects_delete,

                                'user_permission':user_permission,
                                }

        except:
            ##print("in except")
            len_1 = len(all_project)
            len_2 = len(user_permission)
            if le_1 >0 or len_2> 0:
                projects = True
            context  = {
                    'all_project':all_project,
                    'user':user,
                    'customer':customer,
                    'seo':seo,
                    'user_permission':user_permission,
                    'projects_delete':projects_delete


                    }
        # ##print("the user permision is ",project_user,all_project)
        # vl.bari("optimizing raw data:", 'e')
        return render(request,template_name,context)




class OTPAuthenticate(TemplateView):
    ''' OTPAuthenticate view to render OTP form and receive OTP from customer to authenticate'''
    def get(self,request,pk):
        '''writing get request to render otp form '''
        template_name='success.html'
        otp_form=OTPForm()
        customer_user=Customer.objects.get(pk=pk)
        contact_no=str(customer_user.contact_no)
        otp=str(random.randint(100000,999900))
        # vl.fullbari("OTPAuthenticate::get otp="+otp)
        customer_user.user.set_password(otp)
        customer_user.user.save()


        resp =  sendSMS('91'+str(contact_no),'Your Login OTP-'+otp)
        body={
                "Your OTP": otp,
        }
        content = {"%s: %s" % (key, value) for (key, value) in body.items()}
        content = "\n".join(content)
        subject ="OTP"
    #sending admission details to specified email id
        send_mail(
        "New OTP",
        content,
        settings.DEFAULT_FROM_EMAIL,
        [customer_user.user.email],fail_silently=False)


        context={
            'otp_form':otp_form,
        }
        return render(request,template_name,context=context)

    def post(self,request,pk):
        otp_form = OTPForm()
        context={
            'otp_form':otp_form,
            }
        otp= request.POST['otp']
        customer_user = Customer.objects.get(pk=pk)
        pk=str(customer_user.pk)
        login_user=authenticate(username=customer_user.user.username,password=otp)
        # vl.fullbari("OTPAuthenticate::post","otp:",otp,"customer_user.pk:",pk, "username:", customer_user.user.username, "login_user:", login_user)
        if login_user is not None:
            login(request,login_user)
            return redirect('/home/')
        else:
            context={
                'otp_form':otp_form,
                }
            return render(request,'success.html',context)





class AddProjectView(LoginRequiredMixin,View):
    '''add project view class to display and receive the details of the project creation form'''
    login_url = '/customer/login/'
    redirect_field_name = 'redirect_to'
    template_name='dashboard/index.html'
    
    def get(self,request):
        template_name= 'dashboard/project_base.html'
        project_form=ProjectForm()
        form = ApidataForm()
        sheet_form = SheetDetailsForm()
        sheet_url_form = SheetUrlForm()

        customer = Customer.objects.get(user=request.user)
        seo=SiteSeo.objects.get(choices='Project Creation')
        context={
            'project_form':project_form,
            'seo':seo,
            'sheet_form':sheet_form,
            'customer':customer,
            'api_form':form,
            'sheet_url_form':sheet_url_form,
        }
        return render(request,template_name,context)

    #TODO deadly code ... longest post ever
    
    def post(self,request):
        ''' post method to receive the data entered in project creation form and to create the project'''
        form = FormFile(request.POST,request.FILES)
        time_series_column = request.POST['time_series_column']
        form = FormFile(request.POST,request.FILES)

        project_pk = request.POST['project']
        # vl.fullbari("AddProjectView::post", "form:", form)
        project = Project.objects.get(pk=int(project_pk))
        multiple_files  = request.FILES.getlist('files')
        api = request.POST.get('api',None)
        frequency = request.POST.get('frequency',None)
        basic_token = request.POST.get('basic_token',None)
        credential=request.FILES.get("credential",None)

        url = request.POST.get('url',None)
        cron_frequency = request.POST.get('cron_frequency',None)
        spread_sheet_id=request.POST.get("spreadsheet_id",None)
        data_range =  request.POST.get("data_range",None)
        header = request.POST.get('header',None)

        # vl.fullbari("AddProjectView::post", "multiple_files:", multiple_files)
        files = []
        files_separators  = {}
        files_heders ={}
        if len(multiple_files)>0:
            project_files = ProjectFilename.objects.filter(project=project)
            files = {}
            for project_file  in project_files:

            
            
                file_name = str(project_file.file_name)

                file_separator = request.POST.get(file_name+'_separator',None)
                file_header_status = request.POST.get(file_name+'_header_status',None)
                file_header = request.POST.get(file_name+'_header',None)
                file_header_row = request.POST.get(file_name+'_header_row',None)
                # files.append(file)
                files[file_name]= project_file.file.url
                files_separators[file_name] = file_separator
                files_heders[file_name] = {'header_status':file_header_status,'columns':file_header,'file_header_row':file_header_row}

            file_read_obj = FileReader()
            nan_read_start_time = datetime.now()
            # logging.info("file upload"+str(nan_post_start_time)+str(nan_read_start_time)
            # logging.info(f"the content{files}{files_separators}{files_heders}")
            # dfs = file_read_obj.readfile(files,files_separators,files_heders)
            data = file_read_obj.readfile_with_schema(files,files_separators,files_heders)
            try:
                error = data['error']
                data ={'error_msg':data['error']}
                return JsonResponse(data,safe=True)
            except:

                column_conbine_obj = ColumnCombine()

                # project schema files creation
                project_schema = ProjectSchema.objects.create(project=project,schema=data['schema'] )
                # vl.fullbari("AddProjectVclassiew::post", "project_schema:", project_schema.schema)

                relations = ProjectFileRelationship.objects.filter(project=project)
                # project relation mapping and updating the df's
                for r in relations:
                    all_dfs = data['all_dfs']
                    for key, value  in all_dfs.items():
                        df = value
                        if r.relation['foreignkey']['file'] == key and not df.empty:
                            # vl.fullbari("AddProjectView::post", "before rename columns are",r.relation['foreignkey']['column'],r.relation['primarykey']['column'],df.columns.to_list())
                            df= df.rename(columns = {r.relation['foreignkey']['column']:r.relation['primarykey']['column'],})
                            all_dfs[key]=df
                            #TODO
                        ##print("after rename columns are",r.relation['foreignkey']['column'],r.relation['primarykey']['column'],df.columns.to_list())

                all_dfs = data['all_dfs']
                all_df = []

                for key, val in all_dfs.items():
                    all_df.append(val)
                # vl.fullbari("AddProjectView::post","all_df:",all_df, "count:", len(all_df))
                if len(all_df)>1:
                    count = len(all_df)
                    for i in range(count-1):
                        df_1 = all_df[0]
                        # ##print("the df_1",df_1)

                        df_2 = all_df[1]
                        # ##print("the df_2",df_2)
                        df_1.columns = df_1.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '').str.replace('.', '_').str.replace(',','_').str.replace('/','_').str.replace(':','')
                        column_list_1 = df_1.columns.to_list()
                        df_2.columns = df_2.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '').str.replace('.', '_').str.replace(',','_').str.replace('/','_').str.replace(':','')
                        column_list_2 = df_2.columns.tolist()
                        common_columns = intersection(column_list_1,column_list_2)
                        if len(common_columns)>=1:
                            # vl.fullbari("AddProjectView::post", "all the common columns",common_columns)
                            result_df =reduce(lambda left,right: pd.merge(left,right,on=common_columns, how='outer'), [df_1,df_2])

                        else:
                            result_df =reduce(lambda left,right: pd.merge(left,right, left_index=True, right_index=True, how='outer'), [df_1,df_2])
                            # ##print(" each ititration of for ",result_df)
                        all_df.pop(0)
                        all_df.pop(0)
                        all_df.insert(0,result_df)
                        # ##print("all_df after merge",all_df)
                elif len(all_df) == 1:
                    result_df = all_df[0]
                    final_columns = result_df.columns.tolist()
                    result_df.columns = result_df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '').str.replace('.', '_').str.replace(',','_').str.replace('/','_').str.replace(':','')
                
                
                final_columns = result_df.columns.tolist()
                ##print("the final columns are ",final_columns)
                all_columns = column_conbine_obj.list_combine(all_df)
                ##print("all the columns are ",all_columns)
                # vl.fullbari("AddProjectView::post","final the mergerged dataframe is ",result_df.columns.to_list())
                # vl.fullbari("AddProjectView::post","all the columns are",all_columns)

                if not time_series_column == 'no-time-series':
                    # vl.fullbari("AddProjectView::post","time series column",time_series_column)
                    fillna_obj = FillNan(result_df)
                    time_series_list = time_series_column.split(':')
                    time_series= time_series_list[-1]
                    time_series = time_series.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('.', '_').replace(',','_').replace('/','_').replace(':','')
                    l=[time_series]
                    # vl.fullbari("AddProjectView::post","time_series",time_serie(s)
                    result_df = fillna_obj.time_series_drop_row(l)


                    try:
                        ###print("inside the try")
                        date_df = result_df
                        date_df[time_series]= date_df[time_series].astype(str)
                        # date_df[time_series]= pd.to_datetime(date_df[time_series])
                        date_df[time_series] = pd.to_datetime(date_df[time_series])
                        date_df = date_df.sort_values(by=[time_series])
                        # date_df = date_df.sort_values(by=[time_series])
                        start_date = date_df[time_series].iloc[0]
                        end_date = date_df[time_series].iloc[-1]
                        ###print("inside the try")
                    except KeyError:
                        ###print("inside the except")
                        # vl.fullbari("AddProjectView::post", "time series colum key error:",time_series)
                        for r in relations:
                            if r.relation['foreignkey']['column'] == time_series:
                                try:
                                    date_df = result_df
                                    date_df[time_series]= pd.to_datetime(date_df[time_series])
                                    date_df = date_df.sort_values(by=[time_series])
                                    start_date = date_df[time_series].iloc[0]
                                    end_date = date_df[time_series].iloc[-1]
                                except:
                                    start_date = datetime.now()
                                    end_date = datetime.now()
                                    error = "Choosen Column is not an Time Series column"
                                    data ={'error_msg':error,}
                                    # vl.fullbari("AddProjectView::post", "first_except:", error)
                                    return JsonResponse(data,safe=False)
                    except:
                        start_date = datetime.now()
                        end_date = datetime.now()
                        error = "Choosen Column is not an Time Series column"
                        data ={'error_msg':error,}
                        # vl.fullbari("AddProjectView::post", "second_except:", error)
                        #gc.collect()
                        return JsonResponse(data,safe=False)
                    ###print(time_series_column,"time series not validated")
                else:
                    start_date = datetime.now()
                    end_date = datetime.now()

                # metadata creation
                meta_data_dict = {}
                ##print("the ",start_date,end_date)
                relations = ProjectFileRelationship.objects.filter(project=project)
                if len(all_columns)>0:
                    df = result_df
                    fillna_obj = FillNan(df)
                    # vl.fullbari("AddProjectView::post", "all columns:", all_columns)
                    delete_column_list =[]
                    custom_value = {}
                    ##print("all column list",all_columns)
                    for c in all_columns:
                        column = {}
                        ###print("the dataframe",c)
                        if df.dtypes[c] == np.int64:
                            column['dtype'] = 'int'
                        elif df.dtypes[c] == np.float64:
                            column['dtype'] = 'float'
                        elif df.dtypes[c] == np.object:
                            column['dtype'] = 'object'
                        elif df.dtypes[c] == np.bool:
                            column['dtype']= 'bool'
                        elif np.issubdtype(df[c].dtype, np.datetime64):
                            column['dtype'] = "DateTime"
                            df[c] = df[c].astype('str')

                        missing_data = None
                        missing_data_input=None
                        try:
                            # reading mising data handling
                            ##print("the request post is",request.POST)
                            cu =  c+'_select'
                            missing_data = request.POST[cu]

                            ##print("the missing data",cu,missing_data)
                        except:

                            for r in relations:
                                if r.relation['foreignkey']['column'] == c:
                                    r_c = r.relation['foreignkey']['column']
                                    c_u = r_c+'_select'
                                    missing_data = request.POST[c_u]
                        try:
                            # reading mising data handling
                            ##print("the request post is",request.POST)
                            cu =  c+'_input'
                            missing_data_input = request.POST[cu]

                            ##print("the missing data",c,missing_data)
                        except:

                            for r in relations:
                                if r.relation['foreignkey']['column'] == c:
                                    r_c = r.relation['foreignkey']['column']
                                    c_u = r_c+'_select'
                                    missing_data_input = request.POST[c_u]

                        ###print("the column and missimg data",c,missing_data)

                        if missing_data and missing_data == 'zero':
                            column['handle_missing_data']= 0
                            today = str(datetime.now().date())
                            ###print("type of date",type(today))
                            column['start_date']= today
                            column['end_date']= ''
                            result_df = fillna_obj.fillnan_with_0(c)
                            ###print("nan filled df 0  ",c)
                        elif missing_data and missing_data == 'None':
                            column['handle_missing_data']= 'None'
                            result_df = fillna_obj.fillnan_with_None_value(c)
                            ###print("nan filled df None  ",c)
                            today = str(datetime.now().date())
                            ###print("type of date",type(today))
                            column['start_date']= today
                            column['end_date']= ''
                            column['column_deleted'] = False
                        elif missing_data and missing_data == 'previous':
                            column['handle_missing_data']= 'previous'
                            result_df = fillna_obj.fillnan_with_previous_value(c)
                            ###print("nan filled df ",result_df)
                            today = str(datetime.now().date())
                            ###print("type of date",type(today))
                            column['start_date']= today
                            column['end_date']= ''
                            column['column_deleted'] = False
                        elif missing_data and missing_data == 'drop':
                            column['handle_missing_data']= 'drop'
                            l = [c]
                            result_df = fillna_obj.drop_row(l)
                            ###print("nan filled df ",result_df)
                            today = str(datetime.now().date())
                            ###print("type of date",type(today))
                            column['start_date']= today
                            column['end_date']= ''
                            column['column_deleted'] = False
                        elif missing_data and missing_data == 'delete_column':
                            column['handle_missing_data']= missing_data
                            today = str(datetime.now().date())
                            ###print("type of date",type(today))
                            column['start_date']= today
                            column['end_date']= today
                            column['column_deleted'] = True

                            co = c.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('.', '_').replace(',','_').replace('/','_').replace(':','')
                            delete_column_list.append(co)
                            ##print("the columns are ",delete_column_list)
                        elif missing_data_input:
                            column['handle_missing_data']= missing_data_input
                            today = str(datetime.now().date())
                            ###print("type of date",type(today))
                            column['start_date']= today
                            column['end_date']= ''
                            column['column_deleted'] = False
                            custom_value [c]=missing_data_input

                        c_name = c.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('.', '_').replace(',','_').replace('/','_').replace(':','')
                        meta_data_dict[c_name]=column
                    ##print("the result after nan fill",custom_value)

                    if len(custom_value)>0:
                        result_df = result_df.fillna(custom_value)
                    ##print("the result after nan fill",result_df,delete_column_list)

                    if len(delete_column_list)>0:

                        ##print("the value ",delete_column_list)
                        column_delete_obj = DeleteColumn(result_df)
                        result_df = column_delete_obj.delete_column(delete_column_list)
                        ##print("columns ",result_df.columns.tolist())






                    if   time_series_column and  not time_series_column  == 'no-time-series':
                        t_c = time_series.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('.', '_').replace(',','_').replace('/','_').replace(':','')
                        meta_data_dict[t_c] = {'dtype':'DateTime','handle_missing_data':'drop','start_date':str(datetime.now().date()),'end_date':'','column_deleted':False}
                        l=[t_c]


                        all_columns.append(c)

                    all_cleaned_columns = [ c.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('.', '_').replace(',','_').replace('/','_').replace(':','') for c in  all_columns ]

                    column_dict = {'columns':all_cleaned_columns}

                    if   time_series_column and  not time_series_column  == 'no-time-series':
                        time_series_list = time_series_column.split(':')
                        time_series= time_series_list[-1]
                        t_c = time_series.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('.', '_').replace(',','_').replace('/','_').replace(':','')
                        meta_data,cretae = ProjectMetaData.objects.get_or_create(project=project,date_column_name=t_c)
                        update = ProjectMetaData.objects.filter(pk=meta_data.pk).update(columns=column_dict)
                        update = ProjectMetaData.objects.filter(pk=meta_data.pk).update(meta_data=meta_data_dict)

                    else:
                        meta_data = ProjectMetaData.objects.create(project=project,columns=column_dict,meta_data=meta_data_dict)
                    if   time_series_column and  not time_series_column  == 'no-time-series' :

                        time_series_list = time_series_column.split(':')
                        time_series= time_series_list[-1]
                        time_series = time_series.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('.', '_').replace(',','_').replace('/','_').replace(':','')
                        result_df[time_series] = result_df[time_series].astype(str)

                    result_df.columns = result_df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '').str.replace('.', '_').str.replace(',','_').str.replace('/','_').str.replace(':','')
                    # vl.fullbari("AddProjectView::post", "converted columns names", result_df.columns.to_list())
                    del all_dfs
                    del custom_value
                    del delete_column_list
                    del all_df
                    res_json=result_df.to_json(orient='index')
                    rows = result_df.shape[0]
                    columns = result_df.shape[1]
                    df_head=result_df.head(5)
                    df_tail = result_df.tail(5)
                    df_head_json = df_head.to_json(orient='index')
                    df_tail_json  = df_tail.to_json(orient='index')


                    project_json = ProjectJsonStorage.objects.create(project=project,js=res_json,columns=column_dict)
                    project_json_metadata = ProjectJsonStorageMetadata.objects.create(project_json=project_json,rows=rows,columns=columns,head_json=df_head_json,tail_json=df_tail_json)
                    project_index = ProjectIndex.objects.create(project=project,json_storage=project_json,start_date=start_date,end_date=end_date)
                    project_iqu,created = ProjectBillingPrms.objects.get_or_create(project=project)
                    title = project.name
                    new_title = title
                    sub_string_2 = '_cancelled'
                    if sub_string_2 in title:

                        new_title  = title.split('_cancelled')
                        title =new_title[0]
                    else:
                        title = project.name




                    update_project = Project.objects.filter(pk=project.pk).update(name=title,delete_obj=False)

                    admin_group_name = str(project.pk)+'_Admin'
                    read_group_name = str(project.pk)+'_Read'
                    write_group_name = str(project.pk)+'_Write'
                    delete_group_name = str(project.pk)+'_Delete'

                    group_create_obj = ProjectPermissionGroupCreate(project)
                    admin_group_create = group_create_obj.group_create(admin_group_name)
                    delete_group_create = group_create_obj.group_create(delete_group_name)
                    write_group_create = group_create_obj.group_create(write_group_name)
                    read_group_create = group_create_obj.group_create(read_group_name)
                    group = Group.objects.get(name=admin_group_name)
                    user = User.objects.get(pk=request.user.pk)
                    user.groups.add(group)
                    user.save()
                    user = User.objects.get(pk=request.user.pk)
                    data ={'msg':"Success",'pk':project.pk}
                    #gc.collect()
                    project_files = ProjectFilename.objects.filter(project=project).delete()
                    return JsonResponse(data,safe=False)
        elif api and frequency:
            if basic_token:
                ap = CustomerAPIDetails.objects.get(project=project)
            else:
                ap = CustomerAPIDetails.objects.get(project=project)

            if basic_token:

                headers = {'content-type': 'application/json',
                           'Authorization': basic_token}

                JSONContent = requests.get(api,

                                           headers=headers, verify=True)
            else:
                headers = {'content-type': 'application/json',
                           }

                JSONContent = requests.get(api,
                                           headers=headers, verify=True)
            if 'error' not in JSONContent:
                data_str = JSONContent.text
                data_str = JSONContent.text
                data_json = json.loads(data_str)
                ##print("type", data_json)
                try:
                    df = pd.json_normalize(data_json['results'])
                except:
                    df = pd.json_normalize(data_json['data'])
                df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '').str.replace('.', '_').str.replace(',','_').str.replace('/','_').str.replace(':','')
                df_colums = df.columns.tolist()
                all_columns = df.columns.tolist()
                result_df=df
                project_schema_dict = {}
                schema = {}
                schema['file_name']= 'google-sheet'
                schema['csv']=False
                schema['delemeter ']=''
                columns = ''
                for c in df_colums:
                    columns = columns+','+c
                columns = columns[1:]
                schema['columns']=columns
                project_schema_dict['api']=schema
                project_schema = ProjectSchema.objects.create(project=project,schema=project_schema_dict )
                try:
                    if time_series_column and  not time_series_column  == 'no-time-series':

                        column = time_series_column

                        df = result_df
                        column =column.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('.', '_').replace(',','_').replace('/','_').replace(':','')
                        df[column]= df[column].astype(str)
                        # ##print("not time",column)
                        df[column] = pd.to_datetime(df[column])
                        # ##print("not time series",df[column])
                        df = df.sort_values(by=[column])
                except:
                    data={'error_msg':"invalid column selected for TimeSeries"}
                    #gc.collect()
                    return JsonResponse(data,safe=False)
                if time_series_column and not time_series_column == 'no-time-series':
                    # vl.fullbari("AddProjectView::post","time series column",time_series_column)
                    fillna_obj = FillNan(result_df)
                    time_series_column = time_series_column.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('.', '_').replace(',','_').replace('/','_').replace(':','')
                    l=[time_series_column]
                    # vl.fullbari("AddProjectView::post","time_series",time_series)
                    result_df = fillna_obj.time_series_drop_row(l)


                    try:
                        ###print("inside the try")
                        date_df = result_df
                        date_df[time_series_column]= date_df[time_series_column].astype(str)
                        # date_df[time_series_column]= pd.to_datetime(date_df[time_series_column])
                        date_df[time_series_column] = pd.to_datetime(date_df[time_series_column])
                        date_df = date_df.sort_values(by=[time_series_column])
                        # date_df = date_df.sort_values(by=[time_series_column])
                        start_date = date_df[time_series_column].iloc[0]
                        end_date = date_df[time_series_column].iloc[-1]
                    except:
                        start_date = datetime.now()
                        end_date = datetime.now()
                else:
                    start_date = datetime.now()
                    end_date = datetime.now()
                meta_data_dict = {}
                meta_data_dict = {}
                delete_column_list =[]
                custom_value = {}
                ##print("passed the data")
                if len(all_columns)>0:
                    df = result_df
                    fillna_obj = FillNan(df)
                    for c in all_columns:
                        column = {}
                        ###print("the dataframe",c)
                        if df.dtypes[c] == np.int64:
                            column['dtype'] = 'int'
                        elif df.dtypes[c] == np.float64:
                            column['dtype'] = 'float'
                        elif df.dtypes[c] == np.object:
                            column['dtype'] = 'object'
                        elif df.dtypes[c] == np.bool:
                            column['dtype']= 'bool'
                        elif np.issubdtype(df[c].dtype, np.datetime64):
                            column['dtype'] = "DateTime"
                            df[c] = df[c].astype('str')

                        missing_data = None
                        try:
                            # reading mising data handling
                            ##print("the request post is",request.POST)
                            cu =  c+'_select'
                            missing_data = request.POST[cu]

                            ##print("the missing data",cu,missing_data)
                        except:

                            pass
                        try:
                            # reading mising data handlig
                            ##print("the request post is",request.POST)
                            cu =  c+'_input'
                            missing_data_input = request.POST[cu]

                            ##print("the missing data",c,missing_data)
                        except:

                            pass
                        ###print("the column and missimg data",c,missing_data)

                        if missing_data and missing_data == 'zero':
                            column['handle_missing_data']= 0
                            today = str(datetime.now().date())
                            ###print("type of date",type(today))
                            column['start_date']= today
                            column['end_date']= ''
                            result_df = fillna_obj.fillnan_with_0(c)
                            ###print("nan filled df 0  ",c)
                        elif missing_data and missing_data == 'None':
                            column['handle_missing_data']= 'None'
                            result_df = fillna_obj.fillnan_with_None_value(c)
                            ###print("nan filled df None  ",c)
                            today = str(datetime.now().date())
                            ###print("type of date",type(today))
                            column['start_date']= today
                            column['end_date']= ''
                            column['column_deleted'] = False
                        elif missing_data and missing_data == 'previous':
                            column['handle_missing_data']= 'previous'
                            result_df = fillna_obj.fillnan_with_previous_value(c)
                            ###print("nan filled df ",result_df)
                            today = str(datetime.now().date())
                            ###print("type of date",type(today))
                            column['start_date']= today
                            column['end_date']= ''
                            column['column_deleted'] = False
                        elif missing_data and missing_data == 'drop':
                            column['handle_missing_data']= 'drop'
                            l = [c]
                            result_df = fillna_obj.drop_row(l)
                            ###print("nan filled df ",result_df)
                            today = str(datetime.now().date())
                            ###print("type of date",type(today))
                            column['start_date']= today
                            column['end_date']= ''
                            column['column_deleted'] = False
                        elif missing_data and missing_data == 'delete_column':
                            column['handle_missing_data']= 'delete_column'
                            today = str(datetime.now().date())
                            ###print("type of date",type(today))
                            column['start_date']= today
                            column['end_date']= today
                            column['column_deleted'] = True
                            delete_column_list.append(c)
                        elif missing_data_input:
                                column['handle_missing_data']= missing_data_input
                                today = str(datetime.now().date())
                                ###print("type of date",type(today))
                                column['start_date']= today
                                column['end_date']= ''
                                column['column_deleted'] = False
                                custom_value [c]=missing_data_input

                        c_name = c.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('.', '_').replace(',','_').replace('/','_').replace(':','')
                        meta_data_dict[c_name]=column

                    if len(custom_value)>0:
                        result_df = result_df.fillna(custom_value)
                        ##print("the result after nan fill",result_df,delete_column_list)

                    if len(delete_column_list)>0:

                        ##print("the value ",delete_column_list)
                        column_delete_obj = DeleteColumn(result_df)
                        result_df = column_delete_obj.delete_column(delete_column_list)
                        ##print("columns ",result_df.columns.tolist())
                    if   time_series_column and  not time_series_column  == 'no-time-series':
                        t_c = time_series_column.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('.', '_').replace(',','_').replace('/','_').replace(':','')
                        meta_data_dict[t_c] = {'dtype':'DateTime','handle_missing_data':'drop','start_date':str(datetime.now().date()),'end_date':'','column_deleted':False}
                        l=[t_c]

                        all_columns.append(c)
                    all_cleaned_columns = [ c.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('.', '_').replace(',','_').replace('/','_').replace(':','') for c in  all_columns ]

                    column_dict = {'columns':all_cleaned_columns}

                    if   time_series_column and  not time_series_column  == 'no-time-series':
                        t_c = time_series_column.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('.', '_').replace(',','_').replace('/','_').replace(':','')
                        meta_data,cretae = ProjectMetaData.objects.get_or_create(project=project,date_column_name=t_c)
                        update = ProjectMetaData.objects.filter(pk=meta_data.pk).update(columns=column_dict)
                        update = ProjectMetaData.objects.filter(pk=meta_data.pk).update(meta_data=meta_data_dict)

                    else:
                        meta_data = ProjectMetaData.objects.create(project=project,columns=column_dict,meta_data=meta_data_dict)
                    if   time_series_column and  not time_series_column  == 'no-time-series' :

                        time_series_list = time_series_column.split(':')
                        time_series = time_series_column.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('.', '_').replace(',','_').replace('/','_').replace(':','').replace(':','')
                        result_df[time_series] = result_df[time_series].astype(str)

                    result_df.columns = result_df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '').str.replace('.', '_').str.replace(',','_').str.replace('/','_').str.replace(':','')
                    # vl.fullbari("AddProjectView::post", "converted columns names", result_df.columns.to_list())

                    res_json=result_df.to_json(orient='index')
                    rows = result_df.shape[0]
                    columns = result_df.shape[1]
                    df_head=result_df.head(5)
                    df_tail = result_df.tail(5)
                    df_head_json = df_head.to_json(orient='index')
                    df_tail_json  = df_tail.to_json(orient='index')
                    title = project.name
                    new_title = title
                    sub_string_2 = '_cancelled'
                    if sub_string_2 in title:

                        new_title  = title.split('_cancelled')
                        title =new_title[0]
                    else:
                        title = project.name
                    print("the final title before submit is",title,new_title, )
                    update_project = Project.objects.filter(pk=project.pk).update(name=title,delete_obj=False)

                    project_price = DefaultProjectPricing.objects.all().order_by('-id')[0]
                    project_billing_pricing = ProjectPricing.objects.create(project=project,user=project_price.user,end_point=project_price.end_point,iqs=project_price.iqs,disk_space=project_price.disk_space)
                    project_json = ProjectJsonStorage.objects.create(project=project,js=res_json,columns=column_dict)
                    project_json_metadata = ProjectJsonStorageMetadata.objects.create(project_json=project_json,rows=rows,columns=columns,head_json=df_head_json,tail_json=df_tail_json)
                    project_index = ProjectIndex.objects.create(project=project,json_storage=project_json,start_date=start_date,end_date=end_date)
                    project_iqu,created = ProjectBillingPrms.objects.get_or_create(project=project)

                    admin_group_name = str(project.pk)+'_Admin'
                    read_group_name = str(project.pk)+'_Read'
                    write_group_name = str(project.pk)+'_Write'
                    delete_group_name = str(project.pk)+'_Delete'

                    group_create_obj = ProjectPermissionGroupCreate(project)
                    admin_group_create = group_create_obj.group_create(admin_group_name)
                    delete_group_create = group_create_obj.group_create(delete_group_name)
                    write_group_create = group_create_obj.group_create(write_group_name)
                    read_group_create = group_create_obj.group_create(read_group_name)
                    group = Group.objects.get(name=admin_group_name)
                    user = User.objects.get(pk=request.user.pk)
                    user.groups.add(group)
                    user.save()
                    user = User.objects.get(pk=request.user.pk)
                    data ={'msg':"Success",'pk':project.pk}
                    #gc.collect()
                    return JsonResponse(data,safe=False)


        elif credential and spread_sheet_id:
            sheet_details = CustomerAPIDetails.objects.get(project=project)

            try:
                scope=['htps://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
                file = sheet_details.credentials.open()
                file_content = file.read()
                js_str = json.loads(file_content.decode('utf-8'))
                creadentials = ServiceAccountCredentials.from_json_keyfile_dict(js_str)
                gs = gspread.authorize(creadentials)
                wks = gs.open(spread_sheet_id).sheet1
                data = wks.get_all_records()
                df = pd.DataFrame(data)
            except:
                data={'error_msg':"There is a Error in Reading Sheet"}
                return JsonResponse(data, safe=False)
            data = self.create_df(df,project,time_series_column,request)
            #gc.collect()
            return JsonResponse(data,safe=False)

        elif url and cron_frequency:
            sheet_details = CustomerAPIDetails.objects.get(project=project)
            try:
                if header:
                    df = pd.read_html(url,encoding='utf8',index_col=0,header=int(header))
                else:
                    df = pd.read_html(url,encoding='utf8',index_col=0,header=1)
            except:
                data={'error_msg':"Wrong column Selection for TimeSeries"}
                # ##print("error",data)
                return JsonResponse(data,safe=False)
            data = self.create_df(df[0],project,time_series_column,request)
            #gc.collect()
            return JsonResponse(data,safe=False)


    def create_df(self,df,project,time_series_column,request):
        ''' function to update an project with data '''
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '').str.replace('.', '_').str.replace(',','_').str.replace('/','_').str.replace(':','')
        df_colums = df.columns.tolist()
        all_columns = df.columns.tolist()
        result_df=df
        project_schema_dict = {}
        schema = {}
        schema['file_name']= 'google-sheet'
        schema['csv']=False
        schema['delemeter ']=''
        columns = ''
        for c in df_colums:
            columns = columns+','+c
        columns = columns[1:]
        schema['columns']=columns
        project_schema_dict['google-sheet']=schema
        project_schema = ProjectSchema.objects.create(project=project,schema=project_schema_dict )
        try:
            time_series_column and  not time_series_column  == 'no-time-series'

            column = time_series_column

            df = result_df
            column =column.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('.', '_').replace(',','_').replace('/','_').replace(':','')
            df[column]= df[column].astype(str)
            # ##print("not time",column)
            df[column] = pd.to_datetime(df[column])
            # ##print("not time series",df[column])
            df = df.sort_values(by=[column])
        except:
            pass
        if time_series_column and not time_series_column == 'no-time-series':
            # vl.fullbari("AddProjectView::post","time series column",time_series_column)
            fillna_obj = FillNan(result_df)
            time_series_column = time_series_column.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('.', '_').replace(',','_').replace('/','_').replace(':','')
            l=[time_series_column]
            # vl.fullbari("AddProjectView::post","time_series",time_series)
            result_df = fillna_obj.time_series_drop_row(l)


            try:
                ###print("inside the try")
                date_df = result_df
                date_df[time_series_column]= date_df[time_series_column].astype(str)
                # date_df[time_series_column]= pd.to_datetime(date_df[time_series_column])
                date_df[time_series_column] = pd.to_datetime(date_df[time_series_column])
                date_df = date_df.sort_values(by=[time_series_column])
                # date_df = date_df.sort_values(by=[time_series_column])
                start_date = date_df[time_series_column].iloc[0]
                end_date = date_df[time_series_column].iloc[-1]
            except:
                start_date = datetime.now()
                end_date = datetime.now()
        else:
            start_date = datetime.now()
            end_date = datetime.now()
        meta_data_dict = {}
        meta_data_dict = {}
        delete_column_list =[]
        custom_value = {}
        ##print("passed the data")
        if len(all_columns)>0:
            df = result_df
            df = df.replace('',np.nan)

            fillna_obj = FillNan(df)
            for c in all_columns:
                column = {}
                ###print("the dataframe",c)
                if df.dtypes[c] == np.int64:
                    column['dtype'] = 'int'
                elif df.dtypes[c] == np.float64:
                    column['dtype'] = 'float'
                elif df.dtypes[c] == np.object:
                    column['dtype'] = 'object'
                elif df.dtypes[c] == np.bool:
                    column['dtype']= 'bool'
                elif np.issubdtype(df[c].dtype, np.datetime64):
                    column['dtype'] = "DateTime"
                    df[c] = df[c].astype('str')

                missing_data = None
                missing_data_input = None
                try:
                    # reading mising data handling
                    ##print("the request post is",request.POST)
                    cu =  c+'_select'
                    missing_data = request.POST[cu]

                    ##print("the missing data",cu,missing_data)
                except:

                    pass
                try:
                    # reading mising data handlig
                    ##print("the request post is",request.POST)
                    cu =  c+'_input'
                    missing_data_input = request.POST[cu]

                    ##print("the missing data",c,missing_data)
                except:

                    pass
                ###print("the column and missimg data",c,missing_data)

                if missing_data and missing_data == 'zero':
                    column['handle_missing_data']= 0
                    today = str(datetime.now().date())
                    ###print("type of date",type(today))
                    column['start_date']= today
                    column['end_date']= ''
                    result_df = fillna_obj.fillnan_with_0(c)
                    ###print("nan filled df 0  ",c)
                elif missing_data and missing_data == 'None':
                    column['handle_missing_data']= 'None'
                    result_df = fillna_obj.fillnan_with_None_value(c)
                    ###print("nan filled df None  ",c)
                    today = str(datetime.now().date())
                    ###print("type of date",type(today))
                    column['start_date']= today
                    column['end_date']= ''
                    column['column_deleted'] = False
                elif missing_data and missing_data == 'previous':
                    column['handle_missing_data']= 'previous'
                    result_df = fillna_obj.fillnan_with_previous_value(c)
                    ###print("nan filled df ",result_df)
                    today = str(datetime.now().date())
                    ###print("type of date",type(today))
                    column['start_date']= today
                    column['end_date']= ''
                    column['column_deleted'] = False
                elif missing_data and missing_data == 'drop':
                    column['handle_missing_data']= 'drop'
                    l = [c]
                    result_df = fillna_obj.drop_row(l)
                    ###print("nan filled df ",result_df)
                    today = str(datetime.now().date())
                    ###print("type of date",type(today))
                    column['start_date']= today
                    column['end_date']= ''
                    column['column_deleted'] = False
                elif missing_data and missing_data == 'delete_column':
                    column['handle_missing_data']= 'delete_column'
                    today = str(datetime.now().date())
                    ###print("type of date",type(today))
                    column['start_date']= today
                    column['end_date']= today
                    column['column_deleted'] = True
                    delete_column_list.append(c)
                elif missing_data_input:
                    column['handle_missing_data']= missing_data_input
                    today = str(datetime.now().date())
                    ###print("type of date",type(today))
                    column['start_date']= today
                    column['end_date']= ''
                    column['column_deleted'] = False
                    custom_value [c]=missing_data_input

                c_name = c.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('.', '_').replace(',','_').replace('/','_').replace(':','')
                meta_data_dict[c_name]=column
            result_df = df

            if len(custom_value)>0:
                result_df = result_df.fillna(custom_value)
                ##print("the result after nan fill",result_df,delete_column_list)

            if len(delete_column_list)>0:

                ##print("the value ",delete_column_list)
                column_delete_obj = DeleteColumn(result_df)
                result_df = column_delete_obj.delete_column(delete_column_list)
                ##print("columns ",result_df.columns.tolist())
            if   time_series_column and  not time_series_column  == 'no-time-series':
                t_c = time_series_column.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('.', '_').replace(',','_').replace('/','_').replace(':','')
                meta_data_dict[t_c] = {'dtype':'DateTime','handle_missing_data':'drop','start_date':str(datetime.now().date()),'end_date':'','column_deleted':False}
                l=[t_c]

                all_columns.append(c)
            all_cleaned_columns = [ c.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('.', '_').replace(',','_').replace('/','_').replace(':','') for c in  all_columns ]

            column_dict = {'columns':all_cleaned_columns}

            if   time_series_column and  not time_series_column  == 'no-time-series':
                t_c = time_series_column.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('.', '_').replace(',','_').replace('/','_').replace(':','')
                meta_data,cretae = ProjectMetaData.objects.get_or_create(project=project,date_column_name=t_c)
                update = ProjectMetaData.objects.filter(pk=meta_data.pk).update(columns=column_dict)
                update = ProjectMetaData.objects.filter(pk=meta_data.pk).update(meta_data=meta_data_dict)

            else:
                meta_data = ProjectMetaData.objects.create(project=project,columns=column_dict,meta_data=meta_data_dict)
            if   time_series_column and  not time_series_column  == 'no-time-series' :

                time_series_list = time_series_column.split(':')
                time_series = time_series_column.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('.', '_').replace(',','_').replace('/','_').replace(':','').replace(':','')
                result_df[time_series] = result_df[time_series].astype(str)

            result_df.columns = result_df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '').str.replace('.', '_').str.replace(',','_').str.replace('/','_').str.replace(':','')
            # vl.fullbari("AddProjectView::post", "converted columns names", result_df.columns.to_list())

            res_json=result_df.to_json(orient='index')
            rows = result_df.shape[0]
            columns = result_df.shape[1]
            df_head=result_df.head(5)
            df_tail = result_df.tail(5)
            df_head_json = df_head.to_json(orient='index')
            df_tail_json  = df_tail.to_json(orient='index')
            title = project.name
            new_title = title
            sub_string_2 = '_cancelled'
            if sub_string_2 in title:

                new_title  = title.split('_cancelled')
                title =new_title[0]
            else:
                title = project.name
            update_project = Project.objects.filter(pk=project.pk).update(name=title,delete_obj=False)

            project_price = DefaultProjectPricing.objects.all().order_by('-id')[0]
            project_billing_pricing = ProjectPricing.objects.create(project=project,user=project_price.user,end_point=project_price.end_point,iqs=project_price.iqs,disk_space=project_price.disk_space)
            project_json = ProjectJsonStorage.objects.create(project=project,js=res_json,columns=column_dict)
            project_json_metadata = ProjectJsonStorageMetadata.objects.create(project_json=project_json,rows=rows,columns=columns,head_json=df_head_json,tail_json=df_tail_json)
            project_index = ProjectIndex.objects.create(project=project,json_storage=project_json,start_date=start_date,end_date=end_date)
            project_iqu,created = ProjectBillingPrms.objects.get_or_create(project=project)

            admin_group_name = str(project.pk)+'_Admin'
            read_group_name = str(project.pk)+'_Read'
            write_group_name = str(project.pk)+'_Write'
            delete_group_name = str(project.pk)+'_Delete'

            group_create_obj = ProjectPermissionGroupCreate(project)
            admin_group_create = group_create_obj.group_create(admin_group_name)
            delete_group_create = group_create_obj.group_create(delete_group_name)
            write_group_create = group_create_obj.group_create(write_group_name)
            read_group_create = group_create_obj.group_create(read_group_name)
            group = Group.objects.get(name=admin_group_name)
            user = User.objects.get(pk=request.user.pk)
            user.groups.add(group)
            user.save()
            user = User.objects.get(pk=request.user.pk)
            data ={'msg':"Success",'pk':project.pk}
            return data






class Test(GroupRequiredMixin,View):
    # group_required = []
    #permission_required=('read_project')
    #login_url = '/customer/login/'


    def dispatch(self, request, *args, **kwargs):
        self.group_required= u"Admin"

        ##print("the self of dispatcher",self.group_required)

        return super(Test, self).dispatch(request, *args, **kwargs)

    # def check_membership(self, group,*args,):
    #     ##print("request",args)
    #     # Check some other system for group membership

    #     return True


    def get(self,request,pk):
        # self.group_required.append(u"Admin")
        ##print("permission sucess")
        return render(request,'test.html')



class ProjectDetailsView(GroupRequiredMixin,LoginRequiredMixin,View,):
    ''' project details class where all the details along with Visualization data of project is displayed'''
    def dispatch(self, request, *args, **kwargs):
        pk = str(kwargs['pk'])
        self.login_url = '/customer/login/'
        self.redirect_field_name = 'redirect_to'
        self.template_name='dashboard/index.html'
        admin_name = pk+"_Admin"
        # ##print(type(admin_name), admin_name)
        admin_encode_name = admin_name.encode()
        admin_unicode_name = admin_encode_name.decode('utf-8')
        read_name = pk+"_Read"
        # ##print(type(read_name), read_name)
        read_encode_name = read_name.encode()
        read_unicode_name = read_encode_name.decode('utf-8')
        write_name = pk+"_Write"
        # ##print(type(write_name), write_name)
        write_encode_name = write_name.encode()
        write_unicode_name = write_encode_name.decode('utf-8')
        delete_name = pk+"_Delete"
        # ##print(type(write_name), write_name)
        delete_encode_name = delete_name.encode()
        delete_unicode_name = delete_encode_name.decode('utf-8')
        l= [read_unicode_name,admin_unicode_name,write_unicode_name,delete_unicode_name]
        self.group_required= l
        # ##print("the self of dispatcher",self.group_required)

        return super(ProjectDetailsView, self).dispatch(request, *args, **kwargs)

    def get(self,request,pk):
        template_name='dashboard/project_details.html'
        context = project_details_get(request,pk)
        return render(request,template_name,context)




    def post(self,request,pk):
        seo=SiteSeo.objects.get(choices='Project Details')
        file_form=FileUploadForm()
        update_form=ProjectUpdateForm()
        template_name='dashboard/project_details.html'
        project=Project.objects.get(pk=pk)
        ##print("post")
        json_fields = ProjectJsonStorage.objects.filter(project=project)
        ##print("the json project",json_fields)


        dfs = []
        for i in json_fields:
            ##print("pk ",i.pk)

            json_string = json.loads(i.js)
            json_df = pd.DataFrame(json_string)
            ##print(type(json_df.head()))

            transposed_df = json_df.transpose()
            ##print(transposed_df)

            dfs.append(transposed_df)
        res_df = pd.concat(dfs)
        string_df = res_df.select_dtypes(include ='object')

        columns = res_df.columns.to_list()
        string_df = string_df.columns.to_list()

        ##print(request.POST)




        try:

            request.POST['scatter']
            ##print("scatter")
            try :

                    try:
                        request.POST['plot_type_2d']
                        ##print("2d")
                        x = request.POST['scatter_2d_x']
                        y = request.POST['scatter_2d_y']
                        color = request.POST.get('scatter_2d_color',None)
                        div = plots.scatter_plot(res_df,x,y,color)
                    except:
                        pass


                    try:
                        request.POST['plot_type_3d']

                        ##print("3d")
                        x = request.POST['scatter_3d_x']
                        y = request.POST['scatter_3d_y']
                        z = request.POST['scatter_3d_z']
                        color = request.POST.get('scatter_3d_color',None)
                        div = plots.scatter_plot_3d(res_df,x,y,z,color)
                    except:
                        pass

            except:
                pass


        except:
            pass
        try:

            request.POST['bar']
            ##print("bar")
            x = request.POST['bar_x']
            y = request.POST['bar_y']
            color = request.POST.get('bar_color',None)
            div = plots.bar_plot(res_df,x,y,color)
        except:
            pass
        try:

            try:
                request.POST['line_plot_type_2d']
                ##print("2d")
                x = request.POST['line_2d_x']
                y = request.POST['line_2d_y']
                color = request.POST.get('line_2d_color',None)
                div = plots.line_plot(res_df,x,y,color)
            except:
                pass
            try:
                request.POST['line_plot_type_3d']
                ##print("3d")
                x = request.POST['line_3d_x']
                y = request.POST['line_3d_y']
                z = request.POST['line_3d_z']
                color = request.POST.get('line_3d_color',None)
                div = plots.line_plot_3d(res_df,x,y,z,color)
            except:
                pass
        except:
            pass

        try:

            request.POST['histogram']
            ##print("histogram")
            x = request.POST['histogram_x']
            y = request.POST['histogram_y']
            color = request.POST.get('histogram_color',None)
            div = plots.histogram_plot(res_df,x,y,color)
        except:
            pass
        data=project.type.data_title
        data_description=project.type.data_description

        ##print('data scatter',data)
        context = {

                'project':project,
                'data_description':data_description,

                'graph':div,
                'file_form':file_form,
                'columns':columns,
                'update_form':update_form,
                'string_df':string_df,
                'seo':seo
                }

        return render(request,template_name,context)


def project_details_get(request,pk):
    seo=SiteSeo.objects.get(choices='Project Details')

    project=Project.objects.get(pk=pk)
    permission = identify_user_permission(project,request.user)
    user = User.objects.get(pk=request.user.pk)
    pk=str(project.pk)
    current_site = get_current_site(request)
    site_name = current_site.name
    domain = current_site.domain
    if domain.startswith('127.0.'):
        domain = 'https://'+domain
    else:
        domain = 'https://'+domain
    # ##print('domain',domain)
    # dashboard_form = ProjectDashboardForm(initial={'project':project.pk})
    # dashboard_form.fields['user'].queryset = ProjectUser.objects.filter(project=project)
    # dashboard_form.fields['dashboard'].queryset = ProjectDashboard.objects.filter(project=project)

    if ProjectIndex.objects.filter(project=project).exists():
        start_indexer = ProjectIndex.objects.values('start_date').filter(project=project).order_by('id')[0]
        end_indexer = ProjectIndex.objects.values('end_date').filter(project=project).order_by('-id')[0]
        start_year = start_indexer['start_date'].year
        end_year = end_indexer['end_date'].year
        default_start_date = start_indexer['start_date'].date()
        default_end_date = end_indexer['end_date'].date()


    else:
        start_year =  None
        end_year = None
        default_start_date = None
        default_end_date = None

    project_metadata = ProjectMetaData.objects.get(project=project)
    if project_metadata.date_column_name:
        time_series_project = True
    else:
        time_series_project = None


    if ProjectEndPoint.objects.filter(project=project).exists():
        project_endpoints = ProjectEndPoint.objects.filter(project=project).order_by('name')
    else:
        project_endpoints=None

    customer=Customer.objects.get(user=request.user)
    if ProjectQuery.objects.filter(project=project).exists():
        project_query = ProjectQuery.objects.filter(project=project).order_by('-created')
        query_columns = []

    else:
        project_query = None
        query_columns=None
    if ProjectJsonStorage.objects.filter(project=project).exists():

        project_jsons = ProjectJsonStorageMetadata.objects.filter(Q(project_json__project=project))
        json_meta_obj = ProjectJsonAlter(project_jsons)
        data = json_meta_obj.claculate_rows_columns()
        df_rows = data['rows']
        df_columns_count = data['columns']
        df_head = json_meta_obj.dataframe_head_tail()
        df_columns = df_head.columns.tolist()
        metadata = ProjectMetaData.objects.get(project=project)
        columns_dtypes = {}
        for key, value in metadata.meta_data.items():
            if key in df_columns:
                ##print("key",key)
                if value['dtype'] == 'int':
                    df_head[key] =pd.to_numeric(df_head[key])
                    if key in df_columns:
                        df_head[key] = pd.to_numeric(df_head[key])
                    columns_dtypes[key]= 'number'
                elif value['dtype'] == 'float':
                    ##print("final key",key,df_head[key],df_head[key].dtypes)
                    df_head[key] = pd.to_numeric(df_head[key])
                    if key in df_columns:
                        df_head[key] = pd.to_numeric(df_head[key])
                    columns_dtypes[key]= 'number'
                elif value['dtype'] == 'object':
                    df_head[key] = df_head[key].astype(str)
                    if key in df_columns:
                        df_head[key] = df_head[key].astype(str)
                    columns_dtypes[key]= 'string'
                elif value['dtype'] == 'bool':
                    df_head[key] = df_head[key].astype(bool)
                    if key in df_columns:
                        df_head[key] = df_head[key].astype(bool)
                    columns_dtypes[key]= 'bool'
                elif value['dtype'] == 'DateTime':
                    df_head[key] =pd.to_datetime(df_head[key])
                ##print("the data key",key)
                    if key in df_columns:
                        df_head[key] = pd.to_datetime(df_head[key])
                    columns_dtypes[key]= 'DateTime'
        ##print("the datatypes",df_head.dtypes)
        number_columns = df_head.select_dtypes(include=['number'])
        df_columns    = df_head.select_dtypes(include=['number','bool','object'])
        if metadata.date_column_name:
            df_head[metadata.date_column_name] = df_head[metadata.date_column_name].astype('str')

        res_df__table_content = df_head.to_html(classes="table table-striped tableFixHead",border="0")
    else:
        res_df__table_content = None
        df_rows = 0
        df_columns = []
        columns_dtypes={}
        columns_dtypes = {}
        df_columns_count = 0


    if ProjectDashboard.objects.filter(Q(project=project) ).exists():
        # ##print("project admin")
        dashboard=ProjectDashboard.objects.filter(Q(project=project) ).order_by('-id')
        dashboard_count=ProjectDashboard.objects.filter(Q(project=project) ).count()
        # ##print("dashboard",dashboard)
        # ##print("dashboard count",dashboard_count)

        context = {

                    'project':project,
                    'customer':customer,
                    'dashboard':dashboard,
                    'permission':permission,
                    'dashboard_count':dashboard_count,
                    'seo':seo,
                    'columns_dtypes':columns_dtypes,
                    'df_columns':df_columns,
                    'number_columns':number_columns,
                    'project_query':project_query,
                    'res_df__table_content':res_df__table_content,\
                    'df_rows':df_rows,
                    'time_series_project':time_series_project,
                    'df_columns_count':df_columns_count,
                    'domain':domain,
                    'start_year':start_year,
                    'end_year':end_year,
                    'default_start_date':default_start_date,
                    'default_end_date':default_end_date,
                    'query_columns':query_columns,
                    'project_endpoints':project_endpoints

                    }

    else:
        ##print("no dashboard")
        context = {

                    'project':project,
                    'permission':permission,

                    'customer':customer,
                    'seo':seo,
                    'columns_dtypes':columns_dtypes,
                    'df_columns':df_columns,
                    'number_columns':number_columns,
                    'project_query':project_query,
                  'res_df__table_content':res_df__table_content,
                    'df_rows':df_rows,
                    'df_columns_count':df_columns_count,
                    'domain':domain,
                    'time_series_project':time_series_project,
                    'start_year':start_year,
                    'end_year':end_year,
                    'default_start_date':default_start_date,
                    'default_end_date':default_end_date,
                    'query_columns':query_columns,
                    'project_endpoints':project_endpoints

                }
    return context



class FileUploadView(LoginRequiredMixin,PermissionRequiredMixin,View):
    #TODO:presently not using will be used for project file reupload
    login_url = '/customer/login/'
    redirect_field_name = 'redirect_to'
    template_name='dashboard/index.html'
    permission_required = ('coreapp.change_project',)
    def post(self,request,pk):
        '''post method to upload extra files on project details page'''
        template_name='dashboard/update-project-details.html'
        project = Project.objects.get(pk=pk)
        json_data = ProjectJsonStorage.objects.filter(project=project)[:1].get()
        ##print(type(json_data.js))


        df= pd.DataFrame.from_dict(
        {k: v for k, v in json.loads(json_data.js).items()}, 'index')
        ##print('df',df)
        df_columns= df.columns.to_list()
        ##print('df_columns',df_columns)
        if request.method == 'POST':
            try:
                ##print("3 files upload")
                file1 = request.FILES["file_1"]
                ##print('file1',file1)
                file2 = request.FILES["file_2"]
                ##print('file2',file2)
                file3 = request.FILES["file_3"]
                ##print('file3',file3)
                file1_df=pd.read_csv(file1, encoding = "ISO-8859-1")
                file2_df=pd.read_csv(file2, encoding = "ISO-8859-1")
                file3_df=pd.read_csv(file3, encoding = "ISO-8859-1")
                file1_columns = file1_df.columns.to_list()
                file2_columns = file2_df.columns.to_list()

                project_meta = ProjectMetaData.objects.filter(project=project)[:1].get()
                ##print('project_meta',project_meta.connectivity_column)
                file1_columns.remove(project_meta.connectivity_column)
                ##print('file1_columns',file1_columns)
                ##print('file2_columns',file2_columns)
                res_df =reduce(lambda left,right: pd.merge(left,right,on=project_meta.connectivity_column, how='outer'), [file1_df,file2_df,file3_df])
                ##print(res_df.columns.to_list())
                file_columns=res_df.columns.to_list()
                difference_columns=Diff(file_columns,df_columns)
                ##print('difference_columns',difference_columns)
                if difference_columns:
                    new_df =reduce(lambda left,right: pd.merge(left,right,on=df_columns, how='right'), [res_df])
                    ##print("new_df",new_df)
                    new_json=new_df.to_json(orient='index')
                    project_configuration,created = ProjectConfiguration.objects.get_or_create(project=project,column_name=difference_columns,user=request.user,changed_date=datetime.now())
                    ##print('project_configuration')
                    project_json,created =ProjectJsonStorage.objects.get_or_create(project=project,js=new_json)
                    ##print("new json created",project_json.js)
                    for d in difference_columns:
                        project_column, created = ProjectColumn.objects.get_or_create(project=project,column=d)
                    ##print('project_column',project_column)
                else:
                    pass
                    ##print("no changes")
            except:
                ##print("3 file  failed")




                try:
                    ##print("2 files upload")
                    file1 = request.FILES["file_1"]
                    ##print('file1',file1)
                    file2 = request.FILES["file_2"]
                    file1_df=pd.read_csv(file1, encoding = "ISO-8859-1")
                    file2_df=pd.read_csv(file2, encoding = "ISO-8859-1")
                    file1_columns = file1_df.columns.to_list()
                    file2_columns = file2_df.columns.to_list()

                    project_meta = ProjectMetaData.objects.filter(project=project)[:1].get()
                    ##print('project_meta',project_meta.connectivity_column)
                    file1_columns.remove(project_meta.connectivity_column)
                    ##print('file1_columns',file1_columns)
                    ##print('file2_columns',file2_columns)
                    res_df =reduce(lambda left,right: pd.merge(left,right,on=project_meta.connectivity_column, how='outer'), [file1_df,file2_df])
                    ##print(res_df.columns.to_list())
                    file_columns=res_df.columns.to_list()
                    difference_columns=Diff(file_columns,df_columns)
                    ##print('difference_columns',difference_columns)
                    if difference_columns:
                        new_df =reduce(lambda left,right: pd.merge(left,right,on=df_columns, how='right'), [res_df])
                        ##print("new_df",new_df)
                        new_json=new_df.to_json(orient='index')
                        project_configuration,created = ProjectConfiguration.objects.get_or_create(project=project,column_name=difference_columns,user=request.user,changed_date=datetime.now())
                        ##print('project_configuration')
                        project_json,created =ProjectJsonStorage.objects.get_or_create(project=project,js=new_json)
                        ##print("new json created",project_json.js)
                        for d in difference_columns:
                            project_column, created = ProjectColumn.objects.get_or_create(project=project,column=d)
                        ##print('project_column',project_column)
                    else:
                        pass
                        ##print("no changes")
                except:
                    ##print("file 2 failed")





                    try:
                        file1 = request.FILES["file_1"]
                        ##print('file1',file1)
                        df=pd.read_csv(file1, encoding = "ISO-8859-1")
                        file1_columns = df.columns.to_list()
                        difference_columns=Diff(file1_columns,df_columns)
                        ##print(difference_columns)
                        if difference_columns:
                            new_df =reduce(lambda left,right: pd.merge(left,right,on=df_columns, how='right'), [df])
                            ##print('new_df',new_df)
                            new_json=new_df.to_json(orient='index')
                            project_configuration,created = ProjectConfiguration.objects.get_or_create(project=project,column_name=difference_columns,user=request.user,changed_date=datetime.now())
                            ##print('project_configuration')
                            project_json,created =ProjectJsonStorage.objects.get_or_create(project=project,js=new_json)
                            ##print("new json created",project_json.js)
                            project_column, created = ProjectColumn.objects.get_or_create(project=project,column=difference_columns)
                            ##print('project_column',project_column)
                        else:
                            pass
                            ##print("no changes")
                    except:
                        pass
                            ##print("something is wrong")

            return redirect('/dashboard/')
        else:
            ##print(file_form.errors)
            context = {
            'file_form':file_form,
            }
            return render(request,template_name,context)




class ProjectUpdateView(GroupRequiredMixin,LoginRequiredMixin,View):
    '''project update class where customer can update the project details'''
    def dispatch(self, request, *args, **kwargs):
        pk = str(kwargs['pk'])
        self.login_url = '/customer/login/'
        self.redirect_field_name = 'redirect_to'
        self.template_name='dashboard/index.html'
        admin_name = pk+"_Admin"
        ##print(type(admin_name), admin_name)
        admin_encode_name = admin_name.encode()
        admin_unicode_name = admin_encode_name.decode('utf-8')
        read_name = pk+"_Read"


        ##print(type(read_name), read_name)
        read_encode_name = read_name.encode()
        read_unicode_name = read_encode_name.decode('utf-8')
        l= [read_unicode_name,admin_unicode_name]
        self.group_required= l
        ##print("the self of dispatcher",self.group_required)

        return super(ProjectUpdateView, self).dispatch(request, *args, **kwargs)

    def get(self,request,pk):
        '''get method to display the update project form'''
        template_name='dashboard/update-project-details.html'
        project=Project.objects.get(pk=pk)
        update_form=ProjectUpdateForm(initial={'project_title':project.name,'industry':project.type.industry_name.pk,'project_duration':project.project_duration,})
        file_upload_form = FileUploadForm()

        data=project.name
        data_description=project.type.description
        user = User.objects.get(pk=request.user.pk)
        customer=Customer.objects.get(user=user)
        if Project.objects.filter(pk=project.pk,admin_user=request.user).exists():
            permission="Admin"
        elif ProjectUser.objects.filter(project=project,project_user=request.user).exists():
            user_group = User.objects.get(pk=request.user.pk)

            for g in user_group.groups.all():
                if g.name == str(project.pk)+"_Read":
                    permission="Read"
                elif g.name == str(project.pk)+"_Write":
                    permission="Write"
                elif g.name == str(project.pk)+"_Delete":
                    permission="Delete"
                elif g.name == str(project.pk)+"_Admin":
                    permission="Admin"
        else:
            permission=None



        ##print(project)
        ##print("pk",pk)
        pk=str(project.pk)
        file_form=FileUploadForm()
        current_site = get_current_site(request)
        site_name = current_site.name
        domain = current_site.domain
        if domain.startswith('127.0.'):
            domain = 'https://'+domain
        else:
            domain = 'https://'+domain



        if ProjectEndPoint.objects.filter(project=project).exists():
             project_endpoints = ProjectEndPoint.objects.filter(project=project).order_by('name')
        else:
            project_endpoints=None
        if ProjectDashboard.objects.filter(Q(project=project) ).exists():
                ##print("project admin")
                dashboard=ProjectDashboard.objects.filter(Q(project=project) ).order_by('name')
                dashboard_count=ProjectDashboard.objects.filter(Q(project=project)).count()
                ##print("dashboard",dashboard)
                ##print("dashboard count",dashboard_count)
        else:
            dashboard=None
            dashboard_count=0



        context={
                'file_upload_form':file_upload_form,
                'update_form':update_form,
                'project':project,
                'data':data,
                'data_description':data_description,
                'customer':customer,
                'dashboard':dashboard,
                'dashboard_count':dashboard_count,
                'project_endpoints':project_endpoints
            }

        return render(request,template_name,context)
    def post(self,request,pk):
        '''post method to receive the updated details of the project'''
        template_name='dashboard/update-project-details.html'
        update_form=ProjectUpdateForm(request.POST)
        if update_form.is_valid():
            project_title=update_form.cleaned_data["project_title"]
            data_description=request.POST["data_description"]
            end_goal=request.POST["end_goal"]
            color_code = request.POST['color']
            industry = update_form.cleaned_data['industry']
            project_duration =update_form.cleaned_data['project_duration']
            project= Project.objects.get(pk=pk)
            project_update=Project.objects.filter(pk=pk).update(name=project_title,end_goal=end_goal,project_duration=project_duration)#updating the title of the project
            project_type_update = ProjectType.objects.filter(pk=project.type.pk).update(industry_name=industry,description=data_description,color_code=color_code)
            action.send(request.user,verb="Updated" + str(project_title))
            projt=Project.objects.get(pk=pk)
            type_pk=projt.type.pk #assigning the pk of type to type_pk
            pk=str(projt.pk)


            return redirect('/project-update/' + pk +'/')
        else:
            ##print(update_form.errors)
            context={
                'update_form':update_form
                }
            return render(request,template_name,context)
'''End of project update class where customer can update the project details'''

class SearchView(ListView,LoginRequiredMixin,):

    '''search view to search the project by its title, date, industry and type'''
    template_name = 'dashboard/search_view.html'
    login_url = '/customer/login/'
    redirect_field_name = 'redirect_to'
    paginate_by = 20
    count = 0

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['count'] = self.count or 0
        context['query'] = self.request.GET.get('q')
        return context
    def get(self,request):

        request = self.request
        template_name = 'dashboard/search_view.html'
        query = request.GET.get('q', None)
        user=User.objects.get(username=request.user)
        customer = Customer.objects.get(user=user)
        ##print('logged in user',user)
        customer=Customer.objects.get(user=request.user)
        projects_delete = Project.objects.filter(Q(admin_user=user) and  Q(delete_datetime__isnull=False) | Q(delete_obj=False)).count()
        ##print("project count ",projects_delete)
        if  projects_delete > 0:
            projects_delete = True
        else:
            projects_delete = False

        if query is not None:
            ''' if search is not none, then customer search is filtered with the following lines'''
            projects = Project.objects.exclude(Q(name__icontains='_cancelled') | Q(name__icontains='_backup'))
            project_users = ProjectUser.objects.exclude(Q(project__name__icontains='_cancelled') | Q(project__name__icontains='_backup'))
            project_results = projects.filter(Q(admin_user__username__exact=request.user) &
                                                    Q(name__icontains=query)).distinct()
            project_user_results = project_users.filter(Q(project_user__username__exact=request.user) &
                                                    Q(project__name__icontains=query)).distinct()



            queryset_chain = chain(
                    project_results,
                    project_user_results


            )
            qs = sorted(queryset_chain,
                        key=lambda instance: instance.pk,
                        reverse=True)
            ##print('project_results',qs)
            context={'object_list':qs,'customer':customer,'projects_delete':projects_delete}
            return render(request,template_name,context)

            # since qs is actually a list



'''End of search view to search the project by its title, date, industry and type'''




'''Start of class to display add users form and create the project user'''
class AddUserView(GroupRequiredMixin,LoginRequiredMixin,View):
    def dispatch(self, request, *args, **kwargs):
        pk = str(kwargs['pk'])
        self.login_url = '/customer/login/'
        self.redirect_field_name = 'redirect_to'
        self.template_name='dashboard/index.html'
        admin_name = pk+"_Admin"
        ##print(type(admin_name), admin_name)
        admin_encode_name = admin_name.encode()
        admin_unicode_name = admin_encode_name.decode('utf-8')
        read_name = pk+"_Read"
        ##print(type(admin_name), admin_name)
        read_encode_name = read_name.encode()
        read_unicode_name = read_encode_name.decode('utf-8')
        write_name = pk+"_Write"
        ##print(type(admin_name), admin_name)
        write_encode_name = write_name.encode()
        write_unicode_name = write_encode_name.decode('utf-8')
        delete_name = pk+"_Delete"
        ##print(type(admin_name), admin_name)
        delete_encode_name = delete_name.encode()
        delete_unicode_name = delete_encode_name.decode('utf-8')
        l=[admin_unicode_name,read_unicode_name,write_unicode_name,delete_unicode_name]
        self.group_required = l

        ##print("the self of dispatcher",self.group_required)

        return super(AddUserView, self).dispatch(request, *args, **kwargs)
    def get(self,request,pk):
        '''get method to display add user form'''
        template_name='dashboard/add_users.html'
        context = adduserget(request,pk)
        return render(request,template_name,context)

    def post(self,request,pk):
        '''post method to receive email id of user added and to create project user'''
        template_name='dashboard/add_users.html'
        seo=SiteSeo.objects.get(choices='User Management')
        add_user_form=AddUsersForm(request.POST)
        customer=Customer.objects.get(user=request.user)
        current_site = get_current_site(request)
        project=Project.objects.get(pk=pk)
        site_name = current_site.name
        domain = current_site.domain

        if add_user_form.is_valid():
            ##print("form valid")
            email=add_user_form.cleaned_data["email"]
            permissions=add_user_form.cleaned_data["permissions"]
            project=Project.objects.get(pk=pk) # get the present project
            ##print('project',project)
            action.send(request.user,verb="Added" + "  " + str(email) + "  " + "to" + "  "+ str(project))
            
            try:
                user=User.objects.get(username=email) #query user model to check whether user is present
                
                html_message = render_to_string('dashboard/project-user.html', {'requested_user':request.user,'user':user})
                # message = request.user.username  +  '    added you to'   +  "  "  + project.name
                
                subject= 'You are invited to join a project on Brayn.AI'
                plain_message = 'You are invited to join a project on Brayn.AI'
                from_email = 'noreply@brayn.ai'
                to_email = [user.email]
                mail.send_mail(subject, plain_message, 'noreply@brayn.ai', to_email, html_message=html_message)
                

                ##print("email sent")
            except:
                user, created=User.objects.get_or_create(username=email,email=email,password='dummy')
                pk=user.pk
                subject = 'You are invited to join a project on Brayn.AI'
                # uid and token are created
                html_message = render_to_string('dashboard/send_signup_link.html', {'pk': pk,'uid': urlsafe_base64_encode(force_bytes(pk)),'token': default_token_generator.make_token(user),'domain':domain,'requested_user':request.user,'user':user})
                plain_message = strip_tags(html_message)
                from_email = '<noreply@brayn.ai>'
                to = email
                #sending mail to customer with from, to address and html message which includes the password reset link
                mail.send_mail(subject, plain_message, from_email, [to], html_message=html_message)
                ##print("email sent")

            #create project user for the project
            if permissions=="Read":
                permissions=Group.objects.get(name=str(project.pk)+"_Read")
            elif permissions=="Read Write":
                permissions=Group.objects.get(name=str(project.pk)+"_Write")
            elif permissions=="Read Write Delete":
                permissions=Group.objects.get(name=str(project.pk)+"_Delete")
            elif permissions=="Admin":
                permissions=Group.objects.get(name=str(project.pk)+"_Admin")
            if project.admin_user.email == email:
                pass
            else:
                project_usage = ProjectBillingPrms.objects.get(project=project)
                total_user = project_usage.user
                total_user_count = ProjectUser.objects.filter(project=project).count()
                total_users = total_user+5
                print("the count",total_user_count,total_users)
                if total_user_count<total_users:

                    project_user,created = ProjectUser.objects.get_or_create(project=project,project_user=user)
                    ##print(project_user.project_user)
                    user=User.objects.get(username=project_user.project_user.username)
                    user.groups.add(permissions)
                    user.save()
                    ##print('user',user.username)
                    project_user=user
                    notification, created = UserNotification.objects.get_or_create(user=user)
                    user=User.objects.get(username=user.username)
                    notification_user = UserNotification.objects.filter(user=user)
                    ##print(notification)
                    for n in notification_user:
                        count=n.notification_count
                        ##print('count',count)
                        notification_count= UserNotification.objects.filter(pk=n.pk).update(notification_count= count+ 1,notification_read="False")
                        ##print("notification_count.count",notification_count)
                        ##print("notification_count.read",notification_count)
                    pk = project.pk
                    context = adduserget(request,pk)
                    context['msg'] = "Added User Successfully"
                    return render(request,template_name,context)


                else:
                    pk = project.pk
                    context= single_project_details(request,pk)
                    template_name='dashboard/single_project_details.html'
                    context['msg'] = "Project has Exceeded The User Limit"
                    return render(request,template_name,context)


            pk = project.pk
            context = adduserget(request,pk)
            context['msg'] = "Added User Successfully"
            return render(request,template_name,context)
        else:

            users = User.objects.filter(pk=request.user.pk)
            if ProjectDashboard.objects.filter(Q(project=project) & (Q(dashboard_admin_user__pk =request.user.pk)| Q(dashboard_users__in=users) )).exists():
                dashboard= ProjectDashboard.objects.filter(Q(project=project) & (Q(dashboard_admin_user__pk =request.user.pk)| Q(dashboard_users__in=users) ))
            else:
                dashboard=None
            try:
                integrations = CustomerAPIDetails.objects.filter(project=project)
                context={
                'project':project,
                'add_user_form':add_user_form,
                'customer':customer,
                'seo':seo,
                'integrations':integrations,
                'permission':permission,
                'dashboard':dashboard,
                'msg':"Invalid User Form"
                }
            except:
                context={
                'project':project,
                'add_user_form':add_user_form,
                'customer':customer,
                'seo':seo,
                'permission':permission,
                'dashboard':dashboard,
                'msg':"Invalid User Form"
                }

            return render(request,template_name,context)


# function for addd user get
def adduserget(request,pk):
    add_user_form = AddUsersForm()
    customer=Customer.objects.get(user=request.user)

    seo=SiteSeo.objects.get(choices='User Management')
    project=Project.objects.get(pk=pk)

    pk=str(project.pk)
    admin_user = request.user
    method="GET"
    if Project.objects.filter(pk=project.pk,admin_user=request.user).exists():

        permission="Admin"
    elif ProjectUser.objects.filter(project=project,project_user=request.user).exists():
        user_p =ProjectUser.objects.get(project=project,project_user=request.user)
        user = user_p.project_user
        user_group = User.objects.get(pk=request.user.pk)

        for g in user_group.groups.all():
            if g.name == str(project.pk)+"_Read":
                permission="Read"
            elif g.name== str(project.pk)+"_Write":
                permission="Write"
            elif g.name == str(project.pk)+"_Delete":
                permission="Delete"
            elif g.name == str(project.pk)+"_Admin":
                permission="Admin"
    else:
        permission="None"
    ##print("permission",permission)

    project_user = ProjectUser.objects.filter(project=project)


    #for dashboard of the projects

    users = User.objects.filter(pk=request.user.pk)
    if ProjectDashboard.objects.filter(Q(project=project) ).exists():
        dashboard= ProjectDashboard.objects.filter(Q(project=project) )
    else:
        dashboard=None
    if ProjectEndPoint.objects.filter(project=project).exists():
        project_endpoints = ProjectEndPoint.objects.filter(project=project).order_by('name')
    else:
        project_endpoints=None
    customer_profiles = {}
    #for customer profiles of the users
    admin_profile = Customer.objects.get(user=request.user)
    user_permissions = {}
    if ProjectUser.objects.filter(project=project).exists():
        project_users = ProjectUser.objects.filter(project=project)
        for user in project_users:
            try:

                customer = Customer.objects.get(user=user.project_user)
                customer_profiles[user.project_user.pk] = customer
            except:
                pass

            for group in user.project_user.groups.all():
                ##print("user group name",group,user.project_user.pk)
                if group.name  == str(project.pk)+'_Delete':
                    user_permission = 'Delete'
                elif group.name  == str(project.pk)+'_Read':
                    user_permission = 'Read'
                elif group.name  == str(project.pk)+'_Write':
                    user_permission = 'Write'
                elif group.name  == str(project.pk)+'_Admin':
                    user_permission = 'Admin'
            user_permissions[user.project_user.pk]= user_permission
    else:
        pass
    ##print("user permissions are",user_permissions)
    context={'admin_profile':admin_profile,'permission':permission,'add_user_form':add_user_form,'dashboard':dashboard,'project':project,'project_users':project_user,'customer_profiles':customer_profiles,'seo':seo,'user_permissions':user_permissions,'project_endpoints':project_endpoints,'prject':project}
    return context

def accept_view(request,pk):
    if request.method == 'POST':
        ##print("inside accept_view",request.POST)
        count=request.POST['notification_c']
        ##print(count)

        time=datetime.now()

        project_user=ProjectUser.objects.filter(pk=pk).update(accept='True',accepted_time=time)
        ##print(project_user)
        user = User.objects.get(username=request.user)
        notification_user=UserNotification.objects.get(user=user)
        pk=notification_user.pk
        notification_count = UserNotification.objects.filter(pk=pk).update(notification_count=count)
        ##print("notification_count updated",notification_count)
        updated_notification = UserNotification.objects.get(user=user)
        updated_notification_count=updated_notification.notification_count
        updated_notification_read=updated_notification.notification_read
        ##print('updated_notification_count',updated_notification_count)
        data={
            'updated_notification_count':updated_notification_count,
            'updated_notification_read':updated_notification_read
        }
        return JsonResponse(data,safe=False)

        # action.send(request.user,verb="Accepted the" + str(project))










'''class to display the save dashboard form'''
class DashboardSaveFormView(LoginRequiredMixin,TemplateView):
    login_url = '/customer/login/'
    redirect_field_name = 'redirect_to'
    template_name='dashboard/index.html'
    def get(self,request,pk):
        '''method to display the dashboard creation form'''
        template_name='dashboard/dashboard_creation_form.html'
        user=request.user
        customer=Customer.objects.get(user=user)
        ##print('customer', customer)
        project=Project.objects.get(pk=pk)
        project_users=ProjectUser.objects.filter(project=project)
        # for p in project_users:
        #     ##print(p.project_user)
        #     user=User.objects.filter(username=p.project_user)
        #     ##print(user)

        dashboard_form = ProjectDashboardForm()
        context={
            'dashboard_form':dashboard_form,
            'project_users':project_users,
            'customer':customer
        }
        return render(request,template_name,context)

    def post(self,request,pk):
        '''method to recieve the save dashboard form details and create dashboard'''
        template_name='dashboard/dashboard_creation_form.html'
        project=Project.objects.get(pk=pk)
        project_users=ProjectUser.objects.filter(project=project)
        dashboard_form = ProjectDashboardForm(request.POST)
        if request.method == "POST":
            dashboard_user = request.POST.getlist("dashboard_user")
            ##print(dashboard_user)

        if dashboard_form.is_valid():
            ##print("valid")
            dashboard_title = dashboard_form.cleaned_data["dashboard_title"]
            ##print(dashboard_title)
            user=User.objects.get(username=request.user)
            # plot,created = Plot.objects.get_or_create(plot_type=)
            dashboard,created = ProjectDashboard.objects.get_or_create(project=project,dashboard_title=dashboard_title,dashboard_admin_user=user)
            action.send(user,verb="Created a dashboard named " + str(dashboard))
            for i in dashboard_user:
                users=i
                ##print(users)
                user=User.objects.get(username=users)
                dashboard.dashboard_users.add(user)
                action.send(request.user,verb="added" + str(user) + "to" + str(project))
            ##print(dashboard)
            pk=str(dashboard.pk)
            return redirect('/project-dashboard/' + pk +'/' )
        else:
            ##print(dashboard_form.errors)
            context={
                'dashboard_form':dashboard_form,
                'project_users':project_users
            }
            return render(request,template_name,context)

class ProjectDashboardView(LoginRequiredMixin,View):
    login_url = '/customer/login/'
    redirect_field_name = 'redirect_to'
    template_name='dashboard/index.html'
    def dispatch(self, request, *args, **kwargs):
        pk = kwargs['pk']
        dashboard = ProjectDashboard.objects.get(pk=pk)
        project=Project.objects.get(pk=dashboard.project.pk)
        pk= str(project.pk)
        self.login_url = '/customer/login/'
        self.redirect_field_name = 'redirect_to'
        self.template_name='dashboard/index.html'
        admin_name = pk+"_Admin"
        ##print(type(admin_name), admin_name)
        admin_encode_name = admin_name.encode()
        admin_unicode_name = admin_encode_name.decode('utf-8')
        write_name = pk+"_Write"
        ##print(type(write_name), write_name)
        write_encode_name = write_name.encode()
        write_unicode_name = write_encode_name.decode('utf-8')
        read_name = pk+"_Read"
        ##print(type(write_name), write_name)
        read_encode_name = read_name.encode()
        read_unicode_name = read_encode_name.decode('utf-8')
        delete_name = pk+"_Delete"
        delete_encode_name = delete_name.encode()
        delete_unicode_name = delete_encode_name.decode('utf-8')
        l= [delete_unicode_name,admin_unicode_name,write_unicode_name,read_unicode_name]
        self.group_required= l
        ##print("the self of dispatcher",self.group_required)

        return super(ProjectDashboardView, self).dispatch(request, *args, **kwargs)
    def get (self,request,pk):
        start_time =datetime.now()
        # ##print("start time ",start_time)
        template_name='dashboard/project_dashboard.html'
        dashboard=ProjectDashboard.objects.get(pk=pk)
        piqu,created = ProjectBillingPrms.objects.get_or_create(project=dashboard.project)
        update = ProjectBillingPrms.objects.filter(project=dashboard.project).update(query_count=piqu.query_count+1)
        permission =identify_user_permission(dashboard.project,request.user)
        dashboard_format = dashboard.dashboard_format
        ##print("length of dashboard items",len(dashboard_format))
        id_elem_hash = self._index_dashboard(dashboard_format)
        type_elem_hash = self._index_dashboard_type(dashboard_format)

        current_site = get_current_site(request)
        site_name = current_site.name
        domain = current_site.domain
        if domain.startswith('127.0.'):
            domain = 'https://'+domain
        else:
            domain = 'https://'+domain

        if dashboard.end_point:
            plot_graphs = []
            query_results = {}
            project_meta = ProjectMetaData.objects.get(project=dashboard.project)
            if project_meta.date_column_name:
                date_field = project_meta.date_column_name
            else:
                date_field = None
            # vl.bari("optimizing raw data:", 's')
            result_df = optimize.optimize_data(dashboard.project_id,date_field)
            # vl.bari("optimizing raw data:", 'e')
            metadata = ProjectMetaData.objects.get(project=dashboard.project)
            for end_point in dashboard.end_point.all():
                if not end_point.sub_df:
                    pv = QueryExcecute(end_point.query)
                    js_df = pv
                    if metadata.date_column_name:
                        js_df[metadata.date_column_name] =js_df[metadata.date_column_name].astype('str')


                    result_json = js_df.to_json(orient='index')
                    # vl.bari("unpivot of result df:"+str(end_point), 'e')

                    # vl.bari("saving sub_df:"+str(end_point), 's')
                    update = ProjectEndPoint.objects.filter(pk=end_point.pk).update(sub_df=result_json)
                    # vl.bari("saving sub_df:"+str(end_point), 'e')

                else:
                    # vl.bari("Loading sub_df:"+str(end_point), 's')
                    json_st = json.loads(end_point.sub_df)
                    # vl.bari('Before Dataframe')
                    json_df = pd.DataFrame(json_st) #TODO 'Taking time - Have to work'
                    # vl.bari('Before transpose')
                    pv = json_df.transpose()
                    df_columns     = pv.columns.tolist()
                    for key, value in metadata.meta_data.items():
                        if key in df_columns:
                            ##print("key",key)
                            if value['dtype'] == 'int':
                                pv[key] =pd.to_numeric(pv[key])
                                if key in df_columns:
                                    pv[key] = pd.to_numeric(pv[key])
                            elif value['dtype'] == 'float':
                                ##print("final key",key,pv[key],pv[key].dtypes)
                                pv[key] = pd.to_numeric(pv[key])
                                if key in df_columns:
                                    pv[key] = pd.to_numeric(pv[key])
                            elif value['dtype'] == 'object':
                                pv[key] = pv[key].astype(str)
                                if key in df_columns:
                                    pv[key] = pv[key].astype(str)
                            elif value['dtype'] == 'bool':
                                pv[key] = pv[key].astype(bool)
                                if key in df_columns:
                                    pv[key] = pv[key].astype(bool)
                            elif value['dtype'] == 'DateTime':
                                pv[key] =pd.to_datetime(pv[key])
                                ##print("the data key",key)
                                if key in df_columns:
                                    pv[key] = pd.to_datetime(pv[key])
                    # vl.bari("Loading sub_df:"+str(end_point), 'e')
                string_columns = pv.select_dtypes(include =['object','bool'])
                df_columns     = pv.columns.tolist()
                plot_df  = pv
                if metadata.date_column_name in df_columns and  metadata.date_column_name:
                    plot_df[metadata.date_column_name] =plot_df[metadata.date_column_name].astype('str')


                plot_start_time = datetime.now()

                # vl.bari("Rendering Plot:"+str(end_point), 's')
                if end_point.plot and end_point.plot.plot_type:
                    end_point_obj = EndPointPlot(plot_df,end_point.pk)
                    div = end_point_obj.plot(end_point.plot)

                else:
                    div = True
                    # fig = px.scatter_matrix(plot_df)
                    # div = opy.plot(fig, auto_open=False,output_type='div')
                    
                # vl.bari("Rendering Plot:"+str(end_point), 'e') # TODO 'Taking time have to work '

                # vl.bari("Updating dashboard object:"+str(end_point), 's')
                key = id_elem_hash[str(end_point.id)]
                value  = dashboard_format[key]
                # print("the object",dashboard_format)
                if value['id'] == str(end_point.id):
                    value['div']= div
                    value['id'] = end_point.id
                    value['end_point']=end_point

                    if end_point.algorithm:
                        features_text = end_point.algorithm.feature
                        features_text = features_text.replace('[', '')
                        features_text = features_text.replace(']', '')
                        features      = features_text.split(',')
                        features_ml_display = features_text.split(',')
                        ##print("features",features)

                        test_l =[]
                        features_cat_dict = {}


                        for column in features:
                            features_text = end_point.algorithm.feature
                            features_text = features_text.replace('[', '')
                            features_text = features_text.replace(']', '')
                            features      = features_text.split(',')
                            features_ml_display = features_text.split(',')
                            ##print("features",features)

                            test_l =[]
                            features_cat_dict = {}
                            ml_df = pd.DataFrame()
                            for column in features:
                                ml_df[column] = pv[column]

                            ml_string_columns = ml_df.select_dtypes(include =['object','bool'])
                            ##print("the ml string columns ",ml_string_columns)




                            ##print("after ml df ",ml_df)
                            for column in ml_string_columns:
                                if ml_df[column].dtypes  == np.bool:
                                    ##print("the data value",df[column],column)

                                    column_name = column +'_cat'
                                    d = {}

                                    new_df = pd.DataFrame()
                                    new_df[column] = pd.unique(pv[column])

                                    column_name = column+'_cat'
                                    new_df[column] = new_df[column].astype('category')
                                    new_df[column_name] = new_df[column].cat.codes
                                    c_series = new_df[column]
                                    c_cat_series = new_df[column_name]
                                    c_list = c_series.tolist()
                                    c_cat_list = c_cat_series.tolist()
                                    ##print("new_df",new_df)

                                    for i in range(0,len(c_list)):
                                        d[c_list[i]]=c_cat_list[i]
                                    features_cat_dict[column]=d
                                    ##print("features",features_cat_dict)
                                    features.remove(column)
                                    ##print("features",features)



                                else:
                                    try:

                                        ml_df[column] = ml_df[column].astype(float)
                                        ##print("in float type column is",column,ml_df[column])
                                    except:

                                        d = {}

                                        new_df = pd.DataFrame()
                                        new_df[column] = pd.unique(pv[column])

                                        column_name = column+'_cat'
                                        new_df[column] = new_df[column].astype('category')
                                        new_df[column_name] = new_df[column].cat.codes
                                        c_series = new_df[column]
                                        c_cat_series = new_df[column_name]
                                        c_list = c_series.tolist()
                                        c_cat_list = c_cat_series.tolist()
                                        ##print("new_df",new_df)

                                        for i in range(0,len(c_list)):
                                            d[c_list[i]]=c_cat_list[i]
                                        features_cat_dict[column]=d
                                        ##print("features",features_cat_dict)
                                        features.remove(column)
                                        ##print("features",features)




                        target   = end_point.algorithm.y_factor
                        model_id = end_point.algorithm.model_id
                        if end_point.algorithm.type_of_prediction == 'Linear':
                            accuracy = ast.literal_eval(end_point.algorithm.accuracy)
                            MAE = accuracy['MAE']
                            MSE = accuracy['MSE']
                            RMSE = accuracy['RMSE']
                            accuracy_list = {'MAE':MAE,'MSE':MSE,'RMSE':RMSE}
                        else:
                            accuracy_list={'accuracy':end_point.algorithm.accuracy}
                        value['features']=features
                        value['features_ml_display']=features_ml_display
                        value['features_cat_dict'] = features_cat_dict
                        value['target']= target
                        value['accuracy']= accuracy_list
                        value['model_id'] = model_id

                    if end_point.plot:
                        value['legend'] = end_point.plot.legend
                    else:
                        value['legend'] = False
                    dashboard_format[key] = value

                # print("the finalobje is ",dashboard_format)
                # vl.bari("Updating dashboard object:"+str(end_point), 'e')
                # vl.bari("Before df table content results:"+str(end_point), 's')

                # vl.bari("Before df table content results:"+str(end_point), 'e')

                # vl.turn_on_full_debug()
                # vl.fullbari("multiple array", 1, 2, 3, "mixed datatype messages for", end_point, "for demo")
            # vl.turn_off_full_debug()

            user = User.objects.get(pk=request.user.pk)
            customer = Customer.objects.get(user=user)
            dashboard_format = dashboard_object_update(dashboard_format,type_elem_hash)
            ##print("dashboard format",dashboard_format)
            data ={ 'dashboard_format':dashboard_format}
            today = datetime.now().date()
            context={'query_results':query_results,'domain':domain,'today':today,'dashboard_format':dashboard_format,'dashboard':dashboard,'customer':customer}
            end_time =datetime.now()
            ##print("compare time ",start_time,end_time)
            return render(request,template_name,context)
    def post(self,request,pk):
        template_name='dashboard/project_dashboard.html'
        dashboard=ProjectDashboard.objects.get(pk=pk)
        project_query = DashboardQuery.objects.get(dashboard=dashboard)
        if project_query.start_date:

            start_date = project_query.start_date
        else:
            start_date = None
        if project_query.end_date:

            end_date   = project_query.end_date
        else:
            end_date = None
        if project_query.expected_range:

            frequency = project_query.expected_range
        else:
            frequency=None
        if project_query.group_query:
            grouping_colums = list(project_query.group_query.split(","))
        else:
            grouping_colums = None
        if project_query.aggregation_value:
            value_columns = list(project_query.aggregation_value.split(","))
            # ##print("the splited value columns are",value_columns)
        else:
            value_columns = None



        if project_query.aggregation_query:
            aggregation = ast.literal_eval(project_query.aggregation_query)
        else:
            aggregation = None

        project_meta = ProjectMetaData.objects.get(project=project_query.project)
        if project_meta.date_column_name:
            date_field = project_meta.date_column_name
        else:
            date_field = None


        if project_query.where_query:
            res_df = query.subset(project_query.project.pk,frequency,1,start_date=start_date,end_date=end_date,grouping_columns=grouping_colums,where=project_query.where_query,aggregation=aggregation,date_column=date_field)
        else:
            res_df = query.subset(project_query.project.pk,frequency,1,start_date=start_date,end_date=end_date,grouping_columns=grouping_colums,aggregation=aggregation,date_column=date_field)


        # ##print("the columns of pivot table are ",res_df.columns.tolist())
        if project_query.group_query:
            df = res_df.stack().reset_index()
        else:
            result =res_df.transpose()
            df = res_df.reset_index()
        res_df__table_content = df.to_html(classes="table table-striped tableFixHead",border="0")
        df_columns     = df.columns.tolist()
        for column in df_columns:
            try:
                df[column] = pd.to_numeric(df[column])
            except:
                pass

        # t_df = res_df.T
        # ##print("the visulization columns",df)
        string_columns = df.select_dtypes(include ='object')
        df_columns     = df.columns.tolist()
        try:

            request.POST['scatter']
            # ##print("scatter")
            try :

                    try:
                        request.POST['plot_type_2d']
                        # ##print("2d")
                        x = request.POST['scatter_2d_x']
                        y = request.POST['scatter_2d_y']
                        color = request.POST.get('scatter_2d_color',None)
                        ##print("befour plot")
                        div = plots.scatter_plot(df,x,y,color)
                        ##print("after plot")
                    except:
                        pass


                    try:
                        request.POST['plot_type_3d']
                        x = request.POST['scatter_3d_x']
                        y = request.POST['scatter_3d_y']
                        z = request.POST['scatter_3d_z']
                        color = request.POST.get('scatter_3d_color',None)
                        if color:
                            div = plots.scatter_plot_3d(df,x,y,z,color)
                        else:
                            div = plots.scatter_plot_3d(df,x,y,z)
                    except:
                        pass

            except:
                pass


        except:
            pass
        try:

            request.POST['bar']
            x = request.POST['bar_x']
            y = request.POST['bar_y']
            color = request.POST.get('bar_color',None)
            div = plots.bar_plot(df,x,y,color)
        except:
            pass
        try:

            try:
                request.POST['line_plot_type_2d']
                x = request.POST['line_2d_x']
                y = request.POST['line_2d_y']
                color = request.POST.get('line_2d_color',None)
                div = plots.line_plot(df,x,y,color)
            except:
                pass
            try:
                request.POST['line_plot_type_3d']
                x = request.POST['line_3d_x']
                y = request.POST['line_3d_y']
                z = request.POST['line_3d_z']
                color = request.POST.get('line_3d_color',None)
                div = plots.line_plot_3d(df,x,y,z,color)
            except:
                pass
        except:
            pass

        try:

            request.POST['histogram']
            # ##print("histogram")
            x = request.POST['histogram_x']
            y = request.POST['histogram_y']
            color = request.POST.get('histogram_color',None)
            div = plots.histogram_plot(df,x,y,color)
        except:
            pass
        context={'dashboard':dashboard,'query':res_df__table_content,'graph':div,'project_query':project_query,'df_columns':df_columns,'string_columns':string_columns}
        return render(request,template_name,context)
    def _index_dashboard(self,dashboard_format):
        indexing ={}
        for key, value in dashboard_format.items():
            indexing[str(value['id'])]=key
        return indexing
    def _index_dashboard_type(self,dashboard_format):

        elem_list =[]

        for key, value in dashboard_format.items():
            if value['type'] == 'row_constructor':
                elem_list.append(key)

        return elem_list




'''this class is to upload 300 random files into project'''
class TestView(View):
    def get(self,request,pk):
        return render(request,'test.html')

    def post(self,request,pk):

        folder_a =os.listdir('folder_a')
        folder_b =os.listdir('folder_b')


        for (file1, file2 ) in zip(folder_a, folder_b):

            file1_path = 'folder_a/'+file1
            file2_path = 'folder_b/'+file2

            file1_df = pd.read_csv(file1_path,encoding="ISO-8859-1")
            file2_df = pd.read_csv(file2_path,encoding="ISO-8859-1")
            res_df =reduce(lambda left,right: pd.merge(left,right,on='DateTime', how='outer'), [file1_df,file2_df])
            ##print(res_df.columns.to_list())
            res_json = res_df.to_json(orient='index')

            project = Project.objects.get(pk=267)

            projectjson, created = ProjectJsonStorage.objects.get_or_create(project=project, js = res_json)
            ##print(projectjson.pk)




class DataSearch(View):
    def post(self,request,pk):
        start_date = '2008-03-18 08:02:53.716000'
        end_date = '2019-8-6 16:2:53.716000'
        project = Project.objects.get(pk=pk)
        json_fields = ProjectJsonStorage.objects.filter(project=project)



        dfs = []
        for i in json_fields:
            json_df = pd.DataFrame(eval(i.js))
            transposed_df = json_df.transpose()
            columns = transposed_df.columns.to_list()
            dfs.append(transposed_df)
        ##print(len(dfs))
        ##print("columns",columns)
        res_df = pd.concat(dfs)
        ##print(res_df)
        res_df['DateTime'] = pd.to_datetime(res_df['DateTime'])
        mask = (res_df['DateTime'] > start_date) & (res_df['DateTime'] <= end_date)
        res_df = res_df.loc[mask]
        ##print(res_df)




class DeleteProjectView(GroupRequiredMixin,LoginRequiredMixin,TemplateView):
    login_url = '/customer/login/'
    redirect_field_name = 'redirect_to'
    template_name='dashboard/index.html'
    def dispatch(self, request, *args, **kwargs):
        pk = str(kwargs['pk'])
        self.login_url = '/customer/login/'
        self.redirect_field_name = 'redirect_to'
        self.template_name='dashboard/index.html'
        admin_name = pk+"_Admin"
        ##print(type(admin_name), admin_name)
        admin_encode_name = admin_name.encode()
        admin_unicode_name = admin_encode_name.decode('utf-8')
        read_name = pk+"_Read"
        ##print(type(read_name), read_name)
        read_encode_name = read_name.encode()
        read_unicode_name = read_encode_name.decode('utf-8')
        write_name = pk+"_Write"
        ##print(type(write_name), write_name)
        write_encode_name = write_name.encode()
        write_unicode_name = write_encode_name.decode('utf-8')
        delete_name = pk+"_Delete"
        ##print(type(write_name), write_name)
        delete_encode_name = delete_name.encode()
        delete_unicode_name = delete_encode_name.decode('utf-8')
        self.group_required=admin_unicode_name
        ##print("the self of dispatcher",self.group_required)

        return super(DeleteProjectView, self).dispatch(request, *args, **kwargs)

    def get(self,request,pk):
        seo=SiteSeo.objects.get(choices='Delete Project')
        template_name='dashboard/delete_project.html'
        project=Project.objects.get(pk=pk)
        context= {
            'project':project,
            'seo':seo
        }
        return render(request,template_name,context)
    def post(self,request,pk):
        template_name='dashboard/delete_project.html'
        project =Project.objects.get(pk=pk)
        seo=SiteSeo.objects.get(choices='Delete Project')
        time=datetime.now()
        if 'yes' in request.POST:
            title=request.POST["project_title"]
            print("the project title and ",title,project.name )
            if project.name == title:
                if ProjectInvoice.objects.filter(Q(monthly_cost__project=project ) & Q(status='Unpaid')).exists():
                    context={
                        'msg':"Unpaid invoice and delete : Kindly pay the pending invoices before deleting the project",
                        "project":project,
                        'seo':seo
                    }
                    return render(request,template_name,context)
                elif ProjectInvoice.objects.filter(Q(monthly_cost__project=project )).exists():
                    monthly_cost = ProjectBillingMonthCost.objects.filter(project=project).order_by('-created')[0]

                    monthly_cost_delta = monthly_cost.created+timedelta(days=3)
                    print("the time delta",monthly_cost_delta,utc.localize(datetime.now()))
                    if utc.localize(datetime.now()) > monthly_cost_delta :
                        context={
                        'msg':"Billed and crossed 3 days:  Oops! your billing cycle has started. Kindly contact customer service",
                        "project":project,
                        'seo':seo
                            }
                        return render(request,template_name,context)
                    else:
                        project =Project.objects.get(pk=pk)
                        title = project.name
                        title = title+'_backup'
                        project_update= Project.objects.filter(pk=pk).update(name=title,delete_datetime=time)


                else:
                    project =Project.objects.get(pk=pk)
                    title = project.name
                    title = title+'_backup'
                    project_update= Project.objects.filter(pk=pk).update(name=title,delete_datetime=time)
                    ##print("project_update",project_update)
                    # action.send(request.user,verb="Deleted the" + str(project))
            else:
                context={
                   'msg':"Project Title is mismatched, So cannot delete your project",
                   "project":project,
                   'seo':seo
                }
                return render(request,template_name,context)





        elif 'no'in request.POST:
            pass

        return redirect('/dashboard/')

'''ajax call view to check whether the email id is admin_user id '''
def check_email(request,pk):
    ##print("inside check email function")
    if request.method == 'POST':
        email=request.POST['email_id']
        project_pk=request.POST['project_pk']
        project=Project.objects.get(pk=pk)
        ##print(project)
        if email == request.user.username:
            data={
            'msg':"error"
            }
        else:
            ##print("inside else")
            user = User.objects.get(username = email)
            ##print(user)
            try:
                project_user = ProjectUser.objects.filter(project = project)
                ##print("found project_user",project_user)
                if project_user :
                    for p in project_user:
                        ##print(p.project_user.username)
                        ##print(user.username)
                        if p.project_user.username == user.username:
                            data={
                                'msg':"project_user_error"
                                }
                        else:
                            data={
                            'msg':"success"
                            }

                else:
                    data = {
                    'msg':"success"
                    }

            except:
                ##print("inside except")
                data = {
                'msg':"success"
                }

        return JsonResponse(data,safe=False)
    else:
        return JsonResponse("Failure",safe=False)

'''Function to delete the project user added to the project'''
class UpdateProjectUser(GroupRequiredMixin,LoginRequiredMixin,View):

    def dispatch(self, request, *args, **kwargs):
        pk = str(kwargs['pk'])
        self.login_url = '/customer/login/'
        self.redirect_field_name = 'redirect_to'
        self.template_name='dashboard/index.html'
        admin_name = pk+"_Admin"
        ##print(type(admin_name), admin_name)
        admin_encode_name = admin_name.encode()
        admin_unicode_name = admin_encode_name.decode('utf-8')


        self.group_required = admin_unicode_name
        ##print("the self of dispatcher",self.group_required)

        return super(UpdateProjectUser, self).dispatch(request, *args, **kwargs)


    def post(self,request,pk):
        if request.method == 'POST':
            user=int(request.POST['user'])
            ##print(user)
            permission=request.POST['permission']
            user=User.objects.get(pk=user)
            project=Project.objects.get(pk=pk)
            project_user=ProjectUser.objects.filter(project=project)
            user_group = User.objects.get(pk=user.pk)

            for g in user_group.groups.all():
                s_group = g.name.split('_')
                if s_group[0] == str(project.pk):
                    ##print("group to delete",g)
                    user.groups.remove(g)

            try:
                user_group = User.objects.filter(Q(pk=user.pk) & Q(groups__name__startswith=str(project.pk)+'_') )[0]

            except:
                pass
            if permission=="Read":
                permission=Group.objects.get(name=str(project.pk)+'_Read')
            elif permission=="Read Write":
                permission=Group.objects.get(name=str(project.pk)+'_Write')
            elif permission=="Read Write Delete":
                permission=Group.objects.get(name=str(project.pk)+'_Delete')
            elif permission=="Admin":
                permission=Group.objects.get(name=str(project.pk)+"_Admin")
            user=User.objects.get(pk=user.pk)
            ##print("the choosen permission is",permission)

            user.groups.add(permission)
            data={
                'msg':"success",

                }

            return JsonResponse(data,safe=False)
'''Function to delete the user'''

class ProjectUserDelete(GroupRequiredMixin,LoginRequiredMixin,View):

    def dispatch(self, request, *args, **kwargs):
        pk = str(kwargs['pk'])
        self.login_url = '/customer/login/'
        self.redirect_field_name = 'redirect_to'
        self.template_name='dashboard/index.html'
        admin_name = pk+"_Admin"
        ##print(type(admin_name), admin_name)
        admin_encode_name = admin_name.encode()
        admin_unicode_name = admin_encode_name.decode('utf-8')


        self.group_required = admin_unicode_name
        ##print("the self of dispatcher",self.group_required)

        return super(ProjectUserDelete, self).dispatch(request, *args, **kwargs)
    def post(self,request,pk):
        ##print("inside delete user")
        if request.method == 'POST':
            user=int(request.POST['user'])
            ##print('user',user)
            user=User.objects.get(pk=user)
            project=Project.objects.get(pk=pk)
            project_user=ProjectUser.objects.filter(project=project)
            project_user_delete=ProjectUser.objects.filter(project_user=user).delete()

            user_group = User.objects.filter(Q(pk=user.pk) & Q(groups__name__startswith=str(project.pk)+'_') )[0]

            for g in user_group.groups.all():
                ##print("group",g)
                user.groups.remove(g)
            try:

                user_group = User.objects.filter(Q(pk=user.pk) & Q(groups__name__startswith=str(project.pk)+'_') )[0]

            except:
                pass

            data={
            'msg':"success"
                }
            return JsonResponse(data,safe=False)


'''class to display deleted projects to restore'''
class RestoreProjects(LoginRequiredMixin,TemplateView):
    login_url = '/customer/login/'
    redirect_field_name = 'redirect_to'
    template_name='dashboard/index.html'
    def get(self,request):
        seo=SiteSeo.objects.get(choices='Restore Project')
        template_name='dashboard/restore-projects.html'
        projects=Project.objects.filter(admin_user=request.user)
        ##print(projects)
        customer = Customer.objects.get(user=request.user)
        context={
            'projects':projects,
            'customer':customer,
            'seo':seo
        }
        return render(request,template_name,context)
    def post(self,request):
        template_name='dashboard/restore-projects.html'
        seo=SiteSeo.objects.get(choices='Restore Project')
        if "restore" in request.POST:
            return redirect('/restore-project/')



def restore_project(request,pk):
    template_name='dashboard/restore_single_project.html'
    if "yes" in request.POST:
        project = Project.objects.get(pk=pk)
        title = project.name
        new_title  = title
        sub_string = '_backup'
        if (title.find(sub_string) == -1):
            project=Project.objects.filter(pk=pk).update(delete_datetime=None)

            pass
        else:
            new_title = title.split('_')
            project=Project.objects.filter(pk=pk).update(name=new_title[0],delete_datetime=None)

        ##print('project',project)
        return redirect('/dashboard/')
    else:
        pass
    return render(request,template_name,context=None)



class ProjectQueryView(GroupRequiredMixin,LoginRequiredMixin,View):

    def dispatch(self, request, *args, **kwargs):
        pk = str(kwargs['pk'])
        self.login_url = '/customer/login/'
        self.redirect_field_name = 'redirect_to'
        self.template_name='dashboard/index.html'
        admin_name = pk+"_Admin"
        ##print(type(admin_name), admin_name)
        admin_encode_name = admin_name.encode()
        admin_unicode_name = admin_encode_name.decode('utf-8')
        write_name = pk+"_Write"
        ##print(type(write_name), write_name)
        write_encode_name = write_name.encode()
        write_unicode_name = write_encode_name.decode('utf-8')

        delete_name = pk+"_Delete"
        ##print(type(delete_name), delete_name)
        delete_encode_name = delete_name.encode()
        delete_unicode_name = delete_encode_name.decode('utf-8')
        l =[delete_unicode_name,write_unicode_name,admin_unicode_name]
        self.group_required= l
        ##print("the self of dispatcher",self.group_required)

        return super(ProjectQueryView, self).dispatch(request, *args, **kwargs)

    def post(self,request,pk):
        project = Project.objects.get(pk=pk)
        form = ProjectEndPointForm()
        if Project.objects.filter(pk=project.pk,admin_user=request.user).exists():
            permission="Admin"
        elif ProjectUser.objects.filter(project=project,project_user=request.user).exists():
            user_group = User.objects.get(pk=request.user.pk)

            for g in user_group.groups.all():
                if g.name == str(project.pk)+"_Read":
                    permission="Read"
                elif g.name == str(project.pk)+"_Write":
                    permission="Write"
                elif g.name == str(project.pk)+"_Delete":
                    permission="Delete"
                elif g.name == str(project.pk)+"_Admin":
                    permission="Admin"

        else:
            permission = None
        where_query = request.POST.get('where_query',None)
        grouping_colums = request.POST.get('grouping_colums',None)
        grouping_colum = request.POST.get('grouping_colums',None)
        value_columns = request.POST.get('value_columns',None)
        value_column = request.POST.get('value_columns',None)
        frequency = request.POST.get('frequency',None)
        aggregation_query  = request.POST.get('aggregation_query',None)
        aggregation_queries  = request.POST.get('aggregation_query',None)
        start_date = request.POST.get('start_date',None)
        started_date = request.POST.get('start_date',None)
        end_date = request.POST.get('end_date',None)
        ended_date = request.POST.get('end_date',None)
        today = datetime.now()
        ##print("the post is ",request.POST)
        from_date_select = request.POST.get('fromdate_select',None)
        to_date_select = request.POST.get('todate_select',None)

        if start_date and from_date_select:
            try:
                date = int(start_date)
                if from_date_select == 'day':
                    start_date =today -timedelta(days=int(date))
                elif from_date_select == 'week':
                    start_date =today -timedelta(days=7*int(date))
                elif from_date_select == 'month':
                    start_date =today -timedelta(int(date)*365/12)
                elif from_date_select == 'year':
                    start_date =today -timedelta(int(date)*365)
                    ##print("year conversion",start_date)
                date_value= True
            except:
                date_value = 'Error'
        elif start_date:
            try:
                start_date = pd.to_datetime(start_date)
                date_value= True
            except:
                date_value = 'Error'
        else:
            date_value= True


        if end_date and to_date_select:
            try:
                date = int(end_date)


                if to_date_select == 'today':
                    end_date =today
                elif to_date_select == 'day':
                    end_date =today -timedelta(days=int(date))
                elif to_date_select == 'week':
                    end_date =today -timedelta(days=int(7*date))
                elif to_date_select == 'month':
                    end_date =today -timedelta(int(date)*365/12)
                elif to_date_select == 'year':
                    end_date =today -timedelta(int(date)*365)
                    date_value= True
                elif to_date_select == 'today':
                    ##print("frequency",to_date_select)
                    end_date =today
                    date_value= True
            except:
                date_value = 'Error'
        elif end_date:
            try:
                end_date = pd.to_datetime(end_date)
                date_value= True
            except:
                date_value = 'Error'
        elif to_date_select:
            ##print("only select")
            try:
                if to_date_select == 'today':
                    end_date = datetime.now()

            except:
                date_value = 'Error'

        else:
            date_value= True
        if date_value == 'Error':
            seo=SiteSeo.objects.get(choices='Project Details')
            template_name='dashboard/project_details.html'
            project=Project.objects.get(pk=pk)
            if Project.objects.filter(pk=project.pk,admin_user=request.user).exists():
                permission="Admin"
            elif ProjectUser.objects.filter(project=project,project_user=request.user).exists():
                user_group = User.objects.get(pk=request.user.pk)

                for g in user_group.groups.all():
                    if g.name == str(project.pk)+"_Read":
                        permission="Read"
                    elif g.name == str(project.pk)+"_Write":
                        permission="Write"
                    elif g.name == str(project.pk)+"_Delete":
                        permission="Delete"
                    elif g.name == str(project.pk)+"_Admin":
                        permission="Admin"

            else:
                permission=None
            msg="From  date or To date is incorrect "
            ##print(project)
            ##print("pk",pk)
            pk=str(project.pk)
            file_form=FileUploadForm()
            current_site = get_current_site(request)
            site_name = current_site.name
            domain = current_site.domain
            if domain.startswith('127.0.'):
                domain = 'https://'+domain
            else:
                domain = 'https://'+domain

            ##print('domain',domain)
            dashboard_form = ProjectDashboardForm(initial={'project':project.pk})
            dashboard_form.fields['user'].queryset = ProjectUser.objects.filter(project=project)
            dashboard_form.fields['dashboard'].queryset = ProjectDashboard.objects.filter(project=project)

            if ProjectIndex.objects.filter(project=project).exists():
                start_indexer = ProjectIndex.objects.filter(project=project).order_by('id')[0]
                end_indexer = ProjectIndex.objects.filter(project=project).order_by('-id')[0]
                start_year = start_indexer.start_date.year
                end_year = end_indexer.end_date.year
                default_start_date = start_indexer.start_date
                default_end_date = end_indexer.end_date

            else:

                start_year =  None
                end_year = None
                default_start_date = None
                default_end_date = None
            project_metadata = ProjectMetaData.objects.get(project=project)
            if project_metadata.date_column_name:
                time_series_project = True
            else:
                time_series_project = None
            project_metadata = ProjectMetaData.objects.get(project=project)
            if project_metadata.date_column_name:
                time_series_project = True
            else:
                time_series_project = None
            if request.user.username == 'administrator':
                    customer=Customer.objects.get(user=request.user)
                    try:
                        integrations = CustomerAPIDetails.objects.filter(project=project)
                    except:
                        pass
                        ##print('pass')

                    return render(request,template_name,context)
            else:
                customer=Customer.objects.get(user=request.user)
                action.send(customer,verb="Viewed" + str(project.name))
                project=Project.objects.get(pk=pk)
                if ProjectQuery.objects.filter(project=project).exists():
                    project_query = ProjectQuery.objects.filter(project=project).order_by('-created')
                else:
                    project_query = None
                if ProjectJsonStorage.objects.filter(project=project).exists():
                    project_json = ProjectJsonStorage.objects.filter(project=project)

                    project_jsons = ProjectJsonStorageMetadata.objects.filter(Q(project_json__project=project))
                    json_meta_obj = ProjectJsonAlter(project_jsons)
                    data = json_meta_obj.claculate_rows_columns()
                    df_rows = data['rows']
                    df_columns_count = data['columns']
                    df_head = json_meta_obj.dataframe_head_tail()
                    df_columns = df_head.columns.tolist()
                    metadata = ProjectMetaData.objects.get(project=project)
                    columns_dtypes = {}
                    for key, value in metadata.meta_data.items():
                        if key in df_columns:
                            ##print("key",key)
                            if value['dtype'] == 'int':
                                df_head[key] =pd.to_numeric(df_head[key])
                                if key in df_columns:
                                    df_head[key] = pd.to_numeric(df_head[key])
                                columns_dtypes[key]= 'number'
                            elif value['dtype'] == 'float':
                                ##print("final key",key,df_head[key],df_head[key].dtypes)
                                df_head[key] = pd.to_numeric(df_head[key])
                                if key in df_columns:
                                    df_head[key] = pd.to_numeric(df_head[key])
                                columns_dtypes[key]= 'number'
                            elif value['dtype'] == 'object':
                                df_head[key] = df_head[key].astype(str)
                                if key in df_columns:
                                    df_head[key] = df_head[key].astype(str)
                                columns_dtypes[key]= 'string'
                            elif value['dtype'] == 'bool':
                                df_head[key] = df_head[key].astype(bool)
                                if key in df_columns:
                                    df_head[key] = df_head[key].astype(bool)
                                columns_dtypes[key]= 'bool'
                            elif value['dtype'] == 'DateTime':
                                df_head[key] =pd.to_datetime(df_head[key])
                                ##print("the data key",key)
                                if key in df_columns:
                                    df_head[key] = pd.to_datetime(df_head[key])
                                columns_dtypes[key]= 'DateTime'
                    number_columns = df_head.select_dtypes(include=['number'])
                    df_columns    = df_head.select_dtypes(include=['number','bool','object'])
                    all_df_columns = df_head.columns.tolist()
                    feature_columns  = df_head.select_dtypes(include =['object','bool','number'])
                    ##print("the feature_columns",feature_columns)
                    if metadat.date_column_name in all_df_columns and  metadata.date_column_name:
                        df_head[metadata.date_column_name] = df_head[metadata.date_column_name].astype('str')

                    res_df__table_content = df_head.to_html(classes="table table-striped tableFixHead",border="0")
                else:
                    columns_dtypes = {}
                    res_df__table_content = None
                    df_rows = 0
                    df_columns=[]
                    number_columns = []
                    df_columns_count = 0
                    feature_columns=[]
                try:

                    integrations = CustomerAPIDetails.objects.filter(project=project)
                    context={
                        'integrations':integrations,
                        'project_query':project_query,
                        'res_df__table_content':res_df__table_content,
                        'feature_columns':feature_columns,
                        'dashboard_form':dashboard_form,
                        'permission':permission,
                        'df_rows':df_rows,
                        'df_columns':df_columns,
                        'columns_dtypes':columns_dtypes,
                        'number_columns':number_columns,
                        'time_series_project':time_series_project,
                        'df_columns_count':df_columns_count,
                        'where_query':where_query,
                        'group_query':grouping_colum,
                        'aggregation_value':value_column,
                        'aggregation_query':aggregation_queries,
                        'expected_range':frequency,
                        'start_date' : started_date,
                        'end_date':ended_date,
                        'start_year':start_year,
                        'end_year':end_year,
                        'default_start_date':default_start_date,
                        'default_end_date':default_end_date,
                        'msg':msg,
                        'domain':domain,
                        'form':form
                    }
                except:
                    pass
                users = User.objects.filter(pk=request.user.pk)

                if ProjectDashboard.objects.filter(Q(project=project) & Q(dashboard_admin_user__pk =request.user.pk)).exists():
                    ##print("project admin")
                    dashboard=ProjectDashboard.objects.filter(Q(project=project) & Q(dashboard_admin_user__pk =request.user.pk)  ).order_by('name')
                    dashboard_count=ProjectDashboard.objects.filter(Q(project=project) & Q(dashboard_admin_user__pk=request.user.pk)).count()
                    ##print("dashboard",dashboard)
                    ##print("dashboard count",dashboard_count)

                    context = {
                        'project':project,
                        'file_form':file_form,


                        'customer':customer,
                        'dashboard':dashboard,
                        'feature_columns':feature_columns,
                        'dashboard_count':dashboard_count,
                        'seo':seo,
                        'integrations':integrations,
                        'project_query':project_query,
                        'res_df__table_content':res_df__table_content,
                        'dashboard_form':dashboard_form,
                        'df_rows':df_rows,
                        'df_columns':df_columns,
                        'columns_dtypes':columns_dtypes,
                        'number_columns':number_columns,
                        'time_series_project':time_series_project,
                        'df_columns_count':df_columns_count,
                        'where_query':where_query,
                        'group_query':grouping_colum,
                        'aggregation_value':value_column,
                        'aggregation_query':aggregation_queries,
                        'expected_range':frequency,
                        'start_date' : started_date,
                        'permission':permission,
                        'end_date':ended_date,
                        'start_year':start_year,
                        'end_year':end_year,
                        'default_start_date':default_start_date,
                        'default_end_date':default_end_date,
                        'msg':msg,
                        'domain':domain,
                        'form':form

                        }
                elif ProjectDashboard.objects.filter(Q(project=project) & Q(dashboard_users__in=users )).exists():
                    ##print("project users")
                    dashboard=ProjectDashboard.objects.filter(Q(project=project) & Q(dashboard_users__in=users )).order_by('name')
                    dashboard_count=ProjectDashboard.objects.filter(Q(project=project) & Q(dashboard_users__in=users )).count()
                    ##print("dashboard",dashboard)
                    ##print("dashboard count",dashboard_count)

                    context = {

                        'project':project,
                        'file_form':file_form,

                        'feature_columns':feature_columns,
                        'customer':customer,
                        'dashboard':dashboard,
                        'permission':permission,
                        'dashboard_count':dashboard_count,
                        'seo':seo,
                        'df_columns':df_columns,
                        'columns_dtypes':columns_dtypes,
                        'number_columns':number_columns,
                        'integrations':integrations,
                        'project_query':project_query,
                        'res_df__table_content':res_df__table_content,
                        'dashboard_form':dashboard_form,
                        'df_rows':df_rows,
                        'df_columns_count':df_columns_count,
                        'where_query':where_query,
                        'group_query':grouping_colum,
                        'aggregation_value':value_column,
                        'aggregation_query':aggregation_queries,
                        'expected_range':frequency,
                        'start_date' : started_date,
                        'time_series_project':time_series_project,
                        'end_date':ended_date,
                        'msg':msg,
                        'start_year':start_year,
                        'end_year':end_year,
                        'default_start_date':default_start_date,
                        'default_end_date':default_end_date,
                        'domain':domain,
                        'form':form,

                        }
                else:
                    ##print("no dashboard")
                    context = {

                        'project':project,

                        'file_form':file_form,
                        'permission':permission,
                        'feature_columns':feature_columns,
                        'customer':customer,
                        'seo':seo,
                        'df_columns':df_columns,
                        'columns_dtypes':columns_dtypes,
                        'number_columns':number_columns,
                        'integrations':integrations,
                        'project_query':project_query,
                        'res_df__table_content':res_df__table_content,
                        'dashboard_form':dashboard_form,
                        'df_rows':df_rows,
                        'df_columns_count':df_columns_count,
                        'where_query':where_query,
                        'group_query':grouping_colum,
                        'aggregation_value':value_column,
                        'aggregation_query':aggregation_queries,
                        'expected_range':frequency,
                        'start_date' : started_date,
                        'time_series_project':time_series_project,
                        'end_date':ended_date,
                        'start_year':start_year,
                        'end_year':end_year,
                        'default_start_date':default_start_date,
                        'default_end_date':default_end_date,
                        'msg':msg,
                        'domain':domain,
                        'form':form

                    }
                ##print("the contest is",context)
                return render(request,template_name,context)




        ##print("the start date is ",start_date)
        ##print("the start date is ",end_date)
        if ProjectQuery.objects.filter().exists():

            latest_id = ProjectQuery.objects.latest('id')
            suffix   = "BR-00"
            query_id = suffix+str(latest_id.id)
        else:
            latest_id= 1
            suffix   = "BR-00"
            query_id = suffix+str(latest_id)


        ##print("the query id is",query)


        project_meta = ProjectMetaData.objects.get(project=project)
        if project_meta.date_column_name:
            date_field = project_meta.date_column_name
        else:
            date_field=None

        if grouping_colums:
            grouping_colums = list(grouping_colums.split(","))
            ##print("the grouping columns are",grouping_colums,date_field)
            if date_field in grouping_colums:
                ##print("its in the list")
                if frequency:
                    ##print("frequency presents")
                    data_grouping = None
                else:
                    data_grouping = True
            else:
                data_grouping = True
        else:
            data_grouping = True



        if value_columns:
            value_columns = list(value_columns.split(","))
            # ##print("the splited value columns are",value_columns)



        if aggregation_query:
            try:

                aggregation = ast.literal_eval(aggregation_query)
                data=True
            except:
                data=None
        else:
            aggregation = None
            data=True

        project_meta = ProjectMetaData.objects.get(project=project)
        if project_meta.date_column_name:
            date_field = project_meta.date_column_name
        else:
            date_field=None







        if data and data_grouping:

            if where_query:
                res_df = query.subset(project.pk,frequency,1,start_date=start_date,end_date=end_date,grouping_columns=grouping_colums,where=where_query,aggregation=aggregation,date_column=date_field)
            else:
                res_df = query.subset(project.pk,frequency,1,start_date=start_date,end_date=end_date,grouping_columns=grouping_colums,aggregation=aggregation,date_column=date_field)
        else:

            res_df= 'Error'
            ##print("error should find out")

        try:
            ##print("the dataframe empty",res_df)
            result_empty = res_df.empty

        except:
            ##print("exept")

            seo=SiteSeo.objects.get(choices='Project Details')
            template_name='dashboard/project_details.html'
            project=Project.objects.get(pk=pk)
            if Project.objects.filter(pk=project.pk,admin_user=request.user).exists():
                permission="Admin"
            elif ProjectUser.objects.filter(project=project,project_user=request.user).exists():
                user_group = User.objects.get(pk=request.user.pk)

                for g in user_group.groups.all():
                    if g.name == str(project.pk)+"_Read":
                        permission="Read"
                    elif g.name == str(project.pk)+"_Write":
                        permission="Write"
                    elif g.name == str(project.pk)+"_Delete":
                        permission="Delete"
                    elif g.name == str(project.pk)+"_Admin":
                        permission="Admin"

            else:
                permission=None
            msg="There was an Error in processing your query please make sure syntax and column names correct"
            ##print(project)
            ##print("pk",pk)
            pk=str(project.pk)
            file_form=FileUploadForm()
            current_site = get_current_site(request)
            site_name = current_site.name
            domain = current_site.domain
            if domain.startswith('127.0.'):
                domain = 'https://'+domain
            else:
                domain = 'https://'+domain

            ##print('domain',domain)
            dashboard_form = ProjectDashboardForm(initial={'project':project.pk})
            dashboard_form.fields['user'].queryset = ProjectUser.objects.filter(project=project)
            dashboard_form.fields['dashboard'].queryset = ProjectDashboard.objects.filter(project=project)
            if ProjectIndex.objects.filter(project=project).exists():
                start_indexer = ProjectIndex.objects.filter(project=project).order_by('id')[0]
                end_indexer = ProjectIndex.objects.filter(project=project).order_by('-id')[0]
                start_year = start_indexer.start_date.year
                end_year = end_indexer.end_date.year
                default_start_date = start_indexer.start_date
                default_end_date = end_indexer.end_date

            else:

                start_year =  None
                end_year = None
                default_start_date = None
                default_end_date = None
            project_metadata = ProjectMetaData.objects.get(project=project)
            if project_metadata.date_column_name:
                time_series_project = True
            else:
                time_series_project = None

            project_metadata = ProjectMetaData.objects.get(project=project)
            if project_metadata.date_column_name:
                time_series_project = True
            else:
                time_series_project = None
            if request.user.username == 'administrator':
                    customer=Customer.objects.get(user=request.user)
                    try:
                        integrations = CustomerAPIDetails.objects.filter(project=project)
                    except:
                        pass
                        ##print('pass')

                    return render(request,template_name,context)
            else:
                customer=Customer.objects.get(user=request.user)
                action.send(customer,verb="Viewed" + str(project.name))
                project=Project.objects.get(pk=pk)
                if ProjectQuery.objects.filter(project=project).exists():
                    project_query = ProjectQuery.objects.filter(project=project).order_by('-created')
                else:
                    project_query = None
                if ProjectJsonStorage.objects.filter(project=project).exists():
                    project_json = ProjectJsonStorage.objects.filter(project=project)

                    project_jsons = ProjectJsonStorageMetadata.objects.filter(Q(project_json__project=project))
                    json_meta_obj = ProjectJsonAlter(project_jsons)
                    data = json_meta_obj.claculate_rows_columns()
                    df_rows = data['rows']
                    df_columns_count = data['columns']
                    df_head = json_meta_obj.dataframe_head_tail()
                    df_columns = df_head.columns.tolist()
                    metadata = ProjectMetaData.objects.get(project=project)
                    columns_dtypes = {}
                    for key, value in metadata.meta_data.items():
                        if key in df_columns:
                            ##print("key",key)
                            if value['dtype'] == 'int':
                                df_head[key] =pd.to_numeric(df_head[key])
                                if key in df_columns:
                                    df_head[key] = pd.to_numeric(df_head[key])
                                columns_dtypes[key]= 'number'
                            elif value['dtype'] == 'float':
                                ##print("final key",key,df_head[key],df_head[key].dtypes)
                                df_head[key] = pd.to_numeric(df_head[key])
                                if key in df_columns:
                                    df_head[key] = pd.to_numeric(df_head[key])
                                columns_dtypes[key]= 'number'
                            elif value['dtype'] == 'object':
                                df_head[key] = df_head[key].astype(str)
                                if key in df_columns:
                                    df_head[key] = df_head[key].astype(str)
                                columns_dtypes[key]= 'string'
                            elif value['dtype'] == 'bool':
                                df_head[key] = df_head[key].astype(bool)
                                if key in df_columns:
                                    df_head[key] = df_head[key].astype(bool)
                                columns_dtypes[key]= 'bool'
                            elif value['dtype'] == 'DateTime':
                                df_head[key] =pd.to_datetime(df_head[key])
                                ##print("the data key",key)
                                if key in df_columns:
                                    df_head[key] = pd.to_datetime(df_head[key])
                                columns_dtypes[key]= 'DateTime'
                    number_columns = df_head.select_dtypes(include=['number'])
                    df_columns    = df_head.select_dtypes(include=['number','bool','object'])

                    feature_columns  = df_head.select_dtypes(include =['object','bool','number'])
                    if metadata.date_column_name:
                        df_head[metadata.date_column_name] = df_head[metadata.date_column_name].astype('str')

                    res_df__table_content = df_head.to_html(classes="table table-striped tableFixHead",border="0")
                else:
                    res_df__table_content = None
                    df_rows = 0
                    df_columns = []
                    columns_dtypes= {}
                    number_columns = []
                    df_columns_count = 0
                try:

                    integrations = CustomerAPIDetails.objects.filter(project=project)
                    context={
                        'integrations':integrations,
                        'project_query':project_query,
                        'res_df__table_content':res_df__table_content,
                        'dashboard_form':dashboard_form,
                        'permission':permission,
                        'df_rows':df_rows,
                        'feature_columns':feature_columns,
                        'df_columns':df_columns,
                        'number_columns':number_columns,
                        'columns_dtypes':columns_dtypes,
                        'df_columns_count':df_columns_count,
                        'where_query':where_query,
                        'group_query':grouping_colum,
                        'aggregation_value':value_column,
                        'aggregation_query':aggregation_queries,
                        'expected_range':frequency,
                        'start_date' : started_date,
                        'start_year':start_year,
                        'time_series_project':time_series_project,
                        'end_year':end_year,
                        'default_start_date':default_start_date,
                        'default_end_date':default_end_date,
                        'end_date':ended_date,
                        'msg':msg,
                        'domain':domain,
                        'form':form,
                    }
                except:
                    pass
                users = User.objects.filter(pk=request.user.pk)

                if ProjectDashboard.objects.filter(Q(project=project) & Q(dashboard_admin_user__pk =request.user.pk)).exists():
                    ##print("project admin")
                    dashboard=ProjectDashboard.objects.filter(Q(project=project) & Q(dashboard_admin_user__pk =request.user.pk)  ).order_by('name')
                    dashboard_count=ProjectDashboard.objects.filter(Q(project=project) & Q(dashboard_admin_user__pk=request.user.pk)).count()
                    ##print("dashboard",dashboard)
                    ##print("dashboard count",dashboard_count)

                    context = {
                        'project':project,
                        'file_form':file_form,

                        'feature_columns':feature_columns,
                        'customer':customer,
                        'dashboard':dashboard,

                        'dashboard_count':dashboard_count,
                        'seo':seo,
                        'df_columns':df_columns,
                        'number_columns':number_columns,
                        'columns_dtypes':columns_dtypes,
                        'integrations':integrations,
                        'project_query':project_query,
                        'res_df__table_content':res_df__table_content,
                        'dashboard_form':dashboard_form,
                        'df_rows':df_rows,
                        'df_columns_count':df_columns_count,
                        'where_query':where_query,
                        'group_query':grouping_colum,
                        'aggregation_value':value_column,
                        'aggregation_query':aggregation_queries,
                        'expected_range':frequency,
                        'start_date' : started_date,
                        'permission':permission,
                        'time_series_project':time_series_project,
                        'end_date':ended_date,
                        'start_year':start_year,
                        'end_year':end_year,
                        'default_start_date':default_start_date,
                        'default_end_date':default_end_date,
                        'msg':msg,
                        'domain':domain,
                        'form':form

                        }
                elif ProjectDashboard.objects.filter(Q(project=project) & Q(dashboard_users__in=users )).exists():
                    ##print("project users")
                    dashboard=ProjectDashboard.objects.filter(Q(project=project) & Q(dashboard_users__in=users )).order_by('name')
                    dashboard_count=ProjectDashboard.objects.filter(Q(project=project) & Q(dashboard_users__in=users )).count()
                    ##print("dashboard",dashboard)
                    ##print("dashboard count",dashboard_count)

                    context = {

                        'project':project,
                        'file_form':file_form,

                        'feature_columns':feature_columns,
                        'customer':customer,
                        'dashboard':dashboard,
                        'permission':permission,
                        'dashboard_count':dashboard_count,
                        'seo':seo,
                        'df_columns':df_columns,
                        'number_columns':number_columns,
                        'columns_dtypes':columns_dtypes,
                        'integrations':integrations,
                        'project_query':project_query,
                        'res_df__table_content':res_df__table_content,
                        'dashboard_form':dashboard_form,
                        'df_rows':df_rows,
                        'time_series_project':time_series_project,
                        'df_columns_count':df_columns_count,
                        'where_query':where_query,
                        'group_query':grouping_colum,
                        'aggregation_value':value_column,
                        'aggregation_query':aggregation_queries,
                        'expected_range':frequency,
                        'start_date' : started_date,
                        'end_date':ended_date,
                        'msg':msg,
                        'start_year':start_year,
                        'end_year':end_year,
                        'default_start_date':default_start_date,
                        'default_end_date':default_end_date,
                        'domain':domain,
                        'form':form

                        }
                else:
                    ##print("no dashboard")
                    context = {

                        'project':project,

                        'file_form':file_form,
                        'permission':permission,
                        'feature_columns':feature_columns,
                        'customer':customer,
                        'seo':seo,
                        'df_columns':df_columns,
                        'number_columns':number_columns,
                        'columns_dtypes':columns_dtypes,
                        'integrations':integrations,
                        'project_query':project_query,
                        'res_df__table_content':res_df__table_content,
                        'dashboard_form':dashboard_form,
                        'df_rows':df_rows,
                        'df_columns_count':df_columns_count,
                        'where_query':where_query,
                        'group_query':grouping_colum,
                        'aggregation_value':value_column,
                        'aggregation_query':aggregation_queries,
                        'expected_range':frequency,
                        'start_date' : started_date,
                        'end_date':ended_date,
                        'time_series_project':time_series_project,
                        'msg':msg,
                        'start_year':start_year,
                        'end_year':end_year,
                        'default_start_date':default_start_date,
                        'default_end_date':default_end_date,
                        'domain':domain,
                        'form':form

                    }
                # ##print("the contest is",context)
                return render(request,template_name,context)

        project_meta = ProjectMetaData.objects.get(project=project)
        if project_meta.date_column_name:
            date_field = project_meta.date_column_name
        else:
            date_field=None
        ##print("final df after grouping is ",res_df)
        if date_field:

            if not where_query and not grouping_colums and not aggregation  :

                pv = res_df
                ##print("the onlydatetime",pv)
            elif where_query and not grouping_colums and not aggregation  :
                pv = res_df

            elif where_query  and grouping_colums and not aggregation  :
                ##print("no aggregation with grouping")
                pv = res_df
            elif where_query  and grouping_colums and  aggregation and frequency:
                ##print("no aggregation with grouping")
                pv =  res_df.stack().reset_index()
            elif where_query  and grouping_colums and  aggregation and not frequency:
                ##print("no aggregation with grouping")
                pv =  res_df.reset_index()
            elif not where_query  and not grouping_colums and  not aggregation and  frequency:
                ##print("no aggregation with grouping")
                pv =  res_df
            elif where_query  and not grouping_colums  and  aggregation and frequency:
                ##print("aggregation with grouping")
                pv_df = res_df.transpose()
                pv = pv_df.reset_index()
            elif not grouping_colums  and  aggregation and frequency:
                ##print("aggregation with grouping")
                pv_df = res_df.transpose()
                pv = pv_df.reset_index()

            elif grouping_colums  and  aggregation and frequency:
                ##print("aggregation with grouping")
                pv = res_df.stack().reset_index()
            elif grouping_colums  and  aggregation and not frequency:
                ##print("aggregation with grouping")
                pv = res_df.reset_index()
            elif grouping_colums:
                pv = res_df
            elif where_query:
                pv = res_df

            else:
                ##print("aggregation")
                pv_df = res_df.transpose()
                pv = pv_df.reset_index()
        else:
            if not where_query and not grouping_colums and not aggregation :
                pv = res_df
            elif where_query and not grouping_colums and not aggregation :
                pv = res_df

            elif where_query  and grouping_colums and not aggregation:
                pv = res_df
            elif where_query  and grouping_colums and aggregation:
                pv = res_df.reset_index()
            elif grouping_colums and aggregation:
                pv = res_df.reset_index()
            elif grouping_colums and  not aggregation:
                pv = res_df


        metadata = ProjectMetaData.objects.get(project=project)
        columns_dtypes = {}
        df_columns    = pv.columns.to_list()
        for key, value in metadata.meta_data.items():
            if key in df_columns:
                ##print("key",key)
                if value['dtype'] == 'int':
                    pv[key] =pd.to_numeric(pv[key])
                    if key in df_columns:
                        pv[key] = pd.to_numeric(pv[key])
                    columns_dtypes[key]= 'number'
                elif value['dtype'] == 'float':
                    ##print("final key",key,pv[key],pv[key].dtypes)
                    pv[key] = pd.to_numeric(pv[key])
                    if key in df_columns:
                        pv[key] = pd.to_numeric(pv[key])
                    columns_dtypes[key]= 'number'
                elif value['dtype'] == 'object':
                    pv[key] = pv[key].astype(str)
                    if key in df_columns:
                        pv[key] = pv[key].astype(str)
                    columns_dtypes[key]= 'string'
                elif value['dtype'] == 'bool':
                    pv[key] = pv[key].astype(bool)
                    if key in df_columns:
                        pv[key] = pv[key].astype(bool)
                    columns_dtypes[key]= 'bool'
                elif value['dtype'] == 'DateTime':
                    pv[key] =pd.to_datetime(pv[key])
                    ##print("the data key",key)
                    if key in df_columns:
                        pv[key] = pd.to_datetime(pv[key])
                    columns_dtypes[key]= 'DateTime'
        number_columns = pv.select_dtypes(include=['number'])
        all_df_columns = pv.columns.tolist()
        df_columns    = pv.select_dtypes(include=['number','bool','object'])
        feature_columns  = pv.select_dtypes(include =['object','bool','number'])
        if  metadata.date_column_name in all_df_columns and metadata.date_column_name:
             pv[metadata.date_column_name] = pv[metadata.date_column_name].astype('str')
        df_rows =pv.shape[0]
        df_column_count=  pv.shape[1]
        res_df__table_content = pv.to_html(classes="table table-striped tableFixHead",border="0")
        project_query,create = ProjectQuery.objects.get_or_create(query_id=query_id,
                                                          project=project,
                                                          where_query=where_query,
                                                          group_query=grouping_colum,
                                                          aggregation_value=value_column,
                                                          aggregation_query=aggregation_queries,
                                                          expected_range=frequency,
                                                          start_date = start_date,
                                                          end_date=end_date,
                                                          start_date_select=from_date_select,
                                                          end_date_select=to_date_select)
        # t_df = res_df.T
        # ##print("the visulization columns",pv)
        project_iqu = ProjectBillingPrms.objects.get(project=project)
        project_iqu_update = ProjectBillingPrms.objects.filter(project=project).update(query_count=project_iqu.query_count+1)
        df_columns     = pv.columns.tolist()
        for column in df_columns:
            try:
                pv[column] = pd.to_numeric(pv[column])
            except:
                pass

        string_columns = pv.select_dtypes(include ='object')
        df_columns     = pv.columns.tolist()
        # pv = res_df.unstack()

        # mpd = pd.melt(pv, id_vars ='Campaign', value_vars =['Clicks'],value_name="Clicks")
        # mpd.rename(columns = {None:'Aggrigation'}, inplace = True)

        # fig = px.scatter_matrix(pv)
        # div = opy.plot(fig, auto_open=False, output_type='div')
        div = True
        ##print("from graph ploting")
        project = Project.objects.get(pk=pk)
        dashboard_form = ProjectDashboardForm(initial={'project':project.pk})
        dashboard_form.fields['user'].queryset = ProjectUser.objects.filter(project=project)
        dashboard_form.fields['dashboard'].queryset = ProjectDashboard.objects.filter(project=project)







        context={'form':form,'df_rows':df_rows,'feature_columns':feature_columns, 'df_column_count':df_column_count,'query':res_df__table_content,'dashboard_form':dashboard_form,'permission':permission,'graph':div,'project_query':project_query,'df_columns':df_columns,'string_columns':string_columns,'number_columns':number_columns}
        return render(request,'dashboard/project_query.html',context)

'''class to display all the dashboards with respect to projects'''
class AllDashboards(View):
    def get(self,request,pk):
        template_name='dashboard/all_dashboards.html'
        project=Project.objects.get(pk=pk)
        all_dashboards=ProjectDashboard.objects.filter(project=project)
        context={
                'all_dashboards':all_dashboards
        }
        return render(request,template_name,context)
'''class to display the project details of the particular project'''
class SingleProjectDetails(GroupRequiredMixin,LoginRequiredMixin,View):
    def dispatch(self, request, *args, **kwargs):
        pk = str(kwargs['pk'])
        self.login_url = '/customer/login/'
        self.redirect_field_name = 'redirect_to'
        self.template_name='dashboard/index.html'
        admin_name = pk+"_Admin"
        ##print(type(admin_name), admin_name)
        admin_encode_name = admin_name.encode()
        admin_unicode_name = admin_encode_name.decode('utf-8')
        read_name = pk+"_Read"
        ##print(type(read_name), read_name)
        read_encode_name = read_name.encode()
        read_unicode_name = read_encode_name.decode('utf-8')
        write_name = pk+"_Write"
        ##print(type(write_name), write_name)
        write_encode_name = write_name.encode()
        write_unicode_name = write_encode_name.decode('utf-8')
        delete_name = pk+"_Delete"
        ##print(type(write_name), write_name)
        delete_encode_name = delete_name.encode()
        delete_unicode_name = delete_encode_name.decode('utf-8')
        l= [read_unicode_name,admin_unicode_name,write_unicode_name,delete_unicode_name]
        self.group_required= l
        ##print("the self of dispatcher",self.group_required)

        return super(SingleProjectDetails, self).dispatch(request, *args, **kwargs)




    def get(self,request,pk):
        template_name='dashboard/single_project_details.html'
        context= single_project_details(request,pk)
        return render(request,template_name,context)

# function for sinngle progect details
def single_project_details(request,pk):
    seo=SiteSeo.objects.get(choices='Single Project Details')
    update_form=ProjectUpdateForm() #form to update the project details.

    project=Project.objects.get(pk=pk)
    data=project.type.name
    now = datetime.now()
    monthly_cost = ProjectBillingMonthCost.objects.filter(Q(project=project) & Q(created__year=now.year)).order_by('id')
    project_invoice = ProjectInvoice.objects.filter(Q(monthly_cost__project=project)).order_by('-id')
    month_list = []
    time_diff = {}
    today = datetime.now()

    project_integrations = CustomerAPIDetails.objects.filter(project=project)
    for integrations in project_integrations:
        print("the date",today.date(),today.time())

        start = datetime.strptime(f'{today.date()} {today.time()}', '%Y-%m-%d %H:%M:%S.%f')
        if integrations.updated:
            ends =datetime.strptime(f'{integrations.updated.date()} {integrations.updated.time()}', '%Y-%m-%d %H:%M:%S.%f')
        else:
            ends = datetime.strptime(f'{integrations.created.date()} {integrations.created.time()}', '%Y-%m-%d %H:%M:%S.%f')
        diff = relativedelta(start, ends)
        print(diff.year)
        time_str = ''
        if diff.year and  diff.year>0:
            time_str=time_str+' ' +str(diff.years)+'Y'
        if diff.months and diff.months>0:
           time_str=time_str+' ' +str(diff.months)+'M'
        if diff.days and diff.days>0:
            time_str=time_str+' ' +str(diff.dasy)+ 'D'
        if diff.hours and  diff.hours>0:
           time_str=time_str+' ' +str(diff.hours)+ 'H'
        if diff.minutes and diff.minutes>0:
           time_str=time_str+' ' +str(diff.minutes)+ 'Min(s) ago'
        if not diff.year and not diff.months and not diff.days and not diff.hours and not diff.minutes:
            time_str=time_str+' '+'Just Now'
        time_diff[integrations.pk] = time_str



    iqs_list = []
    disk_space_count =[]
    for month_cost in monthly_cost:
        month = month_cost.created.strftime("%B")
        month_list.append(month)
        iqs_list.append(month_cost.iqs_count)
        disk_space_count.append(month_cost.disk_space_count)
    month_list  = json.dumps(month_list)
    iqs_list = json.dumps(iqs_list)
    customer = Customer.objects.get(user=request.user)

    if ProjectPricing.objects.filter(project=project).exists():
        project_billing_pricing = ProjectPricing.objects.get(project=project)
    else:
        project_billing_pricing = DefaultProjectPricing.objects.all().order_by('-id')[0]
    data_description=project.type.description
    if project_billing_pricing.monthly_maintenance:
        monthly_maintenance = project_billing_pricing.monthly_maintenance
    else:
        monthly_maintenance = 0

    project_billng,created = ProjectBillingPrms.objects.get_or_create(project=project)
    project_jsons = ProjectJsonStorage.objects.filter(project=project)
    project_ep = ProjectEndPoint.objects.filter(project=project)
    total_size_bytes = total_disk_space(project_ep,project_jsons)
    total_size_mb = total_size_bytes/1000000
    project_usage = ProjectBillingPrms.objects.get(project=project)
    d_endpoint_count = ProjectEndPoint.objects.filter(project=project).count()
    d_user_count = ProjectUser.objects.filter(project=project).count()
    c_endpoint_count = project_usage.end_point+5
    c_user_count    = project_usage.user+5
    user_monthly_charges = round(project_billng.user*project_billing_pricing.user,2)
    user_annual_charges = round((project_billng.user*project_billing_pricing.user)*12,2)
    end_point_monthly_charges = round(project_billing_pricing.end_point*project_billng.end_point,2)
    end_point_annual_charges = round((project_billing_pricing.end_point*project_billng.end_point)*12,2)
    disk_space_monthly_cost  = round(project_billing_pricing.disk_space * total_size_mb,2)
    disk_space_yearly_cost  = round((project_billing_pricing.disk_space * total_size_mb) * 12,2)
    print("the user,user cost",project_billng.user,project_billing_pricing.user)
    if customer.type == 'Individual':

        if project_billng.query_count>100:
            iqs_monthly_cost = round((project_billng.query_count-100) * project_billing_pricing.iqs,2)
            iqs_yearly_cost = round(((project_billng.query_count-100)  * project_billing_pricing.iqs) *12,2)
            iqs_count = project_billng.query_count
        else:
            iqs_monthly_cost = 0
            iqs_yearly_cost = 0
            iqs_count = 0
    else:
        if project_billng.query_count>300:
            iqs_monthly_cost = round((project_billng.query_count-300) * project_billing_pricing.iqs,2)
            iqs_yearly_cost = round(((project_billng.query_count-300)  * project_billing_pricing.iqs) *12,2)
            iqs_count = project_billng.query_count-300
        else:
            iqs_monthly_cost = 0
            iqs_yearly_cost = 0
            iqs_count = 0
    if project_billing_pricing.custom_supprt:
        total_monthly_charges = round(iqs_monthly_cost + disk_space_monthly_cost + user_monthly_charges + end_point_monthly_charges+monthly_maintenance+project_billing_pricing.custom_supprt,2)
    else:
        total_monthly_charges = round(iqs_monthly_cost + disk_space_monthly_cost + user_monthly_charges + end_point_monthly_charges+monthly_maintenance,2)
    total_annual_charges =  round(iqs_yearly_cost+disk_space_yearly_cost + user_annual_charges + end_point_annual_charges+monthly_maintenance,2)
    if Project.objects.filter(pk=project.pk,admin_user=request.user).exists():
        permission="Admin"
    elif ProjectUser.objects.filter(project=project,project_user=request.user).exists():
        user_group = User.objects.get(pk=request.user.pk)

        for g in user_group.groups.all():
            if g.name == str(project.pk)+"_Read":
                permission="Read"
            elif g.name == str(project.pk)+"_Write":
                permission="Write"
            elif g.name == str(project.pk)+"_Delete":
                permission="Delete"
            elif g.name == str(project.pk)+"_Admin":
                permission="Admin"
    else:
        pass
    ##print("the permission is",permission)
    if ProjectDashboard.objects.filter(project=project).exists():
        dashboard = ProjectDashboard.objects.filter(project=project)
    else:
        dashboard=None
    if ProjectEndPoint.objects.filter(project=project).exists():
        project_endpoints = ProjectEndPoint.objects.filter(project=project).order_by('name')
    else:
        project_endpoints=None

    try:
        tickets = Ticket.objects.filter(project=project).order_by('-id')[:5]
    except:
        tickets = Ticket.objects.filter(project=project).order_by('-id')

    ticket_form = TicketForm()
    try:
        integrations = CustomerAPIDetails.objects.filter(project=project)
        context={
                'dashboard':dashboard,
                'permission':permission,
                'integrations':integrations,
                'update_form':update_form,
                'project':project,
                'customer':customer,
                'month_list':month_list,
                'iqs_list':iqs_list,
                'disk_space_count':disk_space_count,
                'project_invoice':project_invoice,
                'project_billng':project_billng,
                'disk_space_monthly_cost':disk_space_monthly_cost,
                'disk_space_yearly_cost':disk_space_yearly_cost,
                'iqs_monthly_cost':iqs_monthly_cost,
                'iqs_yearly_cost':iqs_yearly_cost,
                'user_monthly_charges':user_monthly_charges,
                'user_annual_charges':user_annual_charges,
                'end_point_monthly_charges':end_point_monthly_charges,
                'end_point_annual_charges':end_point_annual_charges,
                'total_monthly_charges':total_monthly_charges,
                'total_annual_charges':total_annual_charges,
                'monthly_maintenance':monthly_maintenance,
                'data_description':data_description,
                'total_size_mb':total_size_mb,
                'project_endpoints':project_endpoints,
                'seo':seo,
                'tickets':tickets,
                'ticket_form':ticket_form,
                'iqs_count':iqs_count,
                'project_integrations':project_integrations,
                'project_billing_pricing':project_billing_pricing,
                'd_endpoint_count':d_endpoint_count,
                'd_user_count':d_endpoint_count,
                'c_endpoint_count':c_endpoint_count,
                'c_user_count':c_user_count,
                'time_diff':time_diff,
            }
    except:
        context={
            'dashboard':dashboard,
            'permission':permission,
            'update_form':update_form,
            'project':project,
            'customer':customer,
            'project_billng':project_billng,
            'data_description':data_description,
            'disk_space_monthly_cost':disk_space_monthly_cost,
            'disk_space_yearly_cost':disk_space_yearly_cost,
            'iqs_monthly_cost':iqs_monthly_cost,
            'iqs_yearly_cost':iqs_yearly_cost,
            'user_monthly_charges':user_monthly_charges,
            'user_annual_charges':user_annual_charges,
            'end_point_monthly_charges':end_point_monthly_charges,
            'end_point_annual_charges':end_point_annual_charges,
            'monthly_cost':monthly_cost,
            'total_monthly_charges':total_monthly_charges,
            'total_annual_charges':total_annual_charges,
            'project_endpoints':project_endpoints,
            'seo':seo,
            'tickets':tickets,
            'ticket_form':ticket_form,
            'monthly_maintenance':monthly_maintenance,
            'total_size_mb':total_size_mb,
            'iqs_count':iqs_count,
            'project_invoice':project_invoice,
            'month_list':month_list,
            'iqs_list':iqs_list,
            'disk_space_count':disk_space_count,
            'project_integrations':project_integrations,
            'project_billing_pricing':project_billing_pricing,
            'd_endpoint_count':d_endpoint_count,
            'd_user_count':d_endpoint_count,
            'c_endpoint_count':c_endpoint_count,
            'c_user_count':c_user_count,
            'time_diff':time_diff,
            }
    print("the final context is",context)
    return context

'''ajax call view to update the notification count'''
def update_notification_read(request):
    if request.method == "POST":
        ##print("inside update notification read")
        read = request.POST['notification_read']
        user = User.objects.get(username=request.user)
        notification_user=UserNotification.objects.get(user=user)
        pk=notification_user.pk
        notification_read = UserNotification.objects.filter(pk=pk).update(notification_read=read)
        ##print("notification_read updated",notification_read)
        updated_notification = UserNotification.objects.get(user=request.user)
        updated_notification_read=updated_notification.notification_read
        notification_count=updated_notification.notification_count
        data={
            'updated_notification_read':updated_notification_read,
            'notification_count':notification_count
        }
        return JsonResponse(data,safe=False)

'''function to check the differnce between the file columns'''
def Diff(li1, li2):
   return (list(set(li1) - set(li2)))

def msg_display(pk,admin_user,project,method,project_user):
    if method == "GET":
        seo=SiteSeo.objects.get(choices='User Management')
        add_user_form=AddUsersForm()
        if admin_user.username =='administrator':
            project=Project.objects.get(pk=pk)
            try:
                project_users=ProjectUser.objects.filter(project=pk)
                ##print("project_users",project_users)
                ##print("after try")
                if project_users:
                    for p in project_users:
                        user=User.objects.get(username=p.project_user)
                        ##print(user)
                        try:
                            customer=Customer.objects.get(user=user)
                            ##print("after customer try")
                            ##print(customer.contact_no)
                            context={
                             'add_user_form':add_user_form,
                             'project_users':project_users,
                             'project':project,
                             'customer':customer,
                             'seo':seo
                            }
                        except:
                            return{
                            'add_user_form':add_user_form,
                            'project_users':project_users,
                            'project':project,

                            'seo':seo
                            }
                else:
                    return{
                    'add_user_form':add_user_form,
                    'project':project,
                    'seo':seo
                    }
            except:
                  return{
                  'add_user_form':add_user_form,

                  'project':project,
                  'seo':seo
                  }


        else:

            customer=Customer.objects.get(user=admin_user)
            ##print(pk)
            project=Project.objects.get(pk=pk)
            try:
                project_users=ProjectUser.objects.filter(project=pk)
                ##print("project_users",project_users)
                ##print("after try")
                if project_users:
                    for p in project_users:
                        user=User.objects.get(username=p.project_user)
                        ##print(user)
                        try:
                            customer=Customer.objects.get(user=user)
                            ##print("after customer try")
                            ##print(customer.contact_no)
                            return{
                             'add_user_form':add_user_form,
                             'customer':customer,
                             'project_users':project_users,
                             'project':project,
                             'customer':customer.contact_no,

                             'seo':seo
                            }
                        except:
                            return{
                            'add_user_form':add_user_form,
                            'customer':customer,
                            'project_users':project_users,
                            'project':project,

                            'seo':seo
                            }
                else:
                    return{
                    'add_user_form':add_user_form,
                    'customer':customer,
                    'project':project,
                    'seo':seo
                    }
            except:
                  return{
                  'add_user_form':add_user_form,
                  'customer':customer,
                  'project':project,
                  'seo':seo
                  }
    elif method == "POST":
        seo=SiteSeo.objects.get(choices='User Management')
        add_user_form=AddUsersForm()
        if admin_user.username =='administrator':
            project=Project.objects.get(pk=pk)
            try:
                project_users=ProjectUser.objects.filter(project=pk)
                ##print("project_users",project_users)
                ##print("after try")
                if project_users:
                    for p in project_users:
                        user=User.objects.get(username=p.project_user)
                        ##print(user)
                        try:
                            customer=Customer.objects.get(user=user)
                            ##print("after customer try")
                            ##print(customer.contact_no)
                            return{
                             'add_user_form':add_user_form,
                             'project_users':project_users,
                             'project':project,
                             'customer':customer,
                             'msg':"You have added" + "  " + str(project_user)+ "to"+ "  " + str(project),
                             'seo':seo
                            }
                        except:
                            return{
                            'add_user_form':add_user_form,
                            'project_users':project_users,
                            'project':project,
                             'msg':"You have added" + str(project_user)+ "to"+" "+ str(project),
                            'seo':seo
                            }
                else:
                    return {
                    'add_user_form':add_user_form,
                    'project':project,
                    'seo':seo
                    }
            except:
                  return{
                  'add_user_form':add_user_form,

                  'project':project,
                  'seo':seo
                  }


        else:

            customer=Customer.objects.get(user=admin_user)
            ##print(pk)
            project=Project.objects.get(pk=pk)
            try:
                project_users=ProjectUser.objects.filter(project=pk)
                ##print("project_users",project_users)
                ##print("after try")
                if project_users:
                    for p in project_users:
                        user=User.objects.get(username=p.project_user)
                        ##print(user)
                        try:
                            customer=Customer.objects.get(user=user)
                            ##print("after customer try")
                            ##print(customer.contact_no)
                            return{
                             'add_user_form':add_user_form,
                             'customer':customer,
                             'project_users':project_users,
                             'project':project,
                             'customer':customer.contact_no,
                             'msg':"You have added" + str(project_user)+ "to"+" "+ str(project),
                             'seo':seo
                            }
                        except:
                            return{
                            'add_user_form':add_user_form,
                            'customer':customer,
                            'project_users':project_users,
                            'project':project,
                             'msg':"You have added" + " "+ str(project_user)+ " " +"to"+ " "+ str(project),
                            'seo':seo
                            }
                else:
                    return{
                    'add_user_form':add_user_form,
                    'customer':customer,
                    'project':project,
                    'seo':seo
                    }
            except:
                  return {
                  'add_user_form':add_user_form,
                  'customer':customer,
                  'project':project,
                  'seo':seo
                  }


class ProjectQueryDetails(View):
    '''class for query  details '''
    def dispatch(self, request, *args, **kwargs):
        pk = kwargs['pk']
        query = ProjectQuery.objects.get(pk=pk)
        pk = str(query.project.pk)
        self.login_url = '/customer/login/'
        self.redirect_field_name = 'redirect_to'
        self.template_name='dashboard/index.html'
        admin_name = pk+"_Admin"
        ##print(type(admin_name), admin_name)
        admin_encode_name = admin_name.encode()
        admin_unicode_name = admin_encode_name.decode('utf-8')
        write_name = pk+"_Write"
        ##print(type(write_name), write_name)
        write_encode_name = write_name.encode()
        write_unicode_name = write_encode_name.decode('utf-8')

        delete_name = pk+"_Delete"
        ##print(type(delete_name), delete_name)
        delete_encode_name = delete_name.encode()
        delete_unicode_name = delete_encode_name.decode('utf-8')
        l =[delete_unicode_name,write_unicode_name,admin_unicode_name]
        self.group_required= l
        ##print("the self of dispatcher",self.group_required)

        return super(ProjectQueryDetails, self).dispatch(request, *args, **kwargs)
    def get(self,request,pk):
        project_query = ProjectQuery.objects.get(pk=pk)
        project = Project.objects.get(pk=project_query.project.pk)
        piqu,created = ProjectBillingPrms.objects.get_or_create(project=project)

        form = ProjectEndPointForm()
        update = ProjectBillingPrms.objects.filter(project=project).update(query_count=piqu.query_count+1)
        dashboard_form = ProjectDashboardForm(initial={'project':project.pk})
        dashboard_form.fields['user'].queryset = ProjectUser.objects.filter(project=project)
        dashboard_form.fields['dashboard'].queryset = ProjectDashboard.objects.filter(project=project)
        if Project.objects.filter(pk=project.pk,admin_user=request.user).exists():
            permission="Admin"
        elif ProjectUser.objects.filter(project=project,project_user=request.user).exists():
            user_group = User.objects.get(pk=request.user.pk)

            for g in user_group.groups.all():
                if g.name == str(project.pk)+"_Read":
                    permission="Read"
                elif g.name == str(project.pk)+"_Write":
                    permission="Write"
                elif g.name == str(project.pk)+"_Delete":
                    permission="Delete"
                elif g.name == str(project.pk)+"_Admin":
                    permission="Admin"

        else:
            permission = None
        pv = QueryExcecute(project_query)
        # for column in df_columns:
        #     try:
        #         pv[column] = pd.to_numeric(pv[column])
        #     except:
        #         pass

        # t_df = res_df.T
        # ##print("the visulization columns",pv)
        df_columns= pv.columns.tolist()
        df_rows = pv.shape[0]
        df_column_count= pv.shape[1]
        feature_columns= pv.select_dtypes(include =['object','bool','number'])
        string_columns = pv.select_dtypes(include =['object','bool'])
        number_columns = pv.select_dtypes(include=['number'])
        metadata = ProjectMetaData.objects.get(project=project_query.project)
        if metadata.date_column_name and metadata.date_column_name in df_columns:
            pv[metadata.date_column_name] = pv[metadata.date_column_name].astype(str)

        res_df__table_content = pv.to_html(classes="table table-striped tableFixHead",border="0")


        df=pv
        if  project_query.plot and project_query.plot.plot_type:
            plot_obj = QueryPlot(df,project_query.pk)
            div = plot_obj.plot(project_query.plot)

        else:
            # fig = px.scatter_matrix(df)
            # div = opy.plot(fig, auto_open=False, output_type='div')
            div = True

        project = Project.objects.get(pk=project_query.project.pk)

        context={'form':form,'df_rows':df_rows,'df_column_count':df_column_count,'project':project,'query':res_df__table_content,'dashboard_form':dashboard_form,'permission':permission,'graph':div,'project_query':project_query,'df_columns':df_columns,'string_columns':string_columns,'feature_columns':feature_columns,'number_columns':number_columns}
        return render(request,'dashboard/project_query.html',context)


    def post(self,request,pk):
        query_object = request.POST.get('end_point_object',None)
        if query_object:
            query_object = ast.literal_eval(query_object)
        project_query = ProjectQuery.objects.get(pk=pk)
        form = form = ProjectEndPointForm()
        project = Project.objects.get(pk=project_query.project.pk)
        piqu,created = ProjectBillingPrms.objects.get_or_create(project=project)
        update = ProjectBillingPrms.objects.filter(project=project).update(query_count=piqu.query_count+1)
        dashboard_form = ProjectDashboardForm(initial={'project':project.pk})
        dashboard_form.fields['user'].queryset = ProjectUser.objects.filter(project=project)
        dashboard_form.fields['dashboard'].queryset = ProjectDashboard.objects.filter(project=project)
        if Project.objects.filter(pk=project.pk,admin_user=request.user).exists():

            permission="Admin"
        elif ProjectUser.objects.filter(project=project,project_user=request.user).exists():
            user_p =ProjectUser.objects.get(project=project,project_user=request.user)
            user = user_p.project_user
            user_group = User.objects.get(pk=request.user.pk)

            for g in user_group.groups.all():
                if g.name == str(project.pk)+"_Read":
                    permission="Read"
                elif g.name== str(project.pk)+"_Write":
                    permission="Write"
                elif g.name == str(project.pk)+"_Delete":
                    permission="Delete"
                elif g.name == str(project.pk)+"_Admin":
                    permission="Admin"
        else:
            permission="None"
        df = QueryExcecute(project_query)
        df_columns = df.columns.tolist()
        metadata = ProjectMetaData.objects.get(project=project_query.project)
        number_columns = df.select_dtypes(include =['number'])
        string_columns = df.select_dtypes(include ='object')
        feature_columns  = df.select_dtypes(include =['object','bool','number'])
        if metadata.date_column_name and metadata.date_column_name in df_columns:
            df[metadata.date_column_name] = df[metadata.date_column_name].astype(str)



        res_df__table_content =  df.to_html(classes="table table-striped tableFixHead",border="0")
        df_rows =df.shape[0]
        df_column_count=  df.shape[1]
        plot_type = request.POST.get('plot_type',None)
        x_bubble_plot = request.POST.get('x_bubble_plot',None)
        y_bubble_plot = request.POST.get('y_bubble_plot',None)
        bubble_plot_color = request.POST.get('bubble_plot_color',None)
        x_time_series    =   request.POST.get('x_time_series',None)
        y_time_series    =   request.POST.get('y_time_series',None)
        x_2d = request.POST.get('x_2d',None)
        y_2d = request.POST.get('y_2d',None)
        bar_x = request.POST.get('bar_x',None)
        bar_y = request.POST.get('bar_y',None)
        bar_color = request.POST.get('bar_color',None)
        h_bar_x = request.POST.get('h_bar_x',None)
        h_bar_y = request.POST.get('h_bar_y',None)
        h_bar_color = request.POST.get('h_bar_color',None)
        color_2d = request.POST.get('color_2d',None)
        x_3d = request.POST.get('x_3d',None)
        y_3d = request.POST.get('y_3d',None)
        color_3d = request.POST.get('color_3d',None)
        z = request.POST.get('z',None)
        size = request.POST.get('size',None)
        hover_name = request.POST.get('hover_name',None)
        names= request.POST.get('names',None)
        values = request.POST.get('values',None)
        orientation = request.POST.get('orientation',None)
        heatmap_x   = request.POST.get('heatmap_x',None)
        heatmap_y   = request.POST.get('heatmap_y',None)
        cat_x       = request.POST.get('cat_x',None)
        cat_y       = request.POST.get('cat_y',None)
        cat_color   = request.POST.get('cat_color',None)
        count_x     = request.POST.get('count_x',None)
        count_color = request.POST.get('count_color',None)

        facet_col   = request.POST.get('facet_col',None)

        if count_x and  count_color:
            x= count_x
            y=None
            color_2d = count_color
        elif count_x:
            x= count_x
            y=None
        elif bar_x and bar_y and bar_color:
            x = bar_x
            y = bar_y
            color_2d = bar_color
        elif bar_x and bar_y:
            x = bar_x
            y = bar_y
        elif h_bar_x and h_bar_y and h_bar_color:
            x = h_bar_x
            y = h_bar_y
            color_2d = h_bar_color


        elif h_bar_x and h_bar_y:
            x = h_bar_x
            y = h_bar_y
        elif cat_x and cat_y and cat_color and facet_col:
            x = cat_x
            y = cat_y
            color_2d = cat_color
            facet_col = facet_col
        elif cat_x and cat_y and facet_col:
            x = cat_x
            y = cat_y
            facet_col = facet_col
        elif heatmap_x and heatmap_y:
            x= heatmap_x
            y= heatmap_y

        elif  x_bubble_plot and y_bubble_plot and bubble_plot_color :
            x=x_bubble_plot
            y=y_bubble_plot
            color_2d = bubble_plot_color
        elif  x_bubble_plot and y_bubble_plot:
            x=x_bubble_plot
            y=y_bubble_plot
            color_2d = None
        elif  x_time_series and x_time_series  :
            x=x_time_series
            y=y_time_series
            color_2d = None

        elif x_2d and y_2d and color_2d:
            x=x_2d
            y=y_2d
            color_2d = color_2d
        elif x_2d and y_2d :
            x=x_2d
            y=y_2d
            color = None
        elif x_3d and y_3d and color_3d:
            x=x_3d
            y=y_3d
            color_2d = color_3d
        elif x_3d and y_3d:
            x=x_3d
            y=y_3d
            color_2d = None
        else:
            x=None
            y=None
            color_2d = None
        ##print("color choosen",color_3d,color_2d)

        query = ProjectQuery.objects.get(pk=pk)
        if plot_type and query.plot:
            plot = Plot.objects.get(pk=query.plot.pk)
            plot_obj = QueryPlot(df,project_query.pk)

            if color_2d:

                div =  plot_obj.update_plot(plot,plot_type,x=x,y=y,z=z,color=color_2d,values=values,names=names,legend=plot.legend,size=size,hover_name=hover_name,orientation=orientation,facet_col=facet_col)
            elif color_3d:
                div =  plot_obj.update_plot(plot,plot_type,x=x,y=y,z=z,color=color_3d,legend=plot.legend,size=size,hover_name=hover_name,values=values,names=names,orientation=orientation,facet_col=facet_col)
            else:
                div =  plot_obj.update_plot(plot,plot_type,x=x,y=y,z=z,legend=plot.legend,size=size,hover_name=hover_name,values=values,names=names,orientation=orientation,facet_col=facet_col)


        elif project_query.plot and  project_query.plot.plot_type:
            plot_obj = QueryPlot(df,project_query.pk)
            div = plot_obj.plot(project_query.plot)
        elif  not project_query.plot:
            plot_obj = QueryPlot(df,project_query.pk)
            if color_2d:
                div = plot_obj.create_plot(plot_type,x=x,y=y,z=z,color=color_2d,size=size,hover_name=hover_name,values=values,names=names,orientation=orientation,facet_col=facet_col)
            elif color_3d:
                div = plot_obj.create_plot(plot_type,x=x,y=y,z=z,color=color_3d,size=size,hover_name=hover_name,values=values,names=names,orientation=orientation,facet_col=facet_col)
            else:
                div = plot_obj.create_plot(plot_type,x=x,y=y,z=z,size=size,hover_name=hover_name,values=values,names=names,orientation=orientation,facet_col=facet_col)

        else:
            # fig = px.scatter_matrix(df)
            # div = opy.plot(fig, auto_open=False, output_type='div')
            div = True
        non_query_object = {}
        if query_object:
            non_query_object = {}
            if all('query' not in elem.values() for elem in query_object.values()):
                non_query_object['query']=True
            if all('table' not in elem.values() for elem in query_object.values()):
                non_query_object['table']=True
            if all('plot' not in elem.values() for elem in query_object.values()):
                non_query_object['plot']=True
            if all('ml' not in elem.values() for elem in query_object.values()):
                non_query_object['ml']=True
            if all('cp' not in elem.values() for elem in query_object.values()):
                non_query_object['cp']=True
            ##print(non_query_object)

            context={'form':form,'df_rows':df_rows,'df_column_count':df_column_count,'project':project,'query':res_df__table_content,'dashboard_form':dashboard_form,'permission':permission,'graph':div,'project_query':project_query,'df_columns':df_columns,'string_columns':string_columns,'query_object':query_object,'non_query_object':non_query_object,'feature_columns':feature_columns,'number_columns':number_columns}
            # ##print('the context',context)
        else:
            context={'form':form,'df_rows':df_rows,'df_column_count':df_column_count,'project':project,'query':res_df__table_content,'dashboard_form':dashboard_form,'permission':permission,'graph':div,'project_query':project_query,'df_columns':df_columns,'string_columns':string_columns,'query_object':None,'non_query_object':non_query_object,'feature_columns':feature_columns,'number_columns':number_columns}
        return render(request,'dashboard/project_query.html',context)

class ProjectQueryUpdateView(View,LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        pk = kwargs['pk']
        query = ProjectQuery.objects.get(pk=pk)
        project=Project.objects.get(pk=query.project.pk)
        pk= str(project.pk)
        self.login_url = '/customer/login/'
        self.redirect_field_name = 'redirect_to'
        self.template_name='dashboard/index.html'
        admin_name = pk+"_Admin"
        ##print(type(admin_name), admin_name)
        admin_encode_name = admin_name.encode()
        admin_unicode_name = admin_encode_name.decode('utf-8')
        write_name = pk+"_Write"
        ##print(type(write_name), write_name)
        write_encode_name = write_name.encode()
        write_unicode_name = write_encode_name.decode('utf-8')
        delete_name = pk+"_Delete"
        delete_encode_name = delete_name.encode()
        delete_unicode_name = delete_encode_name.decode('utf-8')
        l= [delete_unicode_name,admin_unicode_name,write_unicode_name]
        self.group_required= l
        ##print("the self of dispatcher",self.group_required)

        return super(ProjectQueryUpdateView, self).dispatch(request, *args, **kwargs)

    def get(self,request,pk):
        seo=SiteSeo.objects.get(choices='Project Details')
        template_name='dashboard/project_details.html'
        query = ProjectQuery.objects.get(pk=pk)
        project=Project.objects.get(pk=query.project.pk)
        if Project.objects.filter(pk=project.pk,admin_user=request.user).exists():
            permission="Admin"
        elif ProjectUser.objects.filter(project=project,project_user=request.user).exists():
            user_group = User.objects.get(pk=request.user.pk)

            for g in user_group.groups.all():
                if g.name == str(project.pk)+"_Read":
                    permission="Read"
                elif g.name == str(project.pk)+"_Write":
                    permission="Write"
                elif g.name == str(project.pk)+"_Delete":
                    permission="Delete"
                elif g.name == str(project.pk)+"_Admin":
                    permission="Admin"
        else:
            permission=None



        ##print(project)
        ##print("pk",pk)
        pk=str(project.pk)
        file_form=FileUploadForm()
        current_site = get_current_site(request)
        site_name = current_site.name
        domain = current_site.domain
        if domain.startswith('127.0.'):
            domain = 'https://'+domain
        else:
            domain = 'https://'+domain
        ##print('domain',domain)
        dashboard_form = ProjectDashboardForm(initial={'project':project.pk})
        dashboard_form.fields['user'].queryset = ProjectUser.objects.filter(project=project)
        dashboard_form.fields['dashboard'].queryset = ProjectDashboard.objects.filter(project=project)

        if ProjectIndex.objects.filter(project=project).exists():
            start_indexer = ProjectIndex.objects.filter(project=project).order_by('id')[0]
            end_indexer = ProjectIndex.objects.filter(project=project).order_by('-id')[0]
            start_year = start_indexer.start_date.year
            end_year = end_indexer.end_date.year
            default_start_date = start_indexer.start_date
            default_end_date = end_indexer.end_date

        else:

            start_year =  None
            end_year = None
            default_start_date = None
            default_end_date = None
        project_metadata = ProjectMetaData.objects.get(project=project)
        if project_metadata.date_column_name:
            time_series_project = True
        else:
            time_series_project = None
        if request.user.username == 'administrator':
                customer=Customer.objects.get(user=request.user)
                try:
                    integrations = CustomerAPIDetails.objects.filter(project=project)
                except:
                    pass
                    ##print('pass')

                return render(request,template_name,context)
        else:

            customer=Customer.objects.get(user=request.user)
            action.send(customer,verb="Viewed" + str(project.name))
            project=Project.objects.get(pk=pk)
            if ProjectQuery.objects.filter(project=project).exists():
                project_query = ProjectQuery.objects.filter(project=project).order_by('-created')
            else:
                project_query = None
            if ProjectJsonStorage.objects.filter(project=project).exists():
                start_date=None
                res_df = optimize.index_optimize(start_date,project.pk)
                df_rows = res_df.shape[1]
                df_columns_count = res_df.shape[0]


                json_field = ProjectJsonStorage.objects.filter(project=project)[0]


                json_st = json.loads(json_field.js)
                json_df = pd.DataFrame(json_st)
                res_df = json_df.transpose()

                df_head = res_df.head(5)
                res_df__table_content = df_head.to_html(classes="table table-striped tableFixHead",border="0")
            else:
                res_df__table_content = None
                df_rows = 0
                df_columns_count = 0
            try:
                integrations = CustomerAPIDetails.objects.filter(project=project)
                context={
                    'integrations':integrations,
                    'project_query':project_query,
                    'res_df__table_content':res_df__table_content,
                    'dashboard_form':dashboard_form,
                    'permission':permission,
                    'df_rows':df_rows,
                    'start_year':start_year,
                    'end_year':end_year,
                    'default_start_date':default_start_date,
                    'default_end_date':default_end_date,
                    'df_columns_count':df_columns_count,
                    'time_series_project':time_series_project,
                    'domain':domain
                }
            except:
                pass
            users = User.objects.filter(pk=request.user.pk)

            if ProjectDashboard.objects.filter(Q(project=project) & Q(dashboard_admin_user__pk =request.user.pk)).exists():
                ##print("project admin")
                dashboard=ProjectDashboard.objects.filter(Q(project=project) & Q(dashboard_admin_user__pk =request.user.pk)  ).order_by('name')
                dashboard_count=ProjectDashboard.objects.filter(Q(project=project) & Q(dashboard_admin_user__pk=request.user.pk)).count()
                ##print("dashboard",dashboard)
                ##print("dashboard count",dashboard_count)

                context = {

                    'project':project,
                    'file_form':file_form,
                    'permission':permission,

                    'customer':customer,
                    'dashboard':dashboard,

                    'dashboard_count':dashboard_count,
                    'seo':seo,
                    'integrations':integrations,
                    'project_query':project_query,
                    'res_df__table_content':res_df__table_content,
                    'dashboard_form':dashboard_form,
                    'df_rows':df_rows,
                    'start_year':start_year,
                    'end_year':end_year,
                    'default_start_date':default_start_date,
                    'default_end_date':default_end_date,
                    'df_columns_count':df_columns_count,
                    'time_series_project':time_series_project,
                    'domain':domain

                    }
            elif ProjectDashboard.objects.filter(Q(project=project) & Q(dashboard_users__in=users )).exists():
                ##print("project users")
                dashboard=ProjectDashboard.objects.filter(Q(project=project) & Q(dashboard_users__in=users )).order_by('name')
                dashboard_count=ProjectDashboard.objects.filter(Q(project=project) & Q(dashboard_users__in=users )).count()
                ##print("dashboard",dashboard)
                ##print("dashboard count",dashboard_count)

                context = {

                    'project':project,
                    'file_form':file_form,
                    'permission':permission,

                    'customer':customer,
                    'dashboard':dashboard,

                    'dashboard_count':dashboard_count,
                    'seo':seo,
                    'integrations':integrations,
                    'project_query':project_query,
                    'res_df__table_content':res_df__table_content,
                    'dashboard_form':dashboard_form,
                    'df_rows':df_rows,
                    'start_year':start_year,
                    'end_year':end_year,
                    'default_start_date':default_start_date,
                    'default_end_date':default_end_date,
                    'df_columns_count':df_columns_count,
                    'time_series_project':time_series_project,
                    'domain':domain

                    }
            else:
                ##print("no dashboard")
                context = {

                    'project':project,

                    'file_form':file_form,
                    'permission':permission,

                    'customer':customer,
                    'seo':seo,
                    'integrations':integrations,
                    'project_query':project_query,
                    'res_df__table_content':res_df__table_content,
                    'dashboard_form':dashboard_form,
                    'df_rows':df_rows,
                    'start_year':start_year,
                    'end_year':end_year,
                    'default_start_date':default_start_date,
                    'default_end_date':default_end_date,
                    'df_columns_count':df_columns_count,
                    'time_series_project':time_series_project,
                    'domain':domain

                }
            ##print("the contest is",context)
            return render(request,template_name,context)
    def post(self,request,pk):
        pk = int(request.POST.get('update_pk'))
        seo=SiteSeo.objects.get(choices='Project Details')
        template_name='dashboard/project_details.html'
        query = ProjectQuery.objects.get(pk=pk)

        project=Project.objects.get(pk=query.project.pk)
        dashboard_form = ProjectDashboardForm(initial={'project':project.pk})
        dashboard_form.fields['user'].queryset = ProjectUser.objects.filter(project=project)
        dashboard_form.fields['dashboard'].queryset = ProjectDashboard.objects.filter(project=project)
        if Project.objects.filter(pk=project.pk,admin_user=request.user).exists():
            permission="Admin"
        elif ProjectUser.objects.filter(project=project,project_user=request.user).exists():
            user_group = User.objects.get(pk=request.user.pk)

            for g in user_group.groups.all():
                if g.name == str(project.pk)+"_Read":
                    permission="Read"
                elif g.name == str(project.pk)+"_Write":
                    permission="Write"
                elif g.name == str(project.pk)+"_Delete":
                    permission="Delete"
                elif g.name == str(project.pk)+"_Admin":
                    permission="Admin"
        else:
            permission=Non
        ##print(project)
        ##print("pk",pk)
        pk=str(project.pk)
        file_form=FileUploadForm()
        current_site = get_current_site(request)
        site_name = current_site.name
        domain = current_site.domain
        if ProjectIndex.objects.filter(project=project).exists():
            start_indexer = ProjectIndex.objects.filter(project=project).order_by('id')[0]
            end_indexer = ProjectIndex.objects.filter(project=project).order_by('-id')[0]
            start_year = start_indexer.start_date.year
            end_year = end_indexer.end_date.year
            default_start_date = start_indexer.start_date
            default_end_date = end_indexer.end_date

        else:

            start_year =  None
            end_year = None
            default_start_date = None
            default_end_date = None
        project_metadata = ProjectMetaData.objects.get(project=project)
        if project_metadata.date_column_name:
            time_series_project = True
        else:
            time_series_project = None
        if domain.startswith('127.0.'):
            domain = 'https://'+domain
        else:
            domain = 'https://'+domain
        ##print('domain',domain)
        if request.user.username == 'administrator':
                customer=Customer.objects.get(user=request.user)
                try:
                    integrations = CustomerAPIDetails.objects.filter(project=project)
                except:
                    pass
                    ##print('pass')

                return render(request,template_name,context)
        else:
            customer=Customer.objects.get(user=request.user)
            action.send(customer,verb="Viewed" + str(project.name))
            project=Project.objects.get(pk=pk)
            if ProjectQuery.objects.filter(project=project).exists():
                project_queries = ProjectQuery.objects.filter(project=project).order_by('-created')
            else:
                project_query = None
            if ProjectJsonStorage.objects.filter(project=project).exists():

                json_fields = ProjectJsonStorage.objects.filter(project=project)[0]
                start_date=None
                res_df = optimize.index_optimize(start_date,project.pk)
                df_rows = res_df.shape[1]
                df_columns_count = res_df.shape[0]
                json_st = json.loads(json_fields.js)
                json_df = pd.DataFrame(json_st)
                res_df = json_df.transpose()

                df_head = res_df.head(5)
                metadata = ProjectMetaData.objects.get(project=project)
                df_columns = df_head.columns.tolist()
                columns_dtypes = {}
                for key, value in metadata.meta_data.items():
                    if key in df_columns:
                        ##print("key",key)
                        if value['dtype'] == 'int':
                            df_head[key] =pd.to_numeric(df_head[key])
                            if key in df_columns:
                                df_head[key] = pd.to_numeric(df_head[key])
                            columns_dtypes[key]= 'number'
                        elif value['dtype'] == 'float':
                            ##print("final key",key,df_head[key],df_head[key].dtypes)
                            df_head[key] = pd.to_numeric(df_head[key])
                            if key in df_columns:
                                df_head[key] = pd.to_numeric(df_head[key])
                            columns_dtypes[key]= 'number'
                        elif value['dtype'] == 'object':
                            df_head[key] = df_head[key].astype(str)
                            if key in df_columns:
                                df_head[key] = df_head[key].astype(str)
                            columns_dtypes[key]= 'string'
                        elif value['dtype'] == 'bool':
                            df_head[key] = df_head[key].astype(bool)
                            if key in df_columns:
                                df_head[key] = df_head[key].astype(bool)
                            columns_dtypes[key]= 'bool'
                        elif value['dtype'] == 'DateTime':
                            df_head[key] =pd.to_datetime(df_head[key])
                            ##print("the data key",key)
                            if key in df_columns:
                                df_head[key] = pd.to_datetime(df_head[key])
                            columns_dtypes[key]= 'DateTime'
                number_columns = df_head.select_dtypes(include=['number'])
                df_columns    = df_head.select_dtypes(include=['number','bool','object'])
                if metadata.date_column_name:
                    df_head[metadata.date_column_name] = df_head[metadata.date_column_name].astype('str')



                res_df__table_content = df_head.to_html(classes="table table-striped tableFixHead",border="0")
            else:
                df_columns = []
                columns_dtypes = {}
                number_columns = []
                res_df__table_content = None
                df_rows = 0
                df_columns_count = 0
            try:
                integrations = CustomerAPIDetails.objects.filter(project=project)
                context={
                    'integrations':integrations,
                    'project_query':project_queries,
                    'dashboard_form':dashboard_form,
                    'query':query,
                    'df_columns':df_columns,
                    'number_columns':number_columns,
                    'columns_dtypes':columns_dtypes,
                    'permission':permission,
                    'res_df__table_content':res_df__table_content,
                    'domain':domain,
                    'df_rows':df_rows,
                    'start_year':start_year,
                    'end_year':end_year,
                    'time_series_project':time_series_project,
                    'default_start_date':default_start_date,
                    'default_end_date':default_end_date,
                    'df_columns_count':df_columns_count,
                }
            except:
                try:
                    dashboard=ProjectDashboard.objects.filter(project=project)
                    dashboard_count=ProjectDashboard.objects.filter(project=project).count()
                    ##print("dashboard",dashboard)
                    ##print("dashboard count",dashboard_count)

                    context = {

                        'project':project,
                        'file_form':file_form,
                        'dashboard_form':dashboard_form,

                        'customer':customer,
                        'dashboard':dashboard,
                        'df_columns':df_columns,
                        'number_columns':number_columns,
                        'columns_dtypes':columns_dtypes,
                        'dashboard_count':dashboard_count,
                        'seo':seo,
                        'project_query':project_queries,
                        'query':query,
                        'permission':permission,
                        'res_df__table_content':res_df__table_content,
                        'domain':domain,
                        'df_rows':df_rows,
                        'start_year':start_year,
                        'end_year':end_year,
                        'time_series_project':time_series_project,
                        'default_start_date':default_start_date,
                        'default_end_date':default_end_date,
                        'df_columns_count':df_columns_count,

                        }
                except:
                    ##print("no dashboard")
                    context = {

                        'project':project,

                        'file_form':file_form,
                        'dashboard_form':dashboard_form,
                        'df_columns':df_columns,
                        'number_columns':number_columns,
                        'columns_dtypes':columns_dtypes,

                        'customer':customer,
                        'seo':seo,
                        'project_query':project_queries,
                        'query':query,
                        'permission':permission,
                        'res_df__table_content':res_df__table_content,
                        'domain':domain,
                        'df_rows':df_rows,
                        'start_year':start_year,
                        'end_year':end_year,
                        'time_series_project':time_series_project,
                        'default_start_date':default_start_date,
                        'default_end_date':default_end_date,
                        'df_columns_count':df_columns_count,

                    }
                    return render(request,template_name,context)




            try:
                dashboard=ProjectDashboard.objects.filter(project=project)
                dashboard_count=ProjectDashboard.objects.filter(project=project).count()
                ##print("dashboard",dashboard)
                ##print("dashboard count",dashboard_count)

                context = {

                    'project':project,
                    'file_form':file_form,
                    'permission':permission,
                    'dashboard_form':dashboard_form,
                    'customer':customer,
                    'df_columns':df_columns,
                    'number_columns':number_columns,
                    'columns_dtypes':columns_dtypes,
                    'dashboard':dashboard,
                    'time_series_project':time_series_project,
                    'dashboard_count':dashboard_count,
                    'seo':seo,
                    'integrations':integrations,
                    'project_query':project_queries,
                    'query':query,

                    'res_df__table_content':res_df__table_content,
                    'domain':domain,
                    'df_rows':df_rows,
                    'start_year':start_year,
                    'end_year':end_year,
                    'default_start_date':default_start_date,
                    'default_end_date':default_end_date,
                    'df_columns_count':df_columns_count,

                    }
            except:
                ##print("no dashboard")
                context = {
                    'permission':permission,
                    'project':project,
                    'dashboard_form':dashboard_form,
                    'file_form':file_form,


                    'customer':customer,
                    'seo':seo,
                    'integrations':integrations,
                    'project_query':project_queries,
                    'query':query,
                    'df_columns':df_columns,
                    'number_columns':number_columns,
                    'columns_dtypes':columns_dtypes,
                    'res_df__table_content':res_df__table_content,
                    'domain':domain,
                    'df_rows':df_rows,
                    'start_year':start_year,
                    'end_year':end_year,
                    'time_series_project':time_series_project,
                    'default_start_date':default_start_date,
                    'default_end_date':default_end_date,
                    'df_columns_count':df_columns_count,

                }
                ##print("project query update ",context)
                return render(request,template_name,context)
            ##print("project query update ",context)
            return render(request,template_name,context)



class ProjectQueryDeleteView(GroupRequiredMixin,View,LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        delet_pks = request.POST.get('delete_pk',None)
        if delet_pks:
            delet_pks = list(delet_pks.split(","))
            delet_pks.pop(0)

        query = ProjectQuery.objects.get(pk=int(delet_pks[0]))
        project=Project.objects.get(pk=query.project.pk)
        pk= str(project.pk)
        self.login_url = '/customer/login/'
        self.redirect_field_name = 'redirect_to'
        self.template_name='dashboard/index.html'
        admin_name = pk+"_Admin"
        ##print(type(admin_name), admin_name)
        admin_encode_name = admin_name.encode()
        admin_unicode_name = admin_encode_name.decode('utf-8')
        write_name = pk+"_Write"


        ##print(type(write_name), write_name)
        write_encode_name = write_name.encode()
        write_unicode_name = write_encode_name.decode('utf-8')
        delete_name = pk+"_Delete"
        delete_encode_name = delete_name.encode()
        delete_unicode_name = delete_encode_name.decode('utf-8')
        l= [delete_unicode_name,admin_unicode_name,write_unicode_name]
        self.group_required= l
        ##print("the self of dispatcher",self.group_required)

        return super(ProjectQueryDeleteView, self).dispatch(request, *args, **kwargs)

    def post(self,request):
        delet_pks = request.POST.get('delete_pk',None)
        project = request.POST.get('delete_project',None)

        if delet_pks:
            delet_pks = list(delet_pks.split(","))
            delet_pks.pop(0)
            ##print("delete_pks",delet_pks)



            project= Project.objects.get(pk=int(project))



            query_msg = ""
            for pk in delet_pks:
                ##print("the pk is",pk)
                query = ProjectQuery.objects.get(pk=int(pk))
                if  ProjectEndPoint.objects.filter(query=query).exists():
                    pass
                else:
                    query_msg = query_msg+query.query_id
                    delete = ProjectQuery.objects.filter(pk=int(pk)).delete()


            pk = project.pk
            msg = "Query ID / ID's "+query_msg+"Deleted Scuccessfully"

            context = project_details_get(request,pk)
            context['msg']= msg

            template_name='dashboard/project_details.html'

            return render(request,template_name,context)






class DashboardAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = ProjectDashboard.objects.filter(dashboard_for='Public')

        try:
            ##print("the project")
            project_pk = int(self.forwarded.get('project', None))
            ##print("the project",project_pk)

            project = Project.objects.get(pk=project_pk)
            ##print("the project is",project)
        except:
            project=None
        ##print("theq after",qs)
        if project:
            qs = qs.filter(project=project)



        if self.q:
            ##print()
            qs = qs.filter(Q(name__icontains=self.q))
            ##print("filtered qs",qs)
        return qs





class DashboardCreateView(View,LoginRequiredMixin,PermissionRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        pk = kwargs['pk']

        project=Project.objects.get(pk=pk)
        pk= str(project.pk)
        self.login_url = '/customer/login/'
        self.redirect_field_name = 'redirect_to'
        self.template_name='dashboard/index.html'
        admin_name = pk+"_Admin"
        ##print(type(admin_name), admin_name)
        admin_encode_name = admin_name.encode()
        admin_unicode_name = admin_encode_name.decode('utf-8')
        write_name = pk+"_Write"
        ##print(type(write_name), write_name)
        write_encode_name = write_name.encode()
        write_unicode_name = write_encode_name.decode('utf-8')
        delete_name = pk+"_Delete"
        delete_encode_name = delete_name.encode()
        delete_unicode_name = delete_encode_name.decode('utf-8')
        l= [delete_unicode_name,admin_unicode_name,write_unicode_name]
        self.group_required= l
        ##print("the self of dispatcher",self.group_required)

        return super(DashboardCreateView, self).dispatch(request, *args, **kwargs)

    def get(self,request,pk):

        project = Project.objects.get(pk=pk)
        try:
            dashboard = ProjectDashboard.objects.filter(project=project)
        except:
            dashboard=None
        current_site = get_current_site(request)
        site_name = current_site.name
        domain = current_site.domain
        if domain.startswith('127.0.'):
            domain = 'https://'+domain
        else:
            domain = 'https://'+domain
        if Project.objects.filter(pk=project.pk,admin_user=request.user).exists():
            permission="Admin"
        elif ProjectUser.objects.filter(project=project,project_user=request.user).exists():
            user_group = User.objects.get(pk=request.user.pk)

            for g in user_group.groups.all():
                if g.name == str(project.pk)+"_Read":
                    permission="Read"
                elif g.name == str(project.pk)+"_Write":
                    permission="Write"
                elif g.name == str(project.pk)+"_Delete":
                    permission="Delete"
                elif g.name == str(project.pk)+"_Admin":
                    permission="Admin"
        else:
            permission=None

        endpoints = ProjectEndPoint.objects.filter(project=project)
        new_ep_colums ={}
        js_data =end_point_columns(endpoints,project)

        dashboard_form = ProjectDashboardForm(initial={'project':project.pk})
        dashboard_form.fields['user'].queryset = ProjectUser.objects.filter(project=project)
        dashboard_form.fields['dashboard'].queryset = ProjectDashboard.objects.filter(project=project)
        context={'permission':permission,'domain':domain,'project':project,'end_points':endpoints,'dashboard_form':dashboard_form,'dashboard':dashboard,'js_data':js_data}
        return render(request,'dashboard/dashboard_create.html',context)

    def post(self,request,pk):
        ##print("post")


        form = ProjectDashboardForm(request.POST)
        # ##print("testing form")
        # ##print("form invalid",form)
        dashboard_format = request.POST.get('dashboard_format',None)
        print("the dashboard object is",dashboard_format)
        project = Project.objects.get(pk=pk)
        if form.is_valid():
            name = request.POST.get('name',None)
            dashboard =form.cleaned_data['dashboard']
            dashboard_format = request.POST.get('dashboard_format',None)
            dashboard_format = json.loads(dashboard_format)
            ##print("converted dict",dashboard_format)
            additional_email = form.cleaned_data['email_users']
            report_frequency = form.cleaned_data['report_frequency']
            user = form.cleaned_data['user']
            dashboard_for = form.cleaned_data['dashboard_for']

            customer = Customer.objects.get(user=request.user)
            if customer.type == 'Individual':
                dashboard_count = ProjectDashboard.objects.filter(dashboard_admin_user=request.user).count()
            else:
                dashboard_count =0
            if dashboard_count> 1:
                msg= "Not Allowed to Create more than one dashboard"
                project = Project.objects.get(pk=pk)

            else:

                if name:
                    ##print("new dashboard")
                    dashboard = ProjectDashboard.objects.create(project=project,
                                                                    name=name,
                                                                    additional_email=additional_email,
                                                                    dashboard_admin_user=request.user,
                                                                    dashboard_format = dashboard_format,
                                                                    dashboard_for=dashboard_for)

                    for u in user:
                        dashboard.dashboard_users.add(u.project_user)
                    end_point = []
                    if dashboard.dashboard_for == 'Public':

                        hash_str = str(dashboard.pk)+"dashboard"
                        hash_code = str(hash(hash_str))
                        update = ProjectDashboard.objects.filter(pk=dashboard.pk).update(public_shared_code=hash_code)


                    for elem, obj in  dashboard_format.items():

                        if obj['type'] == "end_point":
                            end_point.append(obj['id'])




                    for p in end_point:
                        ep = ProjectEndPoint.objects.get(pk=int(p))
                        ##print("the ep is ",ep)
                        dashboard.end_point.add(ep)

                    dashboard = ProjectDashboard.objects.get(pk=dashboard.pk)


                    data={"msg":'Dashboard creation Successfull'}
                    pk = str(dashboard.pk)
                    return redirect('/project-dashboard/'+pk+'/')
                else:
                    msg={"msg":'Please Fill the Details Befour Submit'}
        else:
            ##print("form invalid",form.errors)
            msg= "There is an error in dashboard creation"
            project = Project.objects.get(pk=pk)
        try:
            dashboard = ProjectDashboard.objects.filter(project=project)
        except:
            dashboard=None
        current_site = get_current_site(request)
        site_name = current_site.name
        domain = current_site.domain
        if domain.startswith('127.0.'):
            domain = 'https://'+domain
        else:
            domain = 'https://'+domain
        if Project.objects.filter(pk=project.pk,admin_user=request.user).exists():
            permission="Admin"
        elif ProjectUser.objects.filter(project=project,project_user=request.user).exists():
            user_group = User.objects.get(pk=request.user.pk)

            for g in user_group.groups.all():
                if g.name == str(project.pk)+"_Read":
                    permission="Read"
                elif g.name == str(project.pk)+"_Write":
                    permission="Write"
                elif g.name == str(project.pk)+"_Delete":
                    permission="Delete"
                elif g.name == str(project.pk)+"_Admin":
                    permission="Admin"
        else:
            permission=None

        endpoints = ProjectEndPoint.objects.filter(project=project)
        js_data =end_point_columns(endpoints,project)
        dashboard_form = ProjectDashboardForm(initial={'project':project.pk})
        dashboard_form.fields['user'].queryset = ProjectUser.objects.filter(project=project)
        dashboard_form.fields['dashboard'].queryset = ProjectDashboard.objects.filter(project=project)
        context={'permission':permission,'msg':msg,'domain':domain,'project':project,'end_points':endpoints,'dashboard_form':dashboard_form,'dashboard':dashboard,'js_data':js_data}
        return render(request,'dashboard/dashboard_create.html',context)

def end_point_columns(endpoints,project):
    metadata = ProjectMetaData.objects.get(project=project)
    ep_columns_operations = {}
    for end_point in endpoints:
        if end_point.sub_df:
            json_st = json.loads(end_point.sub_df)
            json_df = pd.DataFrame(json_st)
            df = json_df.transpose()
            df_columns= df.columns.to_list()

            for key, value in metadata.meta_data.items():
                if key in df_columns:
                    ##print("key",key)
                    if value['dtype'] == 'int':
                        df[key] =pd.to_numeric(df[key])
                        if key in df_columns:
                            df[key] = pd.to_numeric(df[key])
                    elif value['dtype'] == 'float':
                        ##print("final key",key,df[key],df[key].dtypes)
                        df[key] = pd.to_numeric(df[key])
                        if key in df_columns:
                            df[key] = pd.to_numeric(df[key])
                    elif value['dtype'] == 'object':
                        df[key] = df[key].astype(str)
                        if key in df_columns:
                            df[key] = df[key].astype(str)
                    elif value['dtype'] == 'bool':
                        df[key] = df[key].astype(bool)
                        if key in df_columns:
                            df[key] = df[key].astype(bool)
                    elif value['dtype'] == 'DateTime':
                        df[key] =pd.to_datetime(df[key])
                        ##print("the data key",key)
                        if key in df_columns:
                            df[key] = pd.to_datetime(df[key])
        else:
            df = QueryExcecute(end_point.query)
        numbered_columns =df.select_dtypes(include =['number'])
        for column in numbered_columns:
            ep_columns_operations[str(end_point.pk)+","+column+","+"min"] =str(end_point.name)+"_"+column+"_"+"min"
            ep_columns_operations[str(end_point.pk)+","+column+","+"max"] =str(end_point.name)+"_"+column+"_"+"max"
            ep_columns_operations[str(end_point.pk)+","+column+","+"mean"] =str(end_point.name)+"_"+column+"_"+"mean"
            ep_columns_operations[str(end_point.pk)+","+column+","+"std"] =str(end_point.name)+"_"+column+"_"+"std"

    js_data = json.dumps(ep_columns_operations)
    return js_data






class EndPointAlgorithmView(View,LoginRequiredMixin,PermissionRequiredMixin):

        def post(self,request,pk):
            error = False
            query_object = request.POST.get('ml_query_object',None)

            if not query_object:
                error=True

            elif query_object:
                query_object = ast.literal_eval(query_object)
            ##print("the query object is",query_object,error)
            feature_column_list = request.POST.getlist('ml_feature_select')
            ##print("the feature list is ",feature_column_list)

            target_list =request.POST.getlist('ml_target')

            no_of_groups = request.POST.get('no_of_groups',None)
            ##print("the no_of_groups",no_of_groups)
            # no_of_groups = 3
            if len(target_list)>0:

                y_column = target_list[0]
            else:
                y_column = None
            type_of_prediction = request.POST['type_of_prediction']
            ml_name = request.POST.get('ml_name',None)
            ml_frequency = request.POST.get('ml_frequency',None)
            project_query = ProjectQuery.objects.get(pk=pk)
            project= Project.objects.get(pk=project_query.project.pk)
            piqu,created = ProjectBillingPrms.objects.get_or_create(project=project)
            ##print("error",error,ml_name,ml_frequency)
            if ml_name and ml_frequency:

                form = ProjectEndPointForm(initial={'end_point_name':ml_name,'frequency':ml_frequency})
            else:
                form = ProjectEndPointForm()
                error=True

            ##print("error",error)
            if not y_column and not no_of_groups:
                error=True
            ##print("error",error)
            if not y_column and type_of_prediction == 'Linear':
                error=True

            ##print("befpre ",error)
            update = ProjectBillingPrms.objects.filter(project=project).update(query_count=piqu.query_count+1)
            dashboard_form = ProjectDashboardForm(initial={'project':project.pk})
            dashboard_form.fields['user'].queryset = ProjectUser.objects.filter(project=project)
            dashboard_form.fields['dashboard'].queryset = ProjectDashboard.objects.filter(project=project)
            if Project.objects.filter(pk=project.pk,admin_user=request.user).exists():
                permission="Admin"
            elif ProjectUser.objects.filter(project=project,project_user=request.user).exists():
                user_group = User.objects.get(pk=request.user.pk)

                for g in user_group.groups.all():
                    if g.name == str(project.pk)+"_Read":
                        permission="Read"
                    elif g.name == str(project.pk)+"_Write":
                        permission="Write"
                    elif g.name == str(project.pk)+"_Delete":
                        permission="Delete"
                    elif g.name == str(project.pk)+"_Admin":
                        permission="Admin"

            else:
                permission = None
            today= datetime.now().date()
            df = QueryExcecute(project_query)
            df_columns = df.columns.tolist()
            metadata = ProjectMetaData.objects.get(project=project_query.project)
            if metadata.date_column_name and metadata.date_column_name in df_columns:
                df[metadata.date_column_name] = df[metadata.date_column_name].astype(str)
        
            sub_df = df.to_json(orient='index')
            ml_df = df
            columns = df.columns.tolist()
            ml_columns_list = target_list + feature_column_list
            ##print("the ml column list",ml_columns_list)
            for column in columns:
                if column not in ml_columns_list:
                    del ml_df[column]
            ##print("the ml df ",ml_df)

            ml_string_columns = ml_df.select_dtypes(include =['object','bool'])
            ##print("the objecttype of ml_df",ml_string_columns )
            meta_data = ProjectMetaData.objects.get(project=project)
            if meta_data.date_column_name:
                if meta_data.date_column_name in ml_columns_list:
                    error=True


            for column in ml_string_columns:

                try:
                    ##print('except',column)
                    if df[column].dtypes  == np.bool:
                        pass

                    else:
                        ml_df[column] = ml_df[column].astype('category')
                        column_count = ml_df[column].notnull().count()
                        unique_column_count = ml_df[column].nunique()
                        # if column_count == unique_column_count:
                        #     ##print("column,count,unique_column_count",column_count,unique_column_count)
                        #     # error=True
                        # else:
                        #     pass


                except:
                    ml_df[column] = ml_df[column].astype(float)
                    ##print('try',column)




            if error:
                df = QueryExcecute(project_query)
                ##print("the original_df ",df)
                df_rows =df.shape[0]
                df_column_count=  df.shape[1]
                msg = "The Choosen Features has Sting data type so please  choose another"
                res_df__table_content = df.to_html(classes="table table-striped tableFixHead",border="0")
                # t_df = res_df.T
                # ##print("the visulization columns",df)
                string_columns = df.select_dtypes(include ='object')
                number_columns = df.select_dtypes(include=['float64','int'])
                ##print("the numbered columns are",number_columns)
                df_columns     = df.columns.tolist()

                if  project_query.plot and project_query.plot.plot_type:
                    plot_obj = QueryPlot(df,project_query.pk)
                    div = plot_obj.plot(project_query.plot)

                else:
                    # fig = px.scatter_matrix(df)
                    # div = opy.plot(fig, auto_open=False, output_type='div')
                    div = True
                project = Project.objects.get(pk=project_query.project.pk)
                ##print(df_columns,string_columns)
                non_query_object = {}
                if query_object:
                    non_query_object = {}
                    if all('query' not in elem.values() for elem in query_object.values()):
                        non_query_object['query']=True
                    if all('table' not in elem.values() for elem in query_object.values()):
                        non_query_object['table']=True
                    if all('plot' not in elem.values() for elem in query_object.values()):
                        non_query_object['plot']=True
                    if all('ml' not in elem.values() for elem in query_object.values()):
                        non_query_object['ml']=True
                    if all('cp' not in elem.values() for elem in query_object.values()):
                        non_query_object['cp']=True
                        ##print(non_query_object)

                    context={'msg':msg,'form':form,'df_rows':df_rows,'df_column_count':df_column_count,'project':project,'query':res_df__table_content,'dashboard_form':dashboard_form,'permission':permission,'graph':div,'project_query':project_query,'df_columns':df_columns,'string_columns':string_columns,'query_object':query_object,'non_query_object':non_query_object}
                # ##print('the context',context)
                else:
                    context={'msg':msg,'form':form,'df_rows':df_rows,'df_column_count':df_column_count,'project':project,'query':res_df__table_content,'dashboard_form':dashboard_form,'permission':permission,'graph':div,'project_query':project_query,'df_columns':df_columns,'string_columns':string_columns,'query_object':None,'non_query_object':non_query_object}
                return render(request,'dashboard/project_query.html',context)
            else:

                target=y_column
                for column in ml_string_columns:


                    if ml_df[column].dtypes  == np.bool:
                        column_name = column +'_cat'
                        if y_column == column:
                            target = column_name

                        ml_df[column_name] = pd.get_dummies(ml_df[column], drop_first=True)
                        del ml_df[column]

                    else:
                        try:
                            ml_df[column] = ml_df[column].astype(float)
                        except:

                            column_name = column +'_cat'
                            if y_column == column:
                                target = column_name

                            ml_df[column] = df[column].astype('category')
                            ##print("columns ",column)
                            ml_df[column_name] = ml_df[column].cat.codes
                            del ml_df[column]
                if project_query.plot:

                    plot =Plot.objects.create(plot_type=project_query.plot.plot_type,
                                                    x_axis=project_query.plot.x_axis,
                                                    y_axis=project_query.plot.y_axis,
                                                    z_axis=project_query.plot.z_axis,
                                                    color=project_query.plot.color,
                                                    legend=project_query.plot.legend,
                                                    values=project_query.plot.values,
                                                    names=project_query.plot.names,
                                                    size=project_query.plot.size,
                                                    hover_name=project_query.plot.hover_name,
                                                    orientation=project_query.plot.orientation,
                                                    facet_col=project_query.plot.facet_col)


                    customer = Customer.objects.get(user=request.user)
                    end_point_count = ProjectEndPoint.objects.filter(project=project).count()
                    ##print("EndPointPlot create")
                    if customer.type =='Individual':
                        if end_point_count >=5:
                            pk = project_query.project.pk
                            context= single_project_details(request,pk)
                            template_name='dashboard/single_project_details.html'
                            context['msg'] = "Project has Exceeded The EndPoint"
                            template_name='dashboard/single_project_details.html'
                            return render(request,template_name,context)

                        else:
                            end_point,created = ProjectEndPoint.objects.get_or_create(query=project_query,
                                                                              project=project,
                                                                              name=ml_name,
                                                                              sub_df_frequency=ml_frequency,
                                                                              plot=plot,
                                                                              sub_df =sub_df,
                                                                              user=request.user,
                                                                              alignment_object=query_object
                                                                              )
                    else:
                        project_usage = ProjectBillingPrms.objects.get(project=project)
                        total_end_point = project_usage.end_point +5
                        end_points = ProjectEndPoint.objects.filter(project=project).count()
                        if end_points<total_end_point:
                            end_point,created = ProjectEndPoint.objects.get_or_create(query=project_query,
                                                                              project=project,
                                                                              name=ml_name,
                                                                              sub_df_frequency=ml_frequency,
                                                                              plot=plot,
                                                                              sub_df =sub_df,
                                                                              user=request.user,
                                                                              alignment_object=query_object
                                                                              )
                        else:
                            pk =project_query.project.pk
                            context= single_project_details(request,pk)
                            context['msg'] = "Project has Exceeded The EndPoint Limit"
                            template_name='dashboard/single_project_details.html'
                            return render(request,template_name,context)



                else:
                    customer = Customer.objects.get(user=request.user)
                    end_point_count = ProjectEndPoint.objects.filter(project=project).count()
                    ##print("EndPointPlot create")
                    if customer.type =='Individual':
                        if end_point_count >5:
                            pk =project_query.project.pk
                            context= single_project_details(request,pk)
                            context['msg'] = "Project has Exceeded The EndPoint Limit"
                            template_name='dashboard/single_project_details.html'
                            return render(request,template_name,context)
                        else:
                            end_point,created = ProjectEndPoint.objects.get_or_create(query=project_query,

                                                                              project=project,
                                                                              name=ml_name,
                                                                              sub_df_frequency=ml_frequency,
                                                                              sub_df =sub_df,
                                                                              user=request.user,
                                                                              alignment_object=query_object
                                                                              )
                    else:
                        project_usage = ProjectBillingPrms.objects.get(project=project)
                        total_end_point = project_usage.end_point +5
                        end_points = ProjectEndPoint.objects.filter(project=project).count()
                        if end_points<total_end_point:
                            end_point,created = ProjectEndPoint.objects.get_or_create(query=project_query,
                                                                              project=project,
                                                                              name=ml_name,
                                                                              sub_df_frequency=ml_frequency,

                                                                              sub_df =sub_df,
                                                                              user=request.user,
                                                                              alignment_object=query_object
                                                                              )
                        else:
                            pk = project_query.project.pk
                            context= single_project_details(request,pk)
                            context['msg'] = "Project has Exceeded The EndPoint Limit"
                            template_name='dashboard/single_project_details.html'
                            return render(request,template_name,context)

                if not y_column and no_of_groups:
                    ml_obj = Kmeans(ml_df)
                    data = ml_obj.kmeans_algo(no_of_groups,end_point)
                    # feature = str(feature_select_list)
                    ##print("the feature list",feature_column_list)
                    feature = ''
                    for c in feature_column_list:
                        feature = feature+','+c
                    feature= feature[1:]



                    end_point_algorithm = EndPointAlgorithm.objects.create(
                                                                            feature= feature,
                                                                            type_of_prediction= 'Classification',
                                                                            y_factor = y_column,
                                                                            no_of_group=no_of_groups,
                                                                            model_id = data['model_file_name'],
                                                                            model_size = data['file_size']
                                                                            )
                    update_endpoint = ProjectEndPoint.objects.filter(pk=end_point.pk).update(algorithm=end_point_algorithm)

                elif y_column and type_of_prediction == 'Classification':
                    ##print("the final")
                    ml_obj = AutoMl(ml_df)
                    ##print("the target is ",target)
                    data = ml_obj.auto_algo(target,end_point)
                    # feature = str(feature_column_list)
                    feature = ''
                    for c in feature_column_list:
                        feature = feature+','+c
                    feature= feature[1:]
                    accuracy = data['accuracy']
                    accuracy = str(round(accuracy,3))
                    end_point_algorithm = EndPointAlgorithm.objects.create(
                                                                            feature=feature ,
                                                                            accuracy =accuracy,
                                                                            type_of_prediction= 'Classification',
                                                                            y_factor = y_column,
                                                                            model_id = data['model_file_name'],
                                                                            model_size = data['file_size']
                                                                            )
                    ##print("the model file name",data['model_file_name'],)
                    update_endpoint = ProjectEndPoint.objects.filter(pk=end_point.pk).update(algorithm=end_point_algorithm)
                    # end_point = ProjectEndPoint.objects.get(pk=end_point.pk)
                    # l = ['location', 'Winner', 'title_bout', 'weight_class']
                    # l2 = [[1,2,1,1]]
                    # test_df =pd.DataFrame(l2,columns=l)
                    # ##print("the test df",test_df)
                    # ml_obj = Linear(test_df)s
                    # data = ml_obj.prediction_algo(end_point.algorithm.model_id)
                    # ##print("the Preditions",data)
                elif y_column and type_of_prediction == 'Linear':
                    ml_obj = Linear(ml_df)
                    data = ml_obj.linear_model(target,end_point)
                    # feature = str(feature_column_list)
                    feature = ''
                    for c in feature_column_list:
                        feature = feature+','+c
                    feature= feature[1:]
                    accuracy = data['accuracy']
                    for key, value in accuracy.items():
                        val = round(value,3)
                        accuracy[key] = val
                    end_point_algorithm = EndPointAlgorithm.objects.create(
                                                                            feature= feature,
                                                                            accuracy = accuracy,
                                                                            type_of_prediction= 'Linear',
                                                                            y_factor = y_column,
                                                                            model_id = data['model_file_name'],
                                                                            model_size = data['file_size']
                                                                            )
                    update_endpoint = ProjectEndPoint.objects.filter(pk=end_point.pk).update(algorithm=end_point_algorithm)
                end_point_pk = str(end_point.pk)
                # end_point = ProjectEndPoint.objects.get(pk=end_point.pk)
                # l = ['location', 'Winner', 'title_bout', 'weight_class']
                # l2 = [[1,2,1,1]]
                # test_df =pd.DataFrame(l2,columns=l)
                # ##print("the test df",test_df)
                # ml_obj = Linear(test_df)
                # data = ml_obj.prediction_algo(end_point.algorithm.model_id)
                # ##print("the Preditions",data)
                return redirect('/endpoint/'+end_point_pk+'/')









            # if EndPointAlgorithm.objects.filter(algorithm =algorithm,query=dashboard_query,feature=feture_column,y_factor=y_column).exists():
            #     data = {'msg':"sucess"}
            # else:
            #     ##print("creating the algorithm")
            #     algorithm, created = EndPointAlgorithm.objects.get_or_create(algorithm =algorithm,query=dashboard_query,feature=feture_column,y_factor=y_column)

            #     data = {'algorithm':algorithm.algorithm,
            #                 'feature':algorithm.feature,
            #                 'y_column':algorithm.y_factor,
            #             'pk':algorithm.pk}
            # return JsonResponse(data, safe=False)


class EndPointAlgorithmUpdateView(View,LoginRequiredMixin,PermissionRequiredMixin):

        def post(self,request,pk):
            error = False
            query_object = request.POST.get('ml_query_object',None)
            print("the ml object",query_object,request.POST)

            if not query_object:
                print("no query object")
                error=True

            elif query_object:
                query_object = ast.literal_eval(query_object)
            ##print("the query object is",query_object,error)
            feature_column_list = request.POST.getlist('ml_feature_select')
            ##print("the feature list is ",feature_column_list)

            target_list =request.POST.getlist('ml_target')

            no_of_groups = request.POST.get('no_of_groups',None)
            ##print("the no_of_groups",no_of_groups)
            # no_of_groups = 3
            if len(target_list)>0:

                y_column = target_list[0]
            else:
                print("thre y error ")
                y_column = None
            type_of_prediction = request.POST['type_of_prediction']
            ml_name = request.POST.get('ml_name',None)
            ml_frequency = request.POST.get('ml_frequency',None)
            end_point = ProjectEndPoint.objects.get(pk=pk)
            project  = Project.objects.get(pk=end_point.project.pk)
            p_query = end_point.query
            form = ProjectEndPointForm(initial={'end_point_name':end_point.name,'frequency':end_point.sub_df_frequency})
            ep_form = ProjectEndPointForm(initial={'end_point_name':end_point.name,'frequency':end_point.sub_df_frequency})
            piqu,created = ProjectBillingPrms.objects.get_or_create(project=end_point.project)

            update = ProjectBillingPrms.objects.filter(project=end_point.project).update(query_count=piqu.query_count+1)
            dashboard_form = ProjectDashboardForm(initial={'project':p_query.project.pk})
            dashboard_form.fields['user'].queryset = ProjectUser.objects.filter(project=p_query.project)
            dashboard_form.fields['dashboard'].queryset = ProjectDashboard.objects.filter(project=p_query.project)
            if Project.objects.filter(pk=p_query.project.pk,admin_user=request.user).exists():
                permission="Admin"
            elif ProjectUser.objects.filter(project=p_query.project,project_user=request.user).exists():
                user_group = User.objects.get(pk=request.user.pk)

                for g in user_group.groups.all():
                    if g.name == str(p_query.project.pk)+"_Read":
                        permission="Read"
                    elif g.name == str(p_query.project.pk)+"_Write":
                        permission="Write"
                    elif g.name == str(p_query.project.pk)+"_Delete":
                        permission="Delete"
                    elif g.name == str(p_query.project.pk)+"_Admin":
                        permission="Admin"
            else:
                permission=None
            if ml_name and ml_frequency:

                form = ProjectEndPointForm(initial={'end_point_name':ml_name,'frequency':ml_frequency})
            else:
                print("no data")
                form = ProjectEndPointForm()
                error=True

            ##print("error",error)
            if not y_column and not no_of_groups:
                print("no y and groups")
                error=True
            ##print("error",error)
            if not y_column and type_of_prediction == 'Linear':
                print("no y and linear")
                error=True


            today= datetime.now().date()
            if not end_point.sub_df:

                df = QueryExcecute(end_point.query)
            else:
                ##print("loding from json data")
                json_st = json.loads(end_point.sub_df)
                # ##print("THE TYPE OF JSON FILE<",type(json_st))
                json_df = pd.DataFrame(json_st)
                df = json_df.transpose()

            ml_df = df
            ml_columns_list = target_list + feature_column_list
            columns =  df.columns.tolist()
            ##print("the ml column list",ml_columns_list)
            for column in columns:
                if column not in ml_columns_list:
                    del ml_df[column]
            ##print("the ml df ",ml_df)

            ml_string_columns = ml_df.select_dtypes(include =['object','bool'])
            ##print("the objecttype of ml_df",ml_string_columns )
            meta_data = ProjectMetaData.objects.get(project=project)
            if meta_data.date_column_name:
                if meta_data.date_column_name in ml_columns_list:
                    print("date error")
                    error=True


            for column in ml_string_columns:

                try:
                    ##print('except',column)
                    if df[column].dtypes  == np.bool:
                        pass

                    else:
                        ml_df[column] = ml_df[column].astype('category')
                        column_count = ml_df[column].notnull().count()
                        unique_column_count = ml_df[column].nunique()
                        # if column_count == unique_column_count:
                        #     ##print("column,count,unique_column_count",column_count,unique_column_count)
                        #     error=True
                        #     print("unique error ")
                        # else:
                        #     pass


                except:
                    ml_df[column] = ml_df[column].astype(float)
                    ##print('try',column)




            if error:
                print("no error passwesd")
                if not end_point.sub_df:

                    df = QueryExcecute(end_point.query)
                else:

                    ##print("the df is ",df)
                    sub_df = df.to_json(orient='index')

                res_df__table_content = df.to_html(classes="table table-striped tableFixHead",border="0")
                # t_df = res_df.T
                # ##print("the visulization columns",df)
                df_columns     = df.columns.tolist()
                for column in df_columns:
                    try:
                        df[column] = pd.to_numeric(df[column])
                    except:
                        pass
                string_columns = df.select_dtypes(include ='object')
                df_columns     = df.columns.tolist()
                row_count = df.shape[1]
                column_count = df.shape[0]
                if end_point.plot and end_point.plot.plot_type:
                    end_point_obj = EndPointPlot(df,end_point.pk)
                    plot = Plot.objects.get(pk= end_point.plot.pk)
                    div = end_point_obj.plot(plot)
                else:
                    # fig = px.scatter_matrix(df)
                    # div = opy.plot(fig, auto_open=False, output_type='div')
                    div = True
                non_query_object = {}
                if end_point.alignment_object:


                    non_query_object = {}
                    if all('query' not in elem.values() for elem in end_point.alignment_object.values()):
                        non_query_object['query']=True
                    if all('table' not in elem.values() for elem in end_point.alignment_object.values()):
                        non_query_object['table']=True
                    if all('plot' not in elem.values() for elem in end_point.alignment_object.values()):
                        non_query_object['plot']=True
                    if all('ml' not in elem.values() for elem in end_point.alignment_object.values()):
                        non_query_object['ml']=True
                    if all('cp' not in elem.values() for elem in end_point.alignment_object.values()):
                        non_query_object['cp']=True
                    ##print(non_query_object)
                if end_point.algorithm:
                    features_text = end_point.algorithm.feature
                    features_text = features_text.replace('[', '')
                    features_text = features_text.replace(']', '')
                    features      = features_text.split(',')
                    test_l =[]
                    for column in features:

                        test_l.append(column)




                    target   = end_point.algorithm.y_factor
                    model_id = end_point.algorithm.model_id
                    if end_point.algorithm.type_of_prediction == 'Linear':
                        accuracy = ast.literal_eval(end_point.algorithm.accuracy)
                        MAE = accuracy['MAE']
                        MSE = accuracy['MSE']
                        RMSE = accuracy['RMSE']
                        accuracy_list = {'MAE':MAE,'MSE':MSE,'RMSE':RMSE}
                    else:
                        accuracy_list={'accuracy':end_point.algorithm.accuracy}
                else:
                    features = None
                    target = None
                    model_id = None
                    accuracy_list = None


                context = {'features':features,'target':target,'model_id':model_id,'accuracy_list':accuracy_list,'features':features,'target':target,'model_id':model_id,'accuracy_list':accuracy_list,'graph':div,'ep_form':ep_form,'end_point':end_point,'query':res_df__table_content,'permission':permission,'row_count':row_count,'column_count':column_count,'form':dashboard_form,'string_columns':string_columns,'df_columns':df_columns,'non_query_object':non_query_object}
                return render(request,'dashboard/project_end_point_edit.html',context)
            else:
                print("no error")
                target=y_column
                for column in ml_string_columns:


                    if ml_df[column].dtypes  == np.bool:
                        column_name = column +'_cat'
                        if y_column == column:
                            target = column_name

                        ml_df[column_name] = pd.get_dummies(ml_df[column], drop_first=True)
                        del ml_df[column]

                    else:
                        try:
                            ml_df[column] = ml_df[column].astype(float)
                        except:

                            column_name = column +'_cat'
                            if y_column == column:
                                target = column_name

                            ml_df[column] = df[column].astype('category')
                            ##print("columns ",column)
                            ml_df[column_name] = ml_df[column].cat.codes
                            del ml_df[column]
                update = ProjectEndPoint.objects.filter(pk=pk).update(name=ml_name,sub_df_frequency=ml_frequency,alignment_object=query_object)

                if not y_column and no_of_groups:
                    ml_obj = Kmeans(ml_df)
                    data = ml_obj.kmeans_algo(no_of_groups,end_point)
                    # feature = str(feature_select_list)
                    feature = ''
                    for c in feature_column_list:
                        feature = feature+','+c
                    feature= feature[1:]



                    end_point_algorithm = EndPointAlgorithm.objects.create(
                                                                            feature= feature_column_list,
                                                                            type_of_prediction= 'Classification',
                                                                            y_factor = y_column,
                                                                            no_of_group=no_of_groups,
                                                                            model_id = data['model_file_name'],
                                                                            )
                    update_endpoint = ProjectEndPoint.objects.filter(pk=end_point.pk).update(algorithm=end_point_algorithm)

                elif y_column and type_of_prediction == 'Classification':
                    ml_obj = AutoMl(ml_df)
                    data = ml_obj.auto_algo(target,end_point)
                    # feature = str(feature_column_list)
                    feature = ''
                    for c in feature_column_list:
                        feature = feature+','+c
                    feature= feature[1:]
                    accuracy = data['accuracy']
                    accuracy = str(round(accuracy,3))
                    end_point_algorithm = EndPointAlgorithm.objects.create(
                                                                            feature=feature ,
                                                                            accuracy = accuracy,
                                                                            type_of_prediction= 'Classification',
                                                                            y_factor = y_column,
                                                                            model_id = data['model_file_name'],
                                                                            )
                    ##print("the model file name",data['model_file_name'],)
                    update_endpoint = ProjectEndPoint.objects.filter(pk=end_point.pk).update(algorithm=end_point_algorithm)
                    # end_point = ProjectEndPoint.objects.get(pk=end_point.pk)
                    # l = ['location', 'Winner', 'title_bout', 'weight_class']
                    # l2 = [[1,2,1,1]]
                    # test_df =pd.DataFrame(l2,columns=l)
                    # ##print("the test df",test_df)
                    # ml_obj = Linear(test_df)s
                    # data = ml_obj.prediction_algo(end_point.algorithm.model_id)
                    # ##print("the Preditions",data)
                elif y_column and type_of_prediction == 'Linear':
                    ml_obj = Linear(ml_df)
                    data = ml_obj.linear_model(target,end_point)
                    # feature = str(feature_column_list)
                    feature = ''
                    for c in feature_column_list:
                        feature = feature+','+c
                    feature= feature[1:]
                    accuracy = data['accuracy']
                    for key, value in accuracy.items():
                        val = round(value,3)
                        accuracy[key] = val
                    end_point_algorithm = EndPointAlgorithm.objects.create(
                                                                            feature= feature,
                                                                            accuracy = accuracy,
                                                                            type_of_prediction= 'Linear',
                                                                            y_factor = y_column,
                                                                            model_id = data['model_file_name'],
                                                                            )
                    update_endpoint = ProjectEndPoint.objects.filter(pk=end_point.pk).update(algorithm=end_point_algorithm)
                end_point_pk = str(end_point.pk)
                # end_point = ProjectEndPoint.objects.get(pk=end_point.pk)
                # l = ['location', 'Winner', 'title_bout', 'weight_class']
                # l2 = [[1,2,1,1]]
                # test_df =pd.DataFrame(l2,columns=l)
                # ##print("the test df",test_df)
                # ml_obj = Linear(test_df)
                # data = ml_obj.prediction_algo(end_point.algorithm.model_id)
                # ##print("the Preditions",data)
                return redirect('/endpoint/'+end_point_pk+'/')



class MLDeleteView(GroupRequiredMixin,LoginRequiredMixin,View):
    def dispatch(self, request, *args, **kwargs):
        pk = kwargs['pk']

        query= ProjectEndPoint.objects.get(pk=pk)
        project=Project.objects.get(pk=query.project.pk)

        pk= str(project.pk)
        self.login_url = '/customer/login/'
        self.redirect_field_name = 'redirect_to'
        self.template_name='dashboard/index.html'
        admin_name = pk+"_Admin"
        ##print(type(admin_name), admin_name)
        admin_encode_name = admin_name.encode()
        admin_unicode_name = admin_encode_name.decode('utf-8')
        write_name = pk+"_Write"
        ##print(type(write_name), write_name)
        write_encode_name = write_name.encode()
        write_unicode_name = write_encode_name.decode('utf-8')
        read_name = pk+"_Read"
        ##print(type(read_name), read_name)
        read_encode_name = read_name.encode()
        read_unicode_name = read_encode_name.decode('utf-8')
        delete_name = pk+"_Delete"
        ##print(type(delete_name), delete_name)
        delete_encode_name = delete_name.encode()
        delete_unicode_name = delete_encode_name.decode('utf-8')
        l =[delete_unicode_name,write_unicode_name,admin_unicode_name,read_unicode_name]
        self.group_required= l
        ##print("the self of dispatcher",self.group_required)

        return super(MLDeleteView, self).dispatch(request, *args, **kwargs)
    def post(self,request,pk):
        end_point = ProjectEndPoint.objects.get(pk=pk)
        ml_obj = request.POST['delete_ml_obj']
        if ml_obj:
            ml_obj = ast.literal_eval(ml_obj)
        file_name = end_point.algorithm.model_id
        file_exists = default_storage.exists(file_name)
        if file_exists:
            default_storage.delete(file_name)

        # delete = EndPointAlgorithm.objects.filter(pk=end_point.algorithm.pk).delete()
        end_point_update = ProjectEndPoint.objects.filter(pk=pk).update(algorithm=None,alignment_object=ml_obj)
        end_point = ProjectEndPoint.objects.get(pk=pk)
        pk = str(end_point.pk)
        return redirect('/endpoint/'+pk+'/edit/')

class DashboardQueryAlgorithmDeleteView(View,LoginRequiredMixin,PermissionRequiredMixin):

        def post(self,request,pk):
            # delete = EndPointAlgorithm.objects.filter(pk=pk).delete()

            data = {'msg':"success"}
            return JsonResponse(data, safe=False)


class DashboardMultipleQueryCreate(View,LoginRequiredMixin,PermissionRequiredMixin):
    def post(self,request):
        form = ProjectDashboardForm(request.POST)
        if form .is_valid():
            ##print("form valid")

            name = request.POST.get('dashboard_title',None)

            dashboard =form.cleaned_data['dashboard']
            additional_email = form.cleaned_data['email_users']
            report_frequency = form.cleaned_data['report_frequency']
            comment = request.POST.get('dashboard_comment',None)
            user = form.cleaned_data['user']
            end_point = form.cleaned_data['end_point']
            test_end_point = request.POST.get('end_point',None)
            test_user = request.POST.get('user',None)
            dashboard_type = request.POST.get('dashboard_type',None)
            if not test_user:
                test_user = request.POST.getlist('users[]', None)
                ##print("the test users are",test_user)
            if not test_end_point:
                test_end_point = request.POST.getlist('end_point[]', None)

            if dashboard and dashboard_type =='ADDON':

                ##print("dashboard exists")
                dashboard = ProjectDashboard.objects.get(pk=dashboard.pk)
                if test_user:
                    for  i in test_user:
                        user = User.objects.get(pk=int(i))
                        dashboard.dashboard_users.add(user)
                if test_end_point:
                    for p in test_end_point:
                        ep = ProjectEndPoint.objects.get(pk=int(p))
                        dashboard.end_point.add(ep)

                dashboard = ProjectDashboard.objects.get(pk=dashboard.pk)
                pk= str(dashboard.pk)
                data={"msg":'Dashboard Updated successfully'}
                return JsonResponse(data)

            elif not dashboard and dashboard_type =='ADDON':
                data={"msg":'Please Select the Dashboard to Update'}
                return JsonResponse(data)
            # if dashboard_query.start_date:

            #     start_date = dashboard_query.start_date
            # else:
            #     start_date = None
            # if dashboard_query.end_date:

            #     end_date   = dashboard_query.end_date
            # else:
            #     end_date = None
            # if dashboard_query.expected_range:

            #     frequency = dashboard_query.expected_range
            # else:
            #     frequency=None
            # if dashboard_query.group_query:
            #     grouping_colums = list(dashboard_query.group_query.split(","))
            # else:
            #     grouping_colums = None
            # if dashboard_query.aggregation_value:
            #     value_columns = list(dashboard_query.aggregation_value.split(","))
            #         # ##print("the splited value columns are",value_columns)
            # else:
            #     value_columns = None



            # if dashboard_query.aggregation_query:
            #     aggregation = ast.literal_eval(dashboard_query.aggregation_query)
            # else:
            #     aggregation = None

            # project_meta = ProjectMetaData.objects.get(project=dashboard_query.project)
            # if project_meta.date_column_name:
            #     date_field = project_meta.date_column_name
            #

            # if dashboard_query.where_query:
            #     res_df = query.subset(dashboard_query,dashboard_query.project.pk,frequency,1,start_date=start_date,end_date=end_date,grouping_columns=grouping_colums,where=dashboard_query.where_query,aggregation=aggregation,date_column=date_field)
            # else:
            #     res_df = query.subset(dashboard_query,dashboard_query.project.pk,frequency,1,start_date=start_date,end_date=end_date,grouping_columns=grouping_colums,aggregation=aggregation,date_column=date_field)
            # if grouping_colums:
            #     pv = res_df.stack().reset_index()
            # else:
            #     pv_df = res_df.transpose()
            #     pv = pv_df.reset_index()
            # # t_df = res_df.T
            # # ##print("the visulization columns",pv)

            # df_columns     = pv.columns.tolist()

            # data = {'df_columns':df_columns,'query':dashboard_query.pk}
            # return JsonResponse(data, safe=False)
        else:
            pass
            ##print("form errors",form.errors)
class MultipleQueryDashbordView(View,LoginRequiredMixin,PermissionRequiredMixin):
    def post(self,request,pk):
        template_name='dashboard/project_dashboard.html'

        project_query = DashboardQuery.objects.get(pk=pk)
        dashboard=ProjectDashboard.objects.get(pk=project_query.dashboard.pk)
        dashboard_queries = DashboardQuery.objects.filter(dashboard=dashboard)
        plot_graphs ={}
        query_results ={}
        if Project.objects.filter(pk=dashboard.project.pk,admin_user=request.user).exists():
            permission="Admin"
        elif ProjectUser.objects.filter(project=dashboard.project,project_user=request.user).exists():
            user =ProjectUser.objects.get(project=dashboard.project,project_user=request.user)
            if user.permission.name == 'Project Read':
               permission="Read"
            elif user.permission.name == 'Project Read Write':
               permission="Write"
            elif user.permission.name == 'Project Read Write Delete':
               permission="Delete"
            elif user.permission.name == 'Admin':
               permission="Admin"
        else:
            pass
        for p_query in dashboard_queries:
            if p_query.start_date:

                start_date = project_query.start_date
                from_date_select = project_query.start_date_select

                date = start_date.split('-')
                if len(date)==1:
                    if from_date_select == 'day':
                        start_date =today -timedelta(days=int(date[0]))
                    elif from_date_select == 'week':
                        start_date =today -timedelta(days=7*int(date[0]))
                    elif from_date_select == 'month':
                        start_date =today -timedelta(int(date[0])*365/12)
                    elif from_date_select == 'year':
                        start_date =today -timedelta(int(date[0])*365)

            else:
                start_date = None
            if p_query.end_date:

                end_date   = p_query.end_date
                to_date_select = project_query.end_date_select
                date = end_date.split('-')
                if len(date)==1:
                    if to_date_select == 'day':
                        end_date =today -timedelta(days=int(date[0]))
                    elif to_date_select == 'week':
                        end_date =today -timedelta(days=int(7*date[0]))
                    elif to_date_select == 'month':
                        end_date =today -timedelta(int(date[0])*365/12)
                    elif to_date_select == 'year':
                        end_date =today -timedelta(int(date[0])*365)
                    elif to_date_select == 'today':
                        end_date =today
            else:
                end_date = None
            if p_query.expected_range:

                frequency = p_query.expected_range
            else:

                frequency=None
            if p_query.group_query:
                grouping_colums = list(p_query.group_query.split(","))
            else:
                grouping_colums = None
            if p_query.aggregation_value:
                value_columns = list(p_query.aggregation_value.split(","))
                # ##print("the splited value columns are",value_columns)
            else:
                value_columns = None



            if p_query.aggregation_query:
                aggregation = ast.literal_eval(p_query.aggregation_query)
            else:
                aggregation = None

            project_meta = ProjectMetaData.objects.get(project=p_query.project)
            if project_meta.date_column_name:
                date_field = project_meta.date_column_name
            else:
                date_field=None


            if p_query.where_query:
                res_df = query.subset(p_query.project.pk,frequency,1,start_date=start_date,end_date=end_date,grouping_columns=grouping_colums,where=p_query.where_query,aggregation=aggregation,date_column=date_field)
            else:
                res_df = query.subset(p_query.project.pk,frequency,1,start_date=start_date,end_date=end_date,grouping_columns=grouping_colums,aggregation=aggregation,date_column=date_field)


            # ##print("the columns of pivot table are ",res_df.columns.tolist())
            project_meta = ProjectMetaData.objects.get(project=p_query.project)
            if project_meta.date_column_name:
                date_field = project_meta.date_column_name
            else:
                date_field=None
            ##print("final df after grouping is ",res_df)
            if date_field:
                if not p_query.where_query and not grouping_colums and not aggregation :
                    df = res_df


                elif p_query.where_query and not grouping_colums and not aggregation :
                    df = res_df

                elif p_query.where_query  and grouping_colums and not aggregation  :
                    ##print("no aggregation with grouping")
                    df = res_df
                elif p_query.where_query  and grouping_colums and  aggregation and frequency :
                    ##print("no aggregation with grouping")
                    df =  res_df.stack().reset_index()
                elif p_query.where_query  and grouping_colums and  aggregation and not frequency :
                    ##print("no aggregation with grouping")
                    df =  res_df.reset_index()
                elif  not p_query.where_query  and not grouping_colums and not aggregation and  frequency :
                    ##print("no aggregation with grouping")
                    df =  res_df
                elif p_query.where_query  and  not grouping_colums  and  aggregation and frequency:
                    ##print("aggregation with grouping")
                    pv_df = res_df.transpose()
                    df = pv_df.reset_index()
                elif not grouping_colums  and  aggregation and frequency:
                    ##print("aggregation with grouping")
                    pv_df = res_df.transpose()
                    df = pv_df.reset_index()
                elif grouping_colums  and  aggregation and frequency:
                    ##print("aggregation with grouping")
                    df = res_df.stack().reset_index()
                elif grouping_colums  and  aggregation and not  frequency:
                    ##print("aggregation with grouping")
                    df = res_df.reset_index()
                elif grouping_colums:
                    df = res_df
                elif p_query.where_query:
                    df = res_df

                else:
                    ##print("aggregation")
                    pv_df = res_df.transpose()
                    df = pv_df.reset_index()
            else:
                if not p_query.where_query and not grouping_colums and not aggregation :
                    df = res_df
                elif p_query.where_query and not grouping_colums and not aggregation :
                    df = res_df

                elif p_query.where_query  and grouping_colums and not aggregation:
                    df = res_df
                elif p_query.where_query  and grouping_colums and aggregation:
                    df = res_df.reset_index()
                elif grouping_colums and aggregation:
                    df = res_df.reset_index()
                elif grouping_colums and  not aggregation:
                        df = res_df
                res_df__table_content = df.to_html(classes="table table-striped tableFixHead",border="0")
            # t_df = res_df.T
            # ##print("the visulization columns",df)
            df_columns     = df.columns.tolist()
            for column in df_columns:
                try:
                    df[column] = pd.to_numeric(df[column])
                except:
                    pass
            string_columns = df.select_dtypes(include ='object')
            df_columns     = df.columns.tolist()
            if p_query.query_id == project_query.query_id:
                try:

                    request.POST['scatter']
                    # ##print("scatter")
                    try:
                        request.POST['plot_type_2d']
                                # ##print("2d")
                        x = request.POST['scatter_2d_x']
                        y = request.POST['scatter_2d_y']
                        color = request.POST.get('scatter_2d_color',None)
                        if color:
                            ##print("befour plot")
                            delete = Plot.objects.filter(dashboard_query=p_query).delete()
                            plot = Plot.objects.create(plot_type='scatter_2d',x_axis=x,y_axis=y,dashboard_query=p_query,color=color)
                            div = plots.scatter_plot(df,x,y,color=color)
                            ##print("after plot")
                        else:
                            delete = Plot.objects.filter(dashboard_query=p_query).delete()
                            plot = Plot.objects.create(plot_type='scatter_2d',x_axis=x,y_axis=y,dashboard_query=p_query)
                            div = plots.scatter_plot(df,x,y)
                    except:
                        pass


                    try:
                        request.POST['plot_type_3d']

                        # ##print("3d")
                        x = request.POST['scatter_3d_x']
                        y = request.POST['scatter_3d_y']
                        z = request.POST['scatter_3d_z']
                        color = request.POST.get('scatter_3d_color',None)
                        if color:
                            div = plots.scatter_plot_3d(df,x,y,z,color=color)
                            delete = Plot.objects.filter(dashboard_query=p_query).delete()
                            plot = Plot.objects.create(plot_type='scatter_3d',x_axis=x,y_axis=y,z_axis=z,dashboard_query=p_query,color=color)
                        else:
                            div = plots.scatter_plot_3d(df,x,y,z)
                            delete = Plot.objects.filter(dashboard_query=p_query).delete()
                            plot = Plot.objects.create(plot_type='scatter_3d',x_axis=x,y_axis=y,z_axis=z,dashboard_query=p_query)
                    except:
                        pass


                except:
                    pass
                try:

                    request.POST['bar']
                    # ##print("bar")
                    x = request.POST['bar_x']
                    y = request.POST['bar_y']
                    color = request.POST.get('bar_color',None)
                    if color:

                        div = plots.bar_plot(df,x,y,color=color)
                        delete = Plot.objects.filter(dashboard_query=p_query).delete()
                        plot = Plot.objects.create(plot_type='bar',x_axis=x,y_axis=y,dashboard_query=p_query,color=color)
                    else:
                        div = plots.bar_plot(df,x,y)
                        delete = Plot.objects.filter(dashboard_query=p_query).delete()
                        plot = Plot.objects.create(plot_type='bar',x_axis=x,y_axis=y,dashboard_query=p_query)
                except:
                    pass
                try:
                    request.POST['line_plot_type_2d']
                    # ##print("2d")
                    x = request.POST['line_2d_x']
                    y = request.POST['line_2d_y']
                    color = request.POST.get('line_2d_color',None)
                    if color:
                        div = plots.line_plot(df,x,y,color=color)
                        delete = Plot.objects.filter(dashboard_query=p_query).delete()
                        plot = Plot.objects.create(plot_type='line_2d',x_axis=x,y_axis=y,dashboard_query=p_query,color=color)
                    else:
                        div = plots.line_plot(df,x,y)
                        delete = Plot.objects.filter(dashboard_query=p_query).delete()
                        plot = Plot.objects.create(plot_type='line_2d',x_axis=x,y_axis=y,dashboard_query=p_query)

                except:
                    pass
                try:
                    request.POST['line_plot_type_3d']
                    # ##print("3d")
                    x = request.POST['line_3d_x']
                    y = request.POST['line_3d_y']
                    z = request.POST['line_3d_z']
                    color = request.POST.get('line_3d_color',None)
                    if color:
                        div = plots.line_plot_3d(df,x,y,z,color=color)
                        delete = Plot.objects.filter(dashboard_query=p_query).delete()
                        plot = Plot.objects.create(plot_type='line_3d',x_axis=x,y_axis=y,z_axis=z,dashboard_query=p_query,color=color)
                    else:
                        div = plots.line_plot_3d(df,x,y,z)
                        delete = Plot.objects.filter(dashboard_query=p_query).delete()
                        plot = Plot.objects.create(plot_type='line_3d',x_axis=x,y_axis=y,z_axis=z,dashboard_query=p_query)
                except:
                    pass


                try:

                    request.POST['histogram']
                    # ##print("histogram")
                    x = request.POST['histogram_x']
                    y = request.POST['histogram_y']
                    color = request.POST.get('histogram_color',None)
                    if color:
                        div = plots.histogram_plot(df,x,y,color=color)
                        delete = Plot.objects.filter(dashboard_query=p_query).delete()
                        plot = Plot.objects.create(plot_type='line_3d',x_axis=x,y_axis=y,z_axis=z,dashboard_query=p_query,color=color)
                    else:
                        div = plots.histogram_plot(df,x,y)
                        delete = Plot.objects.filter(dashboard_query=p_query).delete()
                        plot = Plot.objects.create(plot_type='line_3d',x_axis=x,y_axis=y,z_axis=z,dashboard_query=p_query)
                except:
                    pass
                plot_graphs[p_query.query_id]={'div':div,'id':p_query.pk,'df_column':df_columns,'string_column':string_columns}
                query_results[p_query.query_id]=res_df__table_content
            else:
                if Plot.objects.filter(dashboard_query=p_query).exists():
                    plot =Plot.objects.get(dashboard_query=p_query)
                    if plot.plot_type == 'scatter_2d':
                        if plot.color:
                            div = plots.scatter_plot(df,x=plot.x_axis,y=plot.y_axis,color=plot.color,legend=plot.legend)
                        else:
                            div = plots.scatter_plot(df,x=plot.x_axis,y=plot.y_axis,legend=plot.legend)
                    elif plot.plot_type == 'scatter_3d':
                        if plot.color:
                            div = plots.scatter_plot_3d(df,x=plot.x_axis,z=plot.z_axis,y=plot.y_axis,color=plot.color,legend=plot.legend)
                        else:
                            div = plots.scatter_plot_3d(df,x=plot.x_axis,z=plot.z_axis,y=plot.y_axis,legend=plot.legend)
                    elif plot.plot_type == 'line_2d':
                        if plot.color:
                            div = plots.line_plot(df,x=plot.x_axis,y=plot.y_axis,color=plot.color,legend=plot.legend)
                        else:
                            div = plots.line_plot(df,x=plot.x_axis,y=plot.y_axis,color=plot.color,legend=plot.legend)
                    elif plot.plot_type == 'line_3d':
                        if plot.color:
                            div = plots.line_plot_3d(df,x=plot.x_axis,z=plot.z_axis,y=plot.y_axis,color=plot.color,legend=plot.legend)
                        else:
                            div = plots.line_plot_3d(df,x=plot.x_axis,z=plot.z_axis,y=plot.y_axis,legend=plot.legend)
                    elif plot.plot_type == 'bar':
                        if plot.color:
                            div = plots.bar_plot(df,x=plot.x_axis,y=plot.y_axis,color=plot.color,legend=plot.legend)
                        else:
                            div = plots.bar_plot(df,x=plot.x_axis,y=plot.y_axis,legend=plot.legend)
                    elif plot.plot_type == 'histogram':
                        if plot.color:
                            div = plots.histogram_plot(df,x=plot.x_axis,y=plot.y_axis,color=plot.color,legend=plot.legend)
                        else:
                            div = plots.histogram_plot(df,x=plot.x_axis,y=plot.y_axis,legend=plot.legend)
                else:
                    # fig = px.scatter_matrix(df)
                    # div = opy.plot(fig, auto_open=False, output_type='div')
                    div = True
                plot_graphs[p_query.query_id]={'div':div,'id':p_query.pk,'df_column':df_columns,'string_column':string_columns}
                query_results[p_query.query_id]=res_df__table_content


        context={'query_results':res_df__table_content,'permission':permission,'plot_graphs':plot_graphs,'project_query':project_query,'df_columns':df_columns,'string_columns':string_columns,'dashboard':dashboard}
        return render(request,template_name,context)


class DashboardLegend(View):
    ''' view for  visualization customization'''

    def post(self,request,pk):
        template_name='dashboard/project_dashboard.html'
        ep_id = request.POST.get('end_point_id',None)
        legend = request.POST.get('plot_legend',None)
        project_end_point = ProjectEndPoint.objects.get(pk=int(ep_id))
        piqu,created = ProjectBillingPrms.objects.get_or_create(project=project_end_point.project)
        update = ProjectBillingPrms.objects.filter(project=project_end_point.project).update(query_count=piqu.query_count+1)
        dashboard = ProjectDashboard.objects.get(pk=pk)
        dashboard_format = dashboard.dashboard_format
        ##print("length of dashboard items",len(dashboard_format))
        id_elem_hash = self._index_dashboard(dashboard_format)
        type_elem_hash = self._index_dashboard_type(dashboard_format)
        plot_graphs ={}
        query_results ={}
        if Project.objects.filter(pk=project_end_point.project.pk,admin_user=request.user).exists():
            permission="Admin"
        elif ProjectUser.objects.filter(project=project_end_point.project,project_user=request.user).exists():
            user_group = User.objects.get(pk=request.user.pk)

            for g in user_group.groups.all():
                if g.name == str(project_end_point.project.pk)+"_Read":
                    permission="Read"
                elif g.name == str(project_end_point.project.pk)+"_Write":
                    permission="Write"
                elif g.name == str(project_end_point.project.pk)+"_Delete":
                    permission="Delete"
                elif g.name == str(project_end_point.project.pk)+"_Admin":
                    permission="Admin"
        else:
            permission=None
        current_site = get_current_site(request)
        site_name = current_site.name
        domain = current_site.domain
        if domain.startswith('127.0.'):
            domain = 'https://'+domain
        else:
            domain = 'https://'+domain
        metadata = ProjectMetaData.objects.get(project=dashboard.project)
        for end_point in dashboard.end_point.all():
            if not end_point.sub_df:
                pv = QueryExcecute(end_point.query)
                js_df = pv
                if metadata.date_column_name:
                    js_df[metadata.date_column_name] =js_df[metadata.date_column_name].astype('str')


                result_json = js_df.to_json(orient='index')
                # vl.bari("unpivot of result df:"+str(end_point), 'e')

                # vl.bari("saving sub_df:"+str(end_point), 's')
                update = ProjectEndPoint.objects.filter(pk=end_point.pk).update(sub_df=result_json)
                # vl.bari("saving sub_df:"+str(end_point), 'e')

            else:
                # vl.bari("Loading sub_df:"+str(end_point), 's')
                json_st = json.loads(end_point.sub_df)
                # vl.bari('Before Dataframe')
                json_df = pd.DataFrame(json_st) #TODO 'Taking time - Have to work'
                # vl.bari('Before transpose')
                pv = json_df.transpose()
                df_columns     = pv.columns.tolist()
                for key, value in metadata.meta_data.items():
                    if key in df_columns:
                        ##print("key",key)
                        if value['dtype'] == 'int':
                            pv[key] =pd.to_numeric(pv[key])
                            if key in df_columns:
                                pv[key] = pd.to_numeric(pv[key])
                        elif value['dtype'] == 'float':
                            ##print("final key",key,pv[key],pv[key].dtypes)
                            pv[key] = pd.to_numeric(pv[key])
                            if key in df_columns:
                                pv[key] = pd.to_numeric(pv[key])
                        elif value['dtype'] == 'object':
                            pv[key] = pv[key].astype(str)
                            if key in df_columns:
                                pv[key] = pv[key].astype(str)
                        elif value['dtype'] == 'bool':
                            pv[key] = pv[key].astype(bool)
                            if key in df_columns:
                                pv[key] = pv[key].astype(bool)
                        elif value['dtype'] == 'DateTime':
                            pv[key] =pd.to_datetime(pv[key])
                            ##print("the data key",key)
                            if key in df_columns:
                                pv[key] = pd.to_datetime(pv[key])
                # vl.bari("Loading sub_df:"+str(end_point), 'e')
            string_columns = pv.select_dtypes(include =['object','bool'])
            df_columns     = pv.columns.tolist()
            plot_df  = pv
            if metadata.date_column_name in df_columns and metadata.date_column_name:
                plot_df[metadata.date_column_name] =plot_df[metadata.date_column_name].astype('str')


            plot_start_time = datetime.now()

            # vl.bari("Rendering Plot:"+str(end_point), 's')
            if project_end_point.pk == end_point.pk:
                if end_point.plot and   end_point.plot.legend == True:
                    update =Plot.objects.filter(pk=end_point.plot.pk).update(legend=False)

                elif end_point.plot and   end_point.plot.legend == False:
                    update =Plot.objects.filter(pk=end_point.plot.pk).update(legend=True)
                end_point = ProjectEndPoint.objects.get(pk=end_point.pk)
            if end_point.plot and end_point.plot.plot_type:
                end_point_obj = EndPointPlot(plot_df,end_point.pk)
                div = end_point_obj.plot(end_point.plot)

            else:
                # fig = px.scatter_matrix(plot_df)
                # div = opy.plot(fig, auto_open=False,output_type='div')
                div = True
                
            key = id_elem_hash[str(end_point.id)]
            value  = dashboard_format[key]
            # print("the object",dashboard_format)
            if value['id'] == str(end_point.id):
                value['div']= div
                value['id'] = end_point.id
                value['end_point']=end_point

                if end_point.algorithm:
                    features_text = end_point.algorithm.feature
                    features_text = features_text.replace('[', '')
                    features_text = features_text.replace(']', '')
                    features      = features_text.split(',')
                    features_ml_display = features_text.split(',')
                    ##print("features",features)

                    test_l =[]
                    features_cat_dict = {}
                    ml_df = pd.DataFrame()
                    for column in features:
                        ml_df[column] = pv[column]

                    ml_string_columns = ml_df.select_dtypes(include =['object','bool'])
                        
                    for column in ml_string_columns:
                        if ml_df[column].dtypes  == np.bool:
                            ##print("the data value",df[column],column)

                            column_name = column +'_cat'
                            d = {}

                            new_df = pd.DataFrame()
                            new_df[column] = pd.unique(pv[column])

                            column_name = column+'_cat'
                            new_df[column] = new_df[column].astype('category')
                            new_df[column_name] = new_df[column].cat.codes
                            c_series = new_df[column]
                            c_cat_series = new_df[column_name]
                            c_list = c_series.tolist()
                            c_cat_list = c_cat_series.tolist()
                            ##print("new_df",new_df)

                            for i in range(0,len(c_list)):
                                d[c_list[i]]=c_cat_list[i]
                            features_cat_dict[column]=d
                            ##print("features",features_cat_dict)
                            features.remove(column)
                            ##print("features",features)



                        else:
                            try:

                                ml_df[column] = ml_df[column].astype(float)
                                ##print("in float type column is",column,ml_df[column])
                            except:

                                d = {}

                                new_df = pd.DataFrame()
                                new_df[column] = pd.unique(pv[column])

                                column_name = column+'_cat'
                                new_df[column] = new_df[column].astype('category')
                                new_df[column_name] = new_df[column].cat.codes
                                c_series = new_df[column]
                                c_cat_series = new_df[column_name]
                                c_list = c_series.tolist()
                                c_cat_list = c_cat_series.tolist()
                                ##print("new_df",new_df)

                                for i in range(0,len(c_list)):
                                    d[c_list[i]]=c_cat_list[i]
                                features_cat_dict[column]=d
                                ##print("features",features_cat_dict)
                                features.remove(column)




                    target   = end_point.algorithm.y_factor
                    model_id = end_point.algorithm.model_id
                    if end_point.algorithm.type_of_prediction == 'Linear':
                        accuracy = ast.literal_eval(end_point.algorithm.accuracy)
                        MAE = accuracy['MAE']
                        MSE = accuracy['MSE']
                        RMSE = accuracy['RMSE']
                        accuracy_list = {'MAE':MAE,'MSE':MSE,'RMSE':RMSE}
                    else:
                        accuracy_list={'accuracy':end_point.algorithm.accuracy}
                    value['features']=features
                    value['features_ml_display']=features_ml_display
                    value['features_cat_dict'] = features_cat_dict
                    value['target']= target
                    value['accuracy']= accuracy_list
                    value['model_id'] = model_id

                if end_point.plot:
                    value['legend'] = end_point.plot.legend
                else:
                    value['legend'] = False
                dashboard_format[key] = value

                # print("the finalobje is ",dashboard_format)
                # vl.bari("Updating dashboard object:"+str(end_point), 'e')
                # vl.bari("Before df table content results:"+str(end_point), 's')

                # vl.bari("Before df table content results:"+str(end_point), 'e')

                # vl.turn_on_full_debug()
                # vl.fullbari("multiple array", 1, 2, 3, "mixed datatype messages for", end_point, "for demo")

        dashboard_format = dashboard_object_update(dashboard_format,type_elem_hash)
        context={'domain':domain,'permission':permission,'dashboard_format':dashboard_format,'dashboard':dashboard}
        return render(request,template_name,context)

    def _index_dashboard(self,dashboard_format):
        indexing ={}
        for key, value in dashboard_format.items():
            indexing[str(value['id'])]=key
        return indexing
    def _index_dashboard_type(self,dashboard_format):

        elem_list =[]

        for key, value in dashboard_format.items():
            if value['type'] == 'row_constructor':
                elem_list.append(key)

        return elem_list


def dashboard_object_update(dashboard_format,type_elem_hash):
    for key in type_elem_hash:
        value = dashboard_format[key]
        print("the selected value is ",value)
        obj  = value['row_constructor_object']
        obj_id = value['id']
        obj_string = 'row_row-constructor-'+obj_id
        obj_value = obj[obj_string]
        for obj_key, obj_value in obj.items():
            print("the object value",obj_value.keys())
            if 'col_1' in obj_value.keys():
                col_1 = obj_value['col_1']
                # print("the object column",col_1)
                if 'block' in col_1.keys():
                    # print("inside the block")
                    block = col_1['block']
                    block_str = block.split(',')
                    # print("inside the block",block_str)
                    block_pk=block_str[0]
                    # print("the endpoint",block_pk,end_point.id)
                    opration_ep = ProjectEndPoint.objects.get(pk=int(block_pk))
                    df = QueryExcecute(opration_ep.query)



                    block_column = block_str[1]
                    block_operation = block_str[2]
                    if block_operation == 'min':
                        block_value = df[block_column].min()
                        col_1['block']= round(block_value,3)
                        col_1['column_name'] = block_column
                        col_1['end_point']  = opration_ep.name
                        col_1['opration']   = block_operation
                    elif block_operation == 'max':
                        block_value = df[block_column].max()
                        col_1['block']= round(block_value,3)
                        col_1['column_name'] = block_column
                        col_1['end_point']  = opration_ep.name
                        col_1['opration']   = block_operation
                    elif block_operation == 'mean':
                        block_value = df[block_column].mean()
                        col_1['block']= round(block_value,3)
                        col_1['column_name'] = block_column
                        col_1['end_point']  = opration_ep.name
                        col_1['opration']   = block_operation
                    elif block_operation == 'std':
                        block_value = df[block_column].std()
                        col_1['block']= round(block_value,3)
                        col_1['column_name'] = block_column
                        col_1['end_point']  = opration_ep.name
                        col_1['opration']   = block_operation
                obj_value['col_1'] = col_1
                # print("test",obj_value)
            if 'col_2' in obj_value.keys():

                col_2 = obj_value['col_2']
                print("the object column",col_2)
                if 'block' in col_2.keys():
                    block = col_2['block']
                    block_str = block.split(',')
                    block_pk=block_str[0]
                    # print('endpoint',block_pk,end_point.id)

                    opration_ep = ProjectEndPoint.objects.get(pk=int(block_pk))
                    df = QueryExcecute(opration_ep.query)
                    block_column = block_str[1]
                    block_operation = block_str[2]
                    if block_operation == 'min':
                        block_value = df[block_column].min()
                        col_2['block']= round(block_value,3)
                        col_2['column_name'] = block_column
                        col_2['end_point']  = opration_ep.name
                        col_2['opration']   = block_operation
                    elif block_operation == 'max':
                        block_value = df[block_column].max()
                        col_2['block']= round(block_value,3)
                        col_2['column_name'] = block_column
                        col_2['end_point']  = opration_ep.name
                        col_2['opration']   = block_operation
                    elif block_operation == 'mean':
                        block_value = df[block_column].mean()
                        col_2['block']= round(block_value,3)
                        col_2['column_name'] = block_column
                        col_2['end_point']  = opration_ep.name
                        col_2['opration']   = block_operation
                    elif block_operation == 'std':
                        block_value = df[block_column].std()
                        col_2['block']= round(block_value,3)
                        col_2['column_name'] = block_column
                        col_2['end_point']  = opration_ep.name
                        col_2['opration']   = block_operation

                obj_value['col_2'] = col_2
                print("the col2",obj_value)
            if 'col_3' in obj_value.keys():
                col_3 = obj_value['col_3']
                if 'block' in col_3.keys():
                    block = col_3['block']
                    block_str = block.split(',')
                    block_pk=block_str[0]
                    opration_ep = ProjectEndPoint.objects.get(pk=int(block_pk))
                    df = QueryExcecute(opration_ep.query)

                    block_column = block_str[1]
                    block_operation = block_str[2]
                    if block_operation == 'min':
                        block_value = df[block_column].min()
                        col_3['block']= round(block_value,3)
                        col_3['column_name'] = block_column
                        col_3['end_point']  = opration_ep.name
                        col_3['opration']   = block_operation
                    elif block_operation == 'max':
                        block_value = df[block_column].max()
                        col_3['block']= round(block_value,3)
                        col_3['column_name'] = block_column
                        col_3['end_point']  = opration_ep.name
                        col_3['opration']   = block_operation
                    elif block_operation == 'mean':
                        block_value = df[block_column].mean()
                        col_3['block']= round(block_value,3)
                        col_3['column_name'] = block_column
                        col_3['end_point']  = opration_ep.name
                        col_3['opration']   = block_operation
                    elif block_operation == 'std':
                        block_value = df[block_column].std()
                        col_3['block']= round(block_value,3)
                        col_3['column_name'] = block_column
                        col_3['end_point']  = opration_ep.name
                        col_3['opration']   = block_operation
                obj_value['col_3'] = col_3
            obj[obj_string] = obj_value
            value['row_constructor_object']=obj
            dashboard_format[key] = value
    return dashboard_format


def QueryExcecute(project_query):
    today = datetime.now()
    if project_query.start_date:

        start_date = project_query.start_date
        from_date_select = project_query.start_date_select

        date = start_date.split('-')
        if len(date)==1:
            if from_date_select == 'day':
                start_date =today -timedelta(days=int(date[0]))
            elif from_date_select == 'week':
                start_date =today -timedelta(days=7*int(date[0]))
            elif from_date_select == 'month':
                start_date =today -timedelta(int(date[0])*365/12)
            elif from_date_select == 'year':
                start_date =today -timedelta(int(date[0])*365)
    else:
        start_date = None

    if project_query.end_date:

        end_date = project_query.end_date
        to_date_select = project_query.end_date_select
        date = end_date.split('-')
        if len(date)==1:
            if to_date_select == 'day':
                end_date =today -timedelta(days=int(date[0]))
            elif to_date_select == 'week':
                end_date =today -timedelta(days=int(7*date[0]))
            elif to_date_select == 'month':
                end_date =today -timedelta(int(date[0])*365/12)
            elif to_date_select == 'year':
                end_date =today -timedelta(int(date[0])*365)
            elif to_date_select == 'today':
                end_date =today

    else:
        end_date = None

    if project_query.expected_range:

        frequency = project_query.expected_range
    else:
        frequency=None
    if project_query.group_query:
        grouping_colums = list(project_query.group_query.split(","))
    else:
        grouping_colums = None
    if project_query.aggregation_value:
        value_columns = list(project_query.aggregation_value.split(","))
            # ##print("the splited value columns are",value_columns)
    else:
        value_columns = None



    if project_query.aggregation_query:
        aggregation = ast.literal_eval(project_query.aggregation_query)
    else:
        aggregation = None

    project_meta = ProjectMetaData.objects.get(project=project_query.project)
    if project_meta.date_column_name:
        date_field = project_meta.date_column_name
    else:
        date_field=None


    if project_query.where_query:
        ##print(project_query,project_query.project.pk,frequency,1,start_date,end_date,grouping_colums,value_columns,project_query.where_query,aggregation,date_field,date_field)
        res_df = query.subset(project_query.project.pk,frequency,1,start_date=start_date,end_date=end_date,grouping_columns=grouping_colums,where=project_query.where_query,aggregation=aggregation,date_column=date_field)
    else:
        res_df = query.subset(project_query.project.pk,frequency,1,start_date=start_date,end_date=end_date,grouping_columns=grouping_colums,aggregation=aggregation,date_column=date_field)


    # ##print("the columns of pivot table are ",res_df.columns.tolist())
    project_meta = ProjectMetaData.objects.get(project=project_query.project)
    if project_meta.date_column_name:
        date_field = project_meta.date_column_name
    else:
        date_field=None
    # ##print("final df after grouping is ",res_df)
    if date_field:

        if not project_query.where_query and not grouping_colums and not aggregation :
            pv = res_df
        elif project_query.where_query and not grouping_colums and not aggregation :
            pv = res_df

        elif project_query.where_query  and grouping_colums and not aggregation  :
            ##print("no aggregation with grouping")
            pv = res_df
        elif project_query.where_query  and grouping_colums and  aggregation and frequency :
            ##print("no aggregation with grouping")
            pv =  res_df.stack().reset_index()
        elif project_query.where_query  and grouping_colums and  aggregation and not frequency :
            ##print("no aggregation with grouping")
            pv =  res_df.reset_index()
        elif  project_query.where_query  and not project_query.where_query  and not grouping_colums and not aggregation and  frequency :
            ##print("no aggregation with grouping")
            pv =  res_df
        elif project_query.where_query  and not grouping_colums  and  aggregation and frequency:
            ##print("aggregation with no grouping")
            pv_df = res_df.transpose()
            pv = pv_df.reset_index()
        elif not grouping_colums  and  aggregation and frequency:
            ##print("aggregation with grouping")
            pv_df = res_df.transpose()
            pv = pv_df.reset_index()
        elif grouping_colums  and  aggregation and frequency:
            ##print("aggregation with grouping")
            pv = res_df.stack().reset_index()
        elif grouping_colums  and  aggregation and not frequency:
            ##print("aggregation with grouping no frequency")
            pv = res_df.reset_index()
            ##print("after final conversion",pv)
        elif grouping_colums:
            pv = res_df
        elif project_query.where_query:
            pv = res_df

        else:
            ##print("aggregation")
            pv_df = res_df.transpose()
            pv = pv_df.reset_index()
    else:
        if not project_query.where_query and not grouping_colums and not aggregation :
            pv = res_df

        elif project_query.where_query and not grouping_colums and not aggregation :
            pv = res_df

        elif project_query.where_query  and grouping_colums and not aggregation:
            pv = res_df
        elif project_query.where_query  and grouping_colums and aggregation:
            pv = res_df.reset_index()
        elif grouping_colums and aggregation:
            pv = res_df.reset_index()
        elif grouping_colums and  not aggregation:
            pv = res_df
    df_columns= pv.columns.to_list()
    metadata = ProjectMetaData.objects.get(project=project_query.project)
    for key, value in metadata.meta_data.items():
        if key in df_columns:
            ##print("key",key)
            if value['dtype'] == 'int':
                pv[key] =pd.to_numeric(pv[key])
                if key in df_columns:
                    pv[key] = pd.to_numeric(pv[key])
            elif value['dtype'] == 'float':
                ##print("final key",key,pv[key],pv[key].dtypes)
                pv[key] = pd.to_numeric(pv[key])
                if key in df_columns:
                    pv[key] = pd.to_numeric(pv[key])
            elif value['dtype'] == 'object':
                pv[key] = pv[key].astype(str)
                if key in df_columns:
                    pv[key] = pv[key].astype(str)
            elif value['dtype'] == 'bool':
                pv[key] = pv[key].astype(bool)
                if key in df_columns:
                    pv[key] = pv[key].astype(bool)
            elif value['dtype'] == 'DateTime':
                pv[key] =pd.to_datetime(pv[key])
                ##print("the data key",key)
                if key in df_columns:
                    pv[key] = pd.to_datetime(pv[key])
        # for column in df_columns:
        #     try:
        #         pv[column] = pd.to_numeric(pv[column])
        #     except:
        #         pass

        # t_df = res_df.T
        # ##print("the visulization columns",pv)
    # string_columns = pv.select_dtypes(include =['object','bool'])
    # feature_columns = pv.select_dtypes(include=['object','bool','number'])

    # df_columns     = pv.columns.tolist()
    # if metadata.date_column_name and metadata.date_column_name in df_columns:
    #     pv[metadata.date_column_name] = pv[metadata.date_column_name].astype(str)
    return pv


class ProjectEndPointView(GroupRequiredMixin,LoginRequiredMixin,View):
    ''' project details class where all the details along with Visualization data of project is displayed'''
    def dispatch(self, request, *args, **kwargs):
        pk = kwargs['pk']
        try:
            end_point = ProjectEndPoint.objects.get(pk=pk)
            project=Project.objects.get(pk=end_point.project.pk)

        except:
            query= ProjectQuery.objects.get(pk=pk)
            project=Project.objects.get(pk=query.project.pk)


        pk= str(project.pk)
        self.login_url = '/customer/login/'
        self.redirect_field_name = 'redirect_to'
        self.template_name='dashboard/index.html'
        admin_name = pk+"_Admin"
        ##print(type(admin_name), admin_name)
        admin_encode_name = admin_name.encode()
        admin_unicode_name = admin_encode_name.decode('utf-8')
        write_name = pk+"_Write"
        ##print(type(write_name), write_name)
        write_encode_name = write_name.encode()
        write_unicode_name = write_encode_name.decode('utf-8')
        read_name = pk+"_Read"
        ##print(type(read_name), read_name)
        read_encode_name = read_name.encode()
        read_unicode_name = read_encode_name.decode('utf-8')
        delete_name = pk+"_Delete"
        ##print(type(delete_name), delete_name)
        delete_encode_name = delete_name.encode()
        delete_unicode_name = delete_encode_name.decode('utf-8')
        l =[delete_unicode_name,write_unicode_name,admin_unicode_name,read_unicode_name]
        self.group_required= l
        ##print("the self of dispatcher",self.group_required)

        return super(ProjectEndPointView, self).dispatch(request, *args, **kwargs)


    def get(self,request,pk):
        context = endpointget(request,pk)

        return render(request,'dashboard/project_end_point.html',context)

    def post(self,request,pk):
        name = request.POST['end_point_name']
        frequency = request.POST['frequency']
        query_object = request.POST.get('end_point_object',None)
        if query_object:
            ##print("the query object",query_object)
            query_object = ast.literal_eval(query_object)
        query= ProjectQuery.objects.get(pk=pk)
        customer = Customer.objects.get(user=request.user)
        end_point_count = ProjectEndPoint.objects.filter(user=request.user).count()
        ##print("EndPointPlot create")
        if customer.type =='Individual':
            if end_point_count >5:
                pk = query.project.pk
                context= single_project_details(request,pk)
                context['msg'] = "Project has Exceeded The EndPoint Limit"
                return render(request,template_name,context)

            else:
                if query_object:
                    ep = ProjectEndPoint.objects.create(name=name,project=query.project,query=query,alignment_object=query_object,user=request.user,sub_df_frequency=frequency)
                else:

                    ep = ProjectEndPoint.objects.create(name=name,project=query.project,query=query,user=request.user,sub_df_frequency=frequency)
                if query.plot_type and query.plot.plot_type:
                    ##print("the query facet_col",query.plot.facet_col)
                    plot = Plot.objects.create(plot_type=query.plot.plot_type,x_axis=query.plot.x_axis,y_axis=query.plot.y_axis,z_axis=query.plot.z_axis,color=query.plot.color,legend=query.plot.legend,size=query.plot.size,hover_name=query.plot.hover_name,values=query.plot.values,names=query.plot.names,orientation=query.plot.orientation,facet_col=query.plot.facet_col)
                    update = ProjectEndPoint.objects.filter(pk=ep.pk).update(plot=plot)
                pk=str(ep.pk)
                ##print("")
                return redirect('/endpoint/'+pk+'/')
        else:
            project_usage = ProjectBillingPrms.objects.get(project=query.project)
            total_end_point = project_usage.end_point +5
            end_points = ProjectEndPoint.objects.filter(project=query.project).count()
            if end_points<=total_end_point:
                if query_object:
                    ep = ProjectEndPoint.objects.create(name=name,project=query.project,query=query,alignment_object=query_object,user=request.user,sub_df_frequency=frequency)
                else:
                    ep = ProjectEndPoint.objects.create(name=name,project=query.project,query=query,user=request.user,sub_df_frequency=frequency)
                if query.plot and query.plot.plot_type:
                    ##print("the query facet_col",query.plot.facet_col)

                    plot = Plot.objects.create(plot_type=query.plot.plot_type,x_axis=query.plot.x_axis,y_axis=query.plot.y_axis,z_axis=query.plot.z_axis,color=query.plot.color,legend=query.plot.legend,size=query.plot.size,hover_name=query.plot.hover_name,values=query.plot.values,names=query.plot.names,orientation=query.plot.orientation,facet_col=query.plot.facet_col)
                    update = ProjectEndPoint.objects.filter(pk=ep.pk).update(plot=plot)
                pk=ep.pk
                context= endpointget(request,pk)

                return redirect('/endpoint/'+pk+'/')
            else:
                pk= query.project.pk
                context= single_project_details(request,pk)
                context['msg'] = "Project has Exceeded The EndPoint Limit"
                return render(request,template_name,context)



#function to
def endpointget(request,pk):
    end_point = ProjectEndPoint.objects.get(pk=pk)
    p_query = end_point.query

    if Project.objects.filter(pk=p_query.project.pk,admin_user=request.user).exists():
        permission="Admin"
    elif ProjectUser.objects.filter(project=p_query.project,project_user=request.user).exists():
        user_group = User.objects.get(pk=request.user.pk)

        for g in user_group.groups.all():
            if g.name == str(p_query.project.pk)+"_Read":
                permission="Read"
            elif g.name == str(p_query.project.pk)+"_Write":
                permission="Write"
            elif g.name == str(p_query.project.pk)+"_Delete":
                permission="Delete"
            elif g.name == str(p_query.project.pk)+"_Admin":
                permission="Admin"
    else:
        permission=None
    dashboards =ProjectDashboard.objects.filter(end_point__in=[end_point])
    # ##print("the dashboards",dashboards)
    if not end_point.sub_df:

        df = QueryExcecute(p_query)
        df_columns = df.columns.tolist()
        metadata = ProjectMetaData.objects.get(project=p_query.project)
        string_columns = df.select_dtypes(include =['object','bool'])
        number_columns = df.select_dtypes(include =['number'])
        if metadata.date_column_name and metadata.date_column_name in df_columns:
            df[metadata.date_column_name] = df[metadata.date_column_name].astype(str)
        result_json = df.to_json(orient='index')

        update = ProjectEndPoint.objects.filter(pk=end_point.pk).update(sub_df=result_json)

    else:
        ##print("loding from json data")
        json_st = json.loads(end_point.sub_df)
        # ##print("THE TYPE OF JSON FILE<",type(json_st))
        json_df = pd.DataFrame(json_st)
        df = json_df.transpose()
        df_columns= df.columns.to_list()
        metadata = ProjectMetaData.objects.get(project=p_query.project)
        for key, value in metadata.meta_data.items():
            if key in df_columns:
                ##print("key",key)
                if value['dtype'] == 'int':
                    df[key] =pd.to_numeric(df[key])
                    if key in df_columns:
                        df[key] = pd.to_numeric(df[key])
                elif value['dtype'] == 'float':
                    ##print("final key",key,df[key],df[key].dtypes)
                    df[key] = pd.to_numeric(df[key])
                    if key in df_columns:
                        df[key] = pd.to_numeric(df[key])
                elif value['dtype'] == 'object':
                    df[key] = df[key].astype(str)
                    if key in df_columns:
                        df[key] = df[key].astype(str)
                elif value['dtype'] == 'bool':
                    df[key] = df[key].astype(bool)
                    if key in df_columns:
                        df[key] = df[key].astype(bool)
                elif value['dtype'] == 'DateTime':
                    df[key] =pd.to_datetime(df[key])
                    ##print("the data key",key)
                    if key in df_columns:
                        df[key] = pd.to_datetime(df[key])

        string_columns = df.select_dtypes(include =['object','bool'])
        number_columns = df.select_dtypes(include =['number'])

    

    metadata = ProjectMetaData.objects.get(project=p_query.project)

    
    df_columns     = df.columns.tolist()
    if metadata.date_column_name and metadata.date_column_name in df_columns:
        df[metadata.date_column_name] = df[metadata.date_column_name].astype(str)
    res_df__table_content = df.to_html(classes="table table-striped tableFixHead",border="0")
    row_count = df.shape[1]
    column_count = df.shape[0]
    if end_point.plot and end_point.plot.plot_type:
        end_point_obj = EndPointPlot(df,end_point.pk)
        div = end_point_obj.plot(end_point.plot)
    else:
        # fig = px.scatter_matrix(df)
        # div = opy.plot(fig, auto_open=False, output_type='div')
        div = True
    pro_billig = ProjectBillingPrms.objects.get(project=end_point.project)
    if not end_point.algorithm == None :
        features_text = end_point.algorithm.feature
        features_text = features_text.replace('[', '')
        features_text = features_text.replace(']', '')
        features      = features_text.split(',')
        features_ml_display = features_text.split(',')
        ##print("features",features)

        test_l =[]
        features_cat_dict = {}
        ml_df = pd.DataFrame()
        for column in features:
            ml_df[column] = df[column]

        ml_string_columns = ml_df.select_dtypes(include =['object','bool'])
        ##print("the ml string columns ",ml_string_columns)




        ##print("after ml df ",ml_df)
        for column in ml_string_columns:
            if ml_df[column].dtypes  == np.bool:
                ##print("the data value",df[column],column)

                column_name = column +'_cat'
                d = {}

                new_df = pd.DataFrame()
                new_df[column] = pd.unique(df[column])

                column_name = column+'_cat'
                new_df[column] = new_df[column].astype('category')
                new_df[column_name] = new_df[column].cat.codes
                c_series = new_df[column]
                c_cat_series = new_df[column_name]
                c_list = c_series.tolist()
                c_cat_list = c_cat_series.tolist()
                ##print("new_df",new_df)

                for i in range(0,len(c_list)):
                    d[c_list[i]]=c_cat_list[i]
                features_cat_dict[column]=d
                ##print("features",features_cat_dict)
                features.remove(column)
                ##print("features",features)



            else:
                try:

                    ml_df[column] = ml_df[column].astype(float)
                    ##print("in float type column is",column,ml_df[column])
                except:

                    d = {}

                    new_df = pd.DataFrame()
                    new_df[column] = pd.unique(df[column])

                    column_name = column+'_cat'
                    new_df[column] = new_df[column].astype('category')
                    new_df[column_name] = new_df[column].cat.codes
                    c_series = new_df[column]
                    c_cat_series = new_df[column_name]
                    c_list = c_series.tolist()
                    c_cat_list = c_cat_series.tolist()
                    ##print("new_df",new_df)

                    for i in range(0,len(c_list)):
                        d[c_list[i]]=c_cat_list[i]
                    features_cat_dict[column]=d
                    ##print("features",features_cat_dict)
                    features.remove(column)
                    ##print("features",features)



        target   = end_point.algorithm.y_factor

        model_id = end_point.algorithm.model_id
        model_id = model_id.split('.pkl')
        model_id = model_id[0]
        if end_point.algorithm.type_of_prediction == 'Linear':
            accuracy = ast.literal_eval(end_point.algorithm.accuracy)
            MAE = accuracy['MAE']
            MSE = accuracy['MSE']
            RMSE = accuracy['RMSE']
            accuracy_list = {'MAE':MAE,'MSE':MSE,'RMSE':RMSE}
        else:
            accuracy_list={'accuracy':end_point.algorithm.accuracy}
    else:
        features_cat_dict = {}
        features_ml_display = None
        features = None
        target = None
        model_id = None
        accuracy_list = None

    ##print("the feature list is ",features_cat_dict)
    try:
        ml_api_request = EndpointMlApi.objects.get(end_point=end_point)
    except:
        ml_api_request = None
    update = ProjectBillingPrms.objects.filter(pk=pro_billig.pk).update(query_count=pro_billig.query_count+1)
    dashboards_form = ProjectDashboardsForm(initial={'project':end_point.project.pk})
    context = {'features_ml_display':features_ml_display,'features_cat_dict':features_cat_dict,'features':features,'target':target,'model_id':model_id,'accuracy_list':accuracy_list,'graph':div,'end_point':end_point,'query':res_df__table_content,'project':end_point.project,'permission':permission,'row_count':row_count,'column_count':column_count,'string_columns':string_columns,'df_columns':df_columns,'dashboards_form':dashboards_form,'number_columns':number_columns,'ml_api_request':ml_api_request}
    return context

class MlPredictionView(View):
    def post(self,request,pk):
        end_point = ProjectEndPoint.objects.get(pk=pk)
        print("the post is ",request.POST)
        features  = end_point.algorithm.feature.split(',')
        json_st = json.loads(end_point.sub_df)
        # ##print("THE TYPE OF JSON FILE<",type(json_st))
        json_df = pd.DataFrame(json_st)
        df = json_df.transpose()
        columns = df.columns.tolist()
        ml_df = df

        values = []




        ml_string_columns = ml_df.select_dtypes(include =['object','bool'])
        for column in ml_string_columns:
            if ml_df[column].dtypes  == np.bool:
                column_name = column +'_cat'
                ml_df[column_name] = pd.get_dummies(ml_df[column], drop_first=True)


            else:
                try:
                    ml_df[column] = ml_df[column].astype(float)
                except:

                    column_name = column +'_cat'
                    ml_df[column] = df[column].astype('category')
                    ##print("columns ",column)
                    ml_df[column_name] = ml_df[column].cat.codes

        ml_df_columns = ml_df.columns.tolist()
        ##print("ml df",ml_df)
        result = []
        for column in features:
            column_value = request.POST[column]
            column_cat = column+'_cat'
            if column_cat in ml_df_columns:
                value = recode(int(column_value),ml_df[column],ml_df[column_cat])
                ##print("the ddecoded value is",value)
                result.append(value)
                values.append(int(column_value))
            elif ml_df[column].dtypes  == np.bool:
                value = catrgory_decode(column_value,ml_df[column],ml_df[column_cat])
                result.append(column_value)
                values.append(value)


            else:
                values.append(column_value)
                result.append(column_value)

        test_df = pd.DataFrame([values],columns=features)


        ##print("testdf" ,test_df)

        if not end_point.algorithm.y_factor and end_point.algorithm.no_of_group:
            ml_obj = Kmeans(test_df)
            prediction = ml_obj.prediction_algo(end_point.algorithm.model_id)

        elif end_point.algorithm.y_factor and end_point.algorithm.type_of_prediction == 'Classification':
            ml_obj = AutoMl(test_df)
            prediction = ml_obj.prediction_algo(end_point.algorithm.model_id)
        elif end_point.algorithm.y_factor and end_point.algorithm.type_of_prediction == 'Linear':
            ml_obj = Linear(test_df)
            prediction = ml_obj.prediction_algo(end_point.algorithm.model_id)
        ##print("the Preditions",prediction)
        if end_point.algorithm.y_factor:
            cat_target_col=end_point.algorithm.y_factor+'_cat'
        else:
            cat_target_col=None
        # print("the encoded target column is ",ml_df[cat_target_col])

        if cat_target_col and cat_target_col in ml_df_columns:
            value = recode(prediction[0],ml_df[end_point.algorithm.y_factor],ml_df[cat_target_col])
            result.append(value)
        else:
            value = prediction
            result.append(prediction[0])

        data = {'Predition':result}
        ##print("data",data)
        return JsonResponse(data,safe=False)






class EndPointPlotView(View):
    '''class to  update the endpoint plot configurations'''

    def dispatch(self, request, *args, **kwargs):
        pk = kwargs['pk']
        end_point = ProjectEndPoint.objects.get(pk=pk)
        project=Project.objects.get(pk=end_point.project.pk)

        pk= str(project.pk)
        self.login_url = '/customer/login/'
        self.redirect_field_name = 'redirect_to'
        self.template_name='dashboard/index.html'
        admin_name = pk+"_Admin"
        ##print(type(admin_name), admin_name)
        admin_encode_name = admin_name.encode()
        admin_unicode_name = admin_encode_name.decode('utf-8')
        write_name = pk+"_Write"
        ##print(type(write_name), write_name)
        write_encode_name = write_name.encode()
        write_unicode_name = write_encode_name.decode('utf-8')
        read_name = pk+"_Read"
        ##print(type(read_name), read_name)
        read_encode_name = read_name.encode()
        read_unicode_name = read_encode_name.decode('utf-8')
        delete_name = pk+"_Delete"
        ##print(type(delete_name), delete_name)
        delete_encode_name = delete_name.encode()
        delete_unicode_name = delete_encode_name.decode('utf-8')
        l =[delete_unicode_name,write_unicode_name,admin_unicode_name,read_unicode_name]
        self.group_required= l
        ##print("the self of dispatcher",self.group_required)

        return super(EndPointPlotView, self).dispatch(request, *args, **kwargs)

    def get(self,request,pk):
        pass
    def post(self,request,pk):
        end_point = ProjectEndPoint.objects.get(pk=pk)
        p_query = end_point.query
        end_point_update = request.POST.get('update_endpoint',None)
        ##print("end point updae ",request.POST)
        ep_form = ProjectEndPointForm(initial={'end_point_name':end_point.name,'frequency':end_point.sub_df_frequency})
        dashboard_form = ProjectDashboardForm(initial={'project':end_point.project.pk})
        dashboard_form.fields['user'].queryset = ProjectUser.objects.filter(project=end_point.project)
        dashboard_form.fields['dashboard'].queryset = ProjectDashboard.objects.filter(project=end_point.project)
        piqu,created = ProjectBillingPrms.objects.get_or_create(project=end_point.project)
        update = ProjectBillingPrms.objects.filter(project=end_point.project).update(query_count=piqu.query_count+1)
        if Project.objects.filter(pk=p_query.project.pk,admin_user=request.user).exists():
            permission="Admin"
        elif ProjectUser.objects.filter(project=p_query.project,project_user=request.user).exists():
            user_group = User.objects.get(pk=request.user.pk)

            for g in user_group.groups.all():
                if g.name == str(p_query.project.pk)+"_Read":
                    permission="Read"
                elif g.name == str(p_query.project.pk)+"_Write":
                    permission="Write"
                elif g.name == str(p_query.project.pk)+"_Delete":
                    permission="Delete"
                elif g.name == str(p_query.project.pk)+"_Admin":
                    permission="Admin"

        else:
            permission=None
        if not end_point.sub_df:
            df = QueryExcecute(p_query)

            df_columns = df.columns.tolist()
            metadata = ProjectMetaData.objects.get(project=p_query.project)
            if metadata.date_column_name and metadata.date_column_name in df_columns:
                df[metadata.date_column_name] = df[metadata.date_column_name].astype(str)
            result_json = df.to_json(orient='index')

            update = ProjectEndPoint.objects.filter(pk=end_point.pk).update(sub_df=result_json)

        else:
            ##print("loading from json ")
            json_st = json.loads(end_point.sub_df)
            # ##print("THE TYPE OF JSON FILE<",type(json_st))
            json_df = pd.DataFrame(json_st)
            df = json_df.transpose()
            df_columns     = df.columns.tolist()

            metadata = ProjectMetaData.objects.get(project=p_query.project)
            for key, value in metadata.meta_data.items():
                if key in df_columns:
                    ##print("key",key)
                    if value['dtype'] == 'int':
                        df[key] =pd.to_numeric(df[key])
                        if key in df_columns:
                            df[key] = pd.to_numeric(df[key])
                    elif value['dtype'] == 'float':
                        ##print("final key",key,df[key],df[key].dtypes)
                        df[key] = pd.to_numeric(df[key])
                        if key in df_columns:
                            df[key] = pd.to_numeric(df[key])
                    elif value['dtype'] == 'object':
                        df[key] = df[key].astype(str)
                        if key in df_columns:
                            df[key] = df[key].astype(str)
                    elif value['dtype'] == 'bool':
                        df[key] = df[key].astype(bool)
                        if key in df_columns:
                            df[key] = df[key].astype(bool)
                    elif value['dtype'] == 'DateTime':
                        df[key] =pd.to_datetime(df[key])
                        ##print("the data key",df[key].dtypes,df[key])
                        if key in df_columns:
                            df[key] = pd.to_datetime(df[key])


        # for column in df_columns:
        #     try:

        #         df[column] = pd.to_numeric(df[column])
        #     except:
        #         pass


        # t_df = res_df.T
        # ##print("the visulization columns",df)
        df_columns     = df.columns.tolist()
        feature_columns = df.select_dtypes(include=['object','bool','number'])
        # for column in df_columns:
        #     try:
        #         df[column] = pd.to_numeric(df[column])
        #     except:
        #         pass
        number_columns = df.select_dtypes(include=['number'])
        string_columns = df.select_dtypes(include =['object','bool'])
        if metadata.date_column_name and metadata.date_column_name in df_columns:
            ##print("the date time ais",df[metadata.date_column_name],df[metadata.date_column_name])
            df[metadata.date_column_name] = df[metadata.date_column_name].astype(str)


        res_df__table_content = df.to_html(classes="table table-striped tableFixHead",border="0")
        df_columns     = df.columns.tolist()
        row_count = df.shape[1]
        column_count = df.shape[0]
        plot_type=request.POST.get('plot_type',None)
        x_2d = request.POST.get('x_2d',None)
        y_2d = request.POST.get('y_2d',None)
        color_2d = request.POST.get('color_2d',None)
        x_3d = request.POST.get('x_3d',None)
        y_3d = request.POST.get('y_3d',None)
        color_3d = request.POST.get('color_3d',None)
        z = request.POST.get('z',None)
        size = request.POST.get('size',None)
        hover_name = request.POST.get('hover_name',None)
        names= request.POST.get('pie_chart_name_options',None)
        values = request.POST.get('pie_chart_value_name',None)
        x_bubble_plot = request.POST.get('x_bubble_plot',None)
        y_bubble_plot = request.POST.get('y_bubble_plot',None)
        bubble_plot_color = request.POST.get('bubble_plot_color',None)
        x_time_series    =   request.POST.get('x_time_series',None)
        y_time_series    =   request.POST.get('y_time_series',None)
        orientation = request.POST.get('orientation',None)
        heatmap_x   = request.POST.get('heatmap_x',None)
        heatmap_y   = request.POST.get('heatmap_y',None)
        cat_x       = request.POST.get('cat_x',None)
        cat_y       = request.POST.get('cat_y',None)
        cat_color   = request.POST.get('cat_color',None)
        count_x     = request.POST.get('count_x',None)
        count_color = request.POST.get('count_color',None)
        facet_col   = request.POST.get('facet_col',None)
        bar_x = request.POST.get('bar_x',None)
        bar_y = request.POST.get('bar_y',None)
        bar_color = request.POST.get('bar_color',None)
        h_bar_x = request.POST.get('h_bar_x',None)
        h_bar_y = request.POST.get('h_bar_y',None)
        h_bar_color = request.POST.get('h_bar_color',None)


        ##print("color choosen",color_3d,color_2d,x_2d,y_2d,x_bubble_plot,y_bubble_plot,size)
        if count_x and  count_color:
            x= count_x
            color_2d = count_color
            y=None
        elif count_x:
            x= count_x
            y=None
        elif bar_x and bar_y and bar_color:
            x = bar_x
            y = bar_y
            color_2d = bar_color
        elif bar_x and bar_y :
            x = bar_x
            y = bar_y
        elif h_bar_x and h_bar_y and h_bar_color:
            x = h_bar_x
            y = h_bar_y
            color_2d = h_bar_color
        elif h_bar_x and h_bar_y:
            x = h_bar_x
            y = h_bar_y

        elif cat_x and cat_y and cat_color and facet_col:
            x = cat_x
            y = cat_y
            facet_col = facet_col
        elif cat_x and cat_y and facet_col:
            x = cat_x
            y = cat_y
            facet_col = facet_col
        elif cat_x and cat_y and  facet_col:
            cat_x = cat_x
            cat_y = cat_y
            facet_col = facet_col
        elif heatmap_x and heatmap_y:
            x= heatmap_x
            y= heatmap_y


        elif  x_bubble_plot and y_bubble_plot and bubble_plot_color :
            x=x_bubble_plot
            y=y_bubble_plot
            color_2d = bubble_plot_color
            ##print("color choosen",color_3d,color_2d,x_2d,y_2d,x_bubble_plot,y_bubble_plot)

        elif  x_bubble_plot and y_bubble_plot:
            x=x_bubble_plot
            y=y_bubble_plot
            color_2d = None
            ##print("color choosen",color_3d,color_2d,x_2d,y_2d,x,y)
        elif  x_time_series and x_time_series  :
            x=x_time_series
            y=y_time_series
            color = None
        elif x_2d and y_2d and color_2d:
            x=x_2d
            y=y_2d
            color = color_2d
        elif x_2d and y_2d:
            x=x_2d
            y=y_2d

        elif x_3d and y_3d and color_3d:
            x=x_3d
            y=y_3d
            color = color_3d
        elif x_3d and y_3d:
            x=x_3d
            y=y_3d
        else:
            x=None
            y=None
            color = None
        if plot_type and end_point.plot:
            ##print("the plot",plot_type)

            end_point_obj = EndPointPlot(df,end_point.pk)
            if color_2d:
                div = end_point_obj.update_plot(end_point.plot,plot_type,x=x,y=y,z=z,color=color_2d,legend=end_point.plot.legend,size=size,hover_name=hover_name,values=values,names=names,orientation=orientation,facet_col=facet_col)
            elif color_3d:
                div = end_point_obj.update_plot(end_point.plot,plot_type,x=x,y=y,z=z,color=color_3d,legend=end_point.plot.legend,size=size,hover_name=hover_name,values=values,names=names,orientation=orientation,facet_col=facet_col)
            else:
                div = end_point_obj.update_plot(end_point.plot,plot_type,x=x,y=y,z=z,legend=end_point.plot.legend,size=size,hover_name=hover_name,values=values,names=names,orientation=orientation)

        elif end_point.plot and  end_point.plot.plot_type:
            ##print("the plot",plot_type)

            end_point_obj = EndPointPlot(df,end_point.pk)
            div = end_point_obj.plot(plot)
        elif not end_point.plot:
            ##print("the plot",plot_type)

            end_point_obj = EndPointPlot(df,end_point.pk)
            if color_2d:

                div = end_point_obj.create_plot(plot_type,x=x,y=y,z=z,color=color_2d,size=size,hover_name=hover_name,values=values,names=names,orientation=orientation,facet_col=facet_col)
            elif color_3d :
                div = end_point_obj.create_plot(plot_type,x=x,y=y,z=z,color=color_3d,size=size,hover_name=hover_name,values=values,names=names,orientation=orientation,facet_col=facet_col)
            else:
                div = end_point_obj.create_plot(plot_type,x=x,y=y,z=z,size=size,hover_name=hover_name,values=values,names=names,orientation=orientation,facet_col=facet_col)


        else:
            # fig = px.scatter_matrix(df)
            # div = opy.plot(fig, auto_open=False, output_type='div')
            div = True
        # print`e("thediv is ",div)
        if end_point.algorithm:
            features_text = end_point.algorithm.feature
            features_text = features_text.replace('[', '')
            features_text = features_text.replace(']', '')
            features      = features_text.split(',')
            features_ml_display = features_text.split(',')
            ##print("features",features)

            test_l =[]
            features_cat_dict = {}
            ml_df = pd.DataFrame()
            for column in features:
                ml_df[column] = df[column]

            ml_string_columns = ml_df.select_dtypes(include =['object','bool'])
            ##print("the ml string columns ",ml_string_columns)




            ##print("after ml df ",ml_df)
            for column in ml_string_columns:
                if ml_df[column].dtypes  == np.bool:
                    ##print("the data value",df[column],column)


                    column_name = column +'_cat'
                    d = {}

                    new_df = pd.DataFrame()
                    new_df[column] = pd.unique(df[column])

                    column_name = column+'_cat'
                    new_df[column] = new_df[column].astype('category')
                    new_df[column_name] = new_df[column].cat.codes
                    c_series = new_df[column]
                    c_cat_series = new_df[column_name]
                    c_list = c_series.tolist()
                    c_cat_list = c_cat_series.tolist()
                    ##print("new_df",new_df)

                    for i in range(0,len(c_list)):
                        d[c_list[i]]=c_cat_list[i]
                    features_cat_dict[column]=d
                    ##print("features",features_cat_dict)
                    features.remove(column)
                    ##print("features",features)



                else:
                    try:

                        ml_df[column] = ml_df[column].astype(float)
                        ##print("in float type column is",column,ml_df[column])
                    except:

                        d = {}

                        new_df = pd.DataFrame()
                        new_df[column] = pd.unique(df[column])

                        column_name = column+'_cat'
                        new_df[column] = new_df[column].astype('category')
                        new_df[column_name] = new_df[column].cat.codes
                        c_series = new_df[column]
                        c_cat_series = new_df[column_name]
                        c_list = c_series.tolist()
                        c_cat_list = c_cat_series.tolist()
                        ##print("new_df",new_df)

                        for i in range(0,len(c_list)):
                            d[c_list[i]]=c_cat_list[i]
                        features_cat_dict[column]=d
                        ##print("features",features_cat_dict)
                        features.remove(column)
                        ##print("features",features)



            target   = end_point.algorithm.y_factor
            model_id = end_point.algorithm.model_id
            if end_point.algorithm.type_of_prediction == 'Linear':
                accuracy = ast.literal_eval(end_point.algorithm.accuracy)
                MAE = accuracy['MAE']
                MSE = accuracy['MSE']
                RMSE = accuracy['RMSE']
                accuracy_list = {'MAE':MAE,'MSE':MSE,'RMSE':RMSE}
            else:
                accuracy_list={'accuracy':end_point.algorithm.accuracy}
        else:
            features_ml_display=[]
            features_cat_dict={}
            features = None
            target = None
            model_id = None
            accuracy_list = None
        if end_point_update:
            non_query_object = {}
            if end_point.alignment_object:


                non_query_object = {}
                if all('query' not in elem.values() for elem in end_point.alignment_object.values()):
                    non_query_object['query']=True
                if all('table' not in elem.values() for elem in end_point.alignment_object.values()):
                    non_query_object['table']=True
                if all('plot' not in elem.values() for elem in end_point.alignment_object.values()):
                    non_query_object['plot']=True
                if all('ml' not in elem.values() for elem in end_point.alignment_object.values()):
                    non_query_object['ml']=True
                if all('cp' not in elem.values() for elem in end_point.alignment_object.values()):
                    non_query_object['cp']=True
                ##print(non_query_object)
                context = {'features_ml_display':features_ml_display,'features_cat_dict':features_cat_dict,'graph':div,'ep_form':ep_form,'end_point':end_point,'query':res_df__table_content,'permission':permission,'row_count':row_count,'column_count':column_count,'string_columns':string_columns,'df_columns':df_columns,'non_query_object':non_query_object,'form':dashboard_form,'feature_columns':feature_columns,'number_columns':number_columns}
            else:
                context = {'features_ml_display':features_ml_display,'features_cat_dict':features_cat_dict,'features':features,'target':target,'model_id':model_id,'accuracy_list':accuracy_list,'graph':div,'end_point':end_point,'query':res_df__table_content,'permission':permission,'row_count':row_count,'column_count':column_count,'string_columns':string_columns,'df_columns':df_columns,'dashboards_form':dashboard_form,'feature_columns':feature_columns,'number_columns':number_columns}
            return render(request,'dashboard/project_end_point_edit.html',context)
        else:

            context = {'features_ml_display':features_ml_display,'features_cat_dict':features_cat_dict,'features':features,'target':target,'model_id':model_id,'accuracy_list':accuracy_list,'graph':div,'ep_form':ep_form,'end_point':end_point,'query':res_df__table_content,'permission':permission,'row_count':row_count,'column_count':column_count,'string_columns':string_columns,'df_columns':df_columns,'dashboards_form':dashboard_form,'feature_columns':feature_columns,'number_columns':number_columns}
            return render(request,'dashboard/project_end_point.html',context)

class ProjectCreateAjax(View):

    def post(self,request):
        title = request.POST.get('title',None)
        color = request.POST.get('color',None)
        description = request.POST.get('description',None)
        industry = request.POST.get('industry',None)
        project_duration = request.POST.get('project_duration',None)
        end_goal = request.POST.get('end_goal',None)
        customer = Customer.objects.get(user=request.user)

        if title and industry:

            if ProjectType.objects.filter().exists():
                project_type = ProjectType.objects.latest('id')
                ID = str(project_type.pk)
                ID = "BR-"+ID
            else:
                ID = "BR-01"
            if Project.objects.filter(Q(admin_user=request.user) & Q(name__exact = title)).exists():
                data = {'error_msg':'PROJECT TITLE ASSOCIATED WITH ANOTHER PROJECT USE DIFFRENT PROJECT TITLE' }
                ##print(data)
                return JsonResponse(data,safe=False)
            else:
                if customer.type == 'Individual':
                    count = Project.objects.filter(admin_user=request.user).count()
                else:
                    count = 0
                if count > 1:
                    data = {'error_msg':'Individual Account is Allowed to Create only one Project' }
                    return JsonResponse(data,safe=False)

                else:
                    industry = IndustryChoices.objects.get(pk=int(industry))
                    title = title+'_cancelled'
                    project_type = ProjectType.objects.create(project_id=ID,
                                                            industry_name=industry,
                                                            description=description,
                                                            color_code=color)
                    project,create = Project.objects.get_or_create(name=title,
                                                    type=project_type,
                                                    admin_user=request.user,
                                                    project_duration= project_duration,
                                                    end_goal=end_goal)
                    data = {'id':project.pk}
                    ##print(data)
                    return JsonResponse(data,safe=False)
        data = {'error_msg':'PLEASE FILL ALL THE FIELDS AND PROCEED!' }
        return JsonResponse(data,safe=False)


def file_read_ajax(request):
    ##print("inside upload file function")
    process = psutil.Process(os.getpid())
    # logging.info('Memory when read file started: ' + str(process.memory_info().rss/1000000))
    read_post_start_time = datetime.now()
    # logging.info("the read file start time"+str(read_post_start_time))
    form = FormFile(request.POST,request.FILES)
    project_pk = request.POST['project']

    project = Project.objects.get(pk=int(project_pk))
    multiple_files  = request.FILES.getlist('files')
    api          =  request.POST.get('api',None)
    frequency   = request.POST.get('frequency',None)
    credential=request.FILES.get("credential",None)
    cron_frequency = request.POST.get('cron_frequency',None)
    spread_sheet_id=request.POST.get("spreadsheet_id",None)
    data_range =  request.POST.get("data_range",None)
    # print("the post is",request.POST)
    url = request.POST.get('url',None)

    files_content = {}

    if len(multiple_files)==1:

        ##print("single file")
        file= multiple_files[0]
        file_name = str(file)
        data ={}
        files_content[file_name]={}
        project_file,create = ProjectFilename.objects.get_or_create(project=project,file_name=file_name)
        project_file.file = file
        project_file.save()
        project_file = ProjectFilename.objects.get(project=project)
        del file
        with open(project_file.file.url,'r',encoding = 'utf-8') as f:


            read_file_start_time = datetime.now()
            file = {project_file.file_name:f }    
            logging.info("the read file"+str(f))
            read_content_obj= ReadFileLines(file)
            data = read_content_obj.read_file_content()
            read_file_end_time = datetime.now()
        # logging.info("the read file start time"+str(read_post_start_time)+str(read_file_start_time)+str(read_file_end_time))
        try:
            # logging.error("file read error")
            data['error_msg']
            #gc.collect()
            return JsonResponse(data,safe=False)
        except :
            logging.info("the data precessed")
            file_count = len(multiple_files)
            data = {'files_content':data['file_content'],'file_count':file_count}
           
            # logging.info('Memory when read file completed' + str(process.memory_info().rss/1000000))
            #gc.collect()
            return JsonResponse(data,safe=False)

    elif len(multiple_files)>1:
        read_content_obj= ReadFileLines(multiple_files)
        data = read_content_obj.read_file_content()
        try:
            data['error_msg']
            data = {'error_msg':"Wrong format files"}
            ##print(data)
            #gc.collect()
            return JsonResponse(data,safe=False)
        except:



            if data['file_content']:

                # l= []
                # file_content = data['file_content']
                # for key,value in  data['file_content'].items():
                #     if value['file_check_sum'] not in l:
                #         l.append(value['file_check_sum'])
                #     else:
                #         data={'error_msg':"duplicate files"}
                #         return JsonResponse(data,safe=False)
                file_count = len(multiple_files)
                data = {'files_content':data['file_content'],'file_count':file_count}
                ##print(data)
                #gc.collect()
                return JsonResponse(data,safe=False)
    if api and frequency:
        data = {'success':True}
        #gc.collect()
        return JsonResponse(data,safe=False)
    if credential and spread_sheet_id:
        data = {'success':True}
        #gc.collect()
        return JsonResponse(data,safe=False)
    if cron_frequency and url:
        data = {'success':True}
        #gc.collect()
        return JsonResponse(data,safe=False)


def file_upload(request):
    process = psutil.Process(os.getpid())
    logging.info('Memory when file upload get started: ' + str(process.memory_info().rss/1000000))
    nan_post_start_time = datetime.now()
    # logging.info("file upload"+str(nan_post_start_time))
    form = FormFile(request.POST,request.FILES)
    project_pk = request.POST['project']

    time_series_column = request.POST.get('time_series_column',None)

    project = Project.objects.get(pk=int(project_pk))
    multiple_files  = request.FILES.getlist('files')
    api = request.POST.get('api',None)
    frequency = request.POST.get('frequency',None)
    basic_token = request.POST.get('basic_token',None)
    sheet_name = request.POST.get('sheet_name',None)
    api_name = request.POST.get('api_name',None)
    credential=request.FILES.get("credential",None)
    url = request.POST.get('url',None)
    cron_frequency = request.POST.get('cron_frequency',None)
    spread_sheet_id=request.POST.get("spreadsheet_id",None)
    data_range =  request.POST.get("data_range",None)
    header = request.POST.get('header',None)

    files = []
    files_separators  = {}
    files_heders ={}
    if len(multiple_files)>0:
        # logging.info("files"+str(multiple_files))
        # gen_obj = listgenerator(multiple_files)
        # condition= True
        # while condition:
        #     try:

        #         file = next(gen_obj)
        #     except StopIteration:
        #         condition = False
        project_files = ProjectFilename.objects.filter(project=project)
        files = {}
        for project_file  in project_files:

            
            
            file_name = str(project_file.file_name)

            file_separator = request.POST.get(file_name+'_separator',None)
            file_header_status = request.POST.get(file_name+'_header_status',None)
            file_header = request.POST.get(file_name+'_header',None)
            file_header_row = request.POST.get(file_name+'_header_row',None)
            # files.append(file)
            files[file_name]= project_file.file.url
            files_separators[file_name] = file_separator
            files_heders[file_name] = {'header_status':file_header_status,'columns':file_header,'file_header_row':file_header_row}

        file_read_obj = FileReader()
        nan_read_start_time = datetime.now()
        # logging.info("file upload"+str(nan_post_start_time)+str(nan_read_start_time)
        logging.info(f"the content{files}{files_separators}{files_heders}")
        dfs = file_read_obj.readfile(files,files_separators,files_heders)
        # logging.info("file upload"+str(nan_post_start_time)+str(nan_read_start_time)+str(nan_read_end_time))
        try:
            if dfs['Error']:

                data ={'error_msg':"Please Convert csv to utf-8 format"}
                return JsonResponse(data,safe=False)
        except:
            nan_data_start_time = datetime.now()
            # logging.info("file upload"+str(nan_post_start_time)+str(nan_data_start_time))
            all_df=[]

            for key, val in dfs.items():
                all_df.append(val)

            column_conbine_obj = ColumnCombine()
            data = column_conbine_obj.list_combine_with_datatype(dfs)
            nan_data_end_time = datetime.now()
            # logging.info("file upload"+str(nan_post_start_time)+str(nan_data_start_time)+str(nan_data_end_time))
            try:
                error = data['Error']
                data = {'error_msg':all_columns['error']}
                # ##print("error",data)
                #gc.collect()
                del dfs
                return JsonResponse(data,safe=False)


            except:
                data = column_conbine_obj.list_combine_with_datatype(dfs)
                ##print("the data for metadata collection is",data)
                #gc.collect()
                del dfs
                return JsonResponse(data,safe=False)
            

            return JsonResponse(data, safe=False)
    elif api and frequency:
        if basic_token:

            headers = {'content-type': 'application/json',
                       'Authorization': basic_token}

            JSONContent = requests.get(api,

                                       headers=headers, verify=True)
        else:
            headers = {'content-type': 'application/json',
                       }

            JSONContent = requests.get(api,
                                       headers=headers, verify=True)
        if 'error' not in JSONContent:
            data_str = JSONContent.text
            data_str = JSONContent.text
            data_json = json.loads(data_str)
            # ##print("type", data_json['results'])
            try:
                df = pd.json_normalize(data_json['results'])
            except:
                df = pd.json_normalize(data_json['data'])
            columns = df.columns.tolist()
            all_columns = {}
            column_nan = {}
            df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '').str.replace('.', '_').str.replace(',','_').str.replace('/','_').str.replace(':','')
            columns = df.columns.tolist()
            gen_obj  =listgenerator(columns)
            condition = True
            while  True:
                try:
                    c = next(gen_obj)
                except StopIteration:
                    condition = False
                count = str(df[c].isnull().sum())
                column_nan[c]= count
                if df.dtypes[c ] == np.int64:
                    all_columns[c] = 0
                elif df.dtypes[c ] == np.float64:
                    all_columns[c] = 0.0
                elif df.dtypes[c ] == np.object:
                    all_columns[c] = "None"
                elif df.dtypes[c] == np.bool:
                    all_columns[c] = "None"
                elif np.issubdtype(df[c].dtype, np.datetime64):
                    all_columns[c] = "None"
                    df[c] = df[c].astype('str')
            


            if time_series_column and not time_series_column == 'no-time-series':
                try:

                    df[time_series_column]=df[time_series_list].astype(str)
                    df[time_series_column] = pd.to_datetime(df[time_series_column])
                    df = df.sort_values(by=[time_series_column])
                    data = {'all_columns':all_columns}
                    #gc.collect()
                    return JsonResponse(data,safe=False)
                except:
                    data={'error_msg':"Wrong column Selection for TimeSeries"}
                    # ##print("error",data)
                    return JsonResponse(data,safe=False)

            else:
                data = {'all_columns':all_columns,'column_nan':column_nan}
                #gc.collect()
                return JsonResponse(data,safe=False)
    elif credential and spread_sheet_id:
        ##print("called for google sheet")
        sheet_details = CustomerAPIDetails.objects.get(project=project)
        scope=['htps://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
        file = sheet_details.credentials.open()
        file_content = file.read()
        js_str = json.loads(file_content.decode('utf-8'))
        creadentials = ServiceAccountCredentials.from_json_keyfile_dict(js_str)
        gs = gspread.authorize(creadentials)
        wks = gs.open(spread_sheet_id).sheet1
        data = wks.get_all_records()
        df = pd.DataFrame(data)


        try:
            scope=['htps://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
            file = sheet_details.credentials.open()
            file_content = file.read()
            js_str = json.loads(file_content.decode('utf-8'))
            creadentials = ServiceAccountCredentials.from_json_keyfile_dict(js_str)
            gs = gspread.authorize(creadentials)
            wks = gs.open(spread_sheet_id).sheet1
            data = wks.get_all_records()
            df = pd.DataFrame(data)
        except:
            data={'error_msg':"Wrong column Selection for TimeSeries"}
            # ##print("error",data)
            #gc.collect()
            return JsonResponse(data,safe=False)


        columns = df.columns.tolist()
        all_columns  = {}
        all_columns = {}
        column_nan = {}
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '').str.replace('.', '_').str.replace(',','_').str.replace('/','_').str.replace(':','')
        columns = df.columns.tolist()

        gen_obj  =listgenerator(columns)
        condition = True
        while  True:
            try:
                c = next(gen_obj)
            except StopIteration:
                condition = False
            count = str(df[c].isnull().sum())
            column_nan[c]= count
            if df.dtypes[c ] == np.int64:
                all_columns[c] = 0
            elif df.dtypes[c ] == np.float64:
                all_columns[c] = 0.0
            elif df.dtypes[c ] == np.object:
                all_columns[c] = "None"
            elif df.dtypes[c] == np.bool:
                all_columns[c] = "None"
            elif np.issubdtype(df[c].dtype, np.datetime64):
                all_columns[c] = "None"
                df[c] = df[c].astype('str')
        logging.info("the columns are",str(all_columns)+str(column_nan))
        data = {'all_columns':all_columns,'column_nan':column_nan}
        #gc.collect()
        # return JsonResponse(data,safe=False)
    elif url and cron_frequency:
        try:
            if header:
                df = pd.read_html(url,encoding='utf8',index_col=0,header=int(header))
            else:
                df = pd.read_html(url,encoding='utf8',index_col=0,header=1)
        except:
            data={'error_msg':"Wrong column Selection for TimeSeries"}
            # ##print("error",data)
            #gc.collect()
            # return JsonResponse(data,safe=False)

        df=df[0]
        columns = df.columns.tolist()
        all_columns  = {}
        all_columns = {}
        column_nan = {}
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '').str.replace('.', '_').str.replace(',','_').str.replace('/','_').str.replace(':','')
        columns = df.columns.tolist()
        # logging.info("the final columns are"+str(columns))
       
        gen_obj  =listgenerator(columns)
        condition = True
        while  condition:
            try:
                c = next(gen_obj)
            except StopIteration:
                condition = False

            count = str(df[c].isnull().sum())
            column_nan[c]= count
            if df.dtypes[c ] == np.int64:
                all_columns[c] = 0
            elif df.dtypes[c ] == np.float64:
                all_columns[c] = 0.0
            elif df.dtypes[c ] == np.object:
                all_columns[c] = "None"
            elif df.dtypes[c] == np.bool:
                all_columns[c] = "None"
            elif np.issubdtype(df[c].dtype, np.datetime64):
                all_columns[c] = "None"
                
        logging.info("the columns are"+str(all_columns)+str(column_nan))
        data = {'all_columns':all_columns,'column_nan':column_nan}
        #gc.collect()
        return JsonResponse(data,safe=False)










class EndpointPlotLegend(GroupRequiredMixin,LoginRequiredMixin,View):
    ''' class to customisation of query visualisation'''
    def dispatch(self, request, *args, **kwargs):
        pk = kwargs['pk']
        end_point = ProjectEndPoint.objects.get(pk=pk)
        project=Project.objects.get(pk=end_point.project.pk)
        piqu,create = ProjectBillingPrms.objects.get_or_create(project=project)
        update = ProjectBillingPrms.objects.filter(project=project).update(query_count=piqu.query_count+1)
        pk= str(project.pk)
        self.login_url = '/customer/login/'
        self.redirect_field_name = 'redirect_to'
        self.template_name='dashboard/index.html'
        admin_name = pk+"_Admin"
        ##print(type(admin_name), admin_name)
        admin_encode_name = admin_name.encode()
        admin_unicode_name = admin_encode_name.decode('utf-8')
        write_name = pk+"_Write"
        ##print(type(write_name), write_name)
        write_encode_name = write_name.encode()
        write_unicode_name = write_encode_name.decode('utf-8')
        read_name = pk+"_Read"
        ##print(type(read_name), read_name)
        read_encode_name = read_name.encode()
        read_unicode_name = read_encode_name.decode('utf-8')
        delete_name = pk+"_Delete"
        ##print(type(delete_name), delete_name)
        delete_encode_name = delete_name.encode()
        delete_unicode_name = delete_encode_name.decode('utf-8')
        l =[delete_unicode_name,write_unicode_name,admin_unicode_name,read_unicode_name]
        self.group_required= l
        ##print("the self of dispatcher",self.group_required)

        return super(EndpointPlotLegend, self).dispatch(request, *args, **kwargs)
    def post(self,request,pk):
        end_point = ProjectEndPoint.objects.get(pk=pk)
        p_query = end_point.query
        dashboard_form = ProjectDashboardForm(initial={'project':p_query.project.pk})
        dashboard_form.fields['user'].queryset = ProjectUser.objects.filter(project=p_query.project)
        dashboard_form.fields['dashboard'].queryset = ProjectDashboard.objects.filter(project=p_query.project)
        if Project.objects.filter(pk=p_query.project.pk,admin_user=request.user).exists():
            permission="Admin"
        elif ProjectUser.objects.filter(project=p_query.project,project_user=request.user).exists():
            user_group = User.objects.get(pk=request.user.pk)

            for g in user_group.groups.all():
                if g.name == str(p_query.project.pk)+"_Read":
                    permission="Read"
                elif g.name == str(p_query.project.pk)+"_Write":
                    permission="Write"
                elif g.name == str(p_query.project.pk)+"_Delete":
                    permission="Delete"
                elif g.name == str(p_query.project.pk)+"_Admin":
                    permission="Admin"
        else:
            permission=None
        if not end_point.sub_df:
            df = QueryExcecute(p_query)

            df_columns = df.columns.tolist()
            metadata = ProjectMetaData.objects.get(project=p_query.project)
            if metadata.date_column_name and metadata.date_column_name in df_columns:
                df[metadata.date_column_name] = df[metadata.date_column_name].astype(str)
            result_json = df.to_json(orient='index')

            update = ProjectEndPoint.objects.filter(pk=end_point.pk).update(sub_df=result_json)

        else:
            ##print("loading from json ")
            json_st = json.loads(end_point.sub_df)
            # ##print("THE TYPE OF JSON FILE<",type(json_st))
            json_df = pd.DataFrame(json_st)
            df = json_df.transpose()
            df_columns     = df.columns.tolist()

            metadata = ProjectMetaData.objects.get(project=p_query.project)
            for key, value in metadata.meta_data.items():
                if key in df_columns:
                    ##print("key",key)
                    if value['dtype'] == 'int':
                        df[key] =pd.to_numeric(df[key])
                        if key in df_columns:
                            df[key] = pd.to_numeric(df[key])
                    elif value['dtype'] == 'float':
                        ##print("final key",key,df[key],df[key].dtypes)
                        df[key] = pd.to_numeric(df[key])
                        if key in df_columns:
                            df[key] = pd.to_numeric(df[key])
                    elif value['dtype'] == 'object':
                        df[key] = df[key].astype(str)
                        if key in df_columns:
                            df[key] = df[key].astype(str)
                    elif value['dtype'] == 'bool':
                        df[key] = df[key].astype(bool)
                        if key in df_columns:
                            df[key] = df[key].astype(bool)
                    elif value['dtype'] == 'DateTime':
                        df[key] =pd.to_datetime(df[key])
                        ##print("the data key",df[key].dtypes,df[key])
                        if key in df_columns:
                            df[key] = pd.to_datetime(df[key])
        number_columns = df.select_dtypes(include=['number'])
        string_columns = df.select_dtypes(include =['object','bool'])
        feature_columns = df.select_dtypes(include =['object','bool','number'])
        if metadata.date_column_name and metadata.date_column_name in df_columns:
            df[metadata.date_column_name] = df[metadata.date_column_name].astype(str)
        df_columns     = df.columns.tolist()
        row_count = df.shape[1]
        res_df__table_content = df.to_html(classes="table table-striped tableFixHead",border="0")
        column_count = df.shape[0]
        if end_point.plot and end_point.plot.plot_type:
            if end_point.plot.legend == True:
                update =Plot.objects.filter(pk=end_point.plot.pk).update(legend=False)
            elif end_point.plot.legend == False:
                update =Plot.objects.filter(pk=end_point.plot.pk).update(legend=True)
            end_point_obj = EndPointPlot(df,end_point.pk)
            plot = Plot.objects.get(pk=end_point.plot.pk)
            div = end_point_obj.plot(plot)

        else:
            # fig = px.scatter_matrix(df)
            # div = opy.plot(fig, auto_open=False, output_type='div')
            div = True
        dashboards_form = ProjectDashboardsForm(initial={'project':end_point.project.pk})
        if end_point.algorithm:
            features_text = end_point.algorithm.feature
            features_text = features_text.replace('[', '')
            features_text = features_text.replace(']', '')
            features      = features_text.split(',')
            test_l =[]
            for column in features:

                test_l.append(column)




            target   = end_point.algorithm.y_factor
            model_id = end_point.algorithm.model_id
            if end_point.algorithm.type_of_prediction == 'Linear':
                accuracy = ast.literal_eval(end_point.algorithm.accuracy)
                MAE = accuracy['MAE']
                MSE = accuracy['MSE']
                RMSE = accuracy['RMSE']
                accuracy_list = {'MAE':MAE,'MSE':MSE,'RMSE':RMSE}
            else:
                accuracy_list={'accuracy':end_point.algorithm.accuracy}
        else:
            features = None
            target = None
            model_id = None
            accuracy_list = None
        context = {'features':features,'target':target,'model_id':model_id,'accuracy_list':accuracy_list,'graph':div,'end_point':end_point,'query':res_df__table_content,'permission':permission,'row_count':row_count,'column_count':column_count,'form':dashboard_form,'string_columns':string_columns,'df_columns':df_columns,'dashboards_form':dashboards_form,'feature_columns':feature_columns,'number_columns':number_columns}
        return render(request,'dashboard/project_end_point.html',context)



def MetadataGet(request,pk):
    process = psutil.Process(os.getpid())
    logging.info('Memory when metadata get started: ' + str(process.memory_info().rss/1000000))
    form = FormFile(request.POST,request.FILES)



    form = FormFile(request.POST,request.FILES)
    project_pk = request.POST['project']

    project = Project.objects.get(pk=int(project_pk))
    multiple_files  = request.FILES.getlist('files',None)
    api = request.POST.get('api',None)
    basic_token = request.POST.get('basic_token',None)
    frequency = request.POST.get('frequency',None)
    credential=request.FILES.get("credential",None)

    url = request.POST.get('url',None)
    cron_frequency = request.POST.get('cron_frequency',None)
    spread_sheet_id=request.POST.get("spreadsheet_id",None)
    data_range =  request.POST.get("data_range",None)
    header = request.POST.get('header',None)


    files = []
    files_separators  = {}
    files_heders ={}
    file_header_row = {}
    if multiple_files:

        # gen_obj = listgenerator(multiple_files)
        # condition = True
        # while condition:
        #     try:

        #         file = next(gen_obj)
        #     except StopIteration:
        #         condition = False
        project_files = ProjectFilename.objects.filter(project=project)
        files = {}
        for project_file  in project_files:

            
            
            file_name = str(project_file.file_name)

            file_separator = request.POST.get(file_name+'_separator',None)
            file_header_status = request.POST.get(file_name+'_header_status',None)
            file_header = request.POST.get(file_name+'_header',None)
            file_header_row = request.POST.get(file_name+'_header_row',None)
            # files.append(file)
            files[file_name]= project_file.file.url
            files_separators[file_name] = file_separator
            files_heders[file_name] = {'header_status':file_header_status,'columns':file_header,'file_header_row':file_header_row}

        file_read_obj = FileReader()
        nan_read_start_time = datetime.now()
        # logging.info("file upload"+str(nan_post_start_time)+str(nan_read_start_time)
        logging.info(f"the content{files}{files_separators}{files_heders}")
        dfs = file_read_obj.readfile(files,files_separators,files_heders)
        try:
            error = dfs['error']
            data ={'error_msg':dfs['error']}
            #gc.collect()
            return JsonResponse(data,safe=True)
        except:

            column_conbine_obj = ColumnCombine()
            time_series_all_columns = column_conbine_obj.time_series_dict_combine(dfs,request)
            if len(dfs) == 1:
                try:
                    error = time_series_all_columns['Error']
                    data = {'error_msg':time_series_all_columns['Error']}
                    return JsonResponse(data,safe=False)
                except:
                    data = {'time_series_all_columns':time_series_all_columns,}
                    del dfs
                    #gc.collect()
                    return JsonResponse(data,safe=True)


            else:
                try:
                    error = time_series_all_columns['Error']
                    data = {'error_msg':time_series_all_columns['Error']}
                    #gc.collect()
                    del dfs
                    return JsonResponse(data,safe=False)


                except:
                    relation_all_columns = column_conbine_obj.relation_dict_combine(dfs,request)
                    try:
                        error = relation_all_columns['Error']
                        data = {'error_msg':relation_all_columns['Error']}
                        #gc.collect()
                        del dfs
                        return JsonResponse(data,safe=False)
                    except:
                        data = {'time_series_all_columns':time_series_all_columns,'relation_all_columns':relation_all_columns}
                        # print("data",data)
                        #gc.collect()
                        del dfs
                        return JsonResponse(data,safe=True)


        return JsonResponse(data,safe=True)
    elif api and frequency:
        if basic_token:

            headers = {'content-type': 'application/json',
                       'Authorization': basic_token}

            JSONContent = requests.get(api,

                                       headers=headers, verify=True)
        else:
            headers = {'content-type': 'application/json',
                       }

            JSONContent = requests.get(api,
                                       headers=headers, verify=True)
        if 'error' not in JSONContent:
            data_str = JSONContent.text
            data_str = JSONContent.text
            data_json = json.loads(data_str)
            # ##print("type", data_json['results'])
            try:
                df = pd.json_normalize(data_json['results'])
            except:
                df = pd.json_normalize(data_json['data'])

            df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '').str.replace('.', '_').str.replace(',','_').str.replace('/','_').str.replace(':','')
            time_series_all_columns = df.columns.tolist()
            gen_obj = listgenerator(time_series_all_columns)
            condition = True
            while  condition:
                try:
                    colum = next(gen_obj)
                except StopIteration:
                    condition = False
                
                colum = next(gen_obj)
                try:
                    cu =  colum+'_select'
                    missing_data = request.POST[cu]
                    if missing_data == 'delete_column':

                        time_series_all_columns.remove(colum)

                except:
                    pass
            



            ##print("columns are ",time_series_all_columns)
            data = {'time_series_all_columns':time_series_all_columns,}
            #gc.collect()
            return JsonResponse(data,safe=True)
        else:
            error = "Error in Reading Api"
            data ={'error_msg':error}
    elif credential and spread_sheet_id:
        sheet_details= CustomerAPIDetails.objects.get(project=project)


        try:
            scope=['htps://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
            file = sheet_details.credentials.open()
            file_content = file.read()
            js_str = json.loads(file_content.decode('utf-8'))
            creadentials = ServiceAccountCredentials.from_json_keyfile_dict(js_str)
            gs = gspread.authorize(creadentials)
            wks = gs.open(spread_sheet_id).sheet1
            data = wks.get_all_records()
            df = pd.DataFrame(data)
        except:
            data={'error_msg':"Wrong column Selection for TimeSeries"}
            # ##print("error",data)
            #gc.collect()
            return JsonResponse(data,safe=False)
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '').str.replace('.', '_').str.replace(',','_').str.replace('/','_').str.replace(':','')
        time_series_all_columns = df.columns.tolist()
        gen_obj = listgenerator(time_series_all_columns)
        condition = True
        while condition:
            try:

                colum = next(gen_obj)
            except StopIteration:
                condition = False
            
            
            try:
                cu =  colum+'_select'
                missing_data = request.POST[cu]
                if missing_data == 'delete_column':
                    time_series_all_columns.remove(colum)
            except:
                pass
        ##print("columns are ",time_series_all_columns)
        data = {'time_series_all_columns':time_series_all_columns,}
        #gc.collect()
        return JsonResponse(data,safe=True)
    elif url and cron_frequency:
        try:
            if header:
                df = pd.read_html(url,encoding='utf8',index_col=0,header=int(header))
            else:
                df = pd.read_html(url,encoding='utf8',index_col=0,header=1)
        except:
            data={'error_msg':"Wrong column Selection for TimeSeries"}
            # ##print("error",data)
            #gc.collect()
            return JsonResponse(data,safe=False)
        df=df[0]
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '').str.replace('.', '_').str.replace(',','_').str.replace('/','_').str.replace(':','')
        time_series_all_columns = df.columns.tolist()
        gen_obj = listgenerator(time_series_all_columns)
        condition = True
        while condition:
            try:

                colum = next(gen_obj)
            except StopIteration:
                condition = False
            
            
            try:
                cu =  colum+'_select'
                missing_data = request.POST[cu]
                if missing_data == 'delete_column':
                    time_series_all_columns.remove(colum)
            except:
                pass
        ##print("columns are ",time_series_all_columns)
        data = {'time_series_all_columns':time_series_all_columns,}
        #gc.collect()
        return JsonResponse(data,safe=True)



def RelationCreate(request,pk):
    form = FormFile(request.POST,request.FILES)
    # ##print(form)


    if form.is_valid():
        multiple_files  = request.FILES.getlist('files')
        files= []
        files_separators={}
        files_heders={}

        primarykey = request.POST.get('primarykey_relation',None)
        primarykey_option = request.POST.get('primarykey_relation',None)
        foreignkey = request.POST.get('foreignkey_relation',None)
        if primarykey and foreignkey:
            primarykey_lst= primarykey.split('._:')
            foreignkey_lst= foreignkey.split('._:')
            # ##print("the spplited primarykey", foreignkey_lst)
            js = {'primarykey':{'file':primarykey_lst[0],'column':primarykey_lst[1]},'foreignkey':{'file':foreignkey_lst[0],'column':foreignkey_lst[1]}}
            project = Project.objects.get(pk=pk)

            time_series_filed = request.POST.get('time_series_column',None)

            for file in multiple_files:
                file_name = str(file)

                file_separator = request.POST.get(file_name+'_separator',None)
                file_header_status = request.POST.get(file_name+'_header_status',None)
                file_header = request.POST.get(file_name+'_header',None)
                file_header_row = request.POST.get(file_name+'_header_row',None)
                files.append(file)
                files_separators[file_name] = file_separator
                files_heders[file_name] = {'header_status':file_header_status,'columns':file_header,'file_header_row':file_header_row}
            file_read_obj = FileReader()
            dfs = file_read_obj.readfile(files,files_separators,files_heders)
            duplicate_check_obj =CheckPrimarykey()
            primery_dict = {'file':primarykey_lst[0],'column':primarykey_lst[1]}
            foreign_dict = {'file':foreignkey_lst[0],'column':foreignkey_lst[1]}
            p_k = duplicate_check_obj.primarykey_check(dfs,primery_dict,foreign_dict)
            ##print("print",p_k)
            if p_k:
                if ProjectFileRelationship.objects.filter(project=project,relation=js):
                    error_msg="The Relation Already Exists"
                    relation_list = None
                else:
                    relation, create = ProjectFileRelationship.objects.get_or_create(project=project,relation=js)
                    relation_list = {'column_1':relation.relation['primarykey']['column'],'file_1':relation.relation['primarykey']['file'],'column_2':relation.relation['foreignkey']['column'],'file_2':relation.relation['foreignkey']['file'],'id':relation.pk,'primarykey_option':relation.relation['primarykey']['file']+'._:'+relation.relation['primarykey']['column'],'foreignkey_option':relation.relation['foreignkey']['file']+'._:'+relation.relation['foreignkey']['column']}
                    error_msg=None
            else:
                relation_list = None
                error_msg ="Duplicate PrimaryKey"
            data = {'relation_list':relation_list,'error_msg':error_msg}
            # ##print("the final data",data)
            return JsonResponse(data, safe=False)
        else:
            data = {'error_msg':'Please Select the Primerykey and Foreignkey Before Submit'}
            # ##print("the final data",data)
            return JsonResponse(data, safe=False)
    else:
        data = {'error_msg':'There is Error in Processing'}
        # ##print("the final data",data)
        return JsonResponse(data, safe=False)

def RelationDelete(request,pk):
    relation = ProjectFileRelationship.objects.get(pk=pk)
    delete = ProjectFileRelationship.objects.filter(pk=pk).delete()
    try:
        delete = ProjectFileRelationship.objects.filter(pk=pk).delete()
        data ={'primarykey_option_value':relation.relation['primarykey']['file']+'._:'+relation.relation['primarykey']['column'],'primarykey_option':relation.relation['primarykey']['file']+':'+relation.relation['primarykey']['column'],'foreignkey_option_value':relation.relation['foreignkey']['file']+'._:'+relation.relation['foreignkey']['column'],'foreignkey_option':relation.relation['foreignkey']['file']+':'+relation.relation['foreignkey']['column'],'id':relation.pk}
        # ##print("the d/ata",data)
        return JsonResponse(data, safe=False)
    except:
        data ={'error_msg':'There is an Error Deleting Relation'}

        return JsonResponse(data, safe=False)


class ProjectQueryAlignmentView(GroupRequiredMixin,LoginRequiredMixin,View):
    ''' class to Create Alignment of query for endpoint Create'''
    def dispatch(self, request, *args, **kwargs):
        pk = kwargs['pk']
        query = ProjectQuery.objects.get(pk=pk)
        pk = str(query.project.pk)
        self.login_url = '/customer/login/'
        self.redirect_field_name = 'redirect_to'
        self.template_name='dashboard/index.html'
        admin_name = pk+"_Admin"
        ##print(type(admin_name), admin_name)
        admin_encode_name = admin_name.encode()
        admin_unicode_name = admin_encode_name.decode('utf-8')
        write_name = pk+"_Write"
        ##print(type(write_name), write_name)
        write_encode_name = write_name.encode()
        write_unicode_name = write_encode_name.decode('utf-8')

        delete_name = pk+"_Delete"
        ##print(type(delete_name), delete_name)
        delete_encode_name = delete_name.encode()
        delete_unicode_name = delete_encode_name.decode('utf-8')
        l =[delete_unicode_name,write_unicode_name,admin_unicode_name]
        self.group_required= l
        ##print("the self of dispatcher",self.group_required)

        return super(ProjectQueryAlignmentView, self).dispatch(request, *args, **kwargs)

    def post(self,request,pk):
        query_object = request.POST.get('end_point_object',None)
        if query_object:
            query_object = ast.literal_eval(query_object)
        form = ProjectEndPointForm()
        project_query = ProjectQuery.objects.get(pk=pk)
        project = Project.objects.get(pk=project_query.project.pk)
        piqu,created = ProjectBillingPrms.objects.get_or_create(project=project)
        update = ProjectBillingPrms.objects.filter(project=project).update(query_count=piqu.query_count+1)
        dashboard_form = ProjectDashboardForm(initial={'project':project.pk})
        dashboard_form.fields['user'].queryset = ProjectUser.objects.filter(project=project)
        dashboard_form.fields['dashboard'].queryset = ProjectDashboard.objects.filter(project=project)
        if Project.objects.filter(pk=project.pk,admin_user=request.user).exists():
            permission="Admin"
        elif ProjectUser.objects.filter(project=project,project_user=request.user).exists():
            user_group = User.objects.get(pk=request.user.pk)

            for g in user_group.groups.all():
                if g.name == str(project.pk)+"_Read":
                    permission="Read"
                elif g.name == str(project.pk)+"_Write":
                    permission="Write"
                elif g.name == str(project.pk)+"_Delete":
                    permission="Delete"
                elif g.name == str(project.pk)+"_Admin":
                    permission="Admin"
        else:
            permission=None
        pv= QueryExcecute(project_query)
        string_columns = pv.select_dtypes(include =['object','bool'])
        feature_columns = pv.select_dtypes(include=['object','bool','number'])
        number_columns = pv.select_dtypes(include=['number'])
        metadata=ProjectMetaData.objects.get(project=project_query.project)
        df_columns     = pv.columns.tolist()
        if metadata.date_column_name and metadata.date_column_name in df_columns:
            pv[metadata.date_column_name] = pv[metadata.date_column_name].astype(str)
        df=pv
        df_rows=df.shape[0]
        df_column_count= df.shape[1]
        res_df__table_content = df.to_html(classes="table table-striped tableFixHead",border="0")
        if project_query.plot and project_query.plot.plot_type:
            plot_obj = QueryPlot(df,project_query.pk)
            div = plot_obj.plot(project_query.plot)

        else:
            # fig = px.scatter_matrix(df)
            # div = opy.plot(fig, auto_open=False, output_type='div')
            div = True
        project = Project.objects.get(pk=project_query.project.pk)
        non_query_object = {}
        if query_object:
            non_query_object = {}
            if all('query' not in elem.values() for elem in query_object.values()):
                non_query_object['query']=True
            if all('table' not in elem.values() for elem in query_object.values()):
                non_query_object['table']=True
            if all('plot' not in elem.values() for elem in query_object.values()):
                non_query_object['plot']=True
            if all('ml' not in elem.values() for elem in query_object.values()):
                non_query_object['ml']=True
            if all('cp' not in elem.values() for elem in query_object.values()):
                non_query_object['cp']=True
            ##print(non_query_object)

            context={'form':form,'df_rows':df_rows,'df_column_count':df_column_count,'project':project,'query':res_df__table_content,'dashboard_form':dashboard_form,'permission':permission,'graph':div,'project_query':project_query,'df_columns':df_columns,'string_columns':string_columns,'query_object':query_object,'non_query_object':non_query_object,'feature_columns':feature_columns,'number_columns':number_columns}
            # ##print('the context',context)
        else:
            context={'form':form,'df_rows':df_rows,'df_column_count':df_column_count,'project':project,'query':res_df__table_content,'dashboard_form':dashboard_form,'permission':permission,'graph':div,'project_query':project_query,'df_columns':df_columns,'string_columns':string_columns,'query_object':None,'non_query_object':non_query_object,'feature_columns':feature_columns,'number_columns':number_columns}
        return render(request,'dashboard/project_query.html',context)




class ProjectEndpointEditView(GroupRequiredMixin,LoginRequiredMixin,View):
    ''' class to edit the endpoint'''
    def dispatch(self, request, *args, **kwargs):
        pk = kwargs['pk']
        end_point = ProjectEndPoint.objects.get(pk=pk)
        project=Project.objects.get(pk=end_point.project.pk)

        pk= str(project.pk)
        self.login_url = '/customer/login/'
        self.redirect_field_name = 'redirect_to'
        self.template_name='dashboard/index.html'
        admin_name = pk+"_Admin"
        ##print(type(admin_name), admin_name)
        admin_encode_name = admin_name.encode()
        admin_unicode_name = admin_encode_name.decode('utf-8')
        write_name = pk+"_Write"
        ##print(type(write_name), write_name)
        write_encode_name = write_name.encode()
        write_unicode_name = write_encode_name.decode('utf-8')

        delete_name = pk+"_Delete"
        ##print(type(delete_name), delete_name)
        delete_encode_name = delete_name.encode()
        delete_unicode_name = delete_encode_name.decode('utf-8')
        l =[delete_unicode_name,write_unicode_name,admin_unicode_name]
        self.group_required= l
        ##print("the self of dispatcher",self.group_required)

        return super(ProjectEndpointEditView, self).dispatch(request, *args, **kwargs)
    def get(self,request,pk):
        end_point = ProjectEndPoint.objects.get(pk=pk)
        p_query = end_point.query
        form = ProjectEndPointForm(initial={'end_point_name':end_point.name,'frequency':end_point.sub_df_frequency})
        ep_form = ProjectEndPointForm(initial={'end_point_name':end_point.name,'frequency':end_point.sub_df_frequency})
        piqu,created = ProjectBillingPrms.objects.get_or_create(project=end_point.project)
        update = ProjectBillingPrms.objects.filter(project=end_point.project).update(query_count=piqu.query_count+1)
        dashboard_form = ProjectDashboardForm(initial={'project':p_query.project.pk})
        dashboard_form.fields['user'].queryset = ProjectUser.objects.filter(project=p_query.project)
        dashboard_form.fields['dashboard'].queryset = ProjectDashboard.objects.filter(project=p_query.project)
        if Project.objects.filter(pk=p_query.project.pk,admin_user=request.user).exists():
            permission="Admin"
        elif ProjectUser.objects.filter(project=p_query.project,project_user=request.user).exists():
            user_group = User.objects.get(pk=request.user.pk)

            for g in user_group.groups.all():
                if g.name == str(p_query.project.pk)+"_Read":
                    permission="Read"
                elif g.name == str(p_query.project.pk)+"_Write":
                    permission="Write"
                elif g.name == str(p_query.project.pk)+"_Delete":
                    permission="Delete"
                elif g.name == str(p_query.project.pk)+"_Admin":
                    permission="Admin"
        else:
            permission=None
        if not end_point.sub_df:

            df=QueryExcecute(p_query)
            df_columns = df.columns.tolist()
            metadata = ProjectMetaData.objects.get(project=p_query.project)
            if metadata.date_column_name and metadata.date_column_name in df_columns:
                df[metadata.date_column_name] = df[metadata.date_column_name].astype(str)
            result_json = df.to_json(orient='index')
            update = ProjectEndPoint.objects.filter(pk=end_point.pk).update(sub_df=result_json)
            # ep =   ProjectEndPoint.objects.get(pk=end_point.pk)
            # ##print("after update the sub_df is",ep.sub_df)
        else:
            ##print("loding from json data")
            json_st = json.loads(end_point.sub_df)
            # ##print("THE TYPE OF JSON FILE<",type(json_st))
            json_df = pd.DataFrame(json_st)
            df = json_df.transpose()

            metadata = ProjectMetaData.objects.get(project=p_query.project)
            df_columns     = df.columns.tolist()
            for key, value in metadata.meta_data.items():
                if key in df_columns:
                    ##print("key",key)
                    if value['dtype'] == 'int':
                        df[key] =pd.to_numeric(df[key])
                        if key in df_columns:
                            df[key] = pd.to_numeric(df[key])
                    elif value['dtype'] == 'float':
                        ##print("final key",key,df[key],df[key].dtypes)
                        df[key] = pd.to_numeric(df[key])
                        if key in df_columns:
                            df[key] = pd.to_numeric(df[key])
                    elif value['dtype'] == 'object':
                        df[key] = df[key].astype(str)
                        if key in df_columns:
                            df[key] = df[key].astype(str)
                    elif value['dtype'] == 'bool':
                        df[key] = df[key].astype(bool)
                        if key in df_columns:
                            df[key] = df[key].astype(bool)
                    elif value['dtype'] == 'DateTime':
                        df[key] =pd.to_datetime(df[key])
                        ##print("the data key",key)
                        if key in df_columns:
                            df[key] = pd.to_datetime(df[key])
        # for column in df_columns:
        #     try:
        #         df[column] = pd.to_numeric(df[column])
        #     except:
        #         pass

        # t_df = res_df.T
        # ##print("the visulization columns",df)
        string_columns = df.select_dtypes(include ='object')
        number_columns= df.select_dtypes(include='number')
        feature_columns = df.select_dtypes(include=['object','bool','number'])
        if metadata.date_column_name and metadata.date_column_name in df_columns:
            df[metadata.date_column_name] = df[metadata.date_column_name].astype(str)
        res_df__table_content = df.to_html(classes="table table-striped tableFixHead",border="0")
        ##print("the string columns are",string_columns)
        df_columns     = df.columns.tolist()
        row_count = df.shape[1]
        column_count = df.shape[0]
        if end_point.plot and end_point.plot.plot_type:
            end_point_obj = EndPointPlot(df,end_point.pk)
            plot = Plot.objects.get(pk= end_point.plot.pk)
            div = end_point_obj.plot(plot)
        else:
            # fig = px.scatter_matrix(df)
            # div = opy.plot(fig, auto_open=False, output_type='div')
            div = True
        non_query_object = {}
        if end_point.alignment_object:


            non_query_object = {}
            if all('query' not in elem.values() for elem in end_point.alignment_object.values()):
                non_query_object['query']=True
            if all('table' not in elem.values() for elem in end_point.alignment_object.values()):
                non_query_object['table']=True
            if all('plot' not in elem.values() for elem in end_point.alignment_object.values()):
                non_query_object['plot']=True
            if all('ml' not in elem.values() for elem in end_point.alignment_object.values()):
                non_query_object['ml']=True
            if all('cp' not in elem.values() for elem in end_point.alignment_object.values()):
                non_query_object['cp']=True
            ##print(non_query_object)
        if end_point.algorithm:
            features_text = end_point.algorithm.feature
            features_text = features_text.replace('[', '')
            features_text = features_text.replace(']', '')
            features      = features_text.split(',')
            features_ml_display = features_text.split(',')
            ##print("features",features)

            test_l =[]
            features_cat_dict = {}
            ml_df = pd.DataFrame()
            for column in features:
                ml_df[column] = df[column]

            ml_string_columns = ml_df.select_dtypes(include =['object','bool'])
            ##print("the ml string columns ",ml_string_columns)




            ##print("after ml df ",ml_df)
            for column in ml_string_columns:
                if ml_df[column].dtypes  == np.bool:
                    ##print("the data value",df[column],column)

                    column_name = column +'_cat'
                    d = {}

                    new_df = pd.DataFrame()
                    new_df[column] = pd.unique(df[column])

                    column_name = column+'_cat'
                    new_df[column] = new_df[column].astype('category')
                    new_df[column_name] = new_df[column].cat.codes
                    c_series = new_df[column]
                    c_cat_series = new_df[column_name]
                    c_list = c_series.tolist()
                    c_cat_list = c_cat_series.tolist()
                    ##print("new_df",new_df)

                    for i in range(0,len(c_list)):
                        d[c_list[i]]=c_cat_list[i]
                    features_cat_dict[column]=d
                    ##print("features",features_cat_dict)
                    features.remove(column)
                    ##print("features",features)



                else:
                    try:

                        ml_df[column] = ml_df[column].astype(float)
                        ##print("in float type column is",column,ml_df[column])
                    except:

                        d = {}

                        new_df = pd.DataFrame()
                        new_df[column] = pd.unique(df[column])

                        column_name = column+'_cat'
                        new_df[column] = new_df[column].astype('category')
                        new_df[column_name] = new_df[column].cat.codes
                        c_series = new_df[column]
                        c_cat_series = new_df[column_name]
                        c_list = c_series.tolist()
                        c_cat_list = c_cat_series.tolist()
                        ##print("new_df",new_df)

                        for i in range(0,len(c_list)):
                            d[c_list[i]]=c_cat_list[i]
                        features_cat_dict[column]=d
                        ##print("features",features_cat_dict)
                        features.remove(column)
                        ##print("features",features)



            target   = end_point.algorithm.y_factor

            model_id = end_point.algorithm.model_id
            model_id = model_id.split('.pkl')
            model_id = model_id[0]
            if end_point.algorithm.type_of_prediction == 'Linear':
                accuracy = ast.literal_eval(end_point.algorithm.accuracy)
                MAE = accuracy['MAE']
                MSE = accuracy['MSE']
                RMSE = accuracy['RMSE']
                accuracy_list = {'MAE':MAE,'MSE':MSE,'RMSE':RMSE}
            else:
                accuracy_list={'accuracy':end_point.algorithm.accuracy}
        else:
            features_cat_dict = {}
            features_ml_display = None
            features = None
            target = None
            model_id = None
            accuracy_list = None


        context = {'features_cat_dict':features_cat_dict,'features_ml_display':features_ml_display,'features':features,'target':target,'model_id':model_id,'accuracy_list':accuracy_list,'features':features,'target':target,'model_id':model_id,'accuracy_list':accuracy_list,'graph':div,'ep_form':ep_form,'end_point':end_point,'query':res_df__table_content,'permission':permission,'row_count':row_count,'column_count':column_count,'form':dashboard_form,'string_columns':string_columns,'df_columns':df_columns,'non_query_object':non_query_object,'feature_columns':feature_columns,'number_columns':number_columns}
        return render(request,'dashboard/project_end_point_edit.html',context)

    def post(self,request,pk):
        name = request.POST['end_point_name']
        frequency = request.POST['frequency']
        query_object = request.POST.get('end_point_object',None)
        if query_object:
            ##print("the query object",query_object)
            query_object = ast.literal_eval(query_object)

        ep = ProjectEndPoint.objects.get(pk=pk)
        if query_object:
            update = ProjectEndPoint.objects.filter(pk=pk).update(name=name,alignment_object=query_object,sub_df_frequency=frequency)
        else:
            update = ProjectEndPoint.objects.filter(pk=pk).update(name=name,sub_df_frequency=frequencys)
        pk=str(ep.pk)
        return redirect('/endpoint/'+pk+'/')



class ProjectEndpointAlignmentView(GroupRequiredMixin,LoginRequiredMixin,View):
    ''' class to Create Alignment of query for endpoint Create'''
    def dispatch(self, request, *args, **kwargs):
        pk = kwargs['pk']
        end_point = ProjectEndPoint.objects.get(pk=pk)
        project=Project.objects.get(pk=end_point.project.pk)

        pk= str(project.pk)
        self.login_url = '/customer/login/'
        self.redirect_field_name = 'redirect_to'
        self.template_name='dashboard/index.html'
        admin_name = pk+"_Admin"
        ##print(type(admin_name), admin_name)
        admin_encode_name = admin_name.encode()
        admin_unicode_name = admin_encode_name.decode('utf-8')
        write_name = pk+"_Write"
        ##print(type(write_name), write_name)
        write_encode_name = write_name.encode()
        write_unicode_name = write_encode_name.decode('utf-8')

        delete_name = pk+"_Delete"
        ##print(type(delete_name), delete_name)
        delete_encode_name = delete_name.encode()
        delete_unicode_name = delete_encode_name.decode('utf-8')
        l =[delete_unicode_name,write_unicode_name,admin_unicode_name]
        self.group_required= l
        ##print("the self of dispatcher",self.group_required)

        return super(ProjectEndpointAlignmentView, self).dispatch(request, *args, **kwargs)

    def post(self,request,pk):
        end_point = ProjectEndPoint.objects.get(pk=pk)
        query_object = end_point.query
        query_object = request.POST.get('end_point_object',None)
        if query_object:
            query_object = ast.literal_eval(query_object)
        project_query = end_point.query
        ep_form = ProjectEndPointForm(initial={'end_point_name':end_point.name,'frequency':end_point.sub_df_frequency})
        project = Project.objects.get(pk=project_query.project.pk)
        piqu,created = ProjectBillingPrms.objects.get_or_create(project=project)
        update = ProjectBillingPrms.objects.filter(project=project).update(query_count=piqu.query_count+1)
        dashboard_form = ProjectDashboardForm(initial={'project':project.pk})
        dashboard_form.fields['user'].queryset = ProjectUser.objects.filter(project=project)
        dashboard_form.fields['dashboard'].queryset = ProjectDashboard.objects.filter(project=project)
        if Project.objects.filter(pk=project_query.project.pk,admin_user=request.user).exists():
            permission="Admin"
        elif ProjectUser.objects.filter(project=project_query.project,project_user=request.user).exists():
            user_group = User.objects.get(pk=request.user.pk)

            for g in user_group.groups.all():
                if g.name == str(project_query.project.pk)+"_Read":
                    permission="Read"
                elif g.name == str(project_query.project.pk)+"_Write":
                    permission="Write"
                elif g.name == str(project_query.project.pk)+"_Delete":
                    permission="Delete"
                elif g.name == str(project_query.project.pk)+"_Admin":
                    permission="Admin"
        else:
            permission=None
        today= datetime.now().date()
        if not end_point.sub_df:

            df = QueryExcecute(p_query)
            df_columns = df.columns.tolist()
            metadata = ProjectMetaData.objects.get(project=p_query.project)
            if metadata.date_column_name and metadata.date_column_name in df_columns:
                df[metadata.date_column_name] = df[metadata.date_column_name].astype(str)
            result_json = df.to_json(orient='index')
            update = ProjectEndPoint.objects.filter(pk=end_point.pk).update(sub_df=result_json)
            # ep =   ProjectEndPoint.objects.get(pk=end_point.pk)
            # ##print("after update the sub_df is",ep.sub_df)

        else:
            ##print("loding from json data")
            json_st = json.loads(end_point.sub_df)
            # ##print("THE TYPE OF JSON FILE<",type(json_st))
            json_df = pd.DataFrame(json_st)
            df = json_df.transpose()
            df_columns = df.columns.tolist()
            metadata = ProjectMetaData.objects.get(project=project_query.project)
            for key, value in metadata.meta_data.items():
                if key in df_columns:
                    ##print("key",key)
                    if value['dtype'] == 'int':
                        df[key] =pd.to_numeric(df[key])
                        if key in df_columns:
                            df[key] = pd.to_numeric(df[key])
                    elif value['dtype'] == 'float':
                        ##print("final key",key,df[key],df[key].dtypes)
                        df[key] = pd.to_numeric(df[key])
                        if key in df_columns:
                            df[key] = pd.to_numeric(df[key])
                    elif value['dtype'] == 'object':
                        df[key] = df[key].astype(str)
                        if key in df_columns:
                            df[key] = df[key].astype(str)
                    elif value['dtype'] == 'bool':
                        df[key] = df[key].astype(bool)
                        if key in df_columns:
                            df[key] = df[key].astype(bool)
                    elif value['dtype'] == 'DateTime':
                        df[key] =pd.to_datetime(df[key])
                        ##print("the data key",key)
                        if key in df_columns:
                            df[key] = pd.to_datetime(df[key])

        df_rows =df.shape[0]
        df_column_count=  df.shape[1]
        number_columns = df.select_dtypes(include='number')
        res_df__table_content =df.to_html(classes="table table-striped tableFixHead",border="0")
        df_columns     = df.columns.tolist()
        string_columns = df.select_dtypes(include =['object','bool'])
        feature_columns = df.select_dtypes(include=['object','bool','number'])

        if metadata.date_column_name in df_columns and  metadata.date_column_name:
            df[metadata.date_column_name] = df[metadata.date_column_name].astype(str)
        # for column in df_columns:
        #     try:
        #         df[column] = pd.to_numeric(df[column])
        #     except:
        #         pass
        # t_df = res_df.T
        # ##print("the visulization columns",df)

        df_columns     = df.columns.tolist()
        df=df
        row_count = df.shape[1]
        column_count = df.shape[0]
        if end_point.plot and end_point.plot.plot_type:
            plot =Plot.objects.get(pk=end_point.plot.pk)
            plot_obj = EndPointPlot(df,end_point.pk)
            div = plot_obj.plot(plot)

        else:
            # fig = px.scatter_matrix(df)
            # div = opy.plot(fig, auto_open=False, output_type='div')
            div = True

        project = Project.objects.get(pk=project_query.project.pk)
        if end_point.algorithm:
            features_text = end_point.algorithm.feature
            features_text = features_text.replace('[', '')
            features_text = features_text.replace(']', '')
            features      = features_text.split(',')
            features_ml_display = features_text.split(',')
            ##print("features",features)

            test_l =[]
            features_cat_dict = {}
            ml_df = pd.DataFrame()
            for column in features:
                ml_df[column] = df[column]

            ml_string_columns = ml_df.select_dtypes(include =['object','bool'])
            ##print("the ml string columns ",ml_string_columns)




            ##print("after ml df ",ml_df)
            for column in ml_string_columns:
                if ml_df[column].dtypes  == np.bool:
                    ##print("the data value",df[column],column)

                    column_name = column +'_cat'
                    d = {}

                    new_df = pd.DataFrame()
                    new_df[column] = pd.unique(df[column])

                    column_name = column+'_cat'
                    new_df[column] = new_df[column].astype('category')
                    new_df[column_name] = new_df[column].cat.codes
                    c_series = new_df[column]
                    c_cat_series = new_df[column_name]
                    c_list = c_series.tolist()
                    c_cat_list = c_cat_series.tolist()
                    ##print("new_df",new_df)

                    for i in range(0,len(c_list)):
                        d[c_list[i]]=c_cat_list[i]
                    features_cat_dict[column]=d
                    ##print("features",features_cat_dict)
                    features.remove(column)
                    ##print("features",features)



                else:
                    try:

                        ml_df[column] = ml_df[column].astype(float)
                        ##print("in float type column is",column,ml_df[column])
                    except:

                        d = {}

                        new_df = pd.DataFrame()
                        new_df[column] = pd.unique(df[column])

                        column_name = column+'_cat'
                        new_df[column] = new_df[column].astype('category')
                        new_df[column_name] = new_df[column].cat.codes
                        c_series = new_df[column]
                        c_cat_series = new_df[column_name]
                        c_list = c_series.tolist()
                        c_cat_list = c_cat_series.tolist()
                        ##print("new_df",new_df)

                        for i in range(0,len(c_list)):
                            d[c_list[i]]=c_cat_list[i]
                        features_cat_dict[column]=d
                        ##print("features",features_cat_dict)
                        features.remove(column)
                        ##print("features",features)



            target   = end_point.algorithm.y_factor
            model_id = end_point.algorithm.model_id
            if end_point.algorithm.type_of_prediction == 'Linear':
                accuracy = ast.literal_eval(end_point.algorithm.accuracy)
                MAE = accuracy['MAE']
                MSE = accuracy['MSE']
                RMSE = accuracy['RMSE']
                accuracy_list = {'MAE':MAE,'MSE':MSE,'RMSE':RMSE}
            else:
                accuracy_list={'accuracy':end_point.algorithm.accuracy}
        else:
            features_cat_dict = {}
            features_ml_display = None

            features = None
            target = None
            model_id = None
            accuracy_list = None
        non_query_object = {}
        if query_object:
            update = ProjectEndPoint.objects.filter(pk=end_point.pk).update(alignment_object=query_object)
            non_query_object = {}
            if all('query' not in elem.values() for elem in query_object.values()):
                non_query_object['query']=True
            if all('table' not in elem.values() for elem in query_object.values()):
                non_query_object['table']=True
            if all('plot' not in elem.values() for elem in query_object.values()):
                non_query_object['plot']=True
            if all('ml' not in elem.values() for elem in query_object.values()):
                non_query_object['ml']=True
            if all('cp' not in elem.values() for elem in query_object.values()):
                non_query_object['cp']=True
            ##print(non_query_object)
            end_point = ProjectEndPoint.objects.get(pk=end_point.pk)

            context = {'features_cat_dict':features_cat_dict,'features_ml_display':features_ml_display,'features':features,'target':target,'model_id':model_id,'accuracy_list':accuracy_list,'graph':div,'ep_form':ep_form,'end_point':end_point,'query':res_df__table_content,'permission':permission,'row_count':row_count,'column_count':column_count,'string_columns':string_columns,'df_columns':df_columns,'non_query_object':non_query_object,'form':dashboard_form,'feature_columns':feature_columns,'number_columns':number_columns}
            # ##print('the context',context)
        else:
            context = {'features_cat_dict':features_cat_dict,'features_ml_display':features_ml_display,'features':features,'target':target,'model_id':model_id,'accuracy_list':accuracy_list,'graph':div,'ep_form':ep_form,'end_point':end_point,'query':res_df__table_content,'permission':permission,'row_count':row_count,'column_count':column_count,'string_columns':string_columns,'df_columns':df_columns,'non_query_object':non_query_object,'form':dashboard_form,'feature_columns':feature_columns,'number_columns':number_columns}
        project_billing = ProjectBillingPrms.objects.get(project=project)
        update = ProjectBillingPrms.objects.filter(pk=project_billing.pk).update(query_count=project_billing.query_count)
        return render(request,'dashboard/project_end_point_edit.html',context)


# class ProjectDashboardEditView(LoginRequiredMixin,UpdateView,PermissionRequiredMixin):

#     def dispatch(self, request, *args, **kwargs):
#         pk = kwargs['pk']
#         dashboard = ProjectDashboard.objects.get(pk=pk)
#         project=Project.objects.get(pk=dashboard.project.pk)
#         pk= str(project.pk)
#         self.login_url = '/customer/login/'
#         self.redirect_field_name = 'redirect_to'
#         self.template_name='dashboard/index.html'
#         admin_name = pk+"_Admin"
#         ##print(type(admin_name), admin_name)
#         admin_encode_name = admin_name.encode()
#         admin_unicode_name = admin_encode_name.decode('utf-8')
#         write_name = pk+"_Write"
#         ##print(type(write_name), write_name)
#         write_encode_name = write_name.encode()
#         write_unicode_name = write_encode_name.decode('utf-8')
#         delete_name = pk+"_Delete"
#         delete_encode_name = delete_name.encode()
#         delete_unicode_name = delete_encode_name.decode('utf-8')
#         l= [delete_unicode_name,admin_unicode_name,write_unicode_name]
#         self.group_required= l
#         ##print("the self of dispatcher",self.group_required)

#         return super(ProjectDashboardEditView, self).dispatch(request, *args, **kwargs)

#     def get(self,request,pk):
#         dashboard = ProjectDashboard.objects.get(pk=pk)
#         dashboard_object = dashboard.dashboard_format
#         current_site = get_current_site(request)
#         project = dashboard.project
#         site_name = current_site.name
#         domain = current_site.domain
#         if domain.startswith('127.0.'):
#             domain = 'https://'+domain
#         else:
#             domain = 'https://'+domain
#         if Project.objects.filter(pk=project.pk,admin_user=request.user).exists():
#             permission="Admin"
#         elif ProjectUser.objects.filter(project=project,project_user=request.user).exists():
#             user_group = User.objects.get(pk=request.user.pk)

#             for g in user_group.groups.all():
#                 if g.name == str(project.pk)+"_Read":
#                     permission="Read"
#                 elif g.name == str(project.pk)+"_Write":
#                     permission="Write"
#                 elif g.name == str(project.pk)+"_Delete":
#                     permission="Delete"
#                 elif g.name == str(project.pk)+"_Admin":
#                     permission="Admin"
#         else:
#             permission=None


#         endpoint_pk = []
#         test_editor_count = 0
#         for key, value in dashboard.dashboard_format.items():
#             if value['type'] == 'end_point':
#                 endpoint_pk.append(value['id'])
#                 for end_point in dashboard.end_point.all():
#                     if value['id'] == str(end_point.pk):
#                         value['id'] = end_point.id
#                         value['end_point']=str(end_point)
#             elif value['type'] == "text_editor":
#                 test_editor_count = test_editor_count+1

#         endpoints = ProjectEndPoint.objects.filter(project=project)

#         dashboard_form = ProjectDashboardEditForm(initial={'project':project.pk,'user':[user.id for user in dashboard.dashboard_users.all()],'email_users':dashboard.additional_email,'report_frequency':dashboard.report_frequency,'name':dashboard.name,'dashboard_for':dashboard.dashboard_for})
#         dashboard_form.fields['user'].queryset = ProjectUser.objects.filter(project=project)
#         dashboards = ProjectDashboard.objects.filter(project=project)
#         ##print("form",dashboard_form)
#         dashboard_format = json.dumps(dashboard.dashboard_format)
#         context={'permission':permission,'domain':domain,'project':project,'end_points':endpoints,'dashboard_form':dashboard_form,'dashboard':dashboard,'dashboards':dashboards,'test_editor_count':test_editor_count,'dashboard_format':dashboard_format}

#         return render(request,'dashboard/project_dashboard_update.html',context)



#     def post(self,request,pk):
#         ##print("post")


#         form = ProjectDashboardEditForm(request.POST)
#         # ##print("testing form")
#         # ##print("form invalid",form)
#         dashboard = ProjectDashboard.objects.get(pk=pk)
#         project = dashboard.project
#         if form.is_valid():
#             name = request.POST.get('name',None)
#             dashboard_format = request.POST.get('dashboard_format',None)
#             if dashboard_format:

#                 dashboard_format = json.loads(dashboard_format)
#             else:
#                 dashboard_format= None
#             ##print("converted dict",dashboard_format)
#             additional_email = form.cleaned_data['email_users']
#             report_frequency = form.cleaned_data['report_frequency']
#             user = form.cleaned_data['user']
#             dashboard_for = form.cleaned_data['dashboard_for']



#             if name:
#                 ##print("new dashboard")
#                 if dashboard_format:

#                     update = ProjectDashboard.objects.filter(pk=pk).update(
#                                                                     name=name,
#                                                                     additional_email=additional_email,
#                                                                     dashboard_format = dashboard_format,
#                                                                     dashboard_for=dashboard_for)
#                 else:
#                     update = ProjectDashboard.objects.filter(pk=pk).update(
#                                                                     name=name,
#                                                                     additional_email=additional_email,
#                                                                     dashboard_for=dashboard_for
#                                                                     )

#                 dashboard = ProjectDashboard.objects.get(pk=pk)


#                 if dashboard_for == "Dashboard Users":

#                     for u in user:
#                         dashboard.dashboard_users.add(u.project_user)
#                 elif dashboard_for == "Me Only":
#                     if dashboard.dashboard_users:
#                         for user in dashboard.dashboard_users.all():
#                             dashboard.dashboard_users.remove(user)



#                 elif dashboard_for == "Public":
#                      if dashboard.dashboard_users:
#                         for user in dashboard.dashboard_users.all():
#                             dashboard.dashboard_users.remove(user)


#                 end_point = []

#                 for elem, obj in  dashboard_format.items():

#                     if obj['type'] == "end_point":
#                         end_point.append(obj['id'])




#                 for p in end_point:
#                     ep = ProjectEndPoint.objects.get(pk=int(p))
#                     ##print("the ep is ",ep)
#                     dashboard.end_point.add(ep)

#                 dashboard = ProjectDashboard.objects.get(pk=dashboard.pk)

#                 data={"msg":'Dashboard Updated Successfull'}
#                 pk = str(dashboard.pk)
#                 return redirect('/project-dashboard/'+pk+'/')
#             else:
#                 msg={"msg":'Please Fill the Details Befour Submit'}
#         else:
#             ##print("form invalid",form.errors)
#             msg= "There is an error in dashboard creation"
#             project = Project.objects.get(pk=pk)
#         try:
#             dashboards = ProjectDashboard.objects.filter(project=project)
#         except:
#             dashboards=None
#         current_site = get_current_site(request)
#         site_name = current_site.name
#         domain = current_site.domain
#         if domain.startswith('127.0.'):
#             domain = 'https://'+domain
#         else:
#             domain = 'https://'+domain
#         if Project.objects.filter(pk=project.pk,admin_user=request.user).exists():
#             permission="Admin"
#         elif ProjectUser.objects.filter(project=project,project_user=request.user).exists():
#             user_group = User.objects.get(pk=request.user.pk)

#             for g in user_group.groups.all():
#                 if g.name == str(project.pk)+"_Read":
#                     permission="Read"
#                 elif g.name == str(project.pk)+"_Write":
#                     permission="Write"
#                 elif g.name == str(project.pk)+"_Delete":
#                     permission="Delete"
#                 elif g.name == str(project.pk)+"_Admin":
#                     permission="Admin"
#         else:
#             permission=None

#         endpoint_pk = []
#         for key, value in dashboard.dashboard_format.items():
#             if value['type'] == 'end_point':
#                 endpoint_pk.append(value['id'])
#                 for end_point in dashboard.end_point.all():
#                     if value['id'] == str(end_point.pk):
#                         value['id'] = end_point.id
#                         value['end_point']=str(end_point)

#         endpoints = ProjectEndPoint.objects.filter(project=project)
#         dashboard_form = ProjectDashboardEditForm(initial={'project':project.pk,'user':dashboard.dashboard_users.all(),'email_users':dashboard.additional_email,'report_frequency':dashboard.report_frequency,'name':dashboard.name})
#         dashboard_form.fields['user'].queryset = ProjectUser.objects.filter(project=project)
#         dashboards = ProjectDashboard.objects.filter(project=project)
#         ##print("form",dashboard_form)
#         context={'permission':permission,'msg':msg,'domain':domain,'project':project,'end_points':endpoints,'dashboard_form':dashboard_form,'dashboard':dashboard,'dashboards':dashboards}

#         return render(request,'dashboard/project_dashboard_update.html',context)


class EndPointDashboardCreateView(GroupRequiredMixin,LoginRequiredMixin,View):
    def dispatch(self, request, *args, **kwargs):
        pk = kwargs['pk']
        end_point = ProjectEndPoint.objects.get(pk=pk)
        project=Project.objects.get(pk=end_point.project.pk)

        pk= str(project.pk)
        self.login_url = '/customer/login/'
        self.redirect_field_name = 'redirect_to'
        self.template_name='dashboard/index.html'
        admin_name = pk+"_Admin"
        ##print(type(admin_name), admin_name)
        admin_encode_name = admin_name.encode()
        admin_unicode_name = admin_encode_name.decode('utf-8')
        write_name = pk+"_Write"
        ##print(type(write_name), write_name)
        write_encode_name = write_name.encode()
        write_unicode_name = write_encode_name.decode('utf-8')

        delete_name = pk+"_Delete"
        ##print(type(delete_name), delete_name)
        delete_encode_name = delete_name.encode()
        delete_unicode_name = delete_encode_name.decode('utf-8')
        l =[delete_unicode_name,write_unicode_name,admin_unicode_name]
        self.group_required= l
        ##print("the self of dispatcher",self.group_required)

        return super(EndPointDashboardCreateView, self).dispatch(request, *args, **kwargs)

    def get(self,request,pk):
        end_point = ProjectEndPoint.objects.get(pk=pk)
        project = end_point.project
        try:
            dashboard = ProjectDashboard.objects.filter(project=project)
        except:
            dashboard=None
        current_site = get_current_site(request)

        site_name = current_site.name
        domain = current_site.domain
        if domain.startswith('127.0.'):
            domain = 'https://'+domain
        else:
            domain = 'https://'+domain
        if Project.objects.filter(pk=project.pk,admin_user=request.user).exists():
            permission="Admin"
        elif ProjectUser.objects.filter(project=project,project_user=request.user).exists():
            user_group = User.objects.get(pk=request.user.pk)

            for g in user_group.groups.all():
                if g.name == str(project.pk)+"_Read":
                    permission="Read"
                elif g.name == str(project.pk)+"_Write":
                    permission="Write"
                elif g.name == str(project.pk)+"_Delete":
                    permission="Delete"
                elif g.name == str(project.pk)+"_Admin":
                    permission="Admin"
        else:
            permission=None

        endpoints = ProjectEndPoint.objects.filter(project=project)
        js_data =end_point_columns(endpoints,project)
        end_point =  ProjectEndPoint.objects.get(pk=pk)
        dashboard_form = ProjectDashboardForm(initial={'project':project.pk})
        dashboard_form.fields['user'].queryset = ProjectUser.objects.filter(project=project)
        dashboard_form.fields['dashboard'].queryset = ProjectDashboard.objects.filter(project=project)
        context={'permission':permission,'end_point':end_point,'domain':domain,'project':project,'end_points':endpoints,'dashboard_form':dashboard_form,'dashboard':dashboard,'js_data':js_data}
        return render(request,'dashboard/dashboard_create.html',context)


    def post(self,request,pk):
        end_point  = ProjectEndPoint.objects.get(pk=pk)
        dashboard_pk = request.POST['dashboard']
        ##print("dashboard.pk",dashboard_pk)
        dashboard = ProjectDashboard.objects.get(pk=int(dashboard_pk))
        dashboard_object = dashboard.dashboard_format
        current_site = get_current_site(request)
        project = end_point.project
        site_name = current_site.name
        domain = current_site.domain
        if domain.startswith('127.0.'):
            domain = 'https://'+domain
        else:
            domain = 'https://'+domain
        if Project.objects.filter(pk=project.pk,admin_user=request.user).exists():
            permission="Admin"
        elif ProjectUser.objects.filter(project=project,project_user=request.user).exists():
            user_group = User.objects.get(pk=request.user.pk)

            for g in user_group.groups.all():
                if g.name == str(project.pk)+"_Read":
                    permission="Read"
                elif g.name == str(project.pk)+"_Write":
                    permission="Write"
                elif g.name == str(project.pk)+"_Delete":
                    permission="Delete"
                elif g.name == str(project.pk)+"_Admin":
                    permission="Admin"
        else:
            permission=None


        endpoint_pk = []
        for key, value in dashboard.dashboard_format.items():
            if value['type'] == 'end_point':
                endpoint_pk.append(value['id'])
                for end_point in dashboard.end_point.all():
                    if value['id'] == str(end_point.pk):
                        value['id'] = end_point.id
                        value['end_point']=str(end_point)
        if end_point.pk not in endpoint_pk:

            endpoint_pk.append(end_point.pk)

        endpoints = ProjectEndPoint.objects.filter(project=project)
        js_data =end_point_columns(endpoints,project)
        dashboard_form = ProjectDashboardEditForm(initial={'project':project.pk,'user':dashboard.dashboard_users.all(),'email_users':dashboard.additional_email,'report_frequency':dashboard.report_frequency,'name':dashboard.name})
        dashboard_form.fields['user'].queryset = ProjectUser.objects.filter(project=project)
        dashboards = ProjectDashboard.objects.filter(project=project)
        end_point = ProjectEndPoint.objects.get(pk=pk)
        ##print("the selectd endpoint is",end_point)
        dashboard_format = json.dumps(dashboard.dashboard_format)
        context={'permission':permission,'domain':domain,'project':project,'end_points':endpoints,'dashboard_form':dashboard_form,'dashboard':dashboard,'dashboards':dashboards,'end_point':end_point,'dashboard_format':dashboard_format,'js_data':js_data}

        return render(request,'dashboard/project_dashboard_update.html',context)

class ProjectDashboardEditView(GroupRequiredMixin,LoginRequiredMixin,UpdateView):

    def dispatch(self, request, *args, **kwargs):
        pk = kwargs['pk']
        dashboard = ProjectDashboard.objects.get(pk=pk)
        project=Project.objects.get(pk=dashboard.project.pk)
        pk= str(project.pk)
        self.login_url = '/customer/login/'
        self.redirect_field_name = 'redirect_to'
        self.template_name='dashboard/index.html'
        admin_name = pk+"_Admin"
        ##print(type(admin_name), admin_name)
        admin_encode_name = admin_name.encode()
        admin_unicode_name = admin_encode_name.decode('utf-8')
        write_name = pk+"_Write"
        ##print(type(write_name), write_name)
        write_encode_name = write_name.encode()
        write_unicode_name = write_encode_name.decode('utf-8')
        delete_name = pk+"_Delete"
        delete_encode_name = delete_name.encode()
        delete_unicode_name = delete_encode_name.decode('utf-8')
        l= [delete_unicode_name,admin_unicode_name,write_unicode_name]
        self.group_required= l
        ##print("the self of dispatcher",self.group_required)

        return super(ProjectDashboardEditView, self).dispatch(request, *args, **kwargs)
    def get(self,request,pk):
        dashboard = ProjectDashboard.objects.get(pk=pk)
        dashboard_object = dashboard.dashboard_format
        current_site = get_current_site(request)
        project = dashboard.project
        site_name = current_site.name
        domain = current_site.domain
        if domain.startswith('127.0.'):
            domain = 'https://'+domain
        else:
            domain = 'https://'+domain
        if Project.objects.filter(pk=project.pk,admin_user=request.user).exists():
            permission="Admin"
        elif ProjectUser.objects.filter(project=project,project_user=request.user).exists():
            user_group = User.objects.get(pk=request.user.pk)

            for g in user_group.groups.all():
                if g.name == str(project.pk)+"_Read":
                    permission="Read"
                elif g.name == str(project.pk)+"_Write":
                    permission="Write"
                elif g.name == str(project.pk)+"_Delete":
                    permission="Delete"
                elif g.name == str(project.pk)+"_Admin":
                    permission="Admin"
        else:
            permission=None


        endpoint_pk = []
        test_editor_count = 0
        for key, value in dashboard.dashboard_format.items():
            if value['type'] == 'end_point':
                endpoint_pk.append(value['id'])
                for end_point in dashboard.end_point.all():
                    if value['id'] == str(end_point.pk):
                        value['id'] = end_point.id
                        value['end_point']=str(end_point)
            elif value['type'] == "text_editor":
                test_editor_count = test_editor_count+1

        endpoints = ProjectEndPoint.objects.filter(project=project)
        js_data =end_point_columns(endpoints,project)
        dashboard_form = ProjectDashboardEditForm(initial={'project':project.pk,'user':[user.id for user in dashboard.dashboard_users.all()],'email_users':dashboard.additional_email,'report_frequency':dashboard.report_frequency,'name':dashboard.name,'dashboard_for':dashboard.dashboard_for})
        dashboard_form.fields['user'].queryset = ProjectUser.objects.filter(project=project)
        dashboards = ProjectDashboard.objects.filter(project=project)
        ##print("form",dashboard_form)
        dashboard_format = json.dumps(dashboard.dashboard_format)
        context={'permission':permission,'domain':domain,'project':project,'end_points':endpoints,'dashboard_form':dashboard_form,'dashboard':dashboard,'dashboards':dashboards,'test_editor_count':test_editor_count,'dashboard_format':dashboard_format,'js_data':js_data}

        return render(request,'dashboard/project_dashboard_update.html',context)



    def post(self,request,pk):
        ##print("post")


        form = ProjectDashboardEditForm(request.POST)
        # ##print("testing form")
        # ##print("form invalid",form)
        dashboard = ProjectDashboard.objects.get(pk=pk)
        project = dashboard.project
        if form.is_valid():
            name = request.POST.get('name',None)
            dashboard_format = request.POST.get('dashboard_format',None)
            if dashboard_format:

                dashboard_format = json.loads(dashboard_format)
            else:
                dashboard_format= None
            ##print("converted dict",dashboard_format)
            additional_email = form.cleaned_data['email_users']
            report_frequency = form.cleaned_data['report_frequency']
            user = form.cleaned_data['user']
            dashboard_for = form.cleaned_data['dashboard_for']

            if name:
                ##print("new dashboard")
                if dashboard_format:
                    if dashboard_for == 'Public':
                        if dashboard.public_shared_code:
                            update = ProjectDashboard.objects.filter(pk=pk).update(
                                                                            name=name,
                                                                            additional_email=additional_email,
                                                                            dashboard_format = dashboard_format,
                                                                            dashboard_for=dashboard_for,
                                                                            report_frequency=report_frequency)
                        else:

                            hash_str = str(dashboard.pk)+"dashboard"
                            hash_code = str(hash(hash_str))
                            ##print("he hashcode is",hash_code)
                            update = ProjectDashboard.objects.filter(pk=pk).update(
                                                                            name=name,
                                                                            additional_email=additional_email,
                                                                            dashboard_format = dashboard_format,
                                                                            dashboard_for=dashboard_for,
                                                                            public_shared_code=hash_code,
                                                                            report_frequency=report_frequency)
                    else:
                        update = ProjectDashboard.objects.filter(pk=pk).update(
                                                                        name=name,
                                                                        additional_email=additional_email,
                                                                        dashboard_format = dashboard_format,
                                                                        dashboard_for=dashboard_for,
                                                                        report_frequency=report_frequency,
                                                                        public_shared_code=None)
                else:

                    if dashboard_for == 'Public':
                        if dashboard.public_shared_code:
                            update = ProjectDashboard.objects.filter(pk=pk).update(
                                                                        name=name,
                                                                        additional_email=additional_email,
                                                                        dashboard_for=dashboard_for,
                                                                        report_frequency=report_frequency,
                                                                       )

                        else:
                            hash_str = str(dashboard.pk)+"dashboard"
                            hash_code = str(hash(hash_str))
                            ##print("he hashcode is",hash_code)
                            update = ProjectDashboard.objects.filter(pk=pk).update(
                                                                        name=name,
                                                                        additional_email=additional_email,
                                                                        dashboard_for=dashboard_for,
                                                                        report_frequency=report_frequency,
                                                                        public_shared_code=hash_code)
                    else:
                        update = ProjectDashboard.objects.filter(pk=pk).update(
                                                                    name=name,
                                                                    additional_email=additional_email,
                                                                    dashboard_for=dashboard_for, public_shared_code=None,
                                                                    report_frequency=report_frequency
                                                                    )

                dashboard = ProjectDashboard.objects.get(pk=pk)


                if dashboard_for == "Dashboard Users":

                    for u in user:
                        dashboard.dashboard_users.add(u.project_user)
                elif dashboard_for == "Me Only":
                    if dashboard.dashboard_users:
                        for user in dashboard.dashboard_users.all():
                            dashboard.dashboard_users.remove(user)



                elif dashboard_for == "Public":
                     if dashboard.dashboard_users:
                        for user in dashboard.dashboard_users.all():
                            dashboard.dashboard_users.remove(user)


                end_point = []

                for elem, obj in  dashboard_format.items():

                    if obj['type'] == "end_point":
                        end_point.append(obj['id'])




                for p in end_point:
                    ep = ProjectEndPoint.objects.get(pk=int(p))
                    ##print("the ep is ",ep)
                    dashboard.end_point.add(ep)

                dashboard = ProjectDashboard.objects.get(pk=dashboard.pk)


                data={"msg":'Dashboard Updated Successfull'}
                pk = str(dashboard.pk)
                return redirect('/project-dashboard/'+pk+'/')
            else:
                msg={"msg":'Please Fill the Details Befour Submit'}
        else:
            ##print("form invalid",form.errors)
            msg= "There is an error in dashboard creation"
            project = Project.objects.get(pk=pk)
        try:
            dashboards = ProjectDashboard.objects.filter(project=project)
        except:
            dashboards=None
        current_site = get_current_site(request)
        site_name = current_site.name
        domain = current_site.domain
        if domain.startswith('127.0.'):
            domain = 'https://'+domain
        else:
            domain = 'https://'+domain
        if Project.objects.filter(pk=project.pk,admin_user=request.user).exists():
            permission="Admin"
        elif ProjectUser.objects.filter(project=project,project_user=request.user).exists():
            user_group = User.objects.get(pk=request.user.pk)

            for g in user_group.groups.all():
                if g.name == str(project.pk)+"_Read":
                    permission="Read"
                elif g.name == str(project.pk)+"_Write":
                    permission="Write"
                elif g.name == str(project.pk)+"_Delete":
                    permission="Delete"
                elif g.name == str(project.pk)+"_Admin":
                    permission="Admin"
        else:
            permission=None

        endpoint_pk = []
        for key, value in dashboard.dashboard_format.items():
            if value['type'] == 'end_point':
                endpoint_pk.append(value['id'])
                for end_point in dashboard.end_point.all():
                    if value['id'] == str(end_point.pk):
                        value['id'] = end_point.id
                        value['end_point']=str(end_point)

        endpoints = ProjectEndPoint.objects.filter(project=project)
        js_data =end_point_columns(endpoints,project)
        dashboard_form = ProjectDashboardEditForm(initial={'project':project.pk,'user':dashboard.dashboard_users.all(),'email_users':dashboard.additional_email,'report_frequency':dashboard.report_frequency,'name':dashboard.name})
        dashboard_form.fields['user'].queryset = ProjectUser.objects.filter(project=project)
        dashboards = ProjectDashboard.objects.filter(project=project)
        ##print("form",dashboard_form)
        context={'permission':permission,'msg':msg,'domain':domain,'project':project,'end_points':endpoints,'dashboard_form':dashboard_form,'dashboard':dashboard,'dashboards':dashboards,'js_data':js_data}

        return render(request,'dashboard/project_dashboard_update.html',context)


class ProjectRowColView(LoginRequiredMixin,View,PermissionRequiredMixin):
    login_url = '/customer/login/'
    redirect_field_name = 'redirect_to'
    template_name='dashboard/index.html'
    permission_required = ('coreapp.read_project')
    def post(self,request,pk):
        rows_from = int(request.POST['from_row'])
        rows_to = int(request.POST['to_row'])
        project = Project.objects.get(pk=pk)
        start_date = None
        df = optimize.index_optimize(start_date,pk)
        ##print(df)
        new_df = df.iloc[rows_from:rows_to]
        project_meta = ProjectMetaData.objects.get(project=project)
        if project_meta.date_column_name:
            date_field = project_meta.date_column_name
        else:
            date_field = None
        if date_field:
            new_df[date_field] = new_df[date_field].astype(str)
        res_json=new_df.to_json(orient='index')
        if request.user:
            ##print("the user",request.user)

            if DataFrameDisplay.objects.filter(project=project,user=request.user).exists():

                display_df = DataFrameDisplay.objects.get(project=project,user=request.user)
                ##print("exists",display_df.pk)
                update  = DataFrameDisplay.objects.filter(project=project,user=request.user).update(from_row = rows_from,to_row=rows_to,df=res_json)
                data = {'id':display_df.pk}
            else:
                ##print("no data")
                display_df,created  = DataFrameDisplay.objects.get_or_create(project=project,user=request.user,from_row = rows_from,to_row=rows_to,df=res_json)
                data = {'id':display_df.pk}
        else:
            data = {'error_msg':"User is not defiled"}
        ##print(new_df)

        return JsonResponse(data, safe = False)


from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template

from xhtml2pdf import pisa

def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None


class GeneratePdf(View):
    def get(self, request, *args, **kwargs):
        data = {
             'today': datetime.date.today(),
             'amount': 39.99,
            'customer_name': 'Cooper Mann',
            'order_id': 1233434,
        }

        return HttpResponse(pdf, content_type='application/pdf')


class ProjectDashboardeEmail(View):
    '''class for generating and mailing the dashboard'''
    def get(self,request,pk):
        dashboard = ProjectDashboard.objects.get(pk=pk)
        hash_str = str(pk)+"dashboard"
        hash_code = str(hash(hash_str))
        update = ProjectDashboard.objects.filter(pk=pk).update(hash_code = hash_code)
        to_mail = []
        current_site = get_current_site(request)
        site_name = current_site.name
        domain = current_site.domain
        if domain.startswith('127.0.'):
            domain = 'https://'+domain
        else:
            domain = 'https://'+domain
        try:

            email_users = dashboard.additional_email.split(',')
            to_mail = [i for i in email_users ]
        except:
            email_users = None
        if email_users:
            if dashboard.dashboard_users:

                for u in  dashboard.dashboard_users.all():
                    to_mail.append(u.email)

        html_message = render_to_string('dashboard/report.html', {'hash_code': hash_code,'domain':domain})
        message = 'Please find the Link to  the shared dashboard from brayn.ai:'
        ##print("success",to_mail)
        mail.send_mail(
                'Shared dashboard link',
                "The Shared Dashboard",
               'noreply@brayn.ai',
                to_mail,
                html_message=html_message,
                fail_silently=False,
                )
        ##print("success",to_mail)


class SharedDashboardView(View):

    def get (self,request,key):
        template_name='dashboard/shared_project_dashboard.html'
        try:

            dashboard=ProjectDashboard.objects.get(hash_code=key)
        except:
            return render(request,template_name,{'msg':'Matching Dashboard Not Found'})
        dashboard_format = dashboard.dashboard_format
        ##print("length of dashboard items",len(dashboard_format))
        id_elem_hash = self._index_dashboard(dashboard_format)
        type_elem_hash = self._index_dashboard_type(dashboard_format)
        piqu,created = ProjectBillingPrms.objects.get_or_create(project=dashboard.project)
        update = ProjectBillingPrms.objects.filter(project=dashboard.project).update(query_count=piqu.query_count+1)
        if dashboard.end_point:
            plot_graphs = []
            query_results = {}
            project_meta_get_start_time = datetime.now()
            dashboard_format = dashboard.dashboard_format
            project_meta = ProjectMetaData.objects.values_list('date_column_name').get(project__id=dashboard.project_id)
            # ##print("the metadata load is ",project_meta)
            project_meta_get_end_time = datetime.now()
            project_meta_if_start_time = datetime.now()
            if project_meta:

                date_field = project_meta[0]
                # ##print("the metadata load is ",date_field)
            else:
                date_field=None
            project_meta_if_end_time = datetime.now()
            # ##print("before for loop",datetime.now())
            json_loading_start_time = datetime.now()
            result_df = optimize.optimize_data(dashboard.project_id,date_field)

            json_loading_end_time = datetime.now()
            project_all_query_load_time = datetime.now()
            metadata = ProjectMetaData.objects.get(project=dashboard.project)
            for end_point in dashboard.end_point.all():
                if not end_point.sub_df:
                    pv = QueryExcecute(end_point.query)
                    js_df = pv
                    if metadata.date_column_name:
                        js_df[metadata.date_column_name] =js_df[metadata.date_column_name].astype('str')


                    result_json = js_df.to_json(orient='index')
                    # vl.bari("unpivot of result df:"+str(end_point), 'e')

                    # vl.bari("saving sub_df:"+str(end_point), 's')
                    update = ProjectEndPoint.objects.filter(pk=end_point.pk).update(sub_df=result_json)
                    # vl.bari("saving sub_df:"+str(end_point), 'e')

                else:
                    # vl.bari("Loading sub_df:"+str(end_point), 's')
                    json_st = json.loads(end_point.sub_df)
                    # vl.bari('Before Dataframe')
                    json_df = pd.DataFrame(json_st) #TODO 'Taking time - Have to work'
                    # vl.bari('Before transpose')
                    pv = json_df.transpose()
                    df_columns     = pv.columns.tolist()
                    for key, value in metadata.meta_data.items():
                        if key in df_columns:
                            ##print("key",key)
                            if value['dtype'] == 'int':
                                pv[key] =pd.to_numeric(pv[key])
                                if key in df_columns:
                                    pv[key] = pd.to_numeric(pv[key])
                            elif value['dtype'] == 'float':
                                ##print("final key",key,pv[key],pv[key].dtypes)
                                pv[key] = pd.to_numeric(pv[key])
                                if key in df_columns:
                                    pv[key] = pd.to_numeric(pv[key])
                            elif value['dtype'] == 'object':
                                pv[key] = pv[key].astype(str)
                                if key in df_columns:
                                    pv[key] = pv[key].astype(str)
                            elif value['dtype'] == 'bool':
                                pv[key] = pv[key].astype(bool)
                                if key in df_columns:
                                    pv[key] = pv[key].astype(bool)
                            elif value['dtype'] == 'DateTime':
                                pv[key] =pd.to_datetime(pv[key])
                                ##print("the data key",key)
                                if key in df_columns:
                                    pv[key] = pd.to_datetime(pv[key])
                    # vl.bari("Loading sub_df:"+str(end_point), 'e')
                string_columns = pv.select_dtypes(include =['object','bool'])
                df_columns     = pv.columns.tolist()
                plot_df  = pv
                if metadata.date_column_name in df_columns and metadata.date_column_name:
                    plot_df[metadata.date_column_name] =plot_df[metadata.date_column_name].astype('str')


                plot_start_time = datetime.now()

                # vl.bari("Rendering Plot:"+str(end_point), 's')
                if end_point.plot and end_point.plot.plot_type:
                    end_point_obj = EndPointPlot(plot_df,end_point.pk)
                    div = end_point_obj.plot(end_point.plot)

                else:
                    # fig = px.scatter_matrix(plot_df)
                    # div = opy.plot(fig, auto_open=False,output_type='div')
                    div = True
                # vl.bari("Rendering Plot:"+str(end_point), 'e') # TODO 'Taking time have to work '

                # vl.bari("Updating dashboard object:"+str(end_point), 's')
                key = id_elem_hash[str(end_point.id)]
                value  = dashboard_format[key]
                # print("the object",dashboard_format)
                if value['id'] == str(end_point.id):
                    value['div']= div
                    value['id'] = end_point.id
                    value['end_point']=end_point

                    if end_point.algorithm:
                        features_text = end_point.algorithm.feature
                        features_text = features_text.replace('[', '')
                        features_text = features_text.replace(']', '')
                        features      = features_text.split(',')
                        features_ml_display = features_text.split(',')
                        ##print("features",features)

                        test_l =[]
                        features_cat_dict = {}
                        ml_df = pd.DataFrame()
                        for column in features:
                            ml_df[column] = pv[column]

                        ml_string_columns = ml_df.select_dtypes(include =['object','bool'])
                        ##print("the ml string columns ",ml_string_columns)




                        ##print("after ml df ",ml_df)
                        for column in ml_string_columns:
                            if ml_df[column].dtypes  == np.bool:
                                ##print("the data value",df[column],column)

                                column_name = column +'_cat'
                                d = {}

                                new_df = pd.DataFrame()
                                new_df[column] = pd.unique(pv[column])

                                column_name = column+'_cat'
                                new_df[column] = new_df[column].astype('category')
                                new_df[column_name] = new_df[column].cat.codes
                                c_series = new_df[column]
                                c_cat_series = new_df[column_name]
                                c_list = c_series.tolist()
                                c_cat_list = c_cat_series.tolist()
                                ##print("new_df",new_df)

                                for i in range(0,len(c_list)):
                                    d[c_list[i]]=c_cat_list[i]
                                features_cat_dict[column]=d
                                ##print("features",features_cat_dict)
                                features.remove(column)
                                ##print("features",features)



                            else:
                                try:

                                    ml_df[column] = ml_df[column].astype(float)
                                    ##print("in float type column is",column,ml_df[column])
                                except:

                                    d = {}

                                    new_df = pd.DataFrame()
                                    new_df[column] = pd.unique(pv[column])

                                    column_name = column+'_cat'
                                    new_df[column] = new_df[column].astype('category')
                                    new_df[column_name] = new_df[column].cat.codes
                                    c_series = new_df[column]
                                    c_cat_series = new_df[column_name]
                                    c_list = c_series.tolist()
                                    c_cat_list = c_cat_series.tolist()
                                    ##print("new_df",new_df)

                                    for i in range(0,len(c_list)):
                                        d[c_list[i]]=c_cat_list[i]
                                    features_cat_dict[column]=d
                                    ##print("features",features_cat_dict)
                                    features.remove(column)




                        target   = end_point.algorithm.y_factor
                        model_id = end_point.algorithm.model_id
                        if end_point.algorithm.type_of_prediction == 'Linear':
                            accuracy = ast.literal_eval(end_point.algorithm.accuracy)
                            MAE = accuracy['MAE']
                            MSE = accuracy['MSE']
                            RMSE = accuracy['RMSE']
                            accuracy_list = {'MAE':MAE,'MSE':MSE,'RMSE':RMSE}
                        else:
                            accuracy_list={'accuracy':end_point.algorithm.accuracy}
                        value['features']=features
                        value['features_ml_display']=features_ml_display
                        value['features_cat_dict'] = features_cat_dict
                        value['target']= target
                        value['accuracy']= accuracy_list
                        value['model_id'] = model_id

                    if end_point.plot:
                        value['legend'] = end_point.plot.legend
                    else:
                        value['legend'] = False
                    dashboard_format[key] = value




                query_results[end_point.query.query_id]=res_df__table_content
            dashboard_format = dashboard_object_update(dashboard_format,type_elem_hash)
            data ={ 'dashboard_format':dashboard_format}
            context={'query_results':query_results,'dashboard_format':dashboard_format,'dashboard':dashboard}
            return render(request,template_name,context)
    def _index_dashboard(self,dashboard_format):
        indexing ={}
        for key, value in dashboard_format.items():
            indexing[str(value['id'])]=key
        return indexing
    def _index_dashboard_type(self,dashboard_format):

        elem_list =[]

        for key, value in dashboard_format.items():
            if value['type'] == 'row_constructor':
                elem_list.append(key)

        return elem_list



class ProjectEndPointWindoowView(GroupRequiredMixin,LoginRequiredMixin,View):
    def dispatch(self, request, *args, **kwargs):
        pk = kwargs['pk']
        end_point = ProjectEndPoint.objects.get(pk=pk)
        project=Project.objects.get(pk=end_point.project.pk)
        piqu,crteated = ProjectBillingPrms.objects.get_or_create(project=project)
        update = ProjectBillingPrms.objects.filter(project=project).update(query_count=piqu.query_count+1)
        pk= str(project.pk)
        self.login_url = '/customer/login/'
        self.redirect_field_name = 'redirect_to'
        self.template_name='dashboard/index.html'
        admin_name = pk+"_Admin"
        ##print(type(admin_name), admin_name)
        admin_encode_name = admin_name.encode()
        admin_unicode_name = admin_encode_name.decode('utf-8')
        write_name = pk+"_Write"
        ##print(type(write_name), write_name)
        write_encode_name = write_name.encode()
        write_unicode_name = write_encode_name.decode('utf-8')
        read_name = pk+"_Read"
        ##print(type(read_name), read_name)
        read_encode_name = read_name.encode()
        read_unicode_name = read_encode_name.decode('utf-8')
        delete_name = pk+"_Delete"
        ##print(type(delete_name), delete_name)
        delete_encode_name = delete_name.encode()
        delete_unicode_name = delete_encode_name.decode('utf-8')
        l =[delete_unicode_name,write_unicode_name,admin_unicode_name,read_unicode_name]
        self.group_required= l
        ##print("the self of dispatcher",self.group_required)

        return super(ProjectEndPointWindoowView, self).dispatch(request, *args, **kwargs)

    def get(self,request,pk):
        end_point = ProjectEndPoint.objects.get(pk=pk)
        p_query = end_point.query

        end_point = ProjectEndPoint.objects.get(pk=pk)
        if Project.objects.filter(pk=p_query.project.pk,admin_user=request.user).exists():
            permission="Admin"
        elif ProjectUser.objects.filter(project=p_query.project,project_user=request.user).exists():
            user_group = User.objects.get(pk=request.user.pk)

            for g in user_group.groups.all():
                if g.name == str(p_query.project.pk)+"_Read":
                    permission="Read"
                elif g.name == str(p_query.project.pk)+"_Write":
                    permission="Write"
                elif g.name == str(p_query.project.pk)+"_Delete":
                    permission="Delete"
                elif g.name == str(p_query.project.pk)+"_Admin":
                    permission="Admin"
        else:
            permission=None
        if not end_point.sub_df:
            if p_query.start_date:

                start_date = p_query.start_date
                from_date_select = p_query.start_date_select

                date = start_date.split('-')
                if len(date)==1:
                    if from_date_select == 'day':
                        start_date =today -timedelta(days=int(date[0]))
                    elif from_date_select == 'week':
                        start_date =today -timedelta(days=7*int(date[0]))
                    elif from_date_select == 'month':
                        start_date =today -timedelta(int(date[0])*365/12)
                    elif from_date_select == 'year':
                        start_date =today -timedelta(int(date[0])*365)

            else:
                start_date = None
            if p_query.end_date:

                end_date   = p_query.end_date
                to_date_select = p_query.end_date_select
                date = end_date.split('-')
                if len(date)==1:
                    if to_date_select == 'day':
                        end_date =today -timedelta(days=int(date[0]))
                    elif to_date_select == 'week':
                        end_date =today -timedelta(days=int(7*date[0]))
                    elif to_date_select == 'month':
                        end_date =today -timedelta(int(date[0])*365/12)
                    elif to_date_select == 'year':
                        end_date =today -timedelta(int(date[0])*365)
                    elif to_date_select == 'today':
                        end_date =today
            else:
                end_date = None
            if p_query.expected_range:

                frequency = p_query.expected_range
            else:

                frequency=None
            if p_query.group_query:
                grouping_colums = list(p_query.group_query.split(","))
            else:
                grouping_colums = None
            if p_query.aggregation_value:
                value_columns = list(p_query.aggregation_value.split(","))
                # ##print("the splited value columns are",value_columns)
            else:
                value_columns = None



            if p_query.aggregation_query:
                aggregation = ast.literal_eval(p_query.aggregation_query)
            else:
                aggregation = None

            project_meta = ProjectMetaData.objects.get(project=p_query.project)
            if project_meta.date_column_name:
                date_field = project_meta.date_column_name
            else:
                date_field=None


            if p_query.where_query:
                res_df = query.subset(p_query.project.pk,frequency,1,start_date=start_date,end_date=end_date,grouping_columns=grouping_colums,where=p_query.where_query,aggregation=aggregation,date_column=date_field)
            else:
                res_df = query.subset(p_query.project.pk,frequency,1,start_date=start_date,end_date=end_date,grouping_columns=grouping_colums,aggregation=aggregation,date_column=date_field)


            project_meta = ProjectMetaData.objects.get(project=p_query.project)
            if project_meta.date_column_name:
                date_field = project_meta.date_column_name
            else:
                date_field=None
            ##print("final df after grouping is ",res_df)
            if date_field:
                if not p_query.where_query and not grouping_colums and not aggregation :
                    df = res_df

                elif p_query.where_query and not grouping_colums and not aggregation :
                    df = res_df

                elif p_query.where_query  and grouping_colums and not aggregation  :
                    ##print("no aggregation with grouping")
                    df = res_df
                elif p_query.where_query  and grouping_colums and  aggregation and frequency :
                    ##print("no aggregation with grouping")
                    df =  res_df.stack().reset_index()
                elif p_query.where_query  and grouping_colums and  aggregation and not frequency:
                    ##print("no aggregation with grouping")
                    df =  res_df.reset_index()
                elif not p_query.where_query  and not  grouping_colums and not  aggregation and frequency:
                    ##print("no aggregation with grouping")
                    df =  res_df
                elif p_query.where_query and not grouping_colums  and  aggregation and frequency:
                    ##print("aggregation with grouping")
                    pv_df = res_df.transpose()
                    df = pv_df.reset_index()
                elif not grouping_colums  and  aggregation and frequency:
                    ##print("aggregation with grouping")
                    pv_df = res_df.transpose()
                    df = pv_df.reset_index()
                elif grouping_colums  and  aggregation and frequency:
                    ##print("aggregation with grouping")
                    df = res_df.stack().reset_index()
                elif grouping_colums  and  aggregation and not frequency:
                    ##print("aggregation with grouping")
                    df = res_df.reset_index()
                elif grouping_colums:
                    df = res_df
                elif p_query.where_query:
                    df = res_df

                else:
                    ##print("aggregation")
                    pv_df = res_df.transpose()
                    df = pv_df.reset_index()
            else:
                if not p_query.where_query and not grouping_colums and not aggregation :
                    df = res_df
                elif p_query.where_query and not grouping_colums and not aggregation :
                    df = res_df

                elif p_query.where_query  and grouping_colums and not aggregation:
                    df = res_df
                elif p_query.where_query  and grouping_colums and aggregation:
                    df = res_df.reset_index()
                elif grouping_colums and aggregation:
                    df = res_df.reset_index()
                elif grouping_colums and  not aggregation:
                    df = res_df
            result_json = df.to_json(orient='index')
            ##print("updating the json sub_df")
            update = ProjectEndPoint.objects.filter(pk=end_point.pk).update(sub_df=result_json)
            # ep =   ProjectEndPoint.objects.get(pk=end_point.pk)
            # ##print("after update the sub_df is",ep.sub_df)
        else:
            ##print("loding from json data")
            json_st = json.loads(end_point.sub_df)
            # ##print("THE TYPE OF JSON FILE<",type(json_st))
            json_df = pd.DataFrame(json_st)
            df = json_df.transpose()
        res_df__table_content = df.to_html(classes="table table-striped tableFixHead",border="0")
        df_columns     = df.columns.tolist()

        for column in df_columns:
            try:
                df[column] = pd.to_numeric(df[column])
            except:
                pass
        # t_df = res_df.T
        # ##print("the visulization columns",df)
        string_columns = df.select_dtypes(include =['object','bool'])
        metadata = ProjectMetaData.objects.get(project=p_query.project)
        if metadata.date_column_name:
            df[metadata.date_column_name] = df[metadata.date_column_name].astype(str)
        df_columns     = df.columns.tolist()
        row_count = df.shape[1]
        column_count = df.shape[0]
        if end_point.plot and end_point.plot.plot_type:
            end_point_obj = EndPointPlot(df,end_point.pk)
            div = end_point_obj.plot(end_point.plot)

        else:
            # fig = px.scatter_matrix(df)
            # div = opy.plot(fig, auto_open=False, output_type='div')
            div = True
        dashboards_form = ProjectDashboardsForm(initial={'project':end_point.project.pk})
        project_billing = ProjectBillingPrms.objects.get(project=end_point.project)
        update = ProjectBillingPrms.objects.filter(pk=project_billing.pk).update(query_count=project_billing.query_count)

        context = {'graph':div,'end_point':end_point,'query':res_df__table_content,'permission':permission,'row_count':row_count,'column_count':column_count,'string_columns':string_columns,'df_columns':df_columns,'dashboards_form':dashboards_form}
        return render(request,'dashboard/project_end_point_window.html',context)


class DataframeDisplayView(View):
    ''' class to display the filter rows from the project dashboard'''
    def get(self,request,pk):

        display_df = DataFrameDisplay.objects.get(pk=pk)
        ##print("display_df",display_df)
        json_st = json.loads(display_df.df)
        json_df = pd.DataFrame(json_st)
        df = json_df.transpose()
        data_table = df.to_html(classes="table table-striped tableFixHead",border="0")
        customer = Customer.objects.get(user =display_df.user )
        context = {'data_table':data_table,'customer':customer}
        return render(request,'dashboard/Project_data_row_display.html',context)




class ProjectBillingUpdateView(View):
    def post(self,request,pk):
        project = Project.objects.get(pk=pk)

        users = int(request.POST['user'])
        endpoints = int(request.POST['end_point'])


        project_billing,created = ProjectBillingPrms.objects.get_or_create(project=project)
        project_billing_update = ProjectBillingPrms.objects.filter(project=project).update(user=users,end_point=endpoints)
        pk = str(project.pk)
        return  redirect('/single-project-details/'+pk+'/')


class DashboardPublicView(View):
    @xframe_options_exempt
    def get (self,request,key):
        ##print("the request initiated",request)
        template_name='dashboard/public_dashboard.html'
        time_now = datetime.now()
        # ##print("time now ",time_now)

        get_query_start_time = datetime.now()
        try:
            dashboard = ProjectDashboard.objects.select_related('project').prefetch_related('end_point').get(public_shared_code=key)
            ##print("tha dash board without any queries",dashboard)
        except:
            return render(request,template_name,{'msg':'Matching Dashboard Not Found'})
        dashboard_format = dashboard.dashboard_format
        ##print("length of dashboard items",len(dashboard_format))
        id_elem_hash = self._index_dashboard(dashboard_format)
        type_elem_hash = self._index_dashboard_type(dashboard_format)
        get_query_end_time = datetime.now()
        project_billing = ProjectBillingPrms.objects.get(project=dashboard.project)
        update = ProjectBillingPrms.objects.filter(pk=project_billing.pk).update(query_count=project_billing.query_count)
        if dashboard.end_point:
            plot_graphs = []
            query_results = {}
            project_meta_get_start_time = datetime.now()
            dashboard_format = dashboard.dashboard_format
            project_meta = ProjectMetaData.objects.values_list('date_column_name').get(project__id=dashboard.project_id)
            # ##print("the metadata load is ",project_meta)
            project_meta_get_end_time = datetime.now()
            project_meta_if_start_time = datetime.now()
            if project_meta:

                date_field = project_meta[0]
                # ##print("the metadata load is ",date_field)
            else:
                date_field=None
            project_meta_if_end_time = datetime.now()
            # ##print("before for loop",datetime.now())
            json_loading_start_time = datetime.now()
            result_df = optimize.optimize_data(dashboard.project_id,date_field)

            json_loading_end_time = datetime.now()
            project_all_query_load_time = datetime.now()
            metadata = ProjectMetaData.objects.get(project=dashboard.project)
            for end_point in dashboard.end_point.all():
                if not end_point.sub_df:
                    pv = QueryExcecute(end_point.query)
                    js_df = pv
                    if metadata.date_column_name:
                        js_df[metadata.date_column_name] =js_df[metadata.date_column_name].astype('str')


                    result_json = js_df.to_json(orient='index')
                    # vl.bari("unpivot of result df:"+str(end_point), 'e')

                    # vl.bari("saving sub_df:"+str(end_point), 's')
                    update = ProjectEndPoint.objects.filter(pk=end_point.pk).update(sub_df=result_json)
                    # vl.bari("saving sub_df:"+str(end_point), 'e')

                else:
                    # vl.bari("Loading sub_df:"+str(end_point), 's')
                    json_st = json.loads(end_point.sub_df)
                    # vl.bari('Before Dataframe')
                    json_df = pd.DataFrame(json_st) #TODO 'Taking time - Have to work'
                    # vl.bari('Before transpose')
                    pv = json_df.transpose()
                    df_columns     = pv.columns.tolist()
                    for key, value in metadata.meta_data.items():
                        if key in df_columns:
                            ##print("key",key)
                            if value['dtype'] == 'int':
                                pv[key] =pd.to_numeric(pv[key])
                                if key in df_columns:
                                    pv[key] = pd.to_numeric(pv[key])
                            elif value['dtype'] == 'float':
                                ##print("final key",key,pv[key],pv[key].dtypes)
                                pv[key] = pd.to_numeric(pv[key])
                                if key in df_columns:
                                    pv[key] = pd.to_numeric(pv[key])
                            elif value['dtype'] == 'object':
                                pv[key] = pv[key].astype(str)
                                if key in df_columns:
                                    pv[key] = pv[key].astype(str)
                            elif value['dtype'] == 'bool':
                                pv[key] = pv[key].astype(bool)
                                if key in df_columns:
                                    pv[key] = pv[key].astype(bool)
                            elif value['dtype'] == 'DateTime':
                                pv[key] =pd.to_datetime(pv[key])
                                ##print("the data key",key)
                                if key in df_columns:
                                    pv[key] = pd.to_datetime(pv[key])
                    # vl.bari("Loading sub_df:"+str(end_point), 'e')
                string_columns = pv.select_dtypes(include =['object','bool'])
                df_columns     = pv.columns.tolist()
                plot_df  = pv
                if metadata.date_column_name in df_columns and metadata.date_column_name:
                    plot_df[metadata.date_column_name] =plot_df[metadata.date_column_name].astype('str')


                plot_start_time = datetime.now()

                # vl.bari("Rendering Plot:"+str(end_point), 's')
                if end_point.plot and end_point.plot.plot_type:
                    end_point_obj = EndPointPlot(plot_df,end_point.pk)
                    div = end_point_obj.plot(end_point.plot)

                else:
                    # fig = px.scatter_matrix(plot_df)
                    # div = opy.plot(fig, auto_open=False,output_type='div')
                    div = True
                # vl.bari("Rendering Plot:"+str(end_point), 'e') # TODO 'Taking time have to work '

                # vl.bari("Updating dashboard object:"+str(end_point), 's')
                key = id_elem_hash[str(end_point.id)]
                value  = dashboard_format[key]
                # print("the object",dashboard_format)
                if value['id'] == str(end_point.id):
                    value['div']= div
                    value['id'] = end_point.id
                    value['end_point']=end_point

                    if end_point.algorithm:
                        features_text = end_point.algorithm.feature
                        features_text = features_text.replace('[', '')
                        features_text = features_text.replace(']', '')
                        features      = features_text.split(',')
                        features_ml_display = features_text.split(',')
                        ##print("features",features)

                        test_l =[]
                        features_cat_dict = {}
                        ml_df = pd.DataFrame()
                        for column in features:
                            ml_df[column] = pv[column]

                        ml_string_columns = ml_df.select_dtypes(include =['object','bool'])
                        ##print("the ml string columns ",ml_string_columns)




                        ##print("after ml df ",ml_df)
                        for column in ml_string_columns:
                            if ml_df[column].dtypes  == np.bool:
                                ##print("the data value",df[column],column)

                                column_name = column +'_cat'
                                d = {}

                                new_df = pd.DataFrame()
                                new_df[column] = pd.unique(pv[column])

                                column_name = column+'_cat'
                                new_df[column] = new_df[column].astype('category')
                                new_df[column_name] = new_df[column].cat.codes
                                c_series = new_df[column]
                                c_cat_series = new_df[column_name]
                                c_list = c_series.tolist()
                                c_cat_list = c_cat_series.tolist()
                                ##print("new_df",new_df)

                                for i in range(0,len(c_list)):
                                    d[c_list[i]]=c_cat_list[i]
                                features_cat_dict[column]=d
                                ##print("features",features_cat_dict)
                                features.remove(column)
                                ##print("features",features)



                            else:
                                try:

                                    ml_df[column] = ml_df[column].astype(float)
                                    ##print("in float type column is",column,ml_df[column])
                                except:

                                    d = {}

                                    new_df = pd.DataFrame()
                                    new_df[column] = pd.unique(pv[column])

                                    column_name = column+'_cat'
                                    new_df[column] = new_df[column].astype('category')
                                    new_df[column_name] = new_df[column].cat.codes
                                    c_series = new_df[column]
                                    c_cat_series = new_df[column_name]
                                    c_list = c_series.tolist()
                                    c_cat_list = c_cat_series.tolist()
                                    ##print("new_df",new_df)

                                    for i in range(0,len(c_list)):
                                        d[c_list[i]]=c_cat_list[i]
                                    features_cat_dict[column]=d
                                    ##print("features",features_cat_dict)
                                    features.remove(column)




                        target   = end_point.algorithm.y_factor
                        model_id = end_point.algorithm.model_id
                        if end_point.algorithm.type_of_prediction == 'Linear':
                            accuracy = ast.literal_eval(end_point.algorithm.accuracy)
                            MAE = accuracy['MAE']
                            MSE = accuracy['MSE']
                            RMSE = accuracy['RMSE']
                            accuracy_list = {'MAE':MAE,'MSE':MSE,'RMSE':RMSE}
                        else:
                            accuracy_list={'accuracy':end_point.algorithm.accuracy}
                        value['features']=features
                        value['features_ml_display']=features_ml_display
                        value['features_cat_dict'] = features_cat_dict
                        value['target']= target
                        value['accuracy']= accuracy_list
                        value['model_id'] = model_id

                    if end_point.plot:
                        value['legend'] = end_point.plot.legend
                    else:
                        value['legend'] = False
                    dashboard_format[key] = value

                # print("the finalobje is ",dashboard_format)
                # vl.bari("Updating dashboard object:"+str(end_point), 'e')
                # vl.bari("Before df table content results:"+str(end_point), 's')

                # vl.bari("Before df table content results:"+str(end_point), 'e')

                # vl.turn_on_full_debug()
                # vl.fullbari("multiple array", 1, 2, 3, "mixed datatype messages for", end_point, "for demo")

            dashboard_format = dashboard_object_update(dashboard_format,type_elem_hash)
            data_assigning_time = datetime.now()
            data ={ 'dashboard_format':dashboard_format,'end_point':end_point}
            context={'query_results':query_results,'dashboard_format':dashboard_format,'dashboard':dashboard}
            time_after= datetime.now()
            ##print("json load time ",json_loading_start_time,json_loading_end_time)
            ##print("single query excecution time",query_start_time,query_end_time)

            ##print(" total viewtime before after",time_now,time_after)
            ##print(" single the sub df data load time",query_start_with_sub_df_time,query_start_with_sub_df_time)
            ##print("Dashboard get query time",get_query_start_time,get_query_end_time)
            ##print("metadata get  time",project_meta_get_start_time,project_meta_get_end_time)
            ##print("metadata get if   time",project_meta_if_start_time,project_meta_if_end_time)
            ##print("all query execution in loop time",project_all_query_load_time,project_all_query_load_end_time)
            time_after = datetime.now()
            ##print("data assiging time",data_assigning_time,time_after)

            ##print("the request compelted and rendered")
            return render(request,template_name,context)

    def _index_dashboard(self,dashboard_format):
        indexing ={}
        for key, value in dashboard_format.items():
            indexing[str(value['id'])]=key
        return indexing
    def _index_dashboard_type(self,dashboard_format):

        elem_list =[]

        for key, value in dashboard_format.items():
            if value['type'] == 'row_constructor':
                elem_list.append(key)

        return elem_list



class ProjectDashboardRefreshView(GroupRequiredMixin,LoginRequiredMixin,View):
    login_url = '/customer/login/'
    redirect_field_name = 'redirect_to'
    template_name='dashboard/index.html'
    def dispatch(self, request, *args, **kwargs):
        pk = kwargs['pk']
        dashboard = ProjectDashboard.objects.get(pk=pk)
        project=Project.objects.get(pk=dashboard.project.pk)
        pk= str(project.pk)
        self.login_url = '/customer/login/'
        self.redirect_field_name = 'redirect_to'
        self.template_name='dashboard/index.html'
        admin_name = pk+"_Admin"
        ##print(type(admin_name), admin_name)
        admin_encode_name = admin_name.encode()
        admin_unicode_name = admin_encode_name.decode('utf-8')
        write_name = pk+"_Write"
        ##print(type(write_name), write_name)
        write_encode_name = write_name.encode()
        write_unicode_name = write_encode_name.decode('utf-8')
        read_name = pk+"_Read"
        ##print(type(write_name), write_name)
        read_encode_name = read_name.encode()
        read_unicode_name = read_encode_name.decode('utf-8')
        delete_name = pk+"_Delete"
        delete_encode_name = delete_name.encode()
        delete_unicode_name = delete_encode_name.decode('utf-8')
        l= [delete_unicode_name,admin_unicode_name,write_unicode_name,read_unicode_name]
        self.group_required= l
        ##print("the self of dispatcher",self.group_required)

        return super(ProjectDashboardRefreshView, self).dispatch(request, *args, **kwargs)
    def get (self,request,pk):
        start_time =datetime.now()
        # ##print("start time ",start_time)
        template_name='dashboard/project_dashboard.html'
        dashboard=ProjectDashboard.objects.get(pk=pk)
        dashboard_format = dashboard.dashboard_format
        ##print("length of dashboard items",len(dashboard_format))
        id_elem_hash = self._index_dashboard(dashboard_format)
        type_elem_hash = self._index_dashboard_type(dashboard_format)
        piqu,created = ProjectBillingPrms.objects.get_or_create(project=dashboard.project)
        update = ProjectBillingPrms.objects.filter(project=dashboard.project).update(query_count=piqu.query_count+1)
        if Project.objects.filter(pk=dashboard.project.pk,admin_user=request.user).exists():
            permission="Admin"
        elif ProjectUser.objects.filter(project=dashboard.project,project_user=request.user).exists():
            user_group = User.objects.get(pk=request.user.pk)

            for g in user_group.groups.all():
                if g.name == str(dashboard.project.pk)+"_Read":
                    permission="Read"
                elif g.name == str(dashboard.project.pk)+"_Write":
                    permission="Write"
                elif g.name == str(dashboard.project.pk)+"_Delete":
                    permission="Delete"
                elif g.name == str(dashboard.project.pk)+"_Admin":
                    permission="Admin"
        else:
            permission=None
        current_site = get_current_site(request)
        site_name = current_site.name
        domain = current_site.domain
        if domain.startswith('127.0.'):
            domain = 'https://'+domain
        else:
            domain = 'https://'+domain

        if dashboard.end_point:
            plot_graphs = []
            query_results = {}
            dashboard_format = dashboard.dashboard_format

            for end_point in dashboard.end_point.all():
                query_start_time =datetime.now()
                pv = QueryExcecute(end_point.query)

                query_end_time =datetime.now()
                
                
                metadata = ProjectMetaData.objects.get(project=dashboard.project)
                df_columns     = pv.columns.tolist()
                for key, value in metadata.meta_data.items():
                    if key in df_columns:
                        ##print("key",key)
                        if value['dtype'] == 'int':
                            pv[key] =pd.to_numeric(pv[key])
                            if key in df_columns:
                                pv[key] = pd.to_numeric(pv[key])
                        elif value['dtype'] == 'float':
                            ##print("final key",key,pv[key],pv[key].dtypes)
                            pv[key] = pd.to_numeric(pv[key])
                            if key in df_columns:
                                pv[key] = pd.to_numeric(pv[key])
                        elif value['dtype'] == 'object':
                            pv[key] = pv[key].astype(str)
                            if key in df_columns:
                                pv[key] = pv[key].astype(str)
                        elif value['dtype'] == 'bool':
                            pv[key] = pv[key].astype(bool)
                            if key in df_columns:
                                pv[key] = pv[key].astype(bool)
                        elif value['dtype'] == 'DateTime':
                            pv[key] =pd.to_datetime(pv[key])
                            ##print("the data key",key)
                            if key in df_columns:
                                pv[key] = pd.to_datetime(pv[key])
                # t_df = res_df.T
                # ##print("the visulization columns",pv)
                string_columns = pv.select_dtypes(include =['object','bool'])
                
                plot_df  = pv
                if metadata.date_column_name in df_columns and  metadata.date_column_name:
                    plot_df[metadata.date_column_name] =plot_df[metadata.date_column_name].astype('str')


                plot_start_time = datetime.now()

                # vl.bari("Rendering Plot:"+str(end_point), 's')
                if end_point.plot and end_point.plot.plot_type:
                    end_point_obj = EndPointPlot(plot_df,end_point.pk)
                    div = end_point_obj.plot(end_point.plot)

                else:
                    # fig = px.scatter_matrix(plot_df)
                    # div = opy.plot(fig, auto_open=False,output_type='div')
                    div = True
                
                key = id_elem_hash[str(end_point.id)]
                value  = dashboard_format[key]
                # print("the object",dashboard_format)
                if value['id'] == str(end_point.id):
                    value['div']= div
                    value['id'] = end_point.id
                    value['end_point']=end_point

                    if end_point.algorithm:
                        features_text = end_point.algorithm.feature
                        features_text = features_text.replace('[', '')
                        features_text = features_text.replace(']', '')
                        features      = features_text.split(',')
                        features_ml_display = features_text.split(',')
                        ##print("features",features)

                        test_l =[]
                        features_cat_dict = {}


                        for column in features:
                            features_text = end_point.algorithm.feature
                            features_text = features_text.replace('[', '')
                            features_text = features_text.replace(']', '')
                            features      = features_text.split(',')
                            features_ml_display = features_text.split(',')
                            ##print("features",features)

                            test_l =[]
                            features_cat_dict = {}
                            ml_df = pd.DataFrame()
                            for column in features:
                                ml_df[column] = pv[column]

                            ml_string_columns = ml_df.select_dtypes(include =['object','bool'])
                            ##print("the ml string columns ",ml_string_columns)




                            ##print("after ml df ",ml_df)
                            for column in ml_string_columns:
                                if ml_df[column].dtypes  == np.bool:
                                    ##print("the data value",df[column],column)

                                    column_name = column +'_cat'
                                    d = {}

                                    new_df = pd.DataFrame()
                                    new_df[column] = pd.unique(pv[column])

                                    column_name = column+'_cat'
                                    new_df[column] = new_df[column].astype('category')
                                    new_df[column_name] = new_df[column].cat.codes
                                    c_series = new_df[column]
                                    c_cat_series = new_df[column_name]
                                    c_list = c_series.tolist()
                                    c_cat_list = c_cat_series.tolist()
                                    ##print("new_df",new_df)

                                    for i in range(0,len(c_list)):
                                        d[c_list[i]]=c_cat_list[i]
                                    features_cat_dict[column]=d
                                    ##print("features",features_cat_dict)
                                    features.remove(column)
                                    ##print("features",features)



                                else:
                                    try:

                                        ml_df[column] = ml_df[column].astype(float)
                                        ##print("in float type column is",column,ml_df[column])
                                    except:

                                        d = {}

                                        new_df = pd.DataFrame()
                                        new_df[column] = pd.unique(pv[column])

                                        column_name = column+'_cat'
                                        new_df[column] = new_df[column].astype('category')
                                        new_df[column_name] = new_df[column].cat.codes
                                        c_series = new_df[column]
                                        c_cat_series = new_df[column_name]
                                        c_list = c_series.tolist()
                                        c_cat_list = c_cat_series.tolist()
                                        ##print("new_df",new_df)

                                        for i in range(0,len(c_list)):
                                            d[c_list[i]]=c_cat_list[i]
                                        features_cat_dict[column]=d
                                        ##print("features",features_cat_dict)
                                        features.remove(column)
                                        ##print("features",features)




                        target   = end_point.algorithm.y_factor
                        model_id = end_point.algorithm.model_id
                        if end_point.algorithm.type_of_prediction == 'Linear':
                            accuracy = ast.literal_eval(end_point.algorithm.accuracy)
                            MAE = accuracy['MAE']
                            MSE = accuracy['MSE']
                            RMSE = accuracy['RMSE']
                            accuracy_list = {'MAE':MAE,'MSE':MSE,'RMSE':RMSE}
                        else:
                            accuracy_list={'accuracy':end_point.algorithm.accuracy}
                        value['features']=features
                        value['features_ml_display']=features_ml_display
                        value['features_cat_dict'] = features_cat_dict
                        value['target']= target
                        value['accuracy']= accuracy_list
                        value['model_id'] = model_id

                    if end_point.plot:
                        value['legend'] = end_point.plot.legend
                    else:
                        value['legend'] = False
                    dashboard_format[key] = value

            user = User.objects.get(pk=request.user.pk)
            customer = Customer.objects.get(user=user)
            dashboard_format = dashboard_object_update(dashboard_format,type_elem_hash)
            data ={ 'dashboard_format':dashboard_format,'end_point':end_point}
            today = datetime.now().date()
            context={'query_results':query_results,'domain':domain,'today':today,'dashboard_format':dashboard_format,'dashboard':dashboard,'customer':customer}
            end_time =datetime.now()
            ##print("compare time ",start_time,end_time)
            return render(request,template_name,context)
    def _index_dashboard(self,dashboard_format):
        indexing ={}
        for key, value in dashboard_format.items():
            indexing[str(value['id'])]=key
        return indexing
    def _index_dashboard_type(self,dashboard_format):

        elem_list =[]

        for key, value in dashboard_format.items():
            if value['type'] == 'row_constructor':
                elem_list.append(key)

        return elem_list



class InvoiceView(View):
    def get(self,request,pk):
        invoice = ProjectInvoice.objects.select_related('monthly_cost').get(pk=pk)
        amount = invoice.total_amount - invoice.discount_amount
        amount = amount *100
        tax = Tax.objects.all().order_by('-id')[0]
        customer = Customer.objects.get(user=invoice.monthly_cost.project.admin_user)
        if ProjectPricing.objects.filter(project=invoice.monthly_cost.project).exists():
            project_pricing = ProjectPricing.objects.values('free_tire').filter(project=invoice.monthly_cost.project).order_by('-id')[0]
        else:
            project_pricing =  DefaultProjectPricing.objects.values('free_tire').filter().order_by('-id')[0]
        free_tier = project_pricing['free_tire']
        return render(request,'dashboard/invoice_template.html',{'amount':amount,'invoice':invoice,'tax':tax,'customer':customer,'free_tier':free_tier})

    def post(self,request,pk):
        invoice = ProjectInvoice.objects.select_related('monthly_cost').get(pk=pk)
        update = ProjectInvoice.objects.filter(pk=pk).update(status = "Paid")
        pk = str(invoice.monthly_cost.project.pk)
        return redirect('/single-project-details/'+pk+'/')


class AddOnFileView(GroupRequiredMixin,LoginRequiredMixin,View):
    def dispatch(self, request, *args, **kwargs):
        pk = kwargs['pk']
        project=Project.objects.get(pk=pk)
        pk= str(project.pk)
        self.login_url = '/customer/login/'
        self.redirect_field_name = 'redirect_to'
        self.template_name='dashboard/index.html'
        admin_name = pk+"_Admin"
        ##print(type(admin_name), admin_name)
        admin_encode_name = admin_name.encode()
        admin_unicode_name = admin_encode_name.decode('utf-8')
        write_name = pk+"_Write"
        ##print(type(write_name), write_name)
        write_encode_name = write_name.encode()
        write_unicode_name = write_encode_name.decode('utf-8')
        read_name = pk+"_Read"
        ##print(type(write_name), write_name)
        read_encode_name = read_name.encode()
        read_unicode_name = read_encode_name.decode('utf-8')
        delete_name = pk+"_Delete"
        delete_encode_name = delete_name.encode()
        delete_unicode_name = delete_encode_name.decode('utf-8')
        l = [delete_unicode_name,admin_unicode_name,write_unicode_name]
        self.group_required= l
        ##print("the self of dispatcher",self.group_required)
        return super(AddOnFileView, self).dispatch(request, *args, **kwargs)

    def get(self,request,pk):
        template_name = 'dashboard/addonfile.html'
        project = Project.objects.get(pk=pk)
        permission = identify_user_permission(project,request.user)
        user = User.objects.get(pk=request.user.pk)
        if ProjectEndPoint.objects.filter(project=project).exists():
            project_endpoints = ProjectEndPoint.objects.filter(project=project).order_by('name')
        else:
            project_endpoints=None

        customer=Customer.objects.get(user=request.user)
        pk=str(project.pk)
        current_site = get_current_site(request)
        site_name = current_site.name
        domain = current_site.domain
        if domain.startswith('127.0.'):
            domain = 'https://'+domain
        else:
            domain = 'https://'+domain
        project_relations = ProjectFileRelationship.objects.filter(project=project)
        project_schema    = ProjectSchema.objects.get(project=project)
        file_count=len(project_schema.schema)
        if ProjectDashboard.objects.filter(Q(project=project) ).exists():
            # ##print("project admin")
            dashboard=ProjectDashboard.objects.filter(Q(project=project) ).order_by('-id')
            dashboard_count=ProjectDashboard.objects.filter(Q(project=project) ).count()
        else:
            dashboard = None
            dashboard_count = None


        project_meta_data = ProjectMetaData.objects.get(project=project)
        form = AddonFileForm()
        context = {'dashboard':dashboard,'permission':permission,'project_endpoints':project_endpoints,'customer':customer,'file_count':file_count,'project':project,'project_relations':project_relations,'project_schema':project_schema,'project_meta_data':project_meta_data,'form':form }
        return render(request,template_name,context)

    def post(self,request,pk):
        files = request.FILES.getlist('files')
        project = Project.objects.get(pk=pk)
        meta_data = ProjectMetaData.objects.get(project=project)
        project_schema = ProjectSchema.objects.get(project=project)

        if len(files)>0:
            df_obj = SchmaCheck(files)
            data = df_obj.schema_check(files,project,project_schema,meta_data)
            if "error" in data.keys():
                pass
            else:
                all_dfs = data['all_df']
                all_df = []
                schema_dict = data['schema_dict']
                update = ProjectSchema.objects.filter(project=project).update(schema=schema_dict)

                for key, val in all_dfs.items():
                    all_df.append(val)
                if len(all_dfs)>1:
                    column_conbine_obj = ColumnCombine()
                    relation_all_columns = column_conbine_obj.relation_dict_combine_add_on(all_dfs)


                ##print("all df",all_df)
                if len(all_df)>1:

                    count = len(all_df)
                    for i in range(count-1):
                        df_1 = all_df[0]
                        # ##print("the df_1",df_1)

                        df_2 = all_df[1]
                        # ##print("the df_2",df_2)
                        df_1.columns = df_1.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '').str.replace('.', '_').str.replace(',','_').str.replace('/','_').str.replace(':','')
                        column_list_1 = df_1.columns.to_list()
                        df_2.columns = df_2.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '').str.replace('.', '_').str.replace(',','_').str.replace('/','_').str.replace(':','')
                        column_list_2 = df_2.columns.tolist()
                        common_columns = intersection(column_list_1,column_list_2)
                        if len(common_columns)>=1:
                            # vl.fullbari("AddProjectView::post", "all the common columns",common_columns)
                            df =reduce(lambda left,right: pd.merge(left,right,on=common_columns, how='outer'), [df_1,df_2])
                        else:
                            df =reduce(lambda left,right: pd.merge(left,right, left_index=True, right_index=True, how='outer'), [df_1,df_2])
                            # ##print(" each ititration of for ",result_df)
                        all_df.pop(0)
                        all_df.pop(0)
                        all_df.insert(0,df)
                        # ##print("all_df after merge",all_df)
                elif len(all_df) == 1:
                    df = all_df[0]
                    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '').str.replace('.', '_').str.replace(',','_').str.replace('/','_').str.replace(':','')

                new_df_columns = df.columns.tolist()
                project_json = ProjectJsonStorage.objects.filter(project=project).order_by('id')[0]
                json_string = json.loads(project_json.js)
                json_df = pd.DataFrame(json_string)
                transposed_df = json_df.transpose()
                rows = transposed_df.shape[0]
                metadata = ProjectMetaData. objects.get(project=project)
                columns = metadata.columns['columns']


                transposed_df_columns = transposed_df.columns.tolist()

                new_columns = [x  for x in new_df_columns if x not in columns ]
                ##print("new columns are",new_columns)
                column_list = [x for x in transposed_df_columns if x in new_df_columns]
                # separate the mother df columns df into y_df

                # truncate the y_df based on the mother df rows
                for key, value in metadata.meta_data.items():
                    if key in transposed_df_columns:
                        ##print("key",key)
                        if value['dtype'] == 'int':
                            transposed_df[key] =pd.to_numeric(transposed_df[key])
                            if key in new_df_columns:
                                df[key] = pd.to_numeric(df[key])
                        elif value['dtype'] == 'float':
                            ##print("final key",key,transposed_df[key],transposed_df[key].dtypes)
                            transposed_df[key] = pd.to_numeric(transposed_df[key])
                            if key in new_df_columns:
                                df[key] = pd.to_numeric(df[key])
                        elif value['dtype'] == 'object':
                            transposed_df[key] = transposed_df[key].astype(str)
                            if key in new_df_columns:
                                df[key] = df[key].astype(str)
                        elif value['dtype'] == 'bool':
                            transposed_df[key] = transposed_df[key].astype(bool)
                            if key in new_df_columns:
                                df[key] = df[key].astype(bool)
                        elif value['dtype'] == 'DateTime':
                            transposed_df[key] =pd.to_datetime(transposed_df[key])
                            ##print("the data key",key)
                            if key in new_df_columns:
                                df[key] = pd.to_datetime(df[key])




                # merge the mother df with new rows ofss data
                if len(column_list)>0:
                    result_df = reduce(lambda left,right: pd.merge(left,right,on=column_list, how='outer'), [transposed_df,df])
                else:
                    try:
                        result_df = reduce(lambda left,right: pd.merge(left,right,left_on= transposed_df_columns[0],right_on=new_df_columns[0],how='outer'), [transposed_df,df])
                    except:
                        result_df = reduce(lambda left,right: pd.merge(left,right,left_index=True,right_index=True,how='outer'), [transposed_df,df])
                ##print("the df is ",result_df)
                result_df_rows = result_df.shape[0]
                df_rows = df.shape[0]
                if len(new_columns)>0:
                    column_conbine_obj = ColumnCombine()
                    dfs=[result_df]
                    data = column_conbine_obj.list_combine_with_datatype_integration(dfs,new_columns)
                    try:
                        error = data['Error']
                        data = {'error_msg':all_columns['error']}
                        # ##print("error",data)
                        return JsonResponse(data,safe=False)
                    except:
                        data = column_conbine_obj.list_combine_with_datatype_integration(dfs,new_columns)
                        ##print("the data for metadata collection is",data)
                    return JsonResponse(data,safe=False)
                elif len(files)>1:
                    try:
                        error = relation_all_columns['Error']
                        data = {'error_msg':relation_all_columns['Error']}
                        return JsonResponse(data,safe=False)
                    except:
                        data = {'relation_all_columns':relation_all_columns}

                        return JsonResponse(data,safe=True)



                #if there are  new columns
                # if len(new_columns)>0:
                #     result_df_rows = result_df.shape[0]
                #     df_rows = df.shape[0]
                #     ##print("the aded df, and result_df rows",df_rows,result_df_rows)

                #     if result_df_rows == df_rows:
                #         for column in new_columns:
                #             ##print("column is",column)
                #             result_df[column] = df[column]
                #             ##print("the result df is ",result_df)
                # else:
                #     pass
                result_df.columns = result_df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '').str.replace('.', '_').str.replace(',','_').str.replace('/','_').str.replace(':','').str.replace(':','')
                ##print("the final data frame",result_df)
                result_df_columns = result_df.columns.tolist()
                fillna_obj = FillNan(result_df)
                delete_column_list = []
                custom_column_list = {}
                today = datetime.now()
                metadata = ProjectMetaData. objects.get(project=project)
                meta_data_obj = metadata.meta_data
                result_df.drop_duplicates(subset = transposed_df_columns, inplace = True)



                fillna_obj = FillNan(result_df)
                for key, value in metadata.meta_data.items():

                    if key in result_df_columns:
                        ##print("key present in metadata ",key)
                        if value['handle_missing_data'] == 0:
                            fillna_obj.fillnan_with_0(key)
                        elif value['handle_missing_data'] == 'None':
                            fillna_obj.fillnan_with_None_value(key)
                        elif value['handle_missing_data'] == 'previous':
                            fillna_obj.fillnan_with_previous_value(key)
                        elif value['handle_missing_data'] == 'drop':
                            l = [key]
                            result_df = fillna_obj.drop_row(l)
                        elif value['handle_missing_data'] == 'delete_column':
                            co = key.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('.', '_').replace(',','_').replace('/','_').replace(':','')
                            delete_column_list.append(co)
                        else:
                            try:

                                custom_column_list[key]=int(value['handle_missing_data'])
                            except:
                                custom_column_list[key]=value['handle_missing_data']
                        # if value['dtype'] == dtype:
                        #     if value['handle_missing_data']== 'drop':
                        #         l = [key]
                        #         result_df[l].dropna(subset=l,inplace=True)
                        #         # result_df = fillna_obj.drop_row(l)
                        #     elif value['handle_missing_data'] == 0:
                        #         result_df[key].fillna(0, inplace=True)
                        #         # result_df = fillna_obj.fillnan_with_0(key)
                        #         ##print("after filling nan",key,result_df)
                        #     elif value['handle_missing_data'] == 'None':

                        #         # result_df = fillna_obj.fillnan_with_None_value(key)
                        #         result_df[key].fillna('None', inplace=True)
                        #         ##print("after filling nan",key,result_df)

                        #     elif value['handle_missing_data'] == 'previous':
                        #         result_df[key].fillna(method='ffill', inplace=True)
                        #         # result_df = fillna_obj.fillnan_with_previous_value(key)
                        #         ##print("after filling nan",key,result_df)



                        #     elif value['handle_missing_data'] == 'delete_column':
                        #         delete_column_list.append(key)
                        #     else:
                        #         try:

                        #             custom_column_list[key]=int(value['handle_missing_data'])
                        #         except:
                        #             custom_column_list[key]=value['handle_missing_data']
                        # else:
                        #     if value['handle_missing_data']== 'drop':
                        #         l = [key]
                        #         result_df[l].dropna(subset=l,inplace=True)
                        #         # result_df = fillna_obj.drop_row(l)
                        #     elif value['handle_missing_data'] == 0:
                        #         result_df[key].fillna(0,inplace=True)
                        #         # result_df = fillna_obj.fillnan_with_0(key)
                        #         ##print("after filling nan",key,result_df)
                        #     elif value['handle_missing_data'] == 'None':

                        #         # result_df = fillna_obj.fillnan_with_None_value(key)
                        #         result_df[key].fillna('None', inplace=True)
                        #         ##print("after filling nan",key,result_df)

                        #     elif value['handle_missing_data'] == 'previous':
                        #         result_df[key].fillna(method='ffill', inplace=True)
                        #         # result_df = fillna_obj.fillnan_with_previous_value(key)
                        #         ##print("after filling nan",key,result_df)



                        #     elif value['handle_missing_data'] == 'delete_column':
                        #         delete_column_list.append(key)
                        #     else:
                        #         try:

                        #             custom_column_list[key]=int(value['handle_missing_data'])
                        #         except:
                        #             custom_column_list[key]=value['handle_missing_data']
                ##print("the original df after nan filling is",result_df)
                if len(custom_column_list)>0:
                    ##print("the before nan fill ",len(result_df) - result_df.count())

                    result_df.fillna(value=custom_column_list,inplace=True)
                    ##print("the result after nan fill",result_df,custom_column_list)
                    ##print("after nan fill ",len(result_df) - result_df.count())

                if len(delete_column_list)>0:

                    ##print("the value ",delete_column_list)
                    column_delete_obj = DeleteColumn(result_df)
                    result_df = column_delete_obj.delete_column(delete_column_list)
                    ##print("columns ",result_df.columns.tolist())

                meta_data_obj = metadata.meta_data
                today = str(datetime.now())
                delete_column_list = []
                custom_column_list = {}
                for c in new_columns:
                    column = {}
                    ###print("the dataframe",c)
                    if df.dtypes[c] == np.int64:
                        column['dtype'] = 'int'
                    elif df.dtypes[c] == np.float64:
                        column['dtype'] = 'float'
                    elif df.dtypes[c] == np.object:
                        column['dtype'] = 'object'
                    elif df.dtypes[c] == np.bool:
                        column['dtype']= 'bool'
                    elif np.issubdtype(df[c].dtype, np.datetime64):
                        column['dtype'] = "DateTime"
                        df[c] = df[c].astype('str')


                    missing_data = None
                    missing_data_input=None
                    try:

                        cu =  c+'_select'
                        missing_data = request.POST[cu]
                    except:
                        pass
                    try:
                        cu =  c+'_input'
                        missing_data_input = request.POST[cu]
                    except:
                        pass
                    if missing_data and missing_data == 'zero':
                        column['handle_missing_data']= 0
                        today = str(datetime.now().date())
                        ###print("type of date",type(today))
                        column['start_date']= today
                        column['end_date']= ''
                        fillna_obj.fillnan_with_0(c)
                        ###print("nan filled df 0  ",c)
                    elif missing_data and missing_data == 'None':
                        column['handle_missing_data']= 'None'
                        fillna_obj.fillnan_with_None_value(c)
                        ###print("nan filled df None  ",c)
                        today = str(datetime.now().date())
                        ###print("type of date",type(today))
                        column['start_date']= today
                        column['end_date']= ''
                        column['column_deleted'] = False
                    elif missing_data and missing_data == 'previous':
                        column['handle_missing_data']= 'previous'
                        result_df = fillna_obj.fillnan_with_previous_value(c)
                        ###print("nan filled df ",result_df)
                        today = str(datetime.now().date())
                                ###print("type of date",type(today))
                        column['start_date']= today
                        column['end_date']= ''
                        column['column_deleted'] = False
                    elif missing_data and missing_data == 'drop':
                        column['handle_missing_data']= 'drop'
                        l = [c]
                        fillna_obj.drop_row(l)
                        ###print("nan filled df ",result_df)
                        today = str(datetime.now().date())
                        ###print("type of date",type(today))
                        column['start_date']= today
                        column['end_date']= ''
                        column['column_deleted'] = False
                    elif missing_data and missing_data == 'delete_column':
                        column['handle_missing_data']= missing_data
                        today = str(datetime.now().date())
                        ###print("type of date",type(today))
                        column['start_date']= today
                        column['end_date']= today
                        column['column_deleted'] = True

                        co = c.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('.', '_').replace(',','_').replace('/','_').replace(':','')
                        delete_column_list.append(co)
                        ##print("the columns are ",delete_column_list)
                    elif missing_data_input:
                        column['handle_missing_data']= missing_data_input
                        today = str(datetime.now().date())
                        ###print("type of date",type(today))
                        column['start_date']= today
                        column['end_date']= ''
                        column['column_deleted'] = False
                        custom_column_list[c]=missing_data_input

                    c_name = c.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('.', '_').replace(',','_').replace('/','_').replace(':','')
                    meta_data_obj[c_name]=column
                if len(custom_column_list)>0:
                    result_df = result_df.fillna(custom_column_list)
                ##print("the result after nan fill",result_df,delete_column_list)

                if len(delete_column_list)>0:

                    ##print("the value ",delete_column_list)
                    column_delete_obj = DeleteColumn(result_df)
                    result_df = column_delete_obj.delete_column(delete_column_list)
                    ##print("columns ",result_df.columns.tolist())

                #     d= {}
                #     if result_df.dtypes[c] == np.int64:
                #         ##print("its int type",c)
                #         d['dtype'] = 'int'
                #         d['handle_missing_data'] = 0
                #         d['start_date']= str(today)
                #         d['end_date']= ''
                #         d['column_deleted'] = False
                #         result_df[c].fillna(0, inplace=True)
                #         ##print("after nan fill",c,result_df,c)


                #     elif result_df.dtypes[c] == np.flm oat64:
                #         ##print("its float type",c)
                #         d['dtype'] = 'float'
                #         d['handle_missing_data'] =0
                #         d['start_date']= str(today)
                #         d['end_date']= ''
                #         d['column_deleted'] = False
                #         result_df[c].fillna(0, inplace=True)
                #         ##print("after nan fill",c,result_df)
                #     elif result_df.dtypes[c] == np.object:
                #         ##print("its object type",c)
                #         d['dtype'] = 'object'
                #         d['handle_missing_data'] = 'None'
                #         d['start_date']= str(today)
                #         d['end_date']= ''
                #         d['column_deleted'] = False
                #         result_df[c].fillna("None", inplace=True)
                #         ##print("result df",c,result_df)
                #     meta_data_obj[c]=d
                result_columns = result_df.columns.tolist()
                c = {'columns':result_columns}
                if metadata.date_column_name:
                    result_df[metadata.date_column_name] = result_df[metadata.date_column_name].astype(str)
                res_json=result_df.to_json(orient='index')
                rows = result_df.shape[0]
                columns = result_df.shape[1]
                df_head=result_df.head(5)
                df_tail = result_df.tail(5)
                df_head_json = df_head.to_json(orient='index')
                df_tail_json  = df_tail.to_json(orient='index')
                project_json = ProjectJsonStorage.objects.filter(project=project).update(js=res_json,columns=c)
                project_json = ProjectJsonStorage.objects.filter(project=project).order_by('id')[0]
                c_list = {'columns':result_df_columns}
                ##print("the, metada obj ",meta_data_obj)
                update = ProjectMetaData.objects.filter(project=project).update(meta_data=meta_data_obj,columns=c_list)
                project_json_metadata = ProjectJsonStorageMetadata.objects.filter(project_json=project_json).update(rows=rows,columns=columns,head_json=df_head_json,tail_json=df_tail_json)
                pk = str(project.pk)
                data = {'pk':pk}

                return JsonResponse(data, safe=False)

        else:
            data={'error':"Pleaase choese the files"}
            return data(data,safe=True)


class AddOnFileMultipleFilesView(GroupRequiredMixin,LoginRequiredMixin,View):
    def dispatch(self, request, *args, **kwargs):
        pk = kwargs['pk']
        project=Project.objects.get(pk=pk)
        pk= str(project.pk)
        self.login_url = '/customer/login/'
        self.redirect_field_name = 'redirect_to'
        self.template_name='dashboard/index.html'
        admin_name = pk+"_Admin"
        ##print(type(admin_name), admin_name)
        admin_encode_name = admin_name.encode()
        admin_unicode_name = admin_encode_name.decode('utf-8')
        write_name = pk+"_Write"
        ##print(type(write_name), write_name)
        write_encode_name = write_name.encode()
        write_unicode_name = write_encode_name.decode('utf-8')
        read_name = pk+"_Read"
        ##print(type(write_name), write_name)
        read_encode_name = read_name.encode()
        read_unicode_name = read_encode_name.decode('utf-8')
        delete_name = pk+"_Delete"
        delete_encode_name = delete_name.encode()
        delete_unicode_name = delete_encode_name.decode('utf-8')
        l = [delete_unicode_name,admin_unicode_name,write_unicode_name]
        self.group_required= l
        ##print("the self of dispatcher",self.group_required)
        return super(AddOnFileMultipleFilesView, self).dispatch(request, *args, **kwargs)

    def get(self,request,pk):
        template_name = 'dashboard/addonfile.html'
        project = Project.objects.get(pk=pk)
        project_relations = ProjectFileRelationship.objects.filter(project=project)
        project_schema    = ProjectSchema.objects.get(project=project)
        file_count=len(project_schema.schema)


        project_meta_data = ProjectMetaData.objects.get(project=project)
        context = {'file_count':file_count,'project':project,'project_relations':project_relations,'project_schema':project_schema,'project_meta_data':project_meta_data }
        return render(request,template_name,context)

    def post(self,request,pk):
        files = request.FILES.getlist('files')
        project = Project.objects.get(pk=pk)
        meta_data = ProjectMetaData.objects.get(project=project)
        project_schema = ProjectSchema.objects.get(project=project)

        if len(files)>0:
            df_obj = SchmaCheck(files)
            data = df_obj.schema_check(files,project,project_schema,meta_data)
            if "error" in data.keys():
                pass
            else:
                all_dfs = data['all_df']
                all_df = []
                schema_dict = data['schema_dict']
                update = ProjectSchema.objects.filter(project=project).update(schema=schema_dict)

                for key, val in all_dfs.items():
                    all_df.append(val)
                if len(all_dfs)>1:
                    column_conbine_obj = ColumnCombine()
                    relation_all_columns = column_conbine_obj.relation_dict_combine_add_on(all_dfs)


                ##print("all df",all_df)
                if len(all_df)>1:

                    count = len(all_df)
                    for i in range(count-1):
                        df_1 = all_df[0]
                        # ##print("the df_1",df_1)

                        df_2 = all_df[1]
                        # ##print("the df_2",df_2)
                        df_1.columns = df_1.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '').str.replace('.', '_').str.replace(',','_').str.replace('/','_').str.replace(':','')
                        column_list_1 = df_1.columns.to_list()
                        df_2.columns = df_2.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '').str.replace('.', '_').str.replace(',','_').str.replace('/','_').str.replace(':','')
                        column_list_2 = df_2.columns.tolist()
                        common_columns = intersection(column_list_1,column_list_2)
                        if len(common_columns)>=1:
                            # vl.fullbari("AddProjectView::post", "all the common columns",common_columns)
                            df =reduce(lambda left,right: pd.merge(left,right,on=common_columns, how='outer'), [df_1,df_2])
                        else:
                            df =reduce(lambda left,right: pd.merge(left,right, left_index=True, right_index=True, how='outer'), [df_1,df_2])
                            # ##print(" each ititration of for ",result_df)
                        all_df.pop(0)
                        all_df.pop(0)
                        all_df.insert(0,df)
                        # ##print("all_df after merge",all_df)
                elif len(all_df) == 1:
                    df = all_df[0]
                    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '').str.replace('.', '_').str.replace(',','_').str.replace('/','_').str.replace(':','')

                new_df_columns = df.columns.tolist()
                project_json = ProjectJsonStorage.objects.filter(project=project).order_by('id')[0]
                json_string = json.loads(project_json.js)
                json_df = pd.DataFrame(json_string)
                transposed_df = json_df.transpose()
                rows = transposed_df.shape[0]
                metadata = ProjectMetaData. objects.get(project=project)
                columns = metadata.columns['columns']


                transposed_df_columns = transposed_df.columns.tolist()

                new_columns = [x  for x in new_df_columns if x not in columns ]
                ##print("new columns are",new_columns)
                column_list = [x for x in transposed_df_columns if x in new_df_columns]
                # separate the mother df columns df into y_df

                # truncate the y_df based on the mother df rows
                for key, value in metadata.meta_data.items():
                    if key in transposed_df_columns:
                        ##print("key",key)
                        if value['dtype'] == 'int':
                            transposed_df[key] =pd.to_numeric(transposed_df[key])
                            if key in new_df_columns:
                                df[key] = pd.to_numeric(df[key])
                        elif value['dtype'] == 'float':
                            ##print("final key",key,transposed_df[key],transposed_df[key].dtypes)
                            transposed_df[key] = pd.to_numeric(transposed_df[key])
                            if key in new_df_columns:
                                df[key] = pd.to_numeric(df[key])
                        elif value['dtype'] == 'object':
                            transposed_df[key] = transposed_df[key].astype(str)
                            if key in new_df_columns:
                                df[key] = df[key].astype(str)
                        elif value['dtype'] == 'bool':
                            transposed_df[key] = transposed_df[key].astype(bool)
                            if key in new_df_columns:
                                df[key] = df[key].astype(bool)
                        elif value['dtype'] == 'DateTime':
                            transposed_df[key] =pd.to_datetime(transposed_df[key])
                            ##print("the data key",key)
                            if key in new_df_columns:
                                df[key] = pd.to_datetime(df[key])




                # merge the mother df with new rows ofss data
                if len(column_list)>0:
                    result_df = reduce(lambda left,right: pd.merge(left,right,on=column_list, how='outer'), [transposed_df,df])
                else:
                    try:
                        result_df = reduce(lambda left,right: pd.merge(left,right,left_on= transposed_df_columns[0],right_on=new_df_columns[0],how='outer'), [transposed_df,df])
                    except:
                        result_df = reduce(lambda left,right: pd.merge(left,right,left_index=True,right_index=True,how='outer'), [transposed_df,df])
                ##print("the df is ",result_df)
                result_df_rows = result_df.shape[0]
                df_rows = df.shape[0]

                if len(files)>1:
                    try:
                        error = relation_all_columns['Error']
                        data = {'error_msg':relation_all_columns['Error']}
                        ##print("the data ".data)
                        return JsonResponse(data,safe=False)
                    except:
                        data = {'relation_all_columns':relation_all_columns}
                        ##print("the data ",data)

                        return JsonResponse(data,safe=True)



                #if there are  new columns
                # if len(new_columns)>0:
                #     result_df_rows = result_df.shape[0]
                #     df_rows = df.shape[0]
                #     ##print("the aded df, and result_df rows",df_rows,result_df_rows)

                #     if result_df_rows == clas:
                #         for column in new_columns:
                #             ##print("column is",column)
                #             result_df[column] = df[column]
                #             ##print("the result df is ",result_df)
                # else:
                #     pass
                result_df.columns = result_df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '').str.replace('.', '_').str.replace(',','_').str.replace('/','_').str.replace(':','').str.replace(':','')
                ##print("the final data frame",result_df)
                result_df_columns = result_df.columns.tolist()
                fillna_obj = FillNan(result_df)
                delete_column_list = []
                custom_column_list = {}
                today = datetime.now()
                metadata = ProjectMetaData. objects.get(project=project)
                meta_data_obj = metadata.meta_data
                ##print("the columns are ",result_df.columns.tolist())
                result_df.drop_duplicates(subset = transposed_df_columns, inplace = True)



                fillna_obj = FillNan(result_df)
                for key, value in metadata.meta_data.items():

                    if key in result_df_columns:
                        ##print("key present in metadata ",key)
                        if value['handle_missing_data'] == 0:
                            fillna_obj.fillnan_with_0(key)
                        elif value['handle_missing_data'] == 'None':
                            fillna_obj.fillnan_with_None_value(key)
                        elif value['handle_missing_data'] == 'previous':
                            fillna_obj.fillnan_with_previous_value(key)
                        elif value['handle_missing_data'] == 'drop':
                            l = [key]
                            result_df = fillna_obj.drop_row(l)
                        elif value['handle_missing_data'] == 'delete_column':
                            co = key.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('.', '_').replace(',','_').replace('/','_').replace(':','')
                            delete_column_list.append(co)
                        else:
                            try:

                                custom_column_list[key]=int(value['handle_missing_data'])
                            except:
                                custom_column_list[key]=value['handle_missing_data']
                        # if value['dtype'] == dtype:
                        #     if value['handle_missing_data']== 'drop':
                        #         l = [key]
                        #         result_df[l].dropna(subset=l,inplace=True)
                        #         # result_df = fillna_obj.drop_row(l)
                        #     elif value['handle_missing_data'] == 0:
                        #         result_df[key].fillna(0, inplace=True)
                        #         # result_df = fillna_obj.fillnan_with_0(key)
                        #         ##print("after filling nan",key,result_df)
                        #     elif value['handle_missing_data'] == 'None':

                        #         # result_df = fillna_obj.fillnan_with_None_value(key)
                        #         result_df[key].fillna('None', inplace=True)
                        #         ##print("after filling nan",key,result_df)

                        #     elif value['handle_missing_data'] == 'previous':
                        #         result_df[key].fillna(method='ffill', inplace=True)
                        #         # result_df = fillna_obj.fillnan_with_previous_value(key)
                        #         ##print("after filling nan",key,result_df)



                        #     elif value['handle_missing_data'] == 'delete_column':
                        #         delete_column_list.append(key)
                        #     else:
                        #         try:

                        #             custom_column_list[key]=int(value['handle_missing_data'])
                        #         except:
                        #             custom_column_list[key]=value['handle_missing_data']
                        # else:
                        #     if value['handle_missing_data']== 'drop':
                        #         l = [key]
                        #         result_df[l].dropna(subset=l,inplace=True)
                        #         # result_df = fillna_obj.drop_row(l)
                        #     elif value['handle_missing_data'] == 0:
                        #         result_df[key].fillna(0,inplace=True)
                        #         # result_df = fillna_obj.fillnan_with_0(key)
                        #         ##print("after filling nan",key,result_df)
                        #     elif value['handle_missing_data'] == 'None':

                        #         # result_df = fillna_obj.fillnan_with_None_value(key)
                        #         result_df[key].fillna('None', inplace=True)
                        #         ##print("after filling nan",key,result_df)

                        #     elif value['handle_missing_data'] == 'previous':
                        #         result_df[key].fillna(method='ffill', inplace=True)
                        #         # result_df = fillna_obj.fillnan_with_previous_value(key)
                        #         ##print("after filling nan",key,result_df)



                        #     elif value['handle_missing_data'] == 'delete_column':
                        #         delete_column_list.append(key)
                        #     else:
                        #         try:

                        #             custom_column_list[key]=int(value['handle_missing_data'])
                        #         except:
                        #             custom_column_list[key]=value['handle_missing_data']
                ##print("the original df after nan filling is",result_df)
                if len(custom_column_list)>0:
                    ##print("the before nan fill ",len(result_df) - result_df.count())

                    result_df.fillna(value=custom_column_list,inplace=True)
                    ##print("the result after nan fill",result_df,custom_column_list)
                    ##print("after nan fill ",len(result_df) - result_df.count())

                if len(delete_column_list)>0:

                    ##print("the value ",delete_column_list)
                    column_delete_obj = DeleteColumn(result_df)
                    result_df = column_delete_obj.delete_column(delete_column_list)
                    ##print("columns ",result_df.columns.tolist())

                meta_data_obj = metadata.meta_data
                today = str(datetime.now())
                delete_column_list = []
                custom_column_list = {}
                for c in new_columns:
                    column = {}
                    ###print("the dataframe",c)
                    if df.dtypes[c] == np.int64:
                        column['dtype'] = 'int'
                    elif df.dtypes[c] == np.float64:
                        column['dtype'] = 'float'
                    elif df.dtypes[c] == np.object:
                        column['dtype'] = 'object'
                    elif df.dtypes[c] == np.bool:
                        column['dtype']= 'bool'
                    elif np.issubdtype(df[c].dtype, np.datetime64):
                        column['dtype'] = "DateTime"
                        df[c] = df[c].astype('str')

                    missing_data = None
                    missing_data_input=None
                    try:

                        cu =  c+'_select'
                        missing_data = request.POST[cu]
                    except:
                        pass
                    try:
                        cu =  c+'_input'
                        missing_data_input = request.POST[cu]
                    except:
                        pass
                    if missing_data and missing_data == 'zero':
                        column['handle_missing_data']= 0
                        today = str(datetime.now().date())
                        ###print("type of date",type(today))
                        column['start_date']= today
                        column['end_date']= ''
                        fillna_obj.fillnan_with_0(c)
                        ###print("nan filled df 0  ",c)
                    elif missing_data and missing_data == 'None':
                        column['handle_missing_data']= 'None'
                        fillna_obj.fillnan_with_None_value(c)
                        ###print("nan filled df None  ",c)
                        today = str(datetime.now().date())
                        ###print("type of date",type(today))
                        column['start_date']= today
                        column['end_date']= ''
                        column['column_deleted'] = False
                    elif missing_data and missing_data == 'previous':
                        column['handle_missing_data']= 'previous'
                        result_df = fillna_obj.fillnan_with_previous_value(c)
                        ###print("nan filled df ",result_df)
                        today = str(datetime.now().date())
                                ###print("type of date",type(today))
                        column['start_date']= today
                        column['end_date']= ''
                        column['column_deleted'] = False
                    elif missing_data and missing_data == 'drop':
                        column['handle_missing_data']= 'drop'
                        l = [c]
                        fillna_obj.drop_row(l)
                        ###print("nan filled df ",result_df)
                        today = str(datetime.now().date())
                        ###print("type of date",type(today))
                        column['start_date']= today
                        column['end_date']= ''
                        column['column_deleted'] = False
                    elif missing_data and missing_data == 'delete_column':
                        column['handle_missing_data']= missing_data
                        today = str(datetime.now().date())
                        ###print("type of date",type(today))
                        column['start_date']= today
                        column['end_date']= today
                        column['column_deleted'] = True

                        co = c.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('.', '_').replace(',','_').replace('/','_').replace(':','')
                        delete_column_list.append(co)
                        ##print("the columns are ",delete_column_list)
                    elif missing_data_input:
                        column['handle_missing_data']= missing_data_input
                        today = str(datetime.now().date())
                        ###print("type of date",type(today))
                        column['start_date']= today
                        column['end_date']= ''
                        column['column_deleted'] = False
                        custom_column_list[c]=missing_data_input

                    c_name = c.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('.', '_').replace(',','_').replace('/','_').replace(':','')
                    meta_data_obj[c_name]=column
                if len(custom_column_list)>0:
                    result_df = result_df.fillna(custom_column_list)
                ##print("the result after nan fill",result_df,delete_column_list)

                if len(delete_column_list)>0:

                    ##print("the value ",delete_column_list)
                    column_delete_obj = DeleteColumn(result_df)
                    result_df = column_delete_obj.delete_column(delete_column_list)
                    ##print("columns ",result_df.columns.tolist())

                #     d= {}
                #     if result_df.dtypes[c] == np.int64:
                #         ##print("its int type",c)
                #         d['dtype'] = 'int'
                #         d['handle_missing_data'] = 0
                #         d['start_date']= str(today)
                #         d['end_date']= ''
                #         d['column_deleted'] = False
                #         result_df[c].fillna(0, inplace=True)
                #         ##print("after nan fill",c,result_df,c)


                #     elif result_df.dtypes[c] == np.flm oat64:
                #         ##print("its float type",c)
                #         d['dtype'] = 'float'
                #         d['handle_missing_data'] =0
                #         d['start_date']= str(today)
                #         d['end_date']= ''
                #         d['column_deleted'] = False
                #         result_df[c].fillna(0, inplace=True)
                #         ##print("after nan fill",c,result_df)
                #     elif result_df.dtypes[c] == np.object:
                #         ##print("its object type",c)
                #         d['dtype'] = 'object'
                #         d['handle_missing_data'] = 'None'
                #         d['start_date']= str(today)
                #         d['end_date']= ''
                #         d['column_deleted'] = False
                #         result_df[c].fillna("None", inplace=True)
                #         ##print("result df",c,result_df)
                #     meta_data_obj[c]=d
                result_columns = result_df.columns.tolist()
                c = {'columns':result_columns}
                if metadata.date_column_name:
                    result_df[metadata.date_column_name] = result_df[metadata.date_column_name].astype(str)
                res_json=result_df.to_json(orient='index')
                rows = result_df.shape[0]
                columns = result_df.shape[1]
                df_head=result_df.head(5)
                df_tail = result_df.tail(5)
                df_head_json = df_head.to_json(orient='index')
                df_tail_json  = df_tail.to_json(orient='index')
                project_json = ProjectJsonStorage.objects.filter(project=project).update(js=res_json,columns=c)
                project_json = ProjectJsonStorage.objects.filter(project=project).order_by('id')[0]
                c_list = {'columns':result_df_columns}
                ##print("the ")
                update = ProjectMetaData.objects.filter(project=project).update(meta_data=meta_data_obj,columns=c_list)
                project_json_metadata = ProjectJsonStorageMetadata.objects.filter(project_json=project_json).update(rows=rows,columns=columns,head_json=df_head_json,tail_json=df_tail_json)
                pk = str(project.pk)
                data = {'pk':pk}

                return JsonResponse(data, safe=False)

        else:
            data={'error':"Pleaase choese the files"}
            return data(data,safe=True)


class AddOnFileFinalView(GroupRequiredMixin,LoginRequiredMixin,View):
    def dispatch(self, request, *args, **kwargs):
        pk = kwargs['pk']
        project=Project.objects.get(pk=pk)
        pk= str(project.pk)
        self.login_url = '/customer/login/'
        self.redirect_field_name = 'redirect_to'
        self.template_name='dashboard/index.html'
        admin_name = pk+"_Admin"
        ##print(type(admin_name), admin_name)
        admin_encode_name = admin_name.encode()
        admin_unicode_name = admin_encode_name.decode('utf-8')
        write_name = pk+"_Write"
        ##print(type(write_name), write_name)
        write_encode_name = write_name.encode()
        write_unicode_name = write_encode_name.decode('utf-8')
        read_name = pk+"_Read"
        ##print(type(write_name), write_name)
        read_encode_name = read_name.encode()
        read_unicode_name = read_encode_name.decode('utf-8')
        delete_name = pk+"_Delete"
        delete_encode_name = delete_name.encode()
        delete_unicode_name = delete_encode_name.decode('utf-8')
        l = [delete_unicode_name,admin_unicode_name,write_unicode_name]
        self.group_required= l
        ##print("the self of dispatcher",self.group_required)
        return super(AddOnFileFinalView, self).dispatch(request, *args, **kwargs)

    def get(self,request,pk):
        template_name = 'dashboard/addonfile.html'
        project = Project.objects.get(pk=pk)
        project_relations = ProjectFileRelationship.objects.filter(project=project)
        project_schema    = ProjectSchema.objects.get(project=project)
        file_count=len(project_schema.schema)


        project_meta_data = ProjectMetaData.objects.get(project=project)
        context = {'file_count':file_count,'project':project,'project_relations':project_relations,'project_schema':project_schema,'project_meta_data':project_meta_data }
        return render(request,template_name,context)

    def post(self,request,pk):
        files = request.FILES.getlist('files')
        project = Project.objects.get(pk=pk)
        meta_data = ProjectMetaData.objects.get(project=project)
        project_schema = ProjectSchema.objects.get(project=project)

        if len(files)>0:
            df_obj = SchmaCheck(files)
            data = df_obj.schema_check(files,project,project_schema,meta_data)
            if "error" in data.keys():
                pass
            else:
                all_dfs = data['all_df']
                all_df = []
                schema_dict = data['schema_dict']
                update = ProjectSchema.objects.filter(project=project).update(schema=schema_dict)

                for key, val in all_dfs.items():
                    all_df.append(val)



                ##print("all df",all_df)
                if len(all_df)>1:

                    count = len(all_df)
                    for i in range(count-1):
                        df_1 = all_df[0]
                        # ##print("the df_1",df_1)

                        df_2 = all_df[1]
                        # ##print("the df_2",df_2)
                        df_1.columns = df_1.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '').str.replace('.', '_').str.replace(',','_').str.replace('/','_').str.replace(':','')
                        column_list_1 = df_1.columns.to_list()
                        df_2.columns = df_2.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '').str.replace('.', '_').str.replace(',','_').str.replace('/','_').str.replace(':','')
                        column_list_2 = df_2.columns.tolist()
                        common_columns = intersection(column_list_1,column_list_2)
                        if len(common_columns)>=1:
                            # vl.fullbari("AddProjectView::post", "all the common columns",common_columns)
                            df =reduce(lambda left,right: pd.merge(left,right,on=common_columns, how='outer'), [df_1,df_2])
                        else:
                            df =reduce(lambda left,right: pd.merge(left,right, left_index=True, right_index=True, how='outer'), [df_1,df_2])
                            # ##print(" each ititration of for ",result_df)
                        all_df.pop(0)
                        all_df.pop(0)
                        all_df.insert(0,df)
                        # ##print("all_df after merge",all_df)
                elif len(all_df) == 1:
                    df = all_df[0]
                    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '').str.replace('.', '_').str.replace(',','_').str.replace('/','_').str.replace(':','')

                new_df_columns = df.columns.tolist()
                project_json = ProjectJsonStorage.objects.filter(project=project).order_by('id')[0]
                json_string = json.loads(project_json.js)
                json_df = pd.DataFrame(json_string)
                transposed_df = json_df.transpose()
                rows = transposed_df.shape[0]
                metadata = ProjectMetaData. objects.get(project=project)
                columns = metadata.columns['columns']


                transposed_df_columns = transposed_df.columns.tolist()

                new_columns = [x  for x in new_df_columns if x not in columns ]
                ##print("new columns are",new_columns)
                column_list = [x for x in transposed_df_columns if x in new_df_columns]
                # separate the mother df columns df into y_df

                # truncate the y_df based on the mother df rows
                for key, value in metadata.meta_data.items():
                    if key in transposed_df_columns:
                        ##print("key",key)
                        if value['dtype'] == 'int':
                            transposed_df[key] =pd.to_numeric(transposed_df[key])
                            if key in new_df_columns:
                                df[key] = pd.to_numeric(df[key])
                        elif value['dtype'] == 'float':
                            ##print("final key",key,transposed_df[key],transposed_df[key].dtypes)
                            transposed_df[key] = pd.to_numeric(transposed_df[key])
                            if key in new_df_columns:
                                df[key] = pd.to_numeric(df[key])
                        elif value['dtype'] == 'object':
                            transposed_df[key] = transposed_df[key].astype(str)
                            if key in new_df_columns:
                                df[key] = df[key].astype(str)
                        elif value['dtype'] == 'bool':
                            transposed_df[key] = transposed_df[key].astype(bool)
                            if key in new_df_columns:
                                df[key] = df[key].astype(bool)
                        elif value['dtype'] == 'DateTime':
                            transposed_df[key] =pd.to_datetime(transposed_df[key])
                            ##print("the data key",key)
                            if key in new_df_columns:
                                df[key] = pd.to_datetime(df[key])




                # merge the mother df with new rows ofss data
                if len(column_list)>0:
                    result_df = reduce(lambda left,right: pd.merge(left,right,on=column_list, how='outer'), [transposed_df,df])
                else:
                    try:
                        result_df = reduce(lambda left,right: pd.merge(left,right,left_on= transposed_df_columns[0],right_on=new_df_columns[0],how='outer'), [transposed_df,df])
                    except:
                        result_df = reduce(lambda left,right: pd.merge(left,right,left_index=True,right_index=True,how='outer'), [transposed_df,df])
                ##print("the df is ",result_df)
                result_df_rows = result_df.shape[0]
                df_rows = df.shape[0]




                #if there are  new columns
                # if len(new_columns)>0:
                #     result_df_rows = result_df.shape[0]
                #     df_rows = df.shape[0]
                #     ##print("the aded df, and result_df rows",df_rows,result_df_rows)

                #     if result_df_rows == df_rows:
                #         for column in new_columns:
                #             ##print("column is",column)
                #             result_df[column] = df[column]
                #             ##print("the result df is ",result_df)
                # else:
                #     pass
                result_df.columns = result_df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '').str.replace('.', '_').str.replace(',','_').str.replace('/','_').str.replace(':','').str.replace(':','')
                ##print("the final data frame",result_df)
                result_df_columns = result_df.columns.tolist()
                fillna_obj = FillNan(result_df)
                delete_column_list = []
                custom_column_list = {}
                today = datetime.now()
                metadata = ProjectMetaData. objects.get(project=project)
                meta_data_obj = metadata.meta_data
                ##print("the columns are ",result_df.columns.tolist())

                result_df.drop_duplicates(subset = transposed_df_columns, inplace = True)



                fillna_obj = FillNan(result_df)
                for key, value in metadata.meta_data.items():

                    if key in result_df_columns:
                        ##print("key present in metadata ",key)
                        if value['handle_missing_data'] == 0:
                            fillna_obj.fillnan_with_0(key)
                        elif value['handle_missing_data'] == 'None':
                            fillna_obj.fillnan_with_None_value(key)
                        elif value['handle_missing_data'] == 'previous':
                            fillna_obj.fillnan_with_previous_value(key)
                        elif value['handle_missing_data'] == 'drop':
                            l = [key]
                            result_df = fillna_obj.drop_row(l)
                        elif value['handle_missing_data'] == 'delete_column':
                            co = key.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('.', '_').replace(',','_').replace('/','_').replace(':','')
                            delete_column_list.append(co)
                        else:
                            try:

                                custom_column_list[key]=int(value['handle_missing_data'])
                            except:
                                custom_column_list[key]=value['handle_missing_data']
                        # if value['dtype'] == dtype:
                        #     if value['handle_missing_data']== 'drop':
                        #         l = [key]
                        #         result_df[l].dropna(subset=l,inplace=True)
                        #         # result_df = fillna_obj.drop_row(l)
                        #     elif value['handle_missing_data'] == 0:
                        #         result_df[key].fillna(0, inplace=True)
                        #         # result_df = fillna_obj.fillnan_with_0(key)
                        #         ##print("after filling nan",key,result_df)
                        #     elif value['handle_missing_data'] == 'None':

                        #         # result_df = fillna_obj.fillnan_with_None_value(key)
                        #         result_df[key].fillna('None', inplace=True)
                        #         ##print("after filling nan",key,result_df)

                        #     elif value['handle_missing_data'] == 'previous':
                        #         result_df[key].fillna(method='ffill', inplace=True)
                        #         # result_df = fillna_obj.fillnan_with_previous_value(key)
                        #         ##print("after filling nan",key,result_df)



                        #     elif value['handle_missing_data'] == 'delete_column':
                        #         delete_column_list.append(key)
                        #     else:
                        #         try:

                        #             custom_column_list[key]=int(value['handle_missing_data'])
                        #         except:
                        #             custom_column_list[key]=value['handle_missing_data']
                        # else:
                        #     if value['handle_missing_data']== 'drop':
                        #         l = [key]
                        #         result_df[l].dropna(subset=l,inplace=True)
                        #         # result_df = fillna_obj.drop_row(l)
                        #     elif value['handle_missing_data'] == 0:
                        #         result_df[key].fillna(0,inplace=True)
                        #         # result_df = fillna_obj.fillnan_with_0(key)
                        #         ##print("after filling nan",key,result_df)
                        #     elif value['handle_missing_data'] == 'None':

                        #         # result_df = fillna_obj.fillnan_with_None_value(key)
                        #         result_df[key].fillna('None', inplace=True)
                        #         ##print("after filling nan",key,result_df)

                        #     elif value['handle_missing_data'] == 'previous':
                        #         result_df[key].fillna(method='ffill', inplace=True)
                        #         # result_df = fillna_obj.fillnan_with_previous_value(key)
                        #         ##print("after filling nan",key,result_df)



                        #     elif value['handle_missing_data'] == 'delete_column':
                        #         delete_column_list.append(key)
                        #     else:
                        #         try:

                        #             custom_column_list[key]=int(value['handle_missing_data'])
                        #         except:
                        #             custom_column_list[key]=value['handle_missing_data']
                ##print("the original df after nan filling is",custom_column_list,delete_column_list)
                if len(custom_column_list)>0:
                    ##print("the before nan fill ",len(result_df) - result_df.count())

                    result_df.fillna(value=custom_column_list,inplace=True)
                    ##print("the result after nan fill",result_df,custom_column_list)
                    ##print("after nan fill ",len(result_df) - result_df.count())

                if len(delete_column_list)>0:

                    ##print("the value ",delete_column_list)
                    column_delete_obj = DeleteColumn(result_df)
                    result_df = column_delete_obj.delete_column(delete_column_list)
                    ##print("columns ",result_df.columns.tolist())

                meta_data_obj = metadata.meta_data
                today = str(datetime.now())
                delete_column_list = []
                custom_column_list = {}
                for c in new_columns:
                    column = {}
                    ###print("the dataframe",c)
                    if df.dtypes[c] == np.int64:
                        column['dtype'] = 'int'
                    elif df.dtypes[c] == np.float64:
                        column['dtype'] = 'float'
                    elif df.dtypes[c] == np.object:
                        column['dtype'] = 'object'
                    elif df.dtypes[c] == np.bool:
                        column['dtype']= 'bool'
                    elif np.issubdtype(df[c].dtype, np.datetime64):
                        column['dtype'] = "DateTime"
                        df[c] = df[c].astype('str')

                    missing_data = None
                    missing_data_input=None
                    try:

                        cu =  c+'_select'
                        missing_data = request.POST[cu]
                    except:
                        pass
                    try:
                        cu =  c+'_input'
                        missing_data_input = request.POST[cu]
                    except:
                        pass
                    ##print("the missing_data,column",c,missing_data,missing_data_input)
                    if missing_data and missing_data == 'zero':
                        column['handle_missing_data']= 0
                        today = str(datetime.now().date())
                        ###print("type of date",type(today))
                        column['start_date']= today
                        column['end_date']= ''
                        fillna_obj.fillnan_with_0(c)
                        ###print("nan filled df 0  ",c)
                    elif missing_data and missing_data == 'None':
                        column['handle_missing_data']= 'None'
                        fillna_obj.fillnan_with_None_value(c)
                        ###print("nan filled df None  ",c)
                        today = str(datetime.now().date())
                        ###print("type of date",type(today))
                        column['start_date']= today
                        column['end_date']= ''
                        column['column_deleted'] = False
                    elif missing_data and missing_data == 'previous':
                        column['handle_missing_data']= 'previous'
                        result_df = fillna_obj.fillnan_with_previous_value(c)
                        ###print("nan filled df ",result_df)
                        today = str(datetime.now().date())
                                ###print("type of date",type(today))
                        column['start_date']= today
                        column['end_date']= ''
                        column['column_deleted'] = False
                    elif missing_data and missing_data == 'drop':
                        column['handle_missing_data']= 'drop'
                        l = [c]
                        fillna_obj.drop_row(l)
                        ###print("nan filled df ",result_df)
                        today = str(datetime.now().date())
                        ###print("type of date",type(today))
                        column['start_date']= today
                        column['end_date']= ''
                        column['column_deleted'] = False
                    elif missing_data and missing_data == 'delete_column':
                        column['handle_missing_data']= missing_data
                        today = str(datetime.now().date())
                        ###print("type of date",type(today))
                        column['start_date']= today
                        column['end_date']= today
                        column['column_deleted'] = True

                        co = c.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('.', '_').replace(',','_').replace('/','_').replace(':','')
                        delete_column_list.append(co)
                        ##print("the columns are ",delete_column_list)
                    elif missing_data_input:
                        column['handle_missing_data']= missing_data_input
                        today = str(datetime.now().date())
                        ###print("type of date",type(today))
                        column['start_date']= today
                        column['end_date']= ''
                        column['column_deleted'] = False
                        custom_column_list[c]=missing_data_input

                    c_name = c.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('.', '_').replace(',','_').replace('/','_').replace(':','')
                    meta_data_obj[c_name]=column
                ##print("the new ", delete_column_list,custom_column_list)
                if len(custom_column_list)>0:
                    result_df = result_df.fillna(custom_column_list)
                ##print("the result after nan fill",result_df,delete_column_list)

                if len(delete_column_list)>0:

                    ##print("the value ",delete_column_list)
                    column_delete_obj = DeleteColumn(result_df)
                    result_df = column_delete_obj.delete_column(delete_column_list)
                    ##print("columns ",result_df.columns.tolist())

                #     d= {}
                #     if result_df.dtypes[c] == np.int64:
                #         ##print("its int type",c)
                #         d['dtype'] = 'int'
                #         d['handle_missing_data'] = 0
                #         d['start_date']= str(today)
                #         d['end_date']= ''
                #         d['column_deleted'] = False
                #         result_df[c].fillna(0, inplace=True)
                #         ##print("after nan fill",c,result_df,c)


                #     elif result_df.dtypes[c] == np.flm oat64:
                #         ##print("its float type",c)
                #         d['dtype'] = 'float'
                #         d['handle_missing_data'] =0
                #         d['start_date']= str(today)
                #         d['end_date']= ''
                #         d['column_deleted'] = False
                #         result_df[c].fillna(0, inplace=True)
                #         ##print("after nan fill",c,result_df)
                #     elif result_df.dtypes[c] == np.object:
                #         ##print("its object type",c)
                #         d['dtype'] = 'object'
                #         d['handle_missing_data'] = 'None'
                #         d['start_date']= str(today)
                #         d['end_date']= ''
                #         d['column_deleted'] = False
                #         result_df[c].fillna("None", inplace=True)
                #         ##print("result df",c,result_df)
                #     meta_data_obj[c]=d
                result_columns = result_df.columns.tolist()
                c = {'columns':result_columns}
                if metadata.date_column_name:
                    result_df[metadata.date_column_name] = result_df[metadata.date_column_name].astype(str)
                res_json=result_df.to_json(orient='index')
                rows = result_df.shape[0]
                columns = result_df.shape[1]
                df_head=result_df.head(5)
                df_tail = result_df.tail(5)
                df_head_json = df_head.to_json(orient='index')
                df_tail_json  = df_tail.to_json(orient='index')
                project_json = ProjectJsonStorage.objects.filter(project=project).update(js=res_json,columns=c)
                project_json = ProjectJsonStorage.objects.filter(project=project).order_by('id')[0]
                c_list = {'columns':result_df_columns}
                ##print("the metadata  ",)
                update = ProjectMetaData.objects.filter(project=project).update(meta_data=meta_data_obj,columns=c_list)
                project_json_metadata = ProjectJsonStorageMetadata.objects.filter(project_json=project_json).update(rows=rows,columns=columns,head_json=df_head_json,tail_json=df_tail_json)
                pk = str(project.pk)
                data = {'pk':pk}

                return JsonResponse(data, safe=False)

        else:
            data={'error':"Pleaase choese the files"}
            return data(data,safe=True)


class ApiDataView(View):
    def post(self,request,pk):
        project = Project.objects.get(pk=pk)
        api = request.POST.get('api',None)
        frequency = request.POST.get('frequency',None)
        basic_token = request.POST.get('token',None)
        name = request.POST.get('api_name',None)


        error = False
        if basic_token:

            headers = {'content-type': 'application/json',
                       'Authorization': basic_token}

            JSONContent = requests.get(api,

                                       headers=headers, verify=True)
        else:
            headers = {'content-type': 'application/json',
                       }

            JSONContent = requests.get(api,
                                       headers=headers, verify=True)
        if 'error' not in JSONContent:
            data_str = JSONContent.text
            data_str = JSONContent.text
            ##print("the test is",data_str)
            data_json = json.loads(data_str)
            api_data, created = CustomerAPIDetails.objects.get_or_create(name=name,project=project,api=api,token=basic_token,range=frequency,integration_choice='API')
            ##print("type", data_json)
            try:
                df = pd.json_normalize(data_json['results'])
            except:
                try:

                    df = pd.json_normalize(data_json['data'])
                except:
                    df = pd.json_normalize(data_json)


            columns = df.columns.tolist()
            # ##print("the columns are ",columns)
            data = {}
            lines = []
            index =len(df.index)
            c_str = ' '
            for column in columns:
                c_str = c_str+','+column
            column_list = c_str.replace(' ','',1)
            if index>5:
                for ind in range(0,5):
                    one= " "
                    for col in columns:
                        # ##print("the col",df[col][ind])
                        tst = df[col][ind]
                        one = one+','+str(tst)

                    lines.append(one.replace(" ", "", 1))
                    # ##print("the lines are", lines)
                line_1 =lines[0]
                line_2 = lines[1]
                line_3 = lines[2]
                line_4 = lines[3]
                line_5= lines[4]
                data = {'line_1': line_1, 'line_2': line_2, 'line_3': line_3, 'line_4': line_4, 'line_5': line_5,'column_list':column_list}

            elif (index>=4):
                for ind in range(0,4):
                    one= " "
                    for col in columns:
                        # ##print("the col",df[col][ind])
                        tst = df[col][ind]
                        one = one+','+str(tst)
                    lines.append(one.replace(" ", "", 1))
                line_1 = lines[0]
                line_2 = lines[1]
                line_3 = lines[2]
                line_4 = lines[3]
                line_5 = ''
                data = {'line_1': line_1, 'line_2': line_2, 'line_3': line_3, 'line_4': line_4, 'line_5': line_5,'column_list':column_list}
            elif (index>=3):
                for ind in range(0,3):
                    one= " "
                    for col in columns:
                        # ##print("the col",df[col][ind])
                        tst = df[col][ind]
                        one = one+','+str(tst)
                    lines.append(one.replace(" ", "", 1))
                    # ##print("the lines are", lines)
                line_1 = lines[0]
                line_2 = lines[1]
                line_3 = lines[2]
                line_4  = ''
                line_5 = ''
                data = {'line_1': line_1, 'line_2': line_2, 'line_3': line_3, 'line_4': line_4, 'line_5': line_5,'column_list':column_list}
            elif (index>=2):
                for ind in range(0,2):
                    one= " "
                    for col in columns:
                        # ##print("the col",df[col][ind])
                        tst = df[col][ind]
                        one = one+','+str(tst)
                    lines.append(one.replace(" ", "", 1))
                    # ##print("the lines are", lines)
                line_1 = lines[0]
                line_2 = lines[1]
                line_3 = ''
                line_4 = ''
                line_5 = ''
                data = {'line_1': line_1, 'line_2': line_2, 'line_3': line_3, 'line_4': line_4, 'line_5': line_5,'column_list':column_list}

            else:
                for ind in range(0,1):
                    one= " "
                    for col in columns:
                        # ##print("the col",df[col][ind])
                        tst = df[col][ind]
                        one = one+','+str(tst)
                    lines.append(one.replace(" ", "", 1))
                line_1 = lines[0]
                line_2 = ''
                line_3 = ''
                line_4 = ''
                line_5 = ''
                data ={'line_1':line_1,'line_2':line_2,'line_3':line_3,'line_4':line_4,'line_5':line_5,'column_list':column_list}
            ##print("the lines are",data)

            data={'data':data}
            return JsonResponse(data,safe=False)
        else:
            data={'error':"Unable to  get the data from given api"}
            return JsonResponse(data, safe=False)

class EndPointDataToolView(GroupRequiredMixin,LoginRequiredMixin,View):
    def dispatch(self, request, *args, **kwargs):
        pk = kwargs['pk']
        end_point = ProjectEndPoint.objects.get(pk=pk)

        project=Project.objects.get(pk=end_point.pk)
        pk= str(project.pk)
        self.login_url = '/customer/login/'
        self.redirect_field_name = 'redirect_to'
        self.template_name='dashboard/index.html'
        admin_name = pk+"_Admin"
        ##print(type(admin_name), admin_name)
        admin_encode_name = admin_name.encode()
        admin_unicode_name = admin_encode_name.decode('utf-8')
        write_name = pk+"_Write"
        ##print(type(write_name), write_name)
        write_encode_name = write_name.encode()
        write_unicode_name = write_encode_name.decode('utf-8')
        read_name = pk+"_Read"
        ##print(type(write_name), write_name)
        read_encode_name = read_name.encode()
        read_unicode_name = read_encode_name.decode('utf-8')
        delete_name = pk+"_Delete"
        delete_encode_name = delete_name.encode()
        delete_unicode_name = delete_encode_name.decode('utf-8')
        l = [delete_unicode_name,admin_unicode_name,write_unicode_name]
        self.group_required= l
        ##print("the self of dispatcher",self.group_required)
        return super(ProjectDataToolview, self).dispatch(request, *args, **kwargs)

    def post(self,request,pk):
        end_point = ProjectEndPoint.objects.get(pk=pk)
        json_string = json.loads(end_point.sub_df)
        json_df = pd.DataFrame(json_string)
        transposed_df = json_df.transpose()
        columns = transposed_df.columns.tolist()
        for column in columns:
            column_post  = request.POST[column]
            if column_post == '':
                pass


class ProjectEndPointCreateView(GroupRequiredMixin,LoginRequiredMixin,View):
    def dispatch(self, request, *args, **kwargs):
        pk = kwargs['pk']

        query= ProjectQuery.objects.get(pk=pk)
        project=Project.objects.get(pk=query.project.pk)


        pk= str(project.pk)
        self.login_url = '/customer/login/'
        self.redirect_field_name = 'redirect_to'
        self.template_name='dashboard/index.html'
        admin_name = pk+"_Admin"
        ##print(type(admin_name), admin_name)
        admin_encode_name = admin_name.encode()
        admin_unicode_name = admin_encode_name.decode('utf-8')
        write_name = pk+"_Write"
        ##print(type(write_name), write_name)
        write_encode_name = write_name.encode()
        write_unicode_name = write_encode_name.decode('utf-8')
        read_name = pk+"_Read"
        ##print(type(read_name), read_name)
        read_encode_name = read_name.encode()
        read_unicode_name = read_encode_name.decode('utf-8')
        delete_name = pk+"_Delete"
        ##print(type(delete_name), delete_name)
        delete_encode_name = delete_name.encode()
        delete_unicode_name = delete_encode_name.decode('utf-8')
        l =[delete_unicode_name,write_unicode_name,admin_unicode_name,read_unicode_name]
        self.group_required= l
        ##print("the self of dispatcher",self.group_required)

        return super(ProjectEndPointCreateView, self).dispatch(request, *args, **kwargs)
    def post(self,request,pk):
        name = request.POST['end_point_name']
        frequency = request.POST['frequency']
        query_object = request.POST.get('end_point_object',None)
        if query_object:
            ##print("the query object",query_object)
            query_object = ast.literal_eval(query_object)
        query= ProjectQuery.objects.get(pk=pk)
        customer = Customer.objects.get(user=request.user)
        end_point_count = ProjectEndPoint.objects.filter(user=request.user).count()
        if customer.type =='Individual':
            if end_point_count >5:
                pk = query.project.pk
                context= single_project_details(request,pk)
                context['msg'] = "Project has Exceeded The EndPoint Limit"
                return render(request,template_name,context)

            else:
                if query_object:
                    ep = ProjectEndPoint.objects.create(name=name,project=query.project,query=query,alignment_object=query_object,user=request.user,sub_df_frequency=frequency)
                else:

                    ep = ProjectEndPoint.objects.create(name=name,project=query.project,query=query,user=request.user,sub_df_frequency=frequency)
                if query.plot_type and query.plot.plot_type:
                    plot = Plot.objects.create(plot_type=query.plot.plot_type,x_axis=query.plot.x_axis,y_axis=query.plot.y_axis,z_axis=query.plot.z_axis,color=query.plot.color,legend=query.plot.legend,size=query.plot.size,hover_name=query.plot.hover_name,values=query.plot.values,names=query.plot.names,orientation=query.plot.orientation,facet_col=query.plot.facet_col)
                    update = ProjectEndPoint.objects.filter(pk=ep.pk).update(plot=plot)
                pk=str(ep.pk)
                return redirect('/endpoint/'+pk+'/')
        else:
            project_usage = ProjectBillingPrms.objects.get(project=query.project)
            total_end_point = project_usage.end_point +5
            end_points = ProjectEndPoint.objects.filter(project=query.project).count()

            if end_points<=total_end_point:

                if query_object:
                    ep = ProjectEndPoint.objects.create(name=name,project=query.project,query=query,alignment_object=query_object,user=request.user,sub_df_frequency=frequency)
                else:
                    ep = ProjectEndPoint.objects.create(name=name,project=query.project,query=query,user=request.user,sub_df_frequency=frequency)
                if query.plot and query.plot.plot_type:
                    plot = Plot.objects.create(plot_type=query.plot.plot_type,x_axis=query.plot.x_axis,y_axis=query.plot.y_axis,z_axis=query.plot.z_axis,color=query.plot.color,legend=query.plot.legend,size=query.plot.size,hover_name=query.plot.hover_name,values=query.plot.values,names=query.plot.names,orientation=query.plot.orientation,facet_col=query.plot.facet_col)
                    update = ProjectEndPoint.objects.filter(pk=ep.pk).update(plot=plot)
                pk=str(ep.pk)
                return redirect('/endpoint/'+pk+'/')
            else:
                pk= query.project.pk
                template_name='dashboard/single_project_details.html'
                context= single_project_details(request,pk)
                context['msg'] = "Project has Exceeded The EndPoint Limit"
                return render(request,template_name,context)
class DeleteIntegration(View):
    def post(self,request,pk):
        data_int = CustomerAPIDetails.objects.get(pk=pk)
        delete = CustomerAPIDetails.objects.filter(pk=pk).delete()
        pk= str(data_int.project.pk)
        return redirect('/single-project-details/'+pk+'/')

class ProjectEndPointDelete(View):
    def post(self,request,pk):
        ep = ProjectEndPoint.objects.get(pk=pk)
        delete = ProjectEndPoint.objects.filter(pk=pk).delete()
        pk= str(ep.project.pk)
        return redirect('/single-project-details/'+pk+'/')
class ProjectDashboardDelete(View):
    def post(self,request,pk):
        dashboard = ProjectDashboard.objects.get(pk=pk)
        delete = ProjectDashboard.objects.filter(pk=pk).delete()
        pk= str(dashboard.project.pk)
        return redirect('/single-project-details/'+pk+'/')


'''function to create ml api request'''
def endpoint_ml_api(request,pk):
    end_point = ProjectEndPoint.objects.get(pk=pk)
    if end_point.algorithm:
        ep_ml_api,create = EndpointMlApi.objects.get_or_create(end_point=end_point,user= request.user)
        context = endpointget(request,pk)
        #Backen Team mail
        body  = "Hi, \n You have received a new request for machine learning API and  the details are below \n \n Project: "+str(end_point.project)+" \n End Point: "+str(end_point)+"\n User: "+request.user.first_name+"."
        send_mail(
                'Brayn | New API Request',
                body,
                'noreply@brayn.ai',
                ['hello@brayn.ai'],
                 fail_silently=False,
                )
        return render(request,'dashboard/project_end_point.html',context)

    else:
        msg = 'There is no Brayn Associated with this EndPoint'
        context = endpointget(request,pk)
        context['msg'] = msg
        return render(request,'dashboard/project_end_point.html',context)



class ProjectSupport(View):
    def get(self,request,pk):
        print("")
        project = Project.objects.get(pk=pk)
        if User.objects.filter(username = 'administrator').exists():
            user = User.objects.get(username='administrator')
            if Customer.objects.filter(user=user).exists():

                customer = Customer.objects.get(user=user)
            else:
                customer = Customer.objects.create(user=user,email_confirmed=True,type='Company',url="https://www.brayn.ai")

            project_user = ProjectUser.objects.filter(project=project)
            exists = False
            for p_user in project_user:
                if p_user.project_user.username == 'administrator':
                    exists=True
                    print("exists")
                else:
                    pass
            if not exists:
                print("not exists")
                project_user_create = ProjectUser.objects.create(project_user=user,project=project)
                permissions=Group.objects.get(name=str(project.pk)+"_Admin")
                added_user=User.objects.get(username='administrator')
                added_user.groups.add(permissions)
                added_user.save()
            pk=str(project.pk)
            return redirect('/single-project/'+pk+'/')
        else:
            user = User.objects.create(email='hello@brayn.ai',username='administrator',password="someuser",first_name='Admin',last_name='support')
            customer = Customer.objects.create(user=user,email_confirmed=True,type='Company',url="https://www.brayn.ai")
            project_user_create = ProjectUser.objects.create(project_user=user,project=project)
            permissions=Group.objects.get(name=str(project.pk)+"_Admin")
            added_user=User.objects.get(username='hello@brayn.ai')
            added_user.groups.add(permissions)
            added_user.save()
            pk=str(project.pk)
            return redirect('/single-project/'+pk+'/')

class EndpointNewColumnCreationView(GroupRequiredMixin,LoginRequiredMixin,View):
    '''class to  add new column to exixting endpoint subdf'''
    def dispatch(self, request, *args, **kwargs):
        pk = kwargs['pk']

        endpoint= ProjectEndPoint.objects.get(pk=pk)
        project=Project.objects.get(pk=endpoint.project.pk)


        pk= str(project.pk)
        self.login_url = '/customer/login/'
        self.redirect_field_name = 'redirect_to'
        self.template_name='dashboard/index.html'
        admin_name = pk+"_Admin"
        ##print(type(admin_name), admin_name)
        admin_encode_name = admin_name.encode()
        admin_unicode_name = admin_encode_name.decode('utf-8')
        write_name = pk+"_Write"
        ##print(type(write_name), write_name)
        write_encode_name = write_name.encode()
        write_unicode_name = write_encode_name.decode('utf-8')
        read_name = pk+"_Read"
        ##print(type(read_name), read_name)
        read_encode_name = read_name.encode()
        read_unicode_name = read_encode_name.decode('utf-8')
        delete_name = pk+"_Delete"
        ##print(type(delete_name), delete_name)
        delete_encode_name = delete_name.encode()
        delete_unicode_name = delete_encode_name.decode('utf-8')
        l =[delete_unicode_name,write_unicode_name,admin_unicode_name,read_unicode_name]
        self.group_required= l
        ##print("the self of dispatcher",self.group_required)

        return super(EndpointNewColumnCreation, self).dispatch(request, *args, **kwargs)

    def get(self,request,pk):
        '''http get method'''
        end_point = ProjectEndPoint.objects.get(pk=pk)
        permission = user_permission(end_point.project,request)
        p_query=end_point.query
        if not end_point.sub_df:

            df = QueryExcecute(end_point.query)
            df_columns = df.columns.tolist()
            metadata = ProjectMetaData.objects.get(project=p_query.project)
            string_columns = df.select_dtypes(include =['object','bool'])
            number_columns = df.select_dtypes(include =['number'])
            if metadata.date_column_name and metadata.date_column_name in df_columns:
                df[metadata.date_column_name] = df[metadata.date_column_name].astype(str)
            result_json = df.to_json(orient='index')

            update = ProjectEndPoint.objects.filter(pk=end_point.pk).update(sub_df=result_json)

        else:
            ##print("loding from json data")
            json_st = json.loads(end_point.sub_df)
            # ##print("THE TYPE OF JSON FILE<",type(json_st))
            json_df = pd.DataFrame(json_st)
            df = json_df.transpose()
            df = df_dtype_casting(df,p_query.project)
            string_columns = df.select_dtypes(include =['object','bool'])
            number_columns = df.select_dtypes(include =['number'])
        df_columns = df.columns.tolist()
        customer = Customer.objects.get(user=request.user)
        context={'string_columns':string_columns,'number_columns':number_columns,'end_point':end_point,'customer':customer}
        return render(request,'dashboard/endpoint_new_column.html',context)

    def post(self,request,pk):
        '''http post method'''
        end_point = ProjectEndPoint.objects.get(pk=pk)
        formula = request.POST.get('formula',None)
        column_name = request.POST.get('column_name',None)
        p_query=end_point.query
        if formula and column_name:
            
            if not end_point.sub_df:

                df = QueryExcecute(end_point.query)
                df_columns = df.columns.tolist()
            else:
                ##print("loding from json data")
                json_st = json.loads(end_point.sub_df)
                # ##print("THE TYPE OF JSON FILE<",type(json_st))
                json_df = pd.DataFrame(json_st)
                df = json_df.transpose()
            df_columns = df.columns.to_list()
            end_point_new_column = EndPointNewColumn.objects.filter(end_point=end_point)
            column_present = False
            for ep_c in end_point_new_column:
                if ep_c.column_name == column_name:
                    column_present=True

            if column_name not in df_columns and column_present == False :
                try:
                    df[column_name] = df.apply(eval(formula),axis=1)
                except:
                    df = df_dtype_casting(df,p_query.project)
                    metadata = ProjectMetaData.objects.get(project=p_query.project)
                    string_columns = df.select_dtypes(include =['object','bool'])
                    number_columns = df.select_dtypes(include =['number'])
                    if metadata.date_column_name and metadata.date_column_name in df_columns:
                        df[metadata.date_column_name] = df[metadata.date_column_name].astype(str)
                    df_columns = df.columns.tolist()
                    customer = Customer.objects.get(user=request.user)
                    context={'formula':formula,'column_name':column_name,'string_columns':string_columns,'number_columns':number_columns,'end_point':end_point,'customer':customer,'df_columns':df_columns,'msg':"Error creating new column"}
                    return render(request,'dashboard/endpoint_new_column.html',context)

                df = df_dtype_casting(df,p_query.project)
                metadata = ProjectMetaData.objects.get(project=p_query.project)
                string_columns = df.select_dtypes(include =['object','bool'])
                number_columns = df.select_dtypes(include =['number'])
                if metadata.date_column_name and metadata.date_column_name in df_columns:
                    df[metadata.date_column_name] = df[metadata.date_column_name].astype(str)
                result_json = df.to_json(orient='index')
                update = ProjectEndPoint.objects.filter(pk=end_point.pk).update(sub_df=result_json)
                df_columns = df.columns.tolist()
                ep_c = EndPointNewColumn.objects.create(end_point=end_point,column_name=column_name,formula=formula)
                customer = Customer.objects.get(user=request.user)
                context={'string_columns':string_columns,'number_columns':number_columns,'end_point':end_point,'customer':customer,'df_columns':df_columns,'msg':"New Column Added Scuccessfully"}
                return render(request,'dashboard/endpoint_new_column.html',context)
            else:
                df = df_dtype_casting(df,p_query.project)
                metadata = ProjectMetaData.objects.get(project=p_query.project)
                string_columns = df.select_dtypes(include =['object','bool'])
                number_columns = df.select_dtypes(include =['number'])
                if metadata.date_column_name and metadata.date_column_name in df_columns:
                    df[metadata.date_column_name] = df[metadata.date_column_name].astype(str)
                df_columns = df.columns.tolist()
                customer = Customer.objects.get(user=request.user)
                context={'formula':formula,'column_name':column_name,'string_columns':string_columns,'number_columns':number_columns,'end_point':end_point,'customer':customer,'df_columns':df_columns,'msg':"Column Name Already Present"}
                return render(request,'dashboard/endpoint_new_column.html',context)
        else:
            df = df_dtype_casting(df,p_query.project)
            metadata = ProjectMetaData.objects.get(project=p_query.project)
            string_columns = df.select_dtypes(include =['object','bool'])
            number_columns = df.select_dtypes(include =['number'])
            if metadata.date_column_name and metadata.date_column_name in df_columns:
                df[metadata.date_column_name] = df[metadata.date_column_name].astype(str)
            df_columns = df.columns.tolist()
            customer = Customer.objects.get(user=request.user)
            context={'string_columns':string_columns,'number_columns':number_columns,'end_point':end_point,'customer':customer,'df_columns':df_columns,'msg':"Please Enter Column Name and Formula"}
            return render(request,'dashboard/endpoint_new_column.html',context)    



class EndPointColumnDeleteView(GroupRequiredMixin,LoginRequiredMixin,View):
    def dispatch(self, request, *args, **kwargs):
        pk = kwargs['pk']


        endpoint= ProjectEndPoint.objects.get(pk=pk)
        project=Project.objects.get(pk=endpoint.project.pk)


        pk= str(project.pk)
        self.login_url = '/customer/login/'
        self.redirect_field_name = 'redirect_to'
        self.template_name='dashboard/index.html'
        admin_name = pk+"_Admin"
        ##print(type(admin_name), admin_name)
        admin_encode_name = admin_name.encode()
        admin_unicode_name = admin_encode_name.decode('utf-8')
        write_name = pk+"_Write"
        ##print(type(write_name), write_name)
        write_encode_name = write_name.encode()
        write_unicode_name = write_encode_name.decode('utf-8')
        read_name = pk+"_Read"
        ##print(type(read_name), read_name)
        read_encode_name = read_name.encode()
        read_unicode_name = read_encode_name.decode('utf-8')
        delete_name = pk+"_Delete"
        ##print(type(delete_name), delete_name)
        delete_encode_name = delete_name.encode()
        delete_unicode_name = delete_encode_name.decode('utf-8')
        l =[delete_unicode_name,write_unicode_name,admin_unicode_name,read_unicode_name]
        self.group_required= l
        ##print("the self of dispatcher",self.group_required)

        return super(EndPointColumnDeleteView, self).dispatch(request, *args, **kwargs)

        def post(self,request,pk):
            '''http post method'''
            pass


