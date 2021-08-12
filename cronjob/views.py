from django.shortcuts import render
from django.shortcuts import render,redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import TemplateView,CreateView,View,UpdateView,ListView
from login.forms import CustomerForm,ProfileForm,UpdateForm,PasswordResetForm,SignupLinkForm,LoginForm
from coreapp.forms import ProjectForm, Fileform,FileUploadForm,ProjectUpdateForm,AddUsersForm,AcceptForm,FormFile,ProjectDashboardForm, ProjectDashboardEditForm, ProjectDashboardsForm
from login.models import Customer,Profile
from coreapp.models import ProjectType,Project,FileUpload,ProjectUser, ProjectColumn,ProjectJsonStorage,ProjectDashboard,UserNotification, \
                                            ProjectMetaData,IndustryChoices,ProjectConfiguration, ProjectQuery, DashboardQuery,Plot,ProjectEndPoint, ProjectFileRelationship, \
                                            ProjectSchema,ProjectIndex, ProjectFilename, ProjectBillingHourlyCost,ProjectBillingDayCost,ProjectBillingMonthCost, ProjectPricing, ProjectBillingPrms, \
                                            ProjectInvoice,Tax, ApiDataGet, DefaultProjectPricing,ProjectJsonStorageMetadata, EndPointNewColumn
from django.contrib.auth.models import Group
from dataintegration.models import CustomerAPIDetails
import sys
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import urllib.request
import urllib.parse
import random
import numpy as np
from django.contrib.auth import authenticate,login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
import pandas as pd
import plotly.offline as opy
import plotly.graph_objs as go
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
from pandas.io.json import json_normalize

import json
from actstream import action
from actstream.models import Action
from datetime import datetime, timedelta
import ast
from django.http import HttpResponse
from dal import autocomplete
from engine.cleaner import FileReader, FillNan,ColumnCombine,CheckPrimarykey,DeleteColumn
from utils import ReadFileLines
import requests
from django.core.files.storage import default_storage
import csv
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import psutil
import pytz
import gc
import logging
utc=pytz.UTC


def listgenerator(l):
    for i in l:
        yield i

class ProjectDashboardeEmail(View):
    '''class for generating and mailing the dashboard'''
    def get(self,request):
        dashboards = ProjectDashboard.objects.all()
        for dashboard in dashboards:
            report_frequency = dashboard.report_frequency
            #print("the report frequency and dashboard",dashboard,dashboard.report_frequency)
            
            if report_frequency == '1Minute':
                utc=pytz.UTC
                time_now = datetime.now()

                time_to_compare = utc.localize(time_now)
                #print("the time now is",time_now,time_to_compare)
                report_time = dashboard.report_time
                send_report_time = report_time+timedelta(minutes=1)
                if send_report_time <= time_to_compare:

                    hash_str = str(dashboard.pk)+"dashboard"
                    hash_code = str(hash(hash_str))
                    update = ProjectDashboard.objects.filter(pk=dashboard.pk).update(hash_code = hash_code,report_time=time_now)
                    to_mail = []
                    to_mail.append(dashboard.dashboard_admin_user.email)
                    current_site = get_current_site(request)
                    site_name = current_site.name
                    domain = current_site.domain
                    if domain.startswith('127.0.'):
                        domain = 'http://'+domain
                    else:
                        domain = 'https://'+domain
                    try:

                        email_users = dashboard.additional_email.split(',')
                        to_mail = [i for i in email_users ]
                        #print("to mail",to_mail)
                    except:
                        email_users = None
                    if email_users:
                        if dashboard.dashboard_users:

                            for u in  dashboard.dashboard_users.all():
                                to_mail.append(u.email)

                    html_message = render_to_string('dashboard/report.html', {'hash_code': hash_code,'domain':domain})
                    message = 'Please find the Link to  the shared dashboard from brayn.ai:'
                    #print("success",to_mail)
                    mail.send_mail(
                            'Shared dashboard link',
                            "The Shared Dashboard",
                        'noreply@brayn.ai',
                            to_mail,
                            html_message=html_message,
                            fail_silently=False,
                            )
                    #print("success",to_mail)
                    return HttpResponse(status="200")
            elif report_frequency == '5Minutes':
                utc=pytz.UTC
                time_now = datetime.now()

                time_to_compare = utc.localize(time_now)
                #print("the time now is",time_now,time_to_compare)
                report_time = dashboard.report_time
                send_report_time = report_time+timedelta(minutes=5)
                if send_report_time <= time_to_compare:

                    hash_str = str(dashboard.pk)+"dashboard"
                    hash_code = str(hash(hash_str))
                    update = ProjectDashboard.objects.filter(pk=dashboard.pk).update(hash_code = hash_code,report_time=time_now)
                    to_mail = []
                    to_mail.append(dashboard.dashboard_admin_user.email)
                    current_site = get_current_site(request)
                    site_name = current_site.name
                    domain = current_site.domain
                    if domain.startswith('127.0.'):
                        domain = 'http://'+domain
                    else:
                        domain = 'https://'+domain
                    try:

                        email_users = dashboard.additional_email.split(',')
                        to_mail = [i for i in email_users ]
                        #print("to mail",to_mail)
                    except:
                        email_users = None
                    if email_users:
                        if dashboard.dashboard_users:

                            for u in  dashboard.dashboard_users.all():
                                to_mail.append(u.email)

                    html_message = render_to_string('dashboard/report.html', {'hash_code': hash_code,'domain':domain})
                    message = 'Please find the Link to  the shared dashboard from brayn.ai:'
                    #print("success",to_mail)
                    mail.send_mail(
                            'Shared dashboard link',
                            "The Shared Dashboard",
                        'noreply@brayn.ai',
                            to_mail,
                            html_message=html_message,
                            fail_silently=False,
                            )
                    #print("success",to_mail)
                    return HttpResponse(status="200")
            elif report_frequency == '10Minutes':
                utc=pytz.UTC
                time_now = datetime.now()

                time_to_compare = utc.localize(time_now)
                #print("the time now is",time_now,time_to_compare)
                report_time = dashboard.report_time
                send_report_time = report_time+timedelta(minutes=10)
                if send_report_time <= time_to_compare:

                    hash_str = str(dashboard.pk)+"dashboard"
                    hash_code = str(hash(hash_str))
                    update = ProjectDashboard.objects.filter(pk=dashboard.pk).update(hash_code = hash_code,report_time=time_now)
                    to_mail = []
                    to_mail.append(dashboard.dashboard_admin_user.email)
                    current_site = get_current_site(request)
                    site_name = current_site.name
                    domain = current_site.domain
                    if domain.startswith('127.0.'):
                        domain = 'http://'+domain
                    else:
                        domain = 'https://'+domain
                    try:

                        email_users = dashboard.additional_email.split(',')
                        to_mail = [i for i in email_users ]
                        #print("to mail",to_mail)
                    except:
                        email_users = None
                    if email_users:
                        if dashboard.dashboard_users:

                            for u in  dashboard.dashboard_users.all():
                                to_mail.append(u.email)

                    html_message = render_to_string('dashboard/report.html', {'hash_code': hash_code,'domain':domain})
                    message = 'Please find the Link to  the shared dashboard from brayn.ai:'
                    #print("success",to_mail)
                    mail.send_mail(
                            'Shared dashboard link',
                            "The Shared Dashboard",
                        'noreply@brayn.ai',
                            to_mail,
                            html_message=html_message,
                            fail_silently=False,
                            )
                    #print("success",to_mail)
                    return HttpResponse(status="200")
            elif report_frequency == '15Minutes':
                utc=pytz.UTC
                time_now = datetime.now()

                time_to_compare = utc.localize(time_now)
                #print("the time now is",time_now,time_to_compare)
                report_time = dashboard.report_time
                send_report_time = report_time+timedelta(minutes=15)
                if send_report_time <= time_to_compare:

                    hash_str = str(dashboard.pk)+"dashboard"
                    hash_code = str(hash(hash_str))
                    update = ProjectDashboard.objects.filter(pk=dashboard.pk).update(hash_code = hash_code,report_time=time_now)
                    to_mail = []
                    to_mail.append(dashboard.dashboard_admin_user.email)
                    current_site = get_current_site(request)
                    site_name = current_site.name
                    domain = current_site.domain
                    if domain.startswith('127.0.'):
                        domain = 'http://'+domain
                    else:
                        domain = 'https://'+domain
                    try:

                        email_users = dashboard.additional_email.split(',')
                        to_mail = [i for i in email_users ]
                        #print("to mail",to_mail)
                    except:
                        email_users = None
                    if email_users:
                        if dashboard.dashboard_users:

                            for u in  dashboard.dashboard_users.all():
                                to_mail.append(u.email)

                    html_message = render_to_string('dashboard/report.html', {'hash_code': hash_code,'domain':domain})
                    message = 'Please find the Link to  the shared dashboard from brayn.ai:'
                    #print("success",to_mail)
                    mail.send_mail(
                            'Shared dashboard link',
                            "The Shared Dashboard",
                        'noreply@brayn.ai',
                            to_mail,
                            html_message=html_message,
                            fail_silently=False,
                            )
                    #print("success",to_mail)
                    return HttpResponse(status="200")
            elif report_frequency == '30Minutes':
                utc=pytz.UTC
                time_now = datetime.now()

                time_to_compare = utc.localize(time_now)
                #print("the time now is",time_now,time_to_compare)
                report_time = dashboard.report_time
                send_report_time = report_time+timedelta(minutes=30)
                if send_report_time <= time_to_compare:

                    hash_str = str(dashboard.pk)+"dashboard"
                    hash_code = str(hash(hash_str))
                    update = ProjectDashboard.objects.filter(pk=dashboard.pk).update(hash_code = hash_code,report_time=time_now)
                    to_mail = []
                    to_mail.append(dashboard.dashboard_admin_user.email)
                    current_site = get_current_site(request)
                    site_name = current_site.name
                    domain = current_site.domain
                    if domain.startswith('127.0.'):
                        domain = 'http://'+domain
                    else:
                        domain = 'https://'+domain
                    try:

                        email_users = dashboard.additional_email.split(',')
                        to_mail = [i for i in email_users ]
                        #print("to mail",to_mail)
                    except:
                        email_users = None
                    if email_users:
                        if dashboard.dashboard_users:

                            for u in  dashboard.dashboard_users.all():
                                to_mail.append(u.email)

                    html_message = render_to_string('dashboard/report.html', {'hash_code': hash_code,'domain':domain})
                    message = 'Please find the Link to  the shared dashboard from brayn.ai:'
                    #print("success",to_mail)
                    mail.send_mail(
                            'Shared dashboard link',
                            "The Shared Dashboard",
                        'noreply@brayn.ai',
                            to_mail,
                            html_message=html_message,
                            fail_silently=False,
                            )
                    #print("success",to_mail)
                    return HttpResponse(status="200")
            elif report_frequency == '1Hour':
                utc=pytz.UTC
                time_now = datetime.now()

                time_to_compare = utc.localize(time_now)
                #print("the time now is",time_now,time_to_compare)
                report_time = dashboard.report_time
                send_report_time = report_time+timedelta(hours=1)
                if send_report_time <= time_to_compare:

                    hash_str = str(dashboard.pk)+"dashboard"
                    hash_code = str(hash(hash_str))
                    update = ProjectDashboard.objects.filter(pk=dashboard.pk).update(hash_code = hash_code,report_time=time_now)
                    to_mail = []
                    to_mail.append(dashboard.dashboard_admin_user.email)
                    current_site = get_current_site(request)
                    site_name = current_site.name
                    domain = current_site.domain
                    if domain.startswith('127.0.'):
                        domain = 'http://'+domain
                    else:
                        domain = 'https://'+domain
                    try:

                        email_users = dashboard.additional_email.split(',')
                        to_mail = [i for i in email_users ]
                        #print("to mail",to_mail)
                    except:
                        email_users = None
                    if email_users:
                        if dashboard.dashboard_users:

                            for u in  dashboard.dashboard_users.all():
                                to_mail.append(u.email)

                    html_message = render_to_string('dashboard/report.html', {'hash_code': hash_code,'domain':domain})
                    message = 'Please find the Link to  the shared dashboard from brayn.ai:'
                    #print("success",to_mail)
                    mail.send_mail(
                            'Shared dashboard link',
                            "The Shared Dashboard",
                        'noreply@brayn.ai',
                            to_mail,
                            html_message=html_message,
                            fail_silently=False,
                            )
                    #print("success",to_mail)
                    return HttpResponse(status="200")
            elif report_frequency == '6Hours':
                utc=pytz.UTC
                time_now = datetime.now()

                time_to_compare = utc.localize(time_now)
                #print("the time now is",time_now,time_to_compare)
                report_time = dashboard.report_time
                send_report_time = report_time+timedelta(hours=6)
                if send_report_time <= time_to_compare:

                    hash_str = str(dashboard.pk)+"dashboard"
                    hash_code = str(hash(hash_str))
                    update = ProjectDashboard.objects.filter(pk=dashboard.pk).update(hash_code = hash_code,report_time=time_now)
                    to_mail = []
                    to_mail.append(dashboard.dashboard_admin_user.email)
                    current_site = get_current_site(request)
                    site_name = current_site.name
                    domain = current_site.domain
                    if domain.startswith('127.0.'):
                        domain = 'http://'+domain
                    else:
                        domain = 'https://'+domain
                    try:

                        email_users = dashboard.additional_email.split(',')
                        to_mail = [i for i in email_users ]
                        #print("to mail",to_mail)
                    except:
                        email_users = None
                    if email_users:
                        if dashboard.dashboard_users:

                            for u in  dashboard.dashboard_users.all():
                                to_mail.append(u.email)

                    html_message = render_to_string('dashboard/report.html', {'hash_code': hash_code,'domain':domain})
                    message = 'Please find the Link to  the shared dashboard from brayn.ai:'
                    #print("success",to_mail)
                    mail.send_mail(
                            'Shared dashboard link',
                            "The Shared Dashboard",
                        'noreply@brayn.ai',
                            to_mail,
                            html_message=html_message,
                            fail_silently=False,
                            )
                    #print("success",to_mail)
                    return HttpResponse(status="200")
            elif report_frequency == '12Hours':
                utc=pytz.UTC
                time_now = datetime.now()

                time_to_compare = utc.localize(time_now)
                #print("the time now is",time_now,time_to_compare)
                report_time = dashboard.report_time
                send_report_time = report_time+timedelta(hours=12)
                if send_report_time <= time_to_compare:

                    hash_str = str(dashboard.pk)+"dashboard"
                    hash_code = str(hash(hash_str))
                    update = ProjectDashboard.objects.filter(pk=dashboard.pk).update(hash_code = hash_code,report_time=time_now)
                    to_mail = []
                    to_mail.append(dashboard.dashboard_admin_user.email)
                    current_site = get_current_site(request)
                    site_name = current_site.name
                    domain = current_site.domain
                    if domain.startswith('127.0.'):
                        domain = 'http://'+domain
                    else:
                        domain = 'https://'+domain
                    try:

                        email_users = dashboard.additional_email.split(',')
                        to_mail = [i for i in email_users ]
                        #print("to mail",to_mail)
                    except:
                        email_users = None
                    if email_users:
                        if dashboard.dashboard_users:

                            for u in  dashboard.dashboard_users.all():
                                to_mail.append(u.email)

                    html_message = render_to_string('dashboard/report.html', {'hash_code': hash_code,'domain':domain})
                    message = 'Please find the Link to  the shared dashboard from brayn.ai:'
                    #print("success",to_mail)
                    mail.send_mail(
                            'Shared dashboard link',
                            "The Shared Dashboard",
                        'noreply@brayn.ai',
                            to_mail,
                            html_message=html_message,
                            fail_silently=False,
                            )
                    #print("success",to_mail)
                    return HttpResponse(status="200")
            elif report_frequency == 'Daily':
                utc=pytz.UTC
                time_now = datetime.now()

                time_to_compare = utc.localize(time_now)
                #print("the time now is",time_now,time_to_compare)
                report_time = dashboard.report_time
                send_report_time = report_time+timedelta(hours=24)
                if send_report_time <= time_to_compare:

                    hash_str = str(dashboard.pk)+"dashboard"
                    hash_code = str(hash(hash_str))
                    update = ProjectDashboard.objects.filter(pk=dashboard.pk).update(hash_code = hash_code,report_time=time_now)
                    to_mail = []
                    to_mail.append(dashboard.dashboard_admin_user.email)
                    current_site = get_current_site(request)
                    site_name = current_site.name
                    domain = current_site.domain
                    if domain.startswith('127.0.'):
                        domain = 'http://'+domain
                    else:
                        domain = 'https://'+domain
                    try:

                        email_users = dashboard.additional_email.split(',')
                        to_mail = [i for i in email_users ]
                        #print("to mail",to_mail)
                    except:
                        email_users = None
                    if email_users:
                        if dashboard.dashboard_users:

                            for u in  dashboard.dashboard_users.all():
                                to_mail.append(u.email)

                    html_message = render_to_string('dashboard/report.html', {'hash_code': hash_code,'domain':domain})
                    message = 'Please find the Link to  the shared dashboard from brayn.ai:'
                    #print("success",to_mail)
                    mail.send_mail(
                            'Shared dashboard link',
                            "The Shared Dashboard",
                        'noreply@brayn.ai',
                            to_mail,
                            html_message=html_message,
                            fail_silently=False,
                            )
                    #print("success",to_mail)
                    return HttpResponse(status="200")
            elif report_frequency == 'Weekly':
                utc=pytz.UTC
                time_now = datetime.now()
                time_to_compare = utc.localize(time_now)
                report_time = dashboard.report_time
                send_report_time = report_time+timedelta(days=7)
                if send_report_time <= time_to_compare:

                    hash_str = str(dashboard.pk)+"dashboard"
                    hash_code = str(hash(hash_str))
                    update = ProjectDashboard.objects.filter(pk=dashboard.pk).update(hash_code = hash_code,report_time=time_now)
                    to_mail = []
                    current_site = get_current_site(request)
                    site_name = current_site.name
                    domain = current_site.domain
                    if domain.startswith('127.0.'):
                        domain = 'http://'+domain
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
                    #print("success",to_mail)
                    mail.send_mail(
                            'Shared dashboard link',
                            "The Shared Dashboard",
                        'noreply@brayn.ai',
                            to_mail,
                            html_message=html_message,
                            fail_silently=False,
                            )
                    #print("success",to_mail)
                    return HttpResponse(status="200")
            elif report_frequency == '15 Days':
                utc=pytz.UTC
                time_now = datetime.now()
                time_to_compare = utc.localize(time_now)
                report_time = dashboard.report_time
                send_report_time = report_time+timedelta(days=15)
                if send_report_time <= time_to_compare:

                    hash_str = str(dashboard.pk)+"dashboard"
                    hash_code = str(hash(hash_str))
                    update = ProjectDashboard.objects.filter(pk=dashboard.pk).update(hash_code = hash_code,report_time=time_now)
                    to_mail = []
                    current_site = get_current_site(request)
                    site_name = current_site.name
                    domain = current_site.domain
                    if domain.startswith('127.0.'):
                        domain = 'http://'+domain
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
                    #print("success",to_mail)
                    mail.send_mail(
                            'Shared dashboard link',
                            "The Shared Dashboard",
                        'noreply@brayn.ai',
                            to_mail,
                            html_message=html_message,
                            fail_silently=False,
                            )
                    #print("success",to_mail)
                    return HttpResponse(status="200")
            elif report_frequency == '1 Month':
                utc=pytz.UTC
                time_now = datetime.now()
                time_to_compare = utc.localize(time_now)
                report_time = dashboard.report_time
                send_report_time = report_time+timedelta(1*365/12)
                if send_report_time <= time_to_compare:

                    hash_str = str(dashboard.pk)+"dashboard"
                    hash_code = str(hash(hash_str))
                    update = ProjectDashboard.objects.filter(pk=dashboard.pk).update(hash_code = hash_code,report_time=time_now)
                    to_mail = []
                    current_site = get_current_site(request)
                    site_name = current_site.name
                    domain = current_site.domain
                    if domain.startswith('127.0.'):
                        domain = 'http://'+domain
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
                    #print("success",to_mail)
                    mail.send_mail(
                            'Shared dashboard link',
                            "The Shared Dashboard",
                        'noreply@brayn.ai',
                            to_mail,
                            html_message=html_message,
                            fail_silently=False,
                            )
                    #print("success",to_mail)
                    return HttpResponse(status="200")
            elif report_frequency == '6 Months':
                utc=pytz.UTC
                time_now = datetime.now()
                time_to_compare = utc.localize(time_now)
                report_time = dashboard.report_time
                send_report_time = report_time+timedelta(6*365/12)
                if send_report_time <= time_to_compare:

                    hash_str = str(dashboard.pk)+"dashboard"
                    hash_code = str(hash(hash_str))
                    update = ProjectDashboard.objects.filter(pk=dashboard.pk).update(hash_code = hash_code,report_time=time_now)
                    to_mail = []
                    current_site = get_current_site(request)
                    site_name = current_site.name
                    domain = current_site.domain
                    if domain.startswith('127.0.'):
                        domain = 'http://'+domain
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
                    #print("success",to_mail)
                    mail.send_mail(
                            'Shared dashboard link',
                            "The Shared Dashboard",
                        'noreply@brayn.ai',
                            to_mail,
                            html_message=html_message,
                            fail_silently=False,
                            )
                    #print("success",to_mail)
                    return HttpResponse(status="200")
            elif report_frequency == 'Quarterly':
                utc=pytz.UTC
                time_now = datetime.now()
                time_to_compare = utc.localize(time_now)
                report_time = dashboard.report_time
                send_report_time = report_time+timedelta(4*365/12)
                if send_report_time <= time_to_compare:

                    hash_str = str(dashboard.pk)+"dashboard"
                    hash_code = str(hash(hash_str))
                    update = ProjectDashboard.objects.filter(pk=dashboard.pk).update(hash_code = hash_code,report_time=time_now)
                    to_mail = []
                    current_site = get_current_site(request)
                    site_name = current_site.name
                    domain = current_site.domain
                    if domain.startswith('127.0.'):
                        domain = 'http://'+domain
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
                    #print("success",to_mail)
                    mail.send_mail(
                            'Shared dashboard link',
                            "The Shared Dashboard",
                        'noreply@brayn.ai',
                            to_mail,
                            html_message=html_message,
                            fail_silently=False,
                            )
                    #print("success",to_mail)
                    return HttpResponse(status="200")
            elif report_frequency == 'Yearly':
                utc=pytz.UTC
                time_now = datetime.now()
                time_to_compare = utc.localize(time_now)
                report_time = dashboard.report_time
                send_report_time = report_time+timedelta(12*365/12)
                if send_report_time <= time_to_compare:

                    hash_str = str(dashboard.pk)+"dashboard"
                    hash_code = str(hash(hash_str))
                    update = ProjectDashboard.objects.filter(pk=dashboard.pk).update(hash_code = hash_code,report_time=time_now)
                    to_mail = []
                    current_site = get_current_site(request)
                    site_name = current_site.name
                    domain = current_site.domain
                    if domain.startswith('127.0.'):
                        domain = 'http://'+domain
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
                    #print("success",to_mail)
                    mail.send_mail(
                            'Shared dashboard link',
                            "The Shared Dashboard",
                        'noreply@brayn.ai',
                            to_mail,
                            html_message=html_message,
                            fail_silently=False,
                            )
                    #print("success",to_mail)
                    return HttpResponse(status="200")


                    
class OneDayCron(View):
    def get(self,request):
        projects = Project.objects.all().order_by('-id')
        for project in projects:
            if project.delete_obj == True:
                delete = Project.objects.filter(pk=project.pk).delete()
            if project.delete_datetime:
                delta_time = project.delete_datetime+datetime.timedelta(days=30)
                if delta_time >= datetime.now():
                    eps = ProjectEndPoint.objects.filter(project=project)
                    if len(eps)>0:
                        if ep.algorithm:
                            file_exists = default_storage.exists(ep.algorithm.model_id)
                            if file_exists:
                                default_storage.delete(ep.algorithm.model_id)
                    delete = Project.objects.filter(pk=project.pk).delete()




class FiveMinutesCron(View):
    
    def get(self,request):
        projects = Project.objects.filter(delete_obj =True).order_by('-id')
        process = psutil.Process(os.getpid())
        logging.info('Memory initial process start: ' + str(process.memory_info().rss/1000000))
        
        try:
            project_call = listgenerator(projects)
            project = next(project_call)

            if project.delete_datetime:

                title = project.name
                sub_string = '_backup'
                if sub_string not in title:
                    #print("the title is",project.name)
                    title = title+'_backup'
                else:
                    pass
                update = Project.objects.filter(pk=project.pk).update(name=title)
            elif project.delete_obj == True:
                title = project.name
                sub_string = '_cancelled'
                if sub_string not in title:
                    title = title+'_cancelled'
                update = Project.objects.filter(pk=project.pk).update(name=title)
                # if project.delete_datetime:

                #     delta_time = project.delete_datetime+timedelta(minutes=1)
                #     if delta_time >= datetime.now():
                #         delete = Project.objects.filter(pk=project.pk).delete()
                # else:
                #     pass
            if not project.delete_obj:   
                #print("the project pk is",project.pk)
                p_b_object = ProjectBilling(project.pk)
                p_b_object.hourly_bill_update()
                p_b_object.daily_bill_update()
                p_b_object.monthy_bill_update()
            elif not  project.delete_datetime:
                #print("the project pk is",project.pk)
                p_b_object = ProjectBilling(project.pk)
                p_b_object.hourly_bill_update()
                p_b_object.daily_bill_update()
                p_b_object.monthy_bill_update()                                                                                                                                                                  
        except StopIteration:
            pass

        # logging.info('Memory after list is created: ' + str(process.memory_info().rss/1000000))
        process = psutil.Process(os.getpid())
        # logging.info('Memory before list is created: ' + str(process.memory_info().rss/1000000))
        google_sheet_data = CustomerAPIDetails.objects.filter(integration_choice='Google Sheets')
        try:
            project_call = listgenerator(google_sheet_data)
            sheet = next(project_call)
            obj = GoogleSheetCron()
            #print("called")
            if sheet.project.delete_obj:
                pass
            elif sheet.project.delete_datetime:
                pass
            else:
                meta_data = ProjectMetaData.objects.get(project=sheet.project)

                data = obj.get_data(sheet,meta_data)
        except StopIteration:
            pass
        api_data = CustomerAPIDetails.objects.filter(integration_choice='API')
        # logging.info('Memory after list is created: ' + str(process.memory_info().rss/1000000))
        process = psutil.Process(os.getpid())
        # logging.info('Memory before list is created: ' + str(process.memory_info().rss/1000000))
        google_sheet_data = CustomerAPIDetails.objects.filter(integration_choice='Google Sheets')
        #print("api product",api_data)
        try:
            project_call = listgenerator(google_sheet_data)
            api_data_obj = next(project_call)
            obj = ApiDataRead()
            if not api_data_obj.project.delete_obj:

                meta_data = ProjectMetaData.objects.get(project=api_data_obj.project)
                project_schema = ProjectSchema.objects.get(project=api_data_obj.project)
                data = obj.get_data(api_data_obj,meta_data,project_schema)
            elif not  api_data_obj.project.delete_datetime:
                meta_data = ProjectMetaData.objects.get(project=api_data_obj.project)
                project_schema = ProjectSchema.objects.get(project=api_data_obj.project)
                data = obj.get_data(api_data_obj,meta_data,project_schema)
        except StopIteration:
            pass
        # logging.info('Memory after list is created: ' + str(process.memory_info().rss/1000000))

        gc.collect()
        process = psutil.Process(os.getpid())
        logging.info('Memory after gc collected: ' + str(process.memory_info().rss/1000000))
        google_sheet_data = CustomerAPIDetails.objects.filter(integration_choice='Google Sheets')
        # p_b_object = ProjectBilling(120)
        # p_b_object.hourly_bill_update()
        # p_b_object.daily_bill_update()
        # p_b_object.monthy_bill_update()
        return HttpResponse(status="200")







class ProjectBilling:
    def __init__(self,pk):
        self.pk=pk
    
    def hourly_bill_update(self):

        pk = self.pk
        project = Project.objects.get(pk=pk)
        if ProjectPricing.objects.filter(project=project).exists():
            project_pricing = ProjectPricing.objects.get(project=project)
        else:
            project_pricing = DefaultProjectPricing.objects.all().order_by('-id')[0]
        project_billing_parms,created = ProjectBillingPrms.objects.get_or_create(project=project)

        hourly_object_ctreate(project,project_billing_parms,project_pricing)

        return "Sucess"
    def daily_bill_update(self):
        pk = self.pk
        project = Project.objects.get(pk=pk)
        if ProjectPricing.objects.filter(project=project).exists():
            project_pricing = ProjectPricing.objects.get(project=project)
        else:
            project_pricing = DefaultProjectPricing.objects.all().order_by('-id')[0]
        # project_pricing = ProjectPricing.objects.get(project=project)
        project_billing_parms,created = ProjectBillingPrms.objects.get_or_create(project=project)
        daily_object_create(project,project_billing_parms,project_pricing)
        return "Sucess"
    
    def monthy_bill_update(self):
        pk = self.pk
        project = Project.objects.get(pk=pk)
        if ProjectPricing.objects.filter(project=project).exists():
            project_pricing = ProjectPricing.objects.get(project=project)
        else:
            project_pricing = DefaultProjectPricing.objects.all().order_by('-id')[0]
        project_billing_parms,created = ProjectBillingPrms.objects.get_or_create(project=project)
        monthly_object_create(project,project_billing_parms,project_pricing)
        return "Sucess"



def totla_disk_space(project_ep,project_jsons):
    total=0
    for ep in project_ep:
        if ep.algorithm:
            if ep.algorithm.model_size:
                file_size = default_storage.size(ep.algorithm.model_id)
                total = total +file_size
            else:
                pass


        total = total +sys.getsizeof(ep.sub_df)
    for json in project_jsons:
        total = total +sys.getsizeof(json.js)
    return total



def hourly_object_ctreate(project,project_billing_parms,project_pricing):

    now = datetime.now()
    one_day_user_price = project_pricing.user/30
    one_hour_user_price = one_day_user_price/24
    one_day_ep_price = project_pricing.end_point/30
    one_hour_ep_price = one_day_ep_price/24
    one_day_disk_space_cost = project_pricing.disk_space/30
    one_hour_disk_space_cost = one_day_disk_space_cost/24
    #print("the one hour cost",one_hour_user_price,one_hour_ep_price)
    project_jsons = ProjectJsonStorage.objects.filter(project=project)
    project_ep = ProjectEndPoint.objects.filter(project=project)
    total_size_bytes = totla_disk_space(project_ep,project_jsons)
    total_size_mb = total_size_bytes/1000000
    #print("total  space",total_size_mb)
    if ProjectBillingHourlyCost.objects.filter(project=project).exists():
        project_billing_hourly_cost = ProjectBillingHourlyCost.objects.filter(project=project).order_by('-id')[0]

        # update_time = project_billing_hourly_cost.updated+timedelta(hours=5,minutes=40)
        update_time = project_billing_hourly_cost.updated+timedelta(hours=1)
        next_updated_time = update_time+timedelta(minutes=1)
        if utc.localize(now) >= update_time and update_time < next_updated_time :
            #print("the updated time and now from if of hourly",update_time,utc.localize(now))
            user_cost  = project_billing_parms.user * one_hour_user_price
            end_point_cost = project_billing_parms.end_point * one_hour_ep_price
            disk_space_c = total_size_mb * one_hour_disk_space_cost
            time = datetime.now()
            project_billing_hourly_cost = ProjectBillingHourlyCost.objects.create(project=project,user_cost=user_cost,end_point_cost=end_point_cost,updated=datetime.now(),disk_space_cost=disk_space_c)

    else:
        created = project.created
        update_time = project.created+timedelta(hours=1)

        next_updated_time = update_time+timedelta(minutes=1)
        if utc.localize(now) >= update_time and update_time < next_updated_time :
            #print("the updated time and now from else of hourly",update_time,utc.localize(now))
            user_cost  = project_billing_parms.user * one_hour_user_price
            end_point_cost = project_billing_parms.end_point * one_hour_ep_price
            disk_space_cost = total_size_mb * project_pricing.disk_space
            time = datetime.now()
            #print("the user and end_point_cost",user_cost,end_point_cost,disk_space_cost)
            project_billing_hourly_cost = ProjectBillingHourlyCost.objects.create(project=project,user_cost=user_cost,end_point_cost=end_point_cost,updated=datetime.now(),disk_space_cost=disk_space_cost)

    return "Sucess"

def daily_object_create(project,project_billing_parms,project_pricing):
    now = datetime.now()
    if ProjectBillingDayCost.objects.filter(project=project).exists():
        project_billing_day_cost = ProjectBillingDayCost.objects.filter(project=project).order_by('-id')[0]
        update_time = project_billing_day_cost.updated+timedelta(hours=24)
        #print("the updated time is",project_billing_day_cost.updated)
        # update_time = project_billing_day_cost.updated+timedelta(hours=6)
        from_date = project_billing_day_cost.updated
        to_date = datetime.now()
        project_billing_hourly_cost = ProjectBillingHourlyCost.objects.filter(Q(project=project)&Q(created__range=(from_date, to_date)))

        next_updated_time = update_time+timedelta(minutes=1)
        if utc.localize(now) >= update_time and update_time < next_updated_time :
            #print("the updated time and now from if of daily",update_time,utc.localize(now))
            user_cost = 0
            end_point_cost = 0
            disk_space_cost = 0
            customer = Customer.objects.get(user=project.admin_user)
            if customer.type == 'Individual':
                iqs_cost = 0.0
            elif customer.type == 'Company':
                if project_billing_parms.query_count> 300:


                    iqs_c = project_billing_parms.query_count * project_pricing.iqs
                    if iqs_c >= project_billing_day_cost.iqs_cost:

                        iqs_cost = iqs_c - project_billing_day_cost.iqs_cost
                    elif  project_billing_day_cost.iqs_cost >=  iqs_c:
                        iqs_cost =  project_billing_day_cost.iqs_cost - iqs_c
                else:
                    iqs_cost = 0.0


            for cost in project_billing_hourly_cost:

                user_cost = user_cost+cost.user_cost
                end_point_cost = end_point_cost+cost.end_point_cost
                disk_space_cost = disk_space_cost+cost.disk_space_cost
            time = datetime.now()


            update = ProjectBillingDayCost.objects.create(project=project,user_cost=user_cost,end_point_cost=end_point_cost,disk_space_cost=disk_space_cost,updated=datetime.now(),iqs_cost=iqs_cost)

    else:
        from_date = project.created
        to_date = datetime.now()
        update_time = project.created+timedelta(hours = 24)
        # update_time = project.created+timedelta(hours=6)
        project_billing_hourly_cost = ProjectBillingHourlyCost.objects.filter(Q(project=project)&Q(created__range=(from_date, to_date)))
        next_updated_time = update_time+timedelta(minutes=1)
        if utc.localize(now) >= update_time and update_time < next_updated_time:
            #print("the updated time and now from else of daily",update_time,utc.localize(now))
            user_cost = 0
            end_point_cost = 0
            disk_space_cost = 0
            customer = Customer.objects.get(user=project.admin_user)
            if customer.type == 'Individual':
                iqs_cost = 0.0
            elif customer.type == 'Company':
                if project_billing_parms.query_count> 300:


                    iqs_c = project_billing_parms.query_count * project_pricing.iqs
                    if iqs_c >= project_billing_day_cost.iqs_cost:

                        iqs_cost = iqs_c
                    elif  project_billing_day_cost.iqs_cost >=  iqs_c:
                        iqs_cost = iqs_c
                else:
                    iqs_cost = 0.0


            for cost in project_billing_hourly_cost:

                user_cost = user_cost+cost.user_cost
                end_point_cost = end_point_cost+cost.end_point_cost
                disk_space_cost = disk_space_cost+cost.disk_space_cost
            update = ProjectBillingDayCost.objects.create(project=project,user_cost=user_cost,end_point_cost=end_point_cost,disk_space_cost=disk_space_cost,updated=datetime.now(),iqs_cost=iqs_cost)
    return "Success"
def monthly_object_create(project,project_billing_parms,project_pricing):
    now = datetime.now()
    if ProjectBillingMonthCost.objects.filter(project=project).exists():
        project_billing_month_cost = ProjectBillingMonthCost.objects.filter(project=project).order_by('-id')[0]
        update_time = project_billing_month_cost.updated+timedelta(days=30)
        # update_time = project_billing_month_cost.updated+timedelta(hours=6,minutes=30)
        from_date = project_billing_month_cost.created
        to_date = datetime.now()
        #print("the month from and to",from_date,to_date)
        project_billing_day_cost = ProjectBillingDayCost.objects.filter(Q(project=project)&Q(created__range=(from_date, to_date)))
        project_jsons = ProjectJsonStorage.objects.filter(project=project)
        project_ep = ProjectEndPoint.objects.filter(project=project)
        total_size_bytes = totla_disk_space(project_ep,project_jsons)
        total_size_mb = total_size_bytes/1000000
        #print("the disk size is ",total_size_mb)
        next_updated_time = update_time+timedelta(minutes=1)
        if utc.localize(now) >= update_time and update_time < next_updated_time :
            #print("the updated time and now from if of monthly",update_time,utc.localize(now))
            user_cost = 0
            end_point_cost = 0
            disk_space_cost = 0
            iqs_cost        = 0
            for cost in project_billing_day_cost:

                user_cost = user_cost+cost.user_cost
                end_point_cost = end_point_cost+cost.end_point_cost
                disk_space_cost = disk_space_cost+cost.disk_space_cost
                iqs_cost        = iqs_cost +cost.iqs_cost
            time = datetime.now()
            user_cost = round(user_cost,2)
            end_point_cost = round(end_point_cost,2)
            disk_space_cost = round(disk_space_cost,2)
            iqs_cost        = round(iqs_cost,2)

            project_month_cost = ProjectBillingMonthCost.objects.create(project=project,user_cost=user_cost,end_point_cost=end_point_cost,disk_space_cost=disk_space_cost,updated=datetime.now(),iqs_cost=iqs_cost,iqs_count=project_billing_parms.query_count,disk_space_count=total_size_mb,custom_supprt=project_pricing.custom_supprt,monthly_maintenance=project_pricing.monthly_maintenance)
            bill_amount = project_month_cost.disk_space_cost+project_month_cost.end_point_cost+project_month_cost.user_cost+project_month_cost.iqs_cost+project_pricing.monthly_maintenance+project_pricing.custom_supprt
            bill_amount = float(bill_amount)
            bill_amount = round(bill_amount,2)
            tax = Tax.objects.all().order_by('-id')[0]
            one_percent = bill_amount/100
            tax_amount = round(tax.tax_percentage *one_percent,2)
            total = round(bill_amount+tax_amount,2)

            if ProjectInvoice.objects.filter().exists():
                p_i = ProjectInvoice.objects.latest('id')
                invoice_id = "INV-BRAYN-"+str(p_i.pk)
            else:
                invoice_id = "INV-BRAYN-001"
            if project_pricing.free_tire == True:
                project_invoice    = ProjectInvoice.objects.create(from_date=project_billing_month_cost.updated,to_date=project_month_cost.created,monthly_cost=project_month_cost,invoice_id=invoice_id,bill_amount=bill_amount,tax_amount=tax_amount,total_amount=total,discount_amount=total)
            else:
                project_invoice    = ProjectInvoice.objects.create(from_date=project_billing_month_cost.updated,to_date=project_month_cost.created,monthly_cost=project_month_cost,invoice_id=invoice_id,bill_amount=bill_amount,tax_amount=tax_amount,total_amount=total)
            update = ProjectBillingPrms.objects.filter(pk=project_billing_parms.pk).update(query_count=0)
    else:
        from_date = project.created
        to_date = datetime.now()
        update_time = project.created+timedelta(days=30)
        # update_time = project.created+timedelta(hours=6,minutes=30)
        project_jsons = ProjectJsonStorage.objects.filter(project=project)
        project_ep = ProjectEndPoint.objects.filter(project=project)
        total_size_bytes = totla_disk_space(project_ep,project_jsons)
        total_size_mb = total_size_bytes/1000000
        project_billing_day_cost = ProjectBillingDayCost.objects.filter(Q(project=project)&Q(created__range=(from_date, to_date)))
        next_updated_time = update_time+timedelta(minutes=1)
        if utc.localize(now) >= update_time and update_time < next_updated_time :
            #print("the updated time and now from else of monthly",update_time,utc.localize(now))
            user_cost = 0
            end_point_cost = 0
            disk_space_cost = 0
            iqs_cost = 0
            for cost in project_billing_day_cost:

                user_cost = user_cost+cost.user_cost
                end_point_cost = end_point_cost+cost.end_point_cost
                disk_space_cost = disk_space_cost+cost.disk_space_cost
                iqs_cost        = iqs_cost +cost.iqs_cost

            project_month_cost = ProjectBillingMonthCost.objects.create(project=project,user_cost=user_cost,end_point_cost=end_point_cost,disk_space_cost=disk_space_cost,updated=datetime.now(),iqs_cost=iqs_cost,iqs_count=project_billing_parms.query_count,disk_space_count=total_size_mb,custom_supprt=project_pricing.custom_supprt,monthly_maintenance=project_pricing.monthly_maintenance)
            bill_amount = project_month_cost.disk_space_cost+project_month_cost.end_point_cost+project_month_cost.user_cost+project_month_cost.iqs_cost+project_pricing.monthly_maintenance+project_pricing.custom_supprt
            tax = Tax.objects.all().order_by('-id')[0]
            one_percent = bill_amount/100
            tax_amount = round(tax.tax_percentage *one_percent,2)
            total = round(bill_amount+tax_amount,2)
            if ProjectInvoice.objects.filter().exists():
                p_i = ProjectInvoice.objects.latest('id')
                invoice_id = "INV-BRAYN-"+str(p_i.pk)
            else:
                invoice_id = "INV-BRAYN-001"
            if project_pricing.free_tire == True:
                project_invoice    = ProjectInvoice.objects.create(from_date=project.created,to_date=project_month_cost.created,monthly_cost=project_month_cost,invoice_id=invoice_id,bill_amount=bill_amount,tax_amount=tax_amount,total_amount=total,discount_amount=total)
            else:
                project_invoice    = ProjectInvoice.objects.create(from_date=project.created,to_date=project_month_cost.created,monthly_cost=project_month_cost,invoice_id=invoice_id,bill_amount=bill_amount,tax_amount=tax_amount,total_amount=total)
            update = ProjectBillingPrms.objects.filter(pk=project_billing_parms.pk).update(query_count=0)
    return "Success"



class ApiDataRead:
    def __init__(self,):
        pass
    
    def get_data(self,api_data_obj,meta_data,project_schema):
        time_now = datetime.now()
        today=time_now.date()
        time_now = utc.localize(time_now)
        #print("called get_data function")
        if  api_data_obj.range == '1Minute':
            if api_data_obj.updated:
                compate_time = api_data_obj.updated
                if time_now >=compate_time+timedelta(minutes=1):
                    #print("call from 1 minutes")
                    self.details(api_data_obj,meta_data,project_schema)
            else:
                compate_time = api_data_obj.created

                if time_now >=compate_time+timedelta(minutes=1):
                    self.details(api_data_obj,meta_data,project_schema)
        elif  api_data_obj.range == '5Minutes':
            if api_data_obj.updated:
                compate_time = api_data_obj.updated+timedelta(minutes=5)
                if time_now >=compate_time:
                    self.details(api_data_obj,meta_data,project_schema)
            else:
                compate_time = api_data_obj.created+timedelta(minutes=5)
                if time_now >=compate_time:
                    self.details(api_data_obj,meta_data,project_schema)
        elif  api_data_obj.range == '10Minutes':
            if api_data_obj.updated:
                compate_time = api_data_obj.updated+timedelta(minutes=10)
                if time_now >=compate_time:
                    self.details(api_data_obj,meta_data,project_schema)
            else:
                compate_time = api_data_obj.created+timedelta(minutes=10)
                if time_now >=compate_time:
                    self.details(api_data_obj,meta_data,project_schema)
        elif  api_data_obj.range == '15Minutes':
            if api_data_obj.updated:
                compate_time = api_data_obj.updated+timedelta(minutes=15)
                if time_now >=compate_time:
                    self.details(api_data_obj,meta_data,project_schema)
            else:
                compate_time = api_data_obj.created+timedelta(minutes=15)
                if time_now >=compate_time:
                    self.details(api_data_obj,meta_data,project_schema)
        elif  api_data_obj.range == '30Minutes':
            if api_data_obj.updated:
                compate_time = api_data_obj.updated+timedelta(minutes=30)
                if time_now >=compate_time:
                    self.details(api_data_obj,meta_data,project_schema)
            else:
                compate_time = api_data_obj.created+timedelta(minutes=30)
                if time_now >=compate_time:
                    self.details(api_data_obj,meta_data,project_schema)
        elif  api_data_obj.range == '1Hour':
            if api_data_obj.updated:
                compate_time = api_data_obj.updated+timedelta(hours=1)
                if time_now >=compate_time:
                    self.details(api_data_obj,meta_data,project_schema)
            else:
                compate_time = api_data_obj.created+timedelta(hours=1)
                if time_now >=compate_time:
                    self.details(api_data_obj,meta_data,project_schema)
        elif  api_data_obj.range == '6Hours':
            if api_data_obj.updated:
                compate_time = api_data_obj.updated+timedelta(hours=6)
                if time_now >=compate_time:
                    self.details(api_data_obj,meta_data,project_schema)
        elif  api_data_obj.range == '12Hours':
            if api_data_obj.updated:
                compate_time = api_data_obj.updated+timedelta(hours=12)
                if time_now >=compate_time:
                    self.details(api_data_obj,meta_data,project_schema)
        elif  api_data_obj.range == 'Weekly':
            if api_data_obj.updated:
                compate_time = api_data_obj.updated+timedelta(days=7)
                if time_now >=compate_time:
                    self.details(api_data_obj,meta_data,project_schema)
            else:
                compate_time = api_data_obj.created+timedelta(days=7)
                if time_now >=compate_time:
                    self.details(api_data_obj,meta_data,project_schema)
        elif  api_data_obj.range == '15 Days':
            if api_data_obj.updated:
                compate_time = api_data_obj.updated+timedelta(days=15)
                if time_now >=compate_time:
                    self.details(api_data_obj,meta_data,project_schema)
            else:
                compate_time = api_data_obj.created+timedelta(days=15)
                if time_now >=compate_time:

                    self.details(api_data_obj,meta_data,project_schema)
        elif  api_data_obj.range == '1 Month':
            if api_data_obj.updated:
                compate_time = api_data_obj.updated+timedelta(days=30)
                if time_now >=compate_time:
                    self.details(api_data_obj,meta_data,project_schema)
            else:
                compate_time = api_data_obj.created+timedelta(days=30)
                if time_now >=compate_time:
                    self.details(api_data_obj,meta_data,project_schema)
        elif  api_data_obj.range == '6 Months':
            if api_data_obj.updated:
                compate_time = api_data_obj.updated+timedelta(days=180)
                if time_now >=compate_time:
                    self.details(api_data_obj,meta_data,project_schema)
            else:
                compate_time = api_data_obj.created+timedelta(days=180)
                if time_now >=compate_time:
                    self.details(api_data_obj,meta_data,project_schema)

    def details(self,api_data_obj,meta_data,project_schema):
        #print("called")
        error = False
        if api_data_obj.token:


            headers =  {'content-type' : 'application/json',
                                        'Authorization':api_data_obj.basic_key}

            JSONContent  = requests.get(api_data_obj.api,

                                headers=headers, verify=True)
        else:
            headers =  {'content-type' : 'application/json',
                                   }

            JSONContent  = requests.get(api_data_obj.api,
                              headers=headers, verify=True)
        if 'error' not in JSONContent:
            data_str = JSONContent.text
            data_json =json.loads(data_str)
            try:
                df = pd.json_normalize(data_json['results'])
            except:
                try:

                    df = pd.json_normalize(data_json['data'])
                except:
                    df = pd.json_normalize(data_json)

            df.columns =  df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '').str.replace('.', '_').str.replace(',','_').str.replace('/','_')
            columns = df.columns.to_list()
            project_json = ProjectJsonStorage.objects.filter(project=api_data_obj.project).order_by('id')[0]
            json_string = json.loads(project_json.js)
            json_df = pd.DataFrame(json_string)
            # #print(type(json_df.head()))

            transposed_df = json_df.transpose()
            rows = transposed_df.shape[0]

            meta_columns = meta_data.columns['columns']
            drop_column_list=[]
            for column in columns:
                if column not in meta_columns:
                    error=True
                    drop_column_list.append(column)
            df = df.drop(drop_column_list, axis=1)

            if not error:
                columns = meta_data.columns['columns']



                transposed_df_columns = transposed_df.columns.tolist()
                new_df_columns = transposed_df.columns.tolist()

                column_list = [x for x in transposed_df_columns if x in new_df_columns]



                new_columns = [x  for x in new_df_columns if x not in columns ]

                for key, value in meta_data.meta_data.items():
                    if key in transposed_df_columns:
                        if value['dtype'] == 'int':
                            transposed_df[key] =pd.to_numeric(transposed_df[key])
                            if key in new_df_columns:
                                df[key] = pd.to_numeric(df[key])
                        elif value['dtype'] == 'float':
                            #print("final key",key,transposed_df[key],transposed_df[key].dtypes)
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
                            #print("the data key",key)
                            if key in new_df_columns:
                                df[key] = pd.to_datetime(df[key])




                # truncate the y_df based on the mother df rows

                if len(column_list)>0:
                    result_df = reduce(lambda left,right: pd.merge(left,right,on=column_list, how='outer'), [transposed_df,df])
                else:
                    try:
                        result_df = reduce(lambda left,right: pd.merge(left,right,left_on= transposed_df_columns[0],right_on=new_df_columns[0],how='outer'), [transposed_df,df])
                    except:
                        result_df = reduce(lambda left,right: pd.merge(left,right,left_index=True,right_index=True,how='outer'), [transposed_df,df])
                # #print("the df is ",result_df) erge the mother df with new rows ofss data
                result_df_columns = result_df.columns.tolist()

                result_df.drop_duplicates(subset = transposed_df_columns, inplace = True)
                fillna_obj = FillNan(result_df)
                delete_column_list = []
                custom_column_list = {}
                for key, value in meta_data.meta_data.items():

                    if key in result_df_columns:
                        # #print("key present in metadata ",key)
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

                # #print("the original df after nan filling is",result_df)
                if len(custom_column_list)>0:
                    # #print("the before nan fill ",len(result_df) - result_df.count())

                    result_df.fillna(value=custom_column_list,inplace=True)
                    # #print("the result after nan fill",result_df,custom_column_list)
                    # #print("after nan fill ",len(result_df) - result_df.count())

                if len(delete_column_list)>0:

                    # #print("the value ",delete_column_list)
                    column_delete_obj = DeleteColumn(result_df)
                    result_df = column_delete_obj.delete_column(delete_column_list)
                    # #print("columns ",result_df.columns.tolist())
                if meta_data.date_column_name:
                    result_df[meta_data.date_column_name]= result_df[meta_data.date_column_name].astype(str)
                column_dict = {'columns':result_df.columns.tolist()}
                res_json=result_df.to_json(orient='index')
                rows = result_df.shape[0]
                columns = result_df.shape[1]
                df_head=result_df.head(5)
                df_tail = result_df.tail(5)
                df_head_json = df_head.to_json(orient='index')
                df_tail_json  = df_tail.to_json(orient='index')
                project_json = ProjectJsonStorage.objects.filter(project=api_data_obj.project).update(js=res_json,columns=column_dict)
                project_json = ProjectJsonStorage.objects.filter(project=api_data_obj.project).order_by('id')[0]
                c_list = {'columns':result_df_columns}
                # #print("the ")

                project_json_metadata = ProjectJsonStorageMetadata.objects.filter(project_json=project_json).update(rows=rows,columns=columns,head_json=df_head_json,tail_json=df_tail_json)
                #print("the data updated ")
            else:
                error = "The existing Schema Dosen't Match with Api Data"
                html_message = render_to_string('api_error_email.html', {'project': meta_data.project,'error':error})

                from_email = '<noreply@brayn.ai>'

                to = ["nag@realmimpex.com"]
                #sending mail to customer with from, to address and html message which includes the password reset link
                mail.send_mail("Error in Api dat Gets","ERROR", from_email, to, html_message=html_message)
        else:
            error = "Error in  Receiving a Data From th API"
            html_message = render_to_string('api_error_email.html', {'project': meta_data.project,'error':error,})

            from_email = 'noreply@brayn.ai'

            to = [meta_data.project.admin_user.email]
            #sending mail to customer with from, to address and html message which includes the password reset link
            mail.send_mail("Error in Api dat Gets","ERROR", from_email, to, html_message=html_message)
        update = CustomerAPIDetails.objects.filter(pk=api_data_obj.pk).update(updated=datetime.now())
        return True

        



class ProjectEndPointSubDfView(View):
    '''class to update the sub df of the endpoint'''
    
    def get(self,request):
        endpoints = ProjectEndPoint.objects.all().order_by('-id')
        time_now = datetime.now()
        time_now = utc.localize(time_now)

        for end_point in endpoints:
            p_query = end_point.query
            if end_point.sub_df_frequency == '1Minute':

                if end_point.updated:
                    compare_time = end_point.updated+timedelta(minutes=1)
                    #print("the endpoint updated",compare_time,time_now)
                    if time_now>=compare_time :
                        #print("satisfied")
                        update_sub_df(end_point,p_query)

                else:

                    compare_time = end_point.created+timedelta(minutes=1)
                    if time_now >= compare_time:
                        #print("satisfied")
                        update_sub_df(end_point,p_query)
            elif end_point.sub_df_frequency == '5Minutes':

                if end_point.updated:
                    compare_time = end_point.updated+timedelta(minutes=5)
                    #print("the endpoint updated",compare_time,time_now)
                    if time_now>=compare_time :
                        #print("satisfied")
                        update_sub_df(end_point,p_query)

                else:

                    compare_time = end_point.created+timedelta(minutes=5)
                    if time_now >= compare_time:
                        #print("satisfied")
                        update_sub_df(end_point,p_query)
            elif end_point.sub_df_frequency == '10Minutes':

                if end_point.updated:
                    compare_time = end_point.updated+timedelta(minutes=10)
                    #print("the endpoint updated",compare_time,time_now)
                    if time_now>=compare_time :
                        #print("satisfied")
                        update_sub_df(end_point,p_query)

                else:

                    compare_time = end_point.created+timedelta(minutes=10)
                    if time_now >= compare_time:
                        #print("satisfied")
                        update_sub_df(end_point,p_query)
            elif end_point.sub_df_frequency == '15Minutes':

                if end_point.updated:
                    compare_time = end_point.updated+timedelta(minutes=15)
                    #print("the endpoint updated",compare_time,time_now)
                    if time_now>=compare_time :
                        #print("satisfied")
                        update_sub_df(end_point,p_query)

                else:

                    compare_time = end_point.created+timedelta(minutes=15)
                    if time_now >= compare_time:
                        #print("satisfied")
                        update_sub_df(end_point,p_query)
            elif end_point.sub_df_frequency == '30Minutes':

                if end_point.updated:
                    compare_time = end_point.updated+timedelta(minutes=30)
                    #print("the endpoint updated",compare_time,time_now)
                    if time_now>=compare_time :
                        #print("satisfied")
                        update_sub_df(end_point,p_query)

                else:

                    compare_time = end_point.created+timedelta(minutes=30)
                    if time_now >= compare_time:
                        #print("satisfied")
                        update_sub_df(end_point,p_query)

            elif end_point.sub_df_frequency == '1Hour':

                if end_point.updated:
                    compare_time = end_point.updated+timedelta(hours=1)
                    if time_now >= compare_time:
                        #print("satisfied")
                        update_sub_df(end_point,p_query)


                else:

                    compare_time = end_point.created+timedelta(hours=1)
                    if time_now >= compare_time :
                        #print("satisfied")
                        update_sub_df(end_point,p_query)
            elif end_point.sub_df_frequency == '6Hour':

                if end_point.updated:
                    compare_time = end_point.updated+timedelta(hours=6)
                    if time_now >= compare_time:
                        #print("satisfied")
                        update_sub_df(end_point,p_query)


                else:

                    compare_time = end_point.created+timedelta(hours=6)
                    if time_now >= compare_time :
                        #print("satisfied")
                        update_sub_df(end_point,p_query)
            elif end_point.sub_df_frequency == '12Hour':

                if end_point.updated:
                    compare_time = end_point.updated+timedelta(hours=12)
                    if time_now >= compare_time:
                        #print("satisfied")
                        update_sub_df(end_point,p_query)


                else:

                    compare_time = end_point.created+timedelta(hours=12)
                    if time_now >= compare_time :
                        #print("satisfied")
                        update_sub_df(end_point,p_query)
            elif end_point.sub_df_frequency == 'Daily':


                if end_point.updated:
                    compare_time = end_point.updated+timedelta(hours=24)
                    if time_now >=compare_time :
                        #print("satisfied")
                        update_sub_df(end_point,p_query)

                else:

                    compare_time = end_point.created+timedelta(hours=24)
                    if time_now >= compare_time :
                        #print("satisfied")
                        update_sub_df(end_point,p_query)


            elif end_point.sub_df_frequency == 'Weekly':
                if end_point.updated:
                    compare_time = end_point.updated+timedelta(days=7)
                    if time_now >= compare_time :
                        #print("satisfied")
                        update_sub_df(end_point,p_query)


                else:

                    compare_time = end_point.created+timedelta(days=7)
                    if time_now >= compare_time :
                        #print("satisfied")
                        update_sub_df(end_point,p_query)

        return HttpResponse(status="200")

class GoogleSheetCron:
    def __init__(self):
        pass
    
    def get_data(self,sheet,meta_data):
        time_now = datetime.now()
        today=time_now.date()
        time_now = utc.localize(time_now)
        #print("called get_data function")
        if  sheet.range == '1Minute':
            if sheet.updated:
                compate_time = sheet.updated
                if time_now >=compate_time+timedelta(minutes=1):
                    #print("call from 1 minutes")
                    readgsheet(sheet,meta_data)
            else:
                compate_time = sheet.created

                if time_now >=compate_time+timedelta(minutes=1):
                    readgsheet(sheet,meta_data)
        elif  sheet.range == '5Minutes':
            if sheet.updated:
                compate_time = sheet.updated+timedelta(minutes=5)
                if time_now >=compate_time:
                    readgsheet(sheet,meta_data)
            else:
                compate_time = sheet.created+timedelta(minutes=5)
                if time_now >=compate_time:
                    readgsheet(sheet,meta_data)
        elif  sheet.range == '10Minutes':
            if sheet.updated:
                compate_time = sheet.updated+timedelta(minutes=10)
                if time_now >=compate_time:
                    readgsheet(sheet,meta_data)
            else:
                compate_time = sheet.created+timedelta(minutes=10)
                if time_now >=compate_time:
                    readgsheet(sheet,meta_data)
        elif  sheet.range == '15Minutes':
            if sheet.updated:
                compate_time = sheet.updated+timedelta(minutes=15)
                if time_now >=compate_time:
                    readgsheet(sheet,meta_data)
            else:
                compate_time = sheet.created+timedelta(minutes=15)
                if time_now >=compate_time:
                    readgsheet(sheet,meta_data)
        elif  sheet.range == '30Minutes':
            if sheet.updated:
                compate_time = sheet.updated+timedelta(minutes=30)
                if time_now >=compate_time:
                    readgsheet(sheet,meta_data)
            else:
                compate_time = sheet.created+timedelta(minutes=30)
                if time_now >=compate_time:
                    readgsheet(sheet,meta_data)
        elif  sheet.range == '1Hour':
            if sheet.updated:
                compate_time = sheet.updated+timedelta(hours=1)
                if time_now >=compate_time:
                    readgsheet(sheet,meta_data)
            else:
                compate_time = sheet.created+timedelta(hours=1)
                if time_now >=compate_time:
                    readgsheet(sheet,meta_data)
        elif  sheet.range == '6Hours':
            if sheet.updated:
                compate_time = sheet.updated+timedelta(hours=6)
                if time_now >=compate_time:
                    readgsheet(sheet,meta_data)
        elif  sheet.range == '12Hours':
            if sheet.updated:
                compate_time = sheet.updated+timedelta(hours=12)
                if time_now >=compate_time:
                    readgsheet(sheet,meta_data)
        elif  sheet.range == 'Weekly':
            if sheet.updated:
                compate_time = sheet.updated+timedelta(days=7)
                if time_now >=compate_time:
                    readgsheet(sheet,meta_data)
            else:
                compate_time = sheet.created+timedelta(days=7)
                if time_now >=compate_time:
                    readgsheet(sheet,meta_data)
        elif  sheet.range == '15 Days':
            if sheet.updated:
                compate_time = sheet.updated+timedelta(days=15)
                if time_now >=compate_time:
                    readgsheet(sheet,meta_data)
            else:
                compate_time = sheet.created+timedelta(days=15)
                if time_now >=compate_time:

                    readgsheet(sheet,meta_data)
        elif  sheet.range == '1 Month':
            if sheet.updated:
                compate_time = sheet.updated+timedelta(days=30)
                if time_now >=compate_time:
                    readgsheet(sheet,meta_data)
            else:
                compate_time = sheet.created+timedelta(days=30)
                if time_now >=compate_time:
                    readgsheet(sheet,meta_data)
        elif  sheet.range == '6 Months':
            if sheet.updated:
                compate_time = sheet.updated.timedelta(days=180)
                if time_now >=compate_time:
                    readgsheet(sheet,meta_data,project_schema)
            else:
                compate_time = sheet.created.timedelta(days=180)
                if time_now >=compate_time:
                    readgsheet(sheet,meta_data,project_schema)






def readgsheet(sheet,meta_data):
    scope=['htps://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive']
    if sheet.credentials:    
        file = sheet.credentials.open()
        file_content = file.read()
        js_str = json.loads(file_content.decode('utf-8'))
        creadentials = ServiceAccountCredentials.from_json_keyfile_dict(js_str)
        gc = gspread.authorize(creadentials)
        wks = gc.open(sheet.file_id).sheet1
        scope=['htps://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
        file = sheet.credentials.open()
        file_content = file.read()
        access_type='offline'
        # #print("the file content-type",file_content)
        js_str = json.loads(file_content.decode('utf-8'))
        #print("the file content-type",js_str)
        creadentials = ServiceAccountCredentials.from_json_keyfile_dict(js_str)
        gc = gspread.authorize(creadentials)
        wks = gc.open(sheet.file_id).sheet1

        data = wks.get_all_records()
        #print("read succefully")



        df = pd.DataFrame(data)
    elif sheet.sheet_url:
        if sheet.sheet_header:
            df = pd.read_html(sheet.sheet_url,encoding='utf8',index_col=0,header=sheet.sheet_header)
        else:
            df = pd.read_html(sheet.sheet_url,encoding='utf8',index_col=0,header=1)
        df = df[0]

    # try:

    #     scope=['htps://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    #     file = sheet.credentials.open()
    #     file_content = file.read()
    #     js_str = json.loads(file_content.decode('utf-8'))
    #     creadentials = ServiceAccountCredentials.from_json_keyfile_dict(js_str)
    #     gc = gspread.authorize(creadentials)
    #     wks = gc.open(sheet.file_id).sheet1

    #     data = wks.get_all_records()
    # except:
    #     pass
    
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '').str.replace('.', '_').str.replace(',','_').str.replace('/','_').str.replace(':','').str.replace(':','')
    new_df_columns = df.columns.tolist()
    columns = df.columns.tolist()
    project_json = ProjectJsonStorage.objects.filter(project=sheet.project).order_by('id')[0]
    json_string = json.loads(project_json.js)
    json_df = pd.DataFrame(json_string)
    # #print(type(json_df.head()))

    transposed_df = json_df.transpose()
    rows = transposed_df.shape[0]
    error=False
    meta_columns = meta_data.columns['columns']
    for column in columns:
            if column not in meta_columns:
                error=True
    if not error:


        columns = meta_data.columns['columns']


        transposed_df_columns = transposed_df.columns.tolist()

        column_list = [x for x in transposed_df_columns if x in new_df_columns]



        new_columns = [x  for x in new_df_columns if x not in columns ]

        for key, value in meta_data.meta_data.items():
            if key in transposed_df_columns:
                if value['dtype'] == 'int':
                    transposed_df[key] =pd.to_numeric(transposed_df[key])
                    if key in new_df_columns:
                        df[key] = pd.to_numeric(df[key])
                elif value['dtype'] == 'float':
                    #print("final key",key,transposed_df[key],transposed_df[key].dtypes)
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
                    #print("the data key",key)
                    if key in new_df_columns:
                        df[key] = pd.to_datetime(df[key])
        result_df =df
        result_df = result_df.replace('',np.nan)
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '').str.replace('.', '_').str.replace(',','_').str.replace('/','_').str.replace(':','').str.replace(':','')
        result_df_columns = result_df.columns.tolist()
        fillna_obj = FillNan(result_df)
        delete_column_list = []
        custom_column_list = {}
        for key, value in meta_data.meta_data.items():

            if key in result_df_columns:
                # logging.info("value "+str(value))
                #print("key present in metadata ",key)
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

        #print("the original df after nan filling is",result_df)
        if len(custom_column_list)>0:
            #print("the before nan fill ",len(result_df) - result_df.count())

            result_df.fillna(value=custom_column_list,inplace=True)
            #print("the result after nan fill",result_df,custom_column_list)
            #print("after nan fill ",len(result_df) - result_df.count())

        if len(delete_column_list)>0:

            #print("the value ",delete_column_list)
            column_delete_obj = DeleteColumn(result_df)
            result_df = column_delete_obj.delete_column(delete_column_list)
            #print("columns ",result_df.columns.tolist())


        # truncate the y_df based on the mother df rows

        if len(column_list)>0:
            result_df = reduce(lambda left,right: pd.merge(left,right,on=column_list, how='outer'), [transposed_df,result_df])
        else:
            try:
                result_df = reduce(lambda left,right: pd.merge(left,right,left_on= transposed_df_columns[0],right_on=new_df_columns[0],how='outer'), [transposed_df,result_df])
            except:
                result_df = reduce(lambda left,right: pd.merge(left,right,left_index=True,right_index=True,how='outer'), [transposed_df,df])

        # #print("the df is ",result_df) erge the mother df with new rows ofss data
        result_df_columns = result_df.columns.tolist()

        result_df.drop_duplicates(subset = transposed_df_columns, inplace = True)
        if meta_data.date_column_name:
            result_df[meta_data.date_column_name]= result_df[meta_data.date_column_name].astype(str)
        column_dict = {'columns':result_df.columns.tolist()}
        res_json=result_df.to_json(orient='index')
        rows = result_df.shape[0]
        columns = result_df.shape[1]
        df_head=result_df.head(5)
        df_tail = result_df.tail(5)
        df_head_json = df_head.to_json(orient='index')
        df_tail_json  = df_tail.to_json(orient='index')
        project_json = ProjectJsonStorage.objects.filter(project=sheet.project).update(js=res_json,columns=column_dict)
        project_json = ProjectJsonStorage.objects.filter(project=sheet.project).order_by('id')[0]
        c_list = {'columns':result_df_columns}
        #print("the ")

        project_json_metadata = ProjectJsonStorageMetadata.objects.filter(project_json=project_json).update(rows=rows,columns=columns,head_json=df_head_json,tail_json=df_tail_json)
    else:
        subject = "The existing Schema Dosen't Match with Google Sheet Data"
        html_message = render_to_string('api_error_email.html', {'project': meta_data.project,'error':error})

        from_email = 'noreply@brayn.ai'

        to = [meta_data.project.admin_user.email]
        # send_mail(subject, "Please delete the previous integration for the new one to work or contact Qdesk support", from_email, to,fail_silently=False)
        #sending mail to customer with from, to address and html message which includes the password
    update = CustomerAPIDetails.objects.filter(pk=sheet.pk).update(updated=datetime.now())
    return True








def update_sub_df(end_point,p_query):
    #print("called")
    time_now = datetime.now()
    today=time_now.date()
    time_now = utc.localize(time_now)
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
                            # #print("the splited value columns are",value_columns)
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


    # #print("the columns of pivot table are ",res_df.columns.tolist())
    project_meta = ProjectMetaData.objects.get(project=p_query.project)
    if project_meta.date_column_name:
        date_field = project_meta.date_column_name
    else:
        date_field=None

    if date_field:
        if not p_query.where_query and not grouping_colums and not aggregation :
            df = res_df

        elif p_query.where_query and not grouping_colums and not aggregation :
            df = res_df

        elif p_query.where_query  and grouping_colums and not aggregation  :
            #print("no aggregation with grouping")
            df = res_df
        elif p_query.where_query  and grouping_colums and  aggregation and frequency :
            #print("no aggregation with grouping")
            df =  res_df.stack().reset_index()
        elif p_query.where_query  and grouping_colums and  aggregation and not frequency :
            #print("no aggregation with grouping")
            df =  res_df.reset_index()
        elif not p_query.where_query  and not grouping_colums and  not aggregation and frequency :
            #print("no aggregation with grouping")
            df =  res_df
        elif p_query.where_query  and not grouping_colums  and  aggregation and frequency:
            #print("aggregation with grouping")
            pv_df = res_df.transpose()
            df = pv_df.reset_index()
        elif not grouping_colums  and  aggregation and frequency:
            #print("aggregation with grouping")
            pv_df = res_df.transpose()
            df = pv_df.reset_index()
        elif grouping_colums  and  aggregation and frequency:
            #print("aggregation with grouping")
            df = res_df.stack().reset_index()
        elif grouping_colums  and  aggregation and not  frequency:
            #print("aggregation with grouping")
            df = res_df.reset_index()
        elif grouping_colums:
            df = res_df
        elif p_query.where_query:
            df = res_df

        else:
            #print("aggregation")
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


    df_columns= df.columns.to_list()
    metadata = ProjectMetaData.objects.get(project= p_query.project)
    for key, value in metadata.meta_data.items():
        if key in df_columns:
            ###print("key",key)
            if value['dtype'] == 'int':
                df[key] =pd.to_numeric(df[key])
                if key in df_columns:
                    df[key] = pd.to_numeric(df[key])
            elif value['dtype'] == 'float':
                ###print("final key",key,df[key],df[key].dtypes)
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
                ###print("the data key",key)
                if key in df_columns:
                    df[key] = pd.to_datetime(df[key])

    end_point_new_column = EndPointNewColumn.objects.filter(end_point=end_point)
    for ep_c in end_point_new_column:
        df[ep_c.column_name] = df.apply(eval(ep_c.formula),axis=1)
        

    df_rows =df.shape[0]
    if metadata.date_column_name and metadata.date_column_name in df_columns:
        df[metadata.date_column_name] = df[metadata.date_column_name].astype(str)
    result_json = df.to_json(orient='index')
    #print("updating the json sub_df",df_rows)
    update = ProjectEndPoint.objects.filter(pk=end_point.pk).update(sub_df=result_json,updated=datetime.now())
    return True
