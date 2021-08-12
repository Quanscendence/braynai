from __future__ import print_function
from django.shortcuts import render,redirect
from django.views.generic import TemplateView,CreateView,View,UpdateView,ListView
from dataintegration.forms import DriveDetailsForm,SheetDetailsForm,DropboxDetailsForm,OneDriveDetailsForm,ApiDataForm,SheetUrlForm
from dataintegration.models import CustomerAPIDetails
from coreapp.models import Project,ProjectType,ProjectJsonStorage,ApiDataGet,ProjectEndPoint,ProjectDashboard,ProjectMetaData,ProjectJsonStorageMetadata,ProjectUser
from login.models import Profile,Customer
import pickle
import os.path
import numpy as np
from django.db.models import Q
from django.contrib.sites.shortcuts import get_current_site
from django.http import JsonResponse
from django.core.files.storage import default_storage
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from coreapp.choices import INTEGRATION_CHOICES
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
import dropbox
import onedrivesdk
from onedrivesdk.helpers import GetAuthCodeServer
import pandas as pd
from functools import reduce
import analytics
from io import StringIO
from cryptography.fernet import Fernet
import base64
from datetime import datetime, timedelta
from braces.views import GroupRequiredMixin
from .keys import key
import io
from googleapiclient.http import MediaIoBaseDownload
from google_drive_downloader import GoogleDriveDownloader as gdd
from seo_app.models import SiteSeo
import csv
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from django.core.files import File
from engine.cleaner import FillNan,  FileReader, FillNan,ColumnCombine,DeleteColumn
import requests

# Create your views here.


'''Start of class to list out the data integration types'''
class IntegrationListView(ListView):
    def get(self,request,pk):
        template_name='integration_list.html'
        project=Project.objects.get(pk=pk)
        return render(request,template_name,context={'project':project})
'''End of class to list out the data integration types'''

class DriveDetailsView(CreateView):
    def get(self,request,pk):
        template_name='file_details.html'
        seo=SiteSeo.objects.get(choices='Google Drive Integration')
        drive_details_form=DriveDetailsForm()
        context={
            'drive_details_form':drive_details_form,
            'seo':seo
        }
        return render(request,template_name,context)
    def post(self,request,pk):
        template_name='file_details.html'
        seo=SiteSeo.objects.get(choices='Google Drive Integration')
        project = Project.objects.get(pk=pk)
        drive_details_form=DriveDetailsForm(request.POST,request.FILES)
        if drive_details_form.is_valid():
            #print("valid")
            credential=request.FILES["credential"]
            #print("the file entered is ",credential)
            file_id=drive_details_form.cleaned_data["file_id"]
            file_id_encrypted = encrypt(file_id)
            drive_details,created = CustomerAPIDetails.objects.get_or_create(project=project,integration_choice='Google Drive',credentials=credential,file_id=file_id_encrypted)
            #print("created")
            pk=drive_details.pk
            # credential_read = CustomerAPIDetails.objects.get(credentials=drive_details.credentials)
            drive_details.credentials.open('r')
            lines = drive_details.credentials.read()
            drive_details.credentials.close()
            file_lines_encrypted=encrypt(lines)
            #print('file_lines_encrypted',file_lines_encrypted)
            drive_details.credentials.open('w')
            drive_details.credentials.write(file_lines_encrypted)
            drive_details_update = CustomerAPIDetails.objects.filter(pk=pk).update(credentials = drive_details.credentials)
            drive_details.credentials.close()
            updated_credential_data = CustomerAPIDetails.objects.get(pk=pk)
            #print('updated_credential_data.token_file',updated_credential_data.token_file)
            updated_credential_data.credentials.open('r')
            lines = updated_credential_data.credentials.read()
            updated_credential_data.credentials.close()
            file_lines_decrypted=decrypt(lines)
            encrypted_file = open('decrypted_credentials.json','w')
            encrypted_file.write(file_lines_decrypted)
            encrypted_file.close()
            credentials = os.path.abspath("decrypted_credentials.json")
            # If modifying these scopes, delete the file token.pickle.
            SCOPES = ['https://www.googleapis.com/auth/drive.file']

            """Shows basic usage of the Drive v3 API.
                Prints the names and ids of the first 10 files the user has access to.
                """
            creds = None
            # The file token.pickle stores the user's access and refresh tokens, and is
            # created automatically when the authorization flow completes for the first
            # time.
            # if os.path.exists('token.pickle_drive'+request.user.username):
            #     with open('token.pickle_drive'+request.user.username, 'rb') as token:
            #         creds = pickle.load(token)
            #         #print(creds)
            # if updated_credential_data.token_file:
            #     #print("inside token file if condition")
            #     with open('token.pickle_drive'+request.user.username, 'wb') as token:
            #         creds = token.write(updated_credential_data.token_file)
            #         #print(creds)
            # else:
            #     #print("token file not available")
            # If there are no (valid) credentials available, let the user log in.
            if not creds or not creds.valid:
                #print("inside first if")
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    #print("place to enter the credentials file")
                    #print('credentials',credentials)
                    flow = InstalledAppFlow.from_client_secrets_file(
                        credentials, SCOPES)
                    #print(flow)
                    creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open('token.pickle_drive'+request.user.username, 'wb') as token:
                    pickle.dump(creds, token)
                with open('token.pickle_drive'+request.user.username, 'rb') as f:
                    file_content = f.read()
                    #print('file_content',file_content)
                    drive_details_update = CustomerAPIDetails.objects.filter(pk=pk).update(token_file = file_content)


            os.remove('decrypted_credentials.json')
            os.remove('token.pickle_drive'+request.user.username)
            service = build('drive', 'v3', credentials=creds)
            file_id_decrypted = decrypt(file_id_encrypted)
            '''downloading the file using user's credential.json file and file id'''
            gdd.download_file_from_google_drive(file_id=file_id_decrypted,
                                    dest_path='./GoogleDrive_files.csv',
                                    unzip=True)
            #print("downloaded")
            file= pd.read_csv('GoogleDrive_files.csv', encoding = "ISO-8859-1")

            res_df =reduce(lambda left,right: pd.merge(left,right,on=file, how='outer'), [file])
            #print(res_df.columns.to_list())
            res_json = file.to_json(orient='index')
        # #print("project",res_json)

            projectjson, created = ProjectJsonStorage.objects.get_or_create(project=project, js = res_json)
            #print(projectjson)

            os.remove('GoogleDrive_files.csv')

        return redirect('/dashboard/')

class SheetDetailsView(CreateView):
    def get(self,request,pk):
        template_name='sheet_details.html'
        project = Project.objects.get(pk=pk)
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
        if ProjectEndPoint.objects.filter(project=project).exists():
            project_endpoints = ProjectEndPoint.objects.filter(project=project).order_by('name')
        else:
            project_endpoints=None

        customer=Customer.objects.get(user=request.user)
        if ProjectDashboard.objects.filter(Q(project=project) ).exists():
            # #print("project admin")
            dashboard=ProjectDashboard.objects.filter(Q(project=project) ).order_by('-id')
            dashboard_count=ProjectDashboard.objects.filter(Q(project=project) ).count()
        else:
            dashboard = None
            dashboard_count = None
        sheet_details_form=SheetDetailsForm()
        url_sheet_form = SheetUrlForm()
        context={
            'sheet_details_form':sheet_details_form,
            'project':project,
            'dashboard':dashboard,
            'permission':permission,
            'customer':customer,
            'project_endpoints':project_endpoints,
            'url_sheet_form':url_sheet_form
        }
        return render(request,template_name,context)
    def post(self,request,pk):
        template_name='sheet_details.html'
        project = Project.objects.get(pk=pk)
        sheet_details_form=SheetDetailsForm(request.POST,request.FILES)
        url_sheet_form = SheetUrlForm(request.POST,request.FILES)
        if sheet_details_form.is_valid():
            # #print("valid")
            credential=request.FILES["credential"]
            name = request.POST['sheet_name']

            spread_sheet_id=sheet_details_form.cleaned_data["spreadsheet_id"]
            data_range =  sheet_details_form.cleaned_data["data_range"]
            sheet_details,created = CustomerAPIDetails.objects.get_or_create(name=name,project=project,integration_choice='Google Sheets',credentials=credential,file_id=spread_sheet_id,range=data_range)
            try:

                scope=['htps://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
                file = sheet_details.credentials.open()
                file_content = file.read()
                js_str = json.loads(file_content.decode('utf-8'))
                creadentials = ServiceAccountCredentials.from_json_keyfile_dict(js_str)
                gc = gspread.authorize(creadentials)
                wks = gc.open(spread_sheet_id).sheet1

                data = wks.get_all_records()
            except:
                context={
                    'project':project,
                    'sheet_details_form':sheet_details_form,
                    'msg':'Unable to Read The Sheet Please Check The Credentials/ File name'
                }
                return render(request,template_name,context)
            df = pd.DataFrame(data)
            df = df.replace('',np.nan)
            data = self.create_df(df,project,sheet_details,request)
            return JsonResponse(data, safe=False)
        elif url_sheet_form.is_valid():
            url = url_sheet_form.cleaned_data['url']
            name = request.POST['sheet_url_name']
            cron_frequency = request.POST['cron_frequency']
            header =request.POST.get('header',None)
            if header:
                sheet_details,created = CustomerAPIDetails.objects.get_or_create(name= name,project=project,integration_choice='Google Sheets',sheet_url=url ,range=cron_frequency,sheet_header=int(header))
            else:
                sheet_details,created = CustomerAPIDetails.objects.get_or_create(name= name,project=project,integration_choice='Google Sheets',sheet_url=url ,range=cron_frequency)
            try:
                if header:
                    df = pd.read_html(url,encoding='utf8',index_col=0,header=int(header))
                else:
                    df = pd.read_html(url,encoding='utf8',index_col=0,header=1)

            except:
                data={'error':"There is a Error in Reading Sheet"}
                return JsonResponse(data, safe=False)
            df = df[0]
            data = self.create_df(df,project,sheet_details,request)
            return JsonResponse(data, safe=False)

            # #print("the entered file is ",credential)
            # spread_sheet_id=sheet_details_form.cleaned_data["spreadsheet_id"]
            # spread_sheet_id_encrypted = encrypt(spread_sheet_id)
            # sheet_details,created = CustomerAPIDetails.objects.get_or_create(project=project,integration_choice='Google Sheets',credentials=credential,file_id=spread_sheet_id_encrypted)
            # #print("created")
            # sheet_details.credentials.open('r')
            # lines = sheet_details.credentials.read()
            # sheet_details.credentials.close()
            # file_lines_encrypted=encrypt(lines)
            # #print('file_lines_encrypted',file_lines_encrypted)
            # sheet_details.credentials.open('w')
            # sheet_details.credentials.write(file_lines_encrypted)
            # pk= sheet_details.pk
            # sheet_details_update = CustomerAPIDetails.objects.filter(pk=pk).update(credentials = sheet_details.credentials)
            # sheet_details.credentials.close()
            # updated_credential_data = CustomerAPIDetails.objects.get(pk=pk)
            # #print('updated_credential_data.token_file',updated_credential_data.token_file)
            # updated_credential_data.credentials.open('r')
            # lines = updated_credential_data.credentials.read()
            # updated_credential_data.credentials.close()
            # file_lines_decrypted=decrypt(lines)
            # encrypted_file = open('decrypted_credentials.json','w')
            # encrypted_file.write(file_lines_decrypted)
            # encrypted_file.close()
            # credentials = os.path.abspath("decrypted_credentials.json")


            SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

            # The ID and range of a sample spreadsheet.

            SAMPLE_RANGE_NAME = 'Sheet1'


            """Shows basic usage of the Sheets API.
            Prints values from a sample spreadsheet.
            """
            creds = None
            # The file token.pickle stores the user's access and refresh tokens, and is
            # created automatically when the authorization flow completes for the first
            # time.
            if os.path.exists('token.pickle_sheet'+request.user.username):
                with open('token.pickle_sheet'+request.user.username, 'rb') as token:
                    creds = pickle.load(token)
            # If there are no (valid) credentials available, let the user log in.
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        credentials, SCOPES)
                    creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open('token.pickle_sheet'+request.user.username, 'wb') as token:
                    pickle.dump(creds, token)
            os.remove('decrypted_credentials.json')
            service = build('sheets', 'v4', credentials=creds)
            spread_sheet_id_decrypted = decrypt(spread_sheet_id_encrypted)
            # Call the Sheets API
            result = service.spreadsheets().values().get(
            spreadsheetId=spread_sheet_id_decrypted, range=SAMPLE_RANGE_NAME).execute()
            values = result.get('values')
            if not values:
                pass
            else:
                for row in values:
                    str_value=''
                    rows = str_value.join(row)
                    #print(rows)
                    file = open('googlesheets.csv','a')
                    file.write(rows)
                file.close()
                df_file = pd.read_csv('googlesheets.csv', encoding = "ISO-8859-1")
                #print(df_file)
                res_df =reduce(lambda left,right: pd.merge(left,right,on=df_file, how='outer'), [df_file])
                #print(res_df.columns.to_list())
                res_json = df_file.to_json(orient='index')
                projectjson, created = ProjectJsonStorage.objects.get_or_create(project=project, js = res_json)
                #print(projectjson)
                os.remove('token.pickle')
                os.remove('googlesheets.csv')
        return redirect('/dashboard/')

    def create_df(self,df,project,sheet_details,request):
        # #print("the original df ",df)
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '').str.replace('.', '_').str.replace(',','_').str.replace('/','_').str.replace(':','').str.replace(':','')
        new_df_columns = df.columns.tolist()
        #print("new df columns",new_df_columns)
        project_json = ProjectJsonStorage.objects.filter(project=project).order_by('id')[0]
        json_string = json.loads(project_json.js)
        json_df = pd.DataFrame(json_string)
        # #print(type(json_df.head()))

        transposed_df = json_df.transpose()
        rows = transposed_df.shape[0]

        metadata = ProjectMetaData. objects.get(project=project)
        columns = metadata.columns['columns']


        transposed_df_columns = transposed_df.columns.tolist()

        column_list = [x for x in transposed_df_columns if x in new_df_columns]



        new_columns = [x  for x in new_df_columns if x not in columns ]

        for key, value in metadata.meta_data.items():
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
        # #print("the dtypes ",transposed_df.dtypes,df.dtypes)
        if len(column_list)>0:
            result_df = reduce(lambda left,right: pd.merge(left,right,on=column_list, how='outer'), [transposed_df,df])
        else:
            try:
                result_df = reduce(lambda left,right: pd.merge(left,right,left_on= transposed_df_columns[0],right_on=new_df_columns[0],how='outer'), [transposed_df,df])
            except:
                result_df = reduce(lambda left,right: pd.merge(left,right,left_index=True,right_index=True,how='outer'), [transposed_df,df])
        # #print("the df is ",result_df) erge the mother df with new rows ofss data
        result_columns = result_df.columns.tolist()
        # result_df = result_df.fillna(0)
        for colum in result_columns:
            try:
                result_df[column] = result_df[column].astype(float)
            except:
                pass
        #print("the result df ",result_df.head(70))
        result_df_rows = result_df.shape[0]
        df_rows = df.shape[0]
        #if there are  new columns
        # if len(new_columns)>0:
        #     result_df_rows = result_df.shape[0]
        #     df_rows = df.shape[0]
        #     #print("the aded df, and result_df rows",df_rows,result_df_rows)

        #     if result_df_rows == df_rows:
        #         for column in new_columns:
        #             #print("column is",column)
        #             result_df[column] = df[column]
        #             #print("the result df is ",result_df)
        # else:
        #     pass

        result_df.columns = result_df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '').str.replace('.', '_').str.replace(',','_').str.replace('/','_').str.replace(':','').str.replace(':','')
        #print("the final data frame",result_df)
        result_df_columns = result_df.columns.tolist()
        delete_column_list = []
        custom_column_list = {}
        today = datetime.now()
        metadata = ProjectMetaData. objects.get(project=project)

        #print("the shappe before duplicate",result_df.shape[0],transposed_df.shape[0],df.shape[0])

        result_df.drop_duplicates(subset = transposed_df_columns, inplace = True)

        # result_df.fillna(0,inplace=True)
        #print("the shappe aftrer duplicate",result_df.tail(50),result_df.shape[0],transposed_df.shape[0],df.shape[0])

        if len(new_columns)>0:
            column_conbine_obj = ColumnCombine()
            dfs=[result_df]
            data = column_conbine_obj.list_combine_with_datatype_integration(dfs,new_columns)
            try:
                error = data['Error']
                data = {'error_msg':all_columns['error']}
                # #print("error",data)
                return JsonResponse(data,safe=False)
            except:
                data = column_conbine_obj.list_combine_with_datatype_integration(dfs,new_columns)
                data['sheet_pk']=sheet_details.pk
                #print("the data for metadata collection is",data)
                return data


        result_df = result_df.replace('',np.nan)
        fillna_obj = FillNan(result_df)
        for key, value in metadata.meta_data.items():

            if key in result_df_columns:
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

        meta_data_obj = metadata.meta_data
        today = str(datetime.now())
        delete_column_list = []
        custom_column_list = {}


        for c in new_columns:
            column = {}
            ##print("the dataframe",c)
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
                ##print("type of date",type(today))
                column['start_date']= today
                column['end_date']= ''
                fillna_obj.fillnan_with_0(c)
                ##print("nan filled df 0  ",c)
            elif missing_data and missing_data == 'None':
                column['handle_missing_data']= 'None'
                fillna_obj.fillnan_with_None_value(c)
                ##print("nan filled df None  ",c)
                today = str(datetime.now().date())
                ##print("type of date",type(today))
                column['start_date']= today
                column['end_date']= ''
                column['column_deleted'] = False
            elif missing_data and missing_data == 'previous':
                column['handle_missing_data']= 'previous'
                result_df = fillna_obj.fillnan_with_previous_value(c)
                ##print("nan filled df ",result_df)
                today = str(datetime.now().date())
                ##print("type of date",type(today))
                column['start_date']= today
                column['end_date']= ''
                column['column_deleted'] = False
            elif missing_data and missing_data == 'drop':
                column['handle_missing_data']= 'drop'
                l = [c]
                fillna_obj.drop_row(l)
                ##print("nan filled df ",result_df)
                today = str(datetime.now().date())
                ##print("type of date",type(today))
                column['start_date']= today
                column['end_date']= ''
                column['column_deleted'] = False
            elif missing_data and missing_data == 'delete_column':
                column['handle_missing_data']= missing_data
                today = str(datetime.now().date())
                ##print("type of date",type(today))
                column['start_date']= today
                column['end_date']= today
                column['column_deleted'] = True

                co = c.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('.', '_').replace(',','_').replace('/','_').replace(':','')
                delete_column_list.append(co)
                #print("the columns are ",delete_column_list)
            elif missing_data_input:
                column['handle_missing_data']= missing_data_input
                today = str(datetime.now().date())
                ##print("type of date",type(today))
                column['start_date']= today
                column['end_date']= ''
                column['column_deleted'] = False
                custom_column_list[c]=missing_data_input

            c_name = c.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('.', '_').replace(',','_').replace('/','_').replace(':','')
            meta_data_obj[c_name]=column
        #print("the custom value is ",custom_column_list)
        if len(custom_column_list)>0:
            result_df = result_df.fillna(value=custom_column_list)
        #print("the result after nan fill",result_df,delete_column_list)

        if len(delete_column_list)>0:

            #print("the value ",delete_column_list)
            column_delete_obj = DeleteColumn(result_df)
            result_df = column_delete_obj.delete_column(delete_column_list)
            #print("columns ",result_df.columns.tolist())

            
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
        #print("the ")
        update = ProjectMetaData.objects.filter(project=project).update(meta_data=meta_data_obj,columns=c_list)
        project_json_metadata = ProjectJsonStorageMetadata.objects.filter(project_json=project_json).update(rows=rows,columns=columns,head_json=df_head_json,tail_json=df_tail_json)
        pk = str(project.pk)
        data = {'pk':pk}
        return data


''' sheetsNan filling '''
class SheetNnaFillView(CreateView):
    def get(self,request,pk):
        template_name='sheet_details.html'
        sheet_details_form=SheetDetailsForm()
        context={
            'sheet_details_form':sheet_details_form
        }
        return render(request,template_name,context)
    def post(self,request,pk):
        template_name='sheet_details.html'
        project = Project.objects.get(pk=pk)
        sheet_details_form=SheetDetailsForm(request.POST,request.FILES)
        url_sheet_form = SheetUrlForm(request.POST,request.FILES)
        if sheet_details_form.is_valid():
            # #print("valid")
            credential=request.FILES["credential"]

            spread_sheet_id=sheet_details_form.cleaned_data["spreadsheet_id"]
            data_range =  sheet_details_form.cleaned_data["data_range"]
            sheet_pk = request.POST.get('sheet_pk',None)
            sheet_details= CustomerAPIDetails.objects.get(pk=int(sheet_pk))
            try:

                scope=['htps://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
                file = sheet_details.credentials.open()
                file_content = file.read()
                js_str = json.loads(file_content.decode('utf-8'))
                creadentials = ServiceAccountCredentials.from_json_keyfile_dict(js_str)
                gc = gspread.authorize(creadentials)
                wks = gc.open(spread_sheet_id).sheet1

                data = wks.get_all_records()
            except:
                context={
                    'sheet_details_form':sheet_details_form,
                    'msg':'Unable to Read The Sheet Please Check The Credentials/ File name'
                }
                return render(request,template_name,context)

            df = pd.DataFrame(data)
            df = df.replace('',np.nan)
            data = self.update_df(df,project,sheet_details,request)
            return JsonResponse(data, safe=False)
        elif url_sheet_form.is_valid():
            url = url_sheet_form.cleaned_data['url']
            name = request.POST['sheet_url_name']
            cron_frequency = request.POST['cron_frequency']
            header =request.POST.get('header',None)

            sheet_pk = request.POST.get('sheet_pk',None)
            sheet_details= CustomerAPIDetails.objects.get(pk=int(sheet_pk))
            if header:
                df = pd.read_html(url,encoding='utf8',index_col=0,header=int(header))
            else:
                df = pd.read_html(url,encoding='utf8',index_col=0,header=1)
            df=df[0]
            data = self.update_df(df,project,sheet_details,request)
            return JsonResponse(data, safe=False)
            # #print("the original df ",df)
            

            # #print("the entered file is ",credential)
            # spread_sheet_id=sheet_details_form.cleaned_data["spreadsheet_id"]
            # spread_sheet_id_encrypted = encrypt(spread_sheet_id)
            # sheet_details,created = CustomerAPIDetails.objects.get_or_create(project=project,integration_choice='Google Sheets',credentials=credential,file_id=spread_sheet_id_encrypted)
            # #print("created")
            # sheet_details.credentials.open('r')
            # lines = sheet_details.credentials.read()
            # sheet_details.credentials.close()
            # file_lines_encrypted=encrypt(lines)
            # #print('file_lines_encrypted',file_lines_encrypted)
            # sheet_details.credentials.open('w')
            # sheet_details.credentials.write(file_lines_encrypted)
            # pk= sheet_details.pk
            # sheet_details_update = CustomerAPIDetails.objects.filter(pk=pk).update(credentials = sheet_details.credentials)
            # sheet_details.credentials.close()
            # updated_credential_data = CustomerAPIDetails.objects.get(pk=pk)
            # #print('updated_credential_data.token_file',updated_credential_data.token_file)
            # updated_credential_data.credentials.open('r')
            # lines = updated_credential_data.credentials.read()
            # updated_credential_data.credentials.close()
            # file_lines_decrypted=decrypt(lines)
            # encrypted_file = open('decrypted_credentials.json','w')
            # encrypted_file.write(file_lines_decrypted)
            # encrypted_file.close()
            # credentials = os.path.abspath("decrypted_credentials.json")


            SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

            # The ID and range of a sample spreadsheet.

            SAMPLE_RANGE_NAME = 'Sheet1'


            """Shows basic usage of the Sheets API.
            Prints values from a sample spreadsheet.
            """
            creds = None
            # The file token.pickle stores the user's access and refresh tokens, and is
            # created automatically when the authorization flow completes for the first
            # time.
            if os.path.exists('token.pickle_sheet'+request.user.username):
                with open('token.pickle_sheet'+request.user.username, 'rb') as token:
                    creds = pickle.load(token)
            # If there are no (valid) credentials available, let the user log in.
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        credentials, SCOPES)
                    creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open('token.pickle_sheet'+request.user.username, 'wb') as token:
                    pickle.dump(creds, token)
            os.remove('decrypted_credentials.json')
            service = build('sheets', 'v4', credentials=creds)
            spread_sheet_id_decrypted = decrypt(spread_sheet_id_encrypted)
            # Call the Sheets API
            result = service.spreadsheets().values().get(
            spreadsheetId=spread_sheet_id_decrypted, range=SAMPLE_RANGE_NAME).execute()
            values = result.get('values')
            if not values:
                pass
            else:
                for row in values:
                    str_value=''
                    rows = str_value.join(row)
                    #print(rows)
                    file = open('googlesheets.csv','a')
                    file.write(rows)
                file.close()
                df_file = pd.read_csv('googlesheets.csv', encoding = "ISO-8859-1")
                #print(df_file)
                res_df =reduce(lambda left,right: pd.merge(left,right,on=df_file, how='outer'), [df_file])
                #print(res_df.columns.to_list())
                res_json = df_file.to_json(orient='index')
                projectjson, created = ProjectJsonStorage.objects.get_or_create(project=project, js = res_json)
                #print(projectjson)
                os.remove('token.pickle')
                os.remove('googlesheets.csv')
        return redirect('/dashboard/')
    def update_df(self,df,project,sheet_details,request):
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '').str.replace('.', '_').str.replace(',','_').str.replace('/','_').str.replace(':','').str.replace(':','')
        new_df_columns = df.columns.tolist()
        #print("new df columns",new_df_columns)
        project_json = ProjectJsonStorage.objects.filter(project=project).order_by('id')[0]
        json_string = json.loads(project_json.js)
        json_df = pd.DataFrame(json_string)
        # #print(type(json_df.head()))

        transposed_df = json_df.transpose()
        rows = transposed_df.shape[0]

        metadata = ProjectMetaData. objects.get(project=project)
        columns = metadata.columns['columns']


        transposed_df_columns = transposed_df.columns.tolist()

        column_list = [x for x in transposed_df_columns if x in new_df_columns]

        new_columns = [x  for x in new_df_columns if x not in columns ]
        #print("new columns are",new_columns)

        for key, value in metadata.meta_data.items():
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

        if len(column_list)>0:
            result_df = reduce(lambda left,right: pd.merge(left,right,on=column_list, how='outer'), [transposed_df,df])
        else:
            try:
                result_df = reduce(lambda left,right: pd.merge(left,right,left_on= transposed_df_columns[0],right_on=new_df_columns[0],how='outer'), [transposed_df,df])
            except:
                result_df = reduce(lambda left,right: pd.merge(left,right,left_index=True,right_index=True,how='outer'), [transposed_df,df])
    
        #print("the result df ",result_df.head(70))
        result_df_rows = result_df.shape[0]
        df_rows = df.shape[0]


        result_df.columns = result_df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '').str.replace('.', '_').str.replace(',','_').str.replace('/','_').str.replace(':','').str.replace(':','')
        # #print("the final data frame",result_df)
        result_df_columns = result_df.columns.tolist()
        delete_column_list = []
        custom_column_list = {}
        today = datetime.now()
        metadata = ProjectMetaData. objects.get(project=project)

        # #print("the shappe before duplicate",result_df.shape[0],transposed_df.shape[0],df.shape[0])

        result_df.drop_duplicates(subset = transposed_df_columns, inplace = True)



        fillna_obj = FillNan(result_df)
        for key, value in metadata.meta_data.items():

            if key in result_df_columns:
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
                    

        if len(custom_column_list)>0:
            result_df.fillna(custom_column_list)


        if len(delete_column_list)>0:

            #print("the value ",delete_column_list)
            column_delete_obj = DeleteColumn(result_df)
            result_df = column_delete_obj.delete_column(delete_column_list)
            #print("columns ",result_df.columns.tolist())

        meta_data_obj = metadata.meta_data
        today = str(datetime.now())
        delete_column_list = []



        for c in new_columns:
            column = {}
            custom_column_list = {}
            ##print("the dataframe",c)
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
                ##print("type of date",type(today))
                column['start_date']= today
                column['end_date']= ''
                fillna_obj.fillnan_with_0(c)
                ##print("nan filled df 0  ",c)
            elif missing_data and missing_data == 'None':
                column['handle_missing_data']= 'None'
                fillna_obj.fillnan_with_None_value(c)
                ##print("nan filled df None  ",c)
                today = str(datetime.now().date())
                ##print("type of date",type(today))
                column['start_date']= today
                column['end_date']= ''
                column['column_deleted'] = False
            elif missing_data and missing_data == 'previous':
                column['handle_missing_data']= 'previous'
                result_df = fillna_obj.fillnan_with_previous_value(c)
                ##print("nan filled df ",result_df)
                today = str(datetime.now().date())
                ##print("type of date",type(today))
                column['start_date']= today
                column['end_date']= ''
                column['column_deleted'] = False
            elif missing_data and missing_data == 'drop':
                column['handle_missing_data']= 'drop'
                l = [c]
                fillna_obj.drop_row(l)
                ##print("nan filled df ",result_df)
                today = str(datetime.now().date())
                ##print("type of date",type(today))
                column['start_date']= today
                column['end_date']= ''
                column['column_deleted'] = False
            elif missing_data and missing_data == 'delete_column':
                column['handle_missing_data']= missing_data
                today = str(datetime.now().date())
                ##print("type of date",type(today))
                column['start_date']= today
                column['end_date']= today
                column['column_deleted'] = True

                co = c.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('.', '_').replace(',','_').replace('/','_').replace(':','')
                delete_column_list.append(co)
                #print("the columns are ",delete_column_list)
            elif missing_data_input:
                column['handle_missing_data']= missing_data_input
                today = str(datetime.now().date())
                ##print("type of date",type(today))
                column['start_date']= today
                column['end_date']= ''
                column['column_deleted'] = False
                co = c.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('.', '_').replace(',','_').replace('/','_').replace(':','')
                try:
                    custom_column_list[co]=int(missing_data_input)
                except:
                    custom_column_list[co]=missing_data_input
                result_df = result_df.fillna(custom_column_list)
                #print("in for ",result_df[co])



            c_name = c.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('.', '_').replace(',','_').replace('/','_').replace(':','')
            meta_data_obj[c_name]=column
            #print("meta_data_obj[c_name]",meta_data_obj[c_name])
        #print("custom columns list",custom_column_list)
        if len(custom_column_list)>0:
            result_df = result_df.fillna(custom_column_list)
        # #print("the result after nan fill",result_df,delete_column_list)

        if len(delete_column_list)>0:

            ###print("the value ",delete_column_list)
            column_delete_obj = DeleteColumn(result_df)
            result_df = column_delete_obj.delete_column(delete_column_list)



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
        #print("the ")
        update = ProjectMetaData.objects.filter(project=project).update(meta_data=meta_data_obj,columns=c_list)
        project_json_metadata = ProjectJsonStorageMetadata.objects.filter(project_json=project_json).update(rows=rows,columns=columns,head_json=df_head_json,tail_json=df_tail_json)
        pk = str(project.pk)
        data = {'pk':pk}
        return data

'''Start of class to receive dropbox details'''
class DropBoxDetailsView(CreateView):
    def get(self,request,pk):
        template_name='dropbox_details.html'
        #print('pk',pk)
        seo=SiteSeo.objects.get(choices='DropBox Integration')
        project = Project.objects.get(pk=pk)
        projects_delete = Project.objects.filter(Q(admin_user=user) and  Q(delete_datetime__isnull=False) ).count()
        #print("project count ",projects_delete)
        if  projects_delete > 0:
            projects_delete = True
        else:
            projects_delete = False
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
        if ProjectEndPoint.objects.filter(project=project).exists():
            project_endpoints = ProjectEndPoint.objects.filter(project=project).order_by('name')
        else:
            project_endpoints=None

        customer=Customer.objects.get(user=request.user)
        if ProjectDashboard.objects.filter(Q(project=project) ).exists():
            # #print("project admin")
            dashboard=ProjectDashboard.objects.filter(Q(project=project) ).order_by('-id')
            dashboard_count=ProjectDashboard.objects.filter(Q(project=project) ).count()
        else:
            dashboard = None
            dashboard_count = None
        dropbox_details_form=DropboxDetailsForm()
        context={
            'dropbox_details_form':dropbox_details_form,
            'seo':seo,
            'project':project,
            'dashboard':dashboard,
            'permission':permission,
            'customer':customer,
            'project_endpoints':project_endpoints,
            'projects_delete':projects_delete,
        }
        return render(request,template_name,context)
    def post(self,request,pk):
        template_name='dropbox_details.html'
        project=Project.objects.get(pk=pk)
        #print(project)
        seo=SiteSeo.objects.get(choices='DropBox Integration')
        dropbox_details_form=DropboxDetailsForm(request.POST,request.FILES)
        if dropbox_details_form.is_valid():
            #print("valid")
            access_token = dropbox_details_form.cleaned_data["access_token"]
            access_token_encrypted=encrypt(access_token)
            #print('access_token_encrypted',access_token_encrypted)
            path_name = dropbox_details_form.cleaned_data["path_name"]
            data_range=dropbox_details_form.cleaned_data["data_range"]
            #print("path_name",path_name)
            dropbox_details, created = CustomerAPIDetails.objects.get_or_create(project=project,access_token=access_token_encrypted,integration_choice='DropBox',file_id=path_name,range=data_range)
            #print(dropbox_details)
            access_token=dropbox_details.access_token
            access_token_decrypted=decrypt(access_token)
            #print('access_token_decrypted',access_token_decrypted)
            path_name=dropbox_details.file_id
            splitted_name=path_name.split('.')
            dbx = dropbox.Dropbox(access_token_decrypted)
            if splitted_name[1] == 'csv':
                file_name = 'drop_box'+str(project.pk)+str(request.user.pk)+'.csv'
                file_exists = default_storage.exists(file_name)
                if file_exists:
                    default_storage.delete(file_name)
                file_id = default_storage.open(file_name,'wb')
                metadata, res = dbx.files_download(path_name)
                file_id.write(res.content)
                file_id.close()
                path = default_storage.path(file_name)

                file= pd.read_csv(path , encoding = "ISO-8859-1")
            elif splitted_name[1] == 'xls':
                file_name = 'drop_box'+str(project.pk)+str(request.user.pk)+'.xls'
                file_exists = default_storage.exists(file_name)
                if file_exists:
                    default_storage.delete(file_name)
                file_id = default_storage.open(file_name,'wb')
                metadata, res = dbx.files_download(path_name)
                file_id.write(res.content)
                file_id.close()
                path = default_storage.path(file_name)
                file = pd.read_excel(path, encoding='utf-8')
            elif splitted_name[1] == 'xlsx':
                file_name = 'drop_box'+str(project.pk)+str(request.user.pk)+'.xls'
                file_exists = default_storage.exists(file_name)
                if file_exists:
                    default_storage.delete(file_name)
                file_id = default_storage.open(file_name,'wb')
                metadata, res = dbx.files_download(path_name)
                file_id.write(res.content)
                #print("the contetnt of the file",res.content)
                file_id.close()
                file_id = default_storage.open(file_name,'rb')
                file_content = file_id.read()
                s=str(file_content)

                data = StringIO(s)
                file = pd.read_csv(data, encoding='utf-8')
            # res_df =reduce(lambda left,right: pd.merge(left,right,on=file, how='outer'), [file])
            # # #print("the result",res_df)
            # #print(res_df.columns.to_list())
            # res_json = file.to_json(orient='index')
            # #print("project",res_json)

            # projectjson, created = ProjectJsonStorage.objects.get_or_create(project=project, js = res_json)
            # #print(projectjson)
            # if splitted_name[1] == 'csv':
            #     os.remove('googlesheets.csv')
            # elif splitted_name[1] == 'xls':
            #     os.remove('googlesheets.xls')
            # elif splitted_name[1] == 'xlsx':
            #     os.remove('googlesheets.xlsx')
            # return redirect('/dashboard/')
        else:
            context={
                'dropbox_details_form':dropbox_details_form,
                'seo':seo
            }
            return render(request,template_name,context)

'''Start of class to receive dropbox details'''
class OneDriveDetailsView(CreateView):
    def get(self,request,pk):
        template_name='onedrive_details.html'
        onedrive_details_form=OneDriveDetailsForm()
        context={
            'onedrive_details_form':onedrive_details_form
        }
        return render(request,template_name,context)
    def post(self,request,pk):
        template_name='onedrive_details.html'
        project=Project.objects.get(pk=pk)
        #print(project)
        onedrive_details_form=OneDriveDetailsForm(request.POST,request.FILES)
        if onedrive_details_form.is_valid():
            #print("valid")
            client_id = onedrive_details_form.cleaned_data["client_id"]
            client_secret_key = onedrive_details_form.cleaned_data["client_secret_key"]
            onedrive_details, created = CustomerAPIDetails.objects.get_or_create(project=project,client_id=client_id,integration_choice='OneDrive',client_secret_key=client_secret_key)
            #print(onedrive_details)
            secret_key=onedrive_details.client_secret_key
            client_id=onedrive_details.client_id
            #print(client_id)
            redirect_uri = 'http://localhost:8080/'
            client_secret = secret_key

            api_base_url='https://api.onedrive.com/v1.0/'
            scopes=['onedrive.readwrite']

            http_provider = onedrivesdk.HttpProvider()
            auth_provider = onedrivesdk.AuthProvider(
            http_provider=http_provider,
            client_id=client_id,
            scopes=scopes)

            client = onedrivesdk.OneDriveClient(api_base_url, auth_provider, http_provider)
            auth_url = client.auth_provider.get_auth_url(redirect_uri)
            # Ask for the code
            #print('Paste this URL into your browser, approve the app\'s access.')
            #print('Copy everything in the address bar after "code=", and paste it below.')
            #print(auth_url)
            code = raw_input('Paste code here: ')
            #print(client)
            return redirect('/dashboard/')

class SegmentDetailsView(CreateView):
    def get(self,request):
        template_name='segment_details.html'
        user=request.user
        analytics.identify(user.username, {
        'email': user.email,
        'name': user.first_name,

                })
        analytics.track(user.username, 'Signed Up', {

            })
        context={
            'analytics':analytics
        }

        return render(request,template_name,context)
# class SegmentReceive(View):
#     def post(self,request):
#         template_name='segment_details.html'
#         #print('segment_receive')
#         if request.method == 'POST':
#             received_json_data=json.loads(request.POST['data'])
#             #print(received_json_data)
#             context={
#              'received_json_data':received_json_data
#             }
#             return render(request,template_name,context)


def encrypt(txt):
    try:# convert integer etc to string first
        txt = str(txt)
        # get the key from settings
        cipher_suite = Fernet(key) # key should be byte
        # #input should be byte, so convert the text to byte
        encrypted_text = cipher_suite.encrypt(txt.encode('ascii'))
        # encode to urlsafe base64 format
        encrypted_text = base64.urlsafe_b64encode(encrypted_text).decode("ascii")
        return encrypted_text
    except:
        pass

def decrypt(txt):
    #print('key',key)
        # base64 decode
    txt = base64.urlsafe_b64decode(txt)
    cipher_suite = Fernet(key)
    decoded_text = cipher_suite.decrypt(txt).decode("ascii")
    return decoded_text


def update_filename(instance, filename):
    format = str(instance.project.admin_user ) + "_" + instance.project.name
    return format



class ApiDataRead(GroupRequiredMixin,View):
    login_url = '/customer/login/'
    redirect_field_name = 'redirect_to'
    template_name='dashboard/index.html'

    def dispatch(self, request, *args, **kwargs):
        pk = kwargs['pk']
        project = Project.objects.get(pk=pk)
        pk= str(project.pk)
        self.login_url = '/customer/login/'
        self.redirect_field_name = 'redirect_to'
        self.template_name='dashboard/index.html'
        admin_name = pk+"_Admin"
        #print(type(admin_name), admin_name)
        admin_encode_name = admin_name.encode()
        admin_unicode_name = admin_encode_name.decode('utf-8')
        write_name = pk+"_Write"
        #print(type(write_name), write_name)
        write_encode_name = write_name.encode()
        write_unicode_name = write_encode_name.decode('utf-8')
        read_name = pk+"_Read"
        #print(type(write_name), write_name)
        read_encode_name = read_name.encode()
        read_unicode_name = read_encode_name.decode('utf-8')
        delete_name = pk+"_Delete"
        delete_encode_name = delete_name.encode()
        delete_unicode_name = delete_encode_name.decode('utf-8')
        l= []
        self.group_required= admin_unicode_name
        #print("the self of dispatcher",self.group_required)

        return super(ApiDataRead, self).dispatch(request, *args, **kwargs)

    def get(self,request,pk):
        #print("get of api data")
        template_name = 'api_data.html'

        project = Project.objects.get(pk=pk)
        permission = identify_user_permission(project,request.user)
        if ApiDataGet.objects.filter(project=project):
            api_data = ApiDataGet.objects.get(project=project)
            form = ApiDataForm(initial={'api':api_data.api,'basic_token':api_data.basic_key,'frequency':api_data.frequency})
        else:
            form = ApiDataForm()
        customer = Customer.objects.get(user=request.user)

        if ProjectDashboard.objects.filter(project=project ).exists():
            # #print("project admin")
            dashboard=ProjectDashboard.objects.filter(project=project ).order_by('-id')
            dashboard_count=ProjectDashboard.objects.filter(project=project) .count()
        else:
            dashboard= None
            dashboard_count= None
        if ProjectEndPoint.objects.filter(project=project).exists():
            project_endpoints = ProjectEndPoint.objects.filter(project=project).order_by('name')
        else:
            project_endpoints=None
        #print("get of api-data")
        return render(request,template_name,{'permission':permission,'customer':customer,'form':form,'dashboard':dashboard,'dashboard_count':dashboard_count,'project_endpoints':project_endpoints,'project':project})

    def post(self,request,pk):
        project= Project.objects.get(pk=pk)
        form = ApiDataForm(request.POST)
        if form.is_valid():

            api = form.cleaned_data['api']
            basic_token = form.cleaned_data['basic_token']
            frequency  = form.cleaned_data['frequency']
            name = request.POST['api_name']
            api_data, created = CustomerAPIDetails.objects.get_or_create(name=name,project=project,api=api,token=basic_token,range=frequency,integration_choice='API')
            if api_data.token:


                headers =  {'content-type' : 'application/json',
                                            'Authorization':api_data.token}

                JSONContent  = requests.get(api_data.api,

                                    headers=headers, verify=True)
            else:
                #print("the api",api)
                headers =  {'content-type' : 'application/json',
                                       }

                JSONContent  = requests.get(api_data.api,
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
                new_df_columns = df.columns.tolist()

                project_json = ProjectJsonStorage.objects.filter(project=project).order_by('id')[0]
                json_string = json.loads(project_json.js)
                json_df = pd.DataFrame(json_string)
                # #print(type(json_df.head()))

                transposed_df = json_df.transpose()
                rows = transposed_df.shape[0]

                metadata = ProjectMetaData. objects.get(project=project)
                columns = metadata.columns['columns']


                transposed_df_columns = transposed_df.columns.tolist()
                y_df = pd.DataFrame()
                # separate the mother df columns df into y_df

                try:
                    for column in columns:
                        y_df[column] = df[column]
                    # #print("the columns are",columns,new_df_columns)
                
                    
                    
                except:
                    pass
                new_columns = [x  for x in new_df_columns if x not in columns ]
                column_list = [x for x in transposed_df_columns if x in new_df_columns]
                if len(column_list)>0:
                    result_df = reduce(lambda left,right: pd.merge(left,right,on=column_list, how='outer'), [transposed_df,df])
                else:
                    try:
                        result_df = reduce(lambda left,right: pd.merge(left,right,left_on= transposed_df_columns[0],right_on=new_df_columns[0],how='outer'), [transposed_df,df])
                    except:
                        result_df = reduce(lambda left,right: pd.merge(left,right,left_index=True,right_index=True,how='outer'), [transposed_df,df])
                
                # #print("the df is ",result_df)
                result_df_rows = result_df.shape[0]
                df_rows = df.shape[0]
                #if there are  new columns

                if len(new_columns)>0:
                    column_conbine_obj = ColumnCombine()
                    dfs=[result_df]
                    data = column_conbine_obj.list_combine_with_datatype_integration(dfs,new_columns)
                    try:
                        error = data['Error']
                        data = {'error_msg':all_columns['error']}
                        # #print("error",data)
                        return JsonResponse(data,safe=False)
                    except:
                        data = column_conbine_obj.list_combine_with_datatype_integration(dfs,new_columns)
                        data['api_pk']=api_data.pk
                        #print("the data for metadata collection is",data)
                        return JsonResponse(data,safe=False)


                else:
                    pass
                result_df.columns = result_df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '').str.replace('.', '_').str.replace(',','_').str.replace('/','_').str.replace(':','').str.replace(':','')

                result_df_columns = result_df.columns.tolist()
                fillna_obj = FillNan(result_df)
                delete_column_list = []
                custom_column_list = {}
                today = datetime.now()
                metadata = ProjectMetaData. objects.get(project=project)
                meta_data_obj = metadata.meta_data



                for key, value in metadata.meta_data.items():

                    if key in result_df_columns:
                        #print("key present in metadata ",key)
                        if result_df.dtypes[key] == np.int64:
                            dtype  = 'int'
                        elif result_df.dtypes[key] == np.float64:
                            dtype = 'float'
                        elif result_df.dtypes[key] == np.object:
                            dtype = 'object'
                        if value['dtype'] == dtype:
                            if value['handle_missing_data']== 'drop':
                                l = [key]
                                result_df[l].dropna(subset=l)
                                # result_df = fillna_obj.drop_row(l)
                            elif value['handle_missing_data'] == 0:
                                result_df[column].fillna(0, inplace=True)
                                # result_df = fillna_obj.fillnan_with_0(key)
                                #print("after filling nan",result_df)
                            elif value['handle_missing_data'] == 'None':

                                # result_df = fillna_obj.fillnan_with_None_value(key)
                                result_df[key].fillna('None', inplace=True)
                                #print("after filling nan",result_df)

                            elif value['handle_missing_data'] == 'previous':
                                result_df[column].fillna(method='ffill', inplace=True)
                                # result_df = fillna_obj.fillnan_with_previous_value(key)
                                #print("after filling nan",result_df)



                            elif value['handle_missing_data'] == 'delete_column':
                                delete_column_list.append(key)
                            else:
                                try:

                                    custom_column_list[key]=int(value['handle_missing_data'])
                                except:
                                    custom_column_list[key]=value['handle_missing_data']
                        else:
                            if value['handle_missing_data']== 'drop':
                                l = [key]
                                result_df[l].dropna(subset=l)
                                # result_df = fillna_obj.drop_row(l)
                            elif value['handle_missing_data'] == 0:
                                result_df[column].fillna(0, inplace=True)
                                # result_df = fillna_obj.fillnan_with_0(key)
                                #print("after filling nan",result_df)
                            elif value['handle_missing_data'] == 'None':

                                # result_df = fillna_obj.fillnan_with_None_value(key)
                                result_df[key].fillna('None', inplace=True)
                                #print("after filling nan",result_df)

                            elif value['handle_missing_data'] == 'previous':
                                result_df[key].fillna(method='ffill', inplace=True)
                                # result_df = fillna_obj.fillnan_with_previous_value(key)
                                #print("after filling nan",result_df)



                            elif value['handle_missing_data'] == 'delete_column':
                                delete_column_list.append(key)
                            else:
                                try:

                                    custom_column_list[key]=int(value['handle_missing_data'])
                                except:
                                    custom_column_list[key]=value['handle_missing_data']

                #print("the final new_columns",new_columns)
                for c in new_columns:
                    d= {}
                    if result_df.dtypes[c] == np.int64:

                        d['dtype'] = 'int'

                    elif result_df.dtypes[c] == np.float64:

                        d['dtype'] = 'float'
                    elif result_df.dtypes[c] == np.object:

                        d['dtype'] = 'object'

                    elif df.dtypes[c] == np.bool:
                        d['dtype']= 'bool'
                    elif np.issubdtype(result_df[c].dtype, np.datetime64):
                        d['dtype'] = "DateTime"
                        df[c] = df[c].astype('str')



                    missing_data = None
                    missing_data_input=None
                    try:
                        # reading mising data handling
                        ###print("the request post is",request.POST)
                        cu =  c+'_select'
                        missing_data = request.POST[cu]
                    except:
                        pass
                    try:
                        # reading mising data handling
                        ###print("the request post is",request.POST)
                        cu =  c+'_input'
                        missing_data_input = request.POST[cu]
                    except:
                        pass
                    if missing_data and missing_data == 'zero':
                        d['handle_missing_data']= 0
                        today = str(datetime.now().date())
                        ####print("type of date",type(today))
                        d['start_date']= today
                        d['end_date']= ''
                        result_df = fillna_obj.fillnan_with_0(c)
                        #int("nan filled df 0  ",c)
                    elif missing_data and missing_data == 'None':
                        d['handle_missing_data']= 'None'
                        result_df = fillna_obj.fillnan_with_None_value(c)
                        ####print("nan filled df None  ",c)
                        today = str(datetime.now().date())
                        ####print("type of date",type(today))
                        d['start_date']= today
                        d['end_date']= ''
                        d['column_deleted'] = False
                    elif missing_data and missing_data == 'previous':
                        d['handle_missing_data']= 'previous'
                        result_df = fillna_obj.fillnan_with_previous_value(c)
                        ####print("nan filled df ",result_df)
                        today = str(datetime.now().date())
                        ####print("type of date",type(today))
                        d['start_date']= today
                        d['end_date']= ''
                        d['column_deleted'] = False
                    elif missing_data and missing_data == 'drop':
                        d['handle_missing_data']= 'drop'
                        l = [c]
                        result_df = fillna_obj.drop_row(l)
                        ####print("nan filled df ",result_df)
                        today = str(datetime.now().date())
                        ####print("type of date",type(today))
                        d['start_date']= today
                        d['end_date']= ''
                        d['column_deleted'] = False
                    elif missing_data and missing_data == 'delete_column':
                        d['handle_missing_data']= missing_data
                        today = str(datetime.now().date())
                        ####print("type of date",type(today))
                        d['start_date']= today
                        d['end_date']= today
                        d['column_deleted'] = True

                        co = c.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('.', '_').replace(',','_').replace('/','_').replace(':','')
                        delete_column_list.append(co)
                        ##print("the columns are ",delete_column_list)
                    elif missing_data_input:
                        d['handle_missing_data']= missing_data_input
                        today = str(datetime.now().date())
                        ####print("type of date",type(tod
                        d['start_date']= today
                        d['end_date']= ''
                        d['column_deleted'] = False
                        custom_column_list[c]=missing_data_input

                    c_name = c.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('.', '_').replace(',','_').replace('/','_').replace(':','')
                    meta_data_obj[c_name]=d




                #print("the cu",custom_column_list)
                if len(custom_column_list)>0:
                    #print("the cu",custom_column_list)

                    result_df = result_df.fillna(value=custom_column_list)
                    #print("the result after nan fill",result_df,custom_column_list)

                if len(delete_column_list)>0:

                    #print("the value ",delete_column_list)
                    column_delete_obj = DeleteColumn(result_df)
                    result_df = column_delete_obj.delete_column(delete_column_list)
                    #print("columns ",result_df.columns.tolist())



                result_columns = result_df.columns.tolist()
                c = {'columns':result_columns}
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
                #print("the ")
                update = ProjectMetaData.objects.filter(project=project).update(meta_data=meta_data_obj,columns=c_list)
                project_json_metadata = ProjectJsonStorageMetadata.objects.filter(project_json=project_json).update(rows=rows,columns=columns,head_json=df_head_json,tail_json=df_tail_json)
                pk = str(project.pk)

                return redirect('/single-project/'+pk+'/')
            pk = str(pk)
            api-data


            return redirect('/single-project/'+pk+'/')

class ApiNnaFillView(CreateView):
    def get(self,request,pk):
        template_name='sheet_details.html'
        sheet_details_form=SheetDetailsForm()
        context={
            'sheet_details_form':sheet_details_form
        }
        return render(request,template_name,context)
    def post(self,request,pk):
        project= Project.objects.get(pk=pk)
        form = ApiDataForm(request.POST)
        if form.is_valid():

            api = form.cleaned_data['api']
            basic_token = form.cleaned_data['basic_token']
            frequency  = form.cleaned_data['frequency']
            name = request.POST['api_name']
            api_pk = request.POST['api_pk']
            api_data = CustomerAPIDetails.objects.get(pk=int(api_pk))
            
            if api_data.token:


                headers =  {'content-type' : 'application/json',
                                            'Authorization':api_data.token}

                JSONContent  = requests.get(api_data.api,

                                    headers=headers, verify=True)
            else:
                #print("the api",api)
                headers =  {'content-type' : 'application/json',
                                       }

                JSONContent  = requests.get(api_data.api,
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

            df = df.replace('',np.nan)
            # #print("the original df ",df)
            df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '').str.replace('.', '_').str.replace(',','_').str.replace('/','_').str.replace(':','').str.replace(':','')
            new_df_columns = df.columns.tolist()
            #print("new df columns",new_df_columns)
            project_json = ProjectJsonStorage.objects.filter(project=project).order_by('id')[0]
            json_string = json.loads(project_json.js)
            json_df = pd.DataFrame(json_string)
            # #print(type(json_df.head()))

            transposed_df = json_df.transpose()
            rows = transposed_df.shape[0]

            metadata = ProjectMetaData. objects.get(project=project)
            columns = metadata.columns['columns']


            transposed_df_columns = transposed_df.columns.tolist()

            column_list = [x for x in transposed_df_columns if x in new_df_columns]

            new_columns = [x  for x in new_df_columns if x not in columns ]
            #print("new columns are",new_columns)

            for key, value in metadata.meta_data.items():
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

            if len(column_list)>0:
                result_df = reduce(lambda left,right: pd.merge(left,right,on=column_list, how='outer'), [transposed_df,df])
            else:
                try:
                    result_df = reduce(lambda left,right: pd.merge(left,right,left_on= transposed_df_columns[0],right_on=new_df_columns[0],how='outer'), [transposed_df,df])
                except:
                    result_df = reduce(lambda left,right: pd.merge(left,right,left_index=True,right_index=True,how='outer'), [transposed_df,df])
            # #print("the df is ",result_df) erge the mother df with new rows ofss data

            # result_df = result_df.fillna(0)
            #print("the result df ",result_df.head(70))
            result_df_rows = result_df.shape[0]
            df_rows = df.shape[0]
            # if there are  new columns
            # if len(new_columns)>0:
            #     result_df_rows = result_df.shape[0]
            #     df_rows = df.shape[0]
            #     #print("the aded df, and result_df rows",df_rows,result_df_rows)

            #     if result_df_rows == df_rows:
            #         for column in new_columns:
            #             #print("column is",column)
            #             result_df[column] = df[column]
            #             #print("the result df is ",result_df)
            # else:
            #     pass

            result_df.columns = result_df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '').str.replace('.', '_').str.replace(',','_').str.replace('/','_').str.replace(':','').str.replace(':','')
            # #print("the final data frame",result_df)
            result_df_columns = result_df.columns.tolist()
            delete_column_list = []
            custom_column_list = {}
            today = datetime.now()
            metadata = ProjectMetaData. objects.get(project=project)

            # #print("the shappe before duplicate",result_df.shape[0],transposed_df.shape[0],df.shape[0])

            result_df.drop_duplicates(subset = transposed_df_columns, inplace = True)

            # result_df.fillna(0,inplace=True)
            # #print("the shappe aftrer duplicate",result_df.tail(50),result_df.shape[0],transposed_df.shape[0],df.shape[0])

            # if len(new_columns)>0:
            #     column_conbine_obj = ColumnCombine()
            #     data = column_conbine_obj.list_combine_with_datatype_integration(dfs,new_columns)
            #     try:
            #         error = data['Error']
            #         data = {'error_msg':all_columns['error']}
            #         # #print("error",data)
            #         return JsonResponse(data,safe=False)
            #     except:
            #         data = column_conbine_obj.list_combine_with_datatype_integration(dfs,new_columns)
            #         #print("the data for metadata collection is",data)
            #         return JsonResponse(data,safe=False)


            fillna_obj = FillNan(result_df)
            for key, value in metadata.meta_data.items():

                if key in result_df_columns:
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
                    # if value['dtype'] == dtype:
                    #     if value['handle_missing_data']== 'drop':
                    #         l = [key]
                    #         result_df[l].dropna(subset=l,inplace=True)
                    #         # result_df = fillna_obj.drop_row(l)
                    #     elif value['handle_missing_data'] == 0:
                    #         result_df[key].fillna(0, inplace=True)
                    #         # result_df = fillna_obj.fillnan_with_0(key)
                    #         #print("after filling nan",key,result_df)
                    #     elif value['handle_missing_data'] == 'None':

                    #         # result_df = fillna_obj.fillnan_with_None_value(key)
                    #         result_df[key].fillna('None', inplace=True)
                    #         #print("after filling nan",key,result_df)

                    #     elif value['handle_missing_data'] == 'previous':
                    #         result_df[key].fillna(method='ffill', inplace=True)
                    #         # result_df = fillna_obj.fillnan_with_previous_value(key)
                    #         #print("after filling nan",key,result_df)



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
                    #         #print("after filling nan",key,result_df)
                    #     elif value['handle_missing_data'] == 'None':

                    #         # result_df = fillna_obj.fillnan_with_None_value(key)
                    #         result_df[key].fillna('None', inplace=True)
                    #         #print("after filling nan",key,result_df)

                    #     elif value['handle_missing_data'] == 'previous':
                    #         result_df[key].fillna(method='ffill', inplace=True)
                    #         # result_df = fillna_obj.fillnan_with_previous_value(key)
                    #         #print("after filling nan",key,result_df)



                    #     elif value['handle_missing_data'] == 'delete_column':
                    #         delete_column_list.append(key)
                    #     else:
                    #         try:

                    #             custom_column_list[key]=int(value['handle_missing_data'])
                    #         except:
                    #             custom_column_list[key]=value['handle_missing_data']

            if len(custom_column_list)>0:
                result_df.fillna(custom_column_list)


            if len(delete_column_list)>0:

                #print("the value ",delete_column_list)
                column_delete_obj = DeleteColumn(result_df)
                result_df = column_delete_obj.delete_column(delete_column_list)
                #print("columns ",result_df.columns.tolist())

            meta_data_obj = metadata.meta_data
            today = str(datetime.now())
            delete_column_list = []



            for c in new_columns:
                column = {}
                custom_column_list = {}
                ##print("the dataframe",c)
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
                    ##print("type of date",type(today))
                    column['start_date']= today
                    column['end_date']= ''
                    fillna_obj.fillnan_with_0(c)
                    ##print("nan filled df 0  ",c)
                elif missing_data and missing_data == 'None':
                    column['handle_missing_data']= 'None'
                    fillna_obj.fillnan_with_None_value(c)
                    ##print("nan filled df None  ",c)
                    today = str(datetime.now().date())
                    ##print("type of date",type(today))
                    column['start_date']= today
                    column['end_date']= ''
                    column['column_deleted'] = False
                elif missing_data and missing_data == 'previous':
                    column['handle_missing_data']= 'previous'
                    result_df = fillna_obj.fillnan_with_previous_value(c)
                    ##print("nan filled df ",result_df)
                    today = str(datetime.now().date())
                            ##print("type of date",type(today))
                    column['start_date']= today
                    column['end_date']= ''
                    column['column_deleted'] = False
                elif missing_data and missing_data == 'drop':
                    column['handle_missing_data']= 'drop'
                    l = [c]
                    fillna_obj.drop_row(l)
                    ##print("nan filled df ",result_df)
                    today = str(datetime.now().date())
                    ##print("type of date",type(today))
                    column['start_date']= today
                    column['end_date']= ''
                    column['column_deleted'] = False
                elif missing_data and missing_data == 'delete_column':
                    column['handle_missing_data']= missing_data
                    today = str(datetime.now().date())
                    ##print("type of date",type(today))
                    column['start_date']= today
                    column['end_date']= today
                    column['column_deleted'] = True

                    co = c.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('.', '_').replace(',','_').replace('/','_').replace(':','')
                    delete_column_list.append(co)
                    #print("the columns are ",delete_column_list)
                elif missing_data_input:
                    column['handle_missing_data']= missing_data_input
                    today = str(datetime.now().date())
                    ##print("type of date",type(today))
                    column['start_date']= today
                    column['end_date']= ''
                    column['column_deleted'] = False
                    co = c.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('.', '_').replace(',','_').replace('/','_').replace(':','')
                    try:
                        custom_column_list[co]=int(missing_data_input)
                    except:
                        custom_column_list[co]=missing_data_input
                    result_df = result_df.fillna(custom_column_list)
                    #print("in for ",result_df[co])



                c_name = c.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('.', '_').replace(',','_').replace('/','_').replace(':','')
                meta_data_obj[c_name]=column
            #print("custom columns list",custom_column_list)
            if len(custom_column_list)>0:
                result_df = result_df.fillna(custom_column_list)
            #print("the result after nan fill",result_df,delete_column_list)

            if len(delete_column_list)>0:

                ###print("the value ",delete_column_list)
                column_delete_obj = DeleteColumn(result_df)
                result_df = column_delete_obj.delete_column(delete_column_list)
            #print("the result after nan fill",result_df,delete_column_list)

            #     d= {}
            #     if result_df.dtypes[c] == np.int64:
            #         #print("its int type",c)
            #         d['dtype'] = 'int'
            #         d['handle_missing_data'] = 0
            #         d['start_date']= str(today)
            #         d['end_date']= ''
            #         d['column_deleted'] = False
            #         result_df[c].fillna(0, inplace=True)
            #         #print("after nan fill",c,result_df,c)


            #     elif result_df.dtypes[c] == np.flm oat64:
            #         #print("its float type",c)
            #         d['dtype'] = 'float'
            #         d['handle_missing_data'] =0
            #         d['start_date']= str(today)
            #         d['end_date']= ''
            #         d['column_deleted'] = False
            #         result_df[c].fillna(0, inplace=True)
            #         #print("after nan fill",c,result_df)
            #     elif result_df.dtypes[c] == np.object:
            #         #print("its object type",c)
            #         d['dtype'] = 'object'
            #         d['handle_missing_data'] = 'None'
            #         d['start_date']= str(today)
            #         d['end_date']= ''
            #         d['column_deleted'] = False
            #         result_df[c].fillna("None", inplace=True)
            #         #print("result df",c,result_df)
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
            #print("the ")
            update = ProjectMetaData.objects.filter(project=project).update(meta_data=meta_data_obj,columns=c_list)
            project_json_metadata = ProjectJsonStorageMetadata.objects.filter(project_json=project_json).update(rows=rows,columns=columns,head_json=df_head_json,tail_json=df_tail_json)
            pk = str(project.pk)
            data = {'pk':pk}

            return JsonResponse(data, safe=False)

            # #print("the entered file is ",credential)
            # spread_sheet_id=sheet_details_form.cleaned_data["spreadsheet_id"]
            # spread_sheet_id_encrypted = encrypt(spread_sheet_id)
            # sheet_details,created = CustomerAPIDetails.objects.get_or_create(project=project,integration_choice='Google Sheets',credentials=credential,file_id=spread_sheet_id_encrypted)
            # #print("created")
            # sheet_details.credentials.open('r')
            # lines = sheet_details.credentials.read()
            # sheet_details.credentials.close()
            # file_lines_encrypted=encrypt(lines)
            # #print('file_lines_encrypted',file_lines_encrypted)
            # sheet_details.credentials.open('w')
            # sheet_details.credentials.write(file_lines_encrypted)
            # pk= sheet_details.pk
            # sheet_details_update = CustomerAPIDetails.objects.filter(pk=pk).update(credentials = sheet_details.credentials)
            # sheet_details.credentials.close()
            # updated_credential_data = CustomerAPIDetails.objects.get(pk=pk)
            # #print('updated_credential_data.token_file',updated_credential_data.token_file)
            # updated_credential_data.credentials.open('r')
            # lines = updated_credential_data.credentials.read()
            # updated_credential_data.credentials.close()
            # file_lines_decrypted=decrypt(lines)
            # encrypted_file = open('decrypted_credentials.json','w')
            # encrypted_file.write(file_lines_decrypted)
            # encrypted_file.close()
            # credentials = os.path.abspath("decrypted_credentials.json")


            SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

            # The ID and range of a sample spreadsheet.

            SAMPLE_RANGE_NAME = 'Sheet1'


            """Shows basic usage of the Sheets API.
            Prints values from a sample spreadsheet.
            """
            creds = None
            # The file token.pickle stores the user's access and refresh tokens, and is
            # created automatically when the authorization flow completes for the first
            # time.
            if os.path.exists('token.pickle_sheet'+request.user.username):
                with open('token.pickle_sheet'+request.user.username, 'rb') as token:
                    creds = pickle.load(token)
            # If there are no (valid) credentials available, let the user log in.
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        credentials, SCOPES)
                    creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open('token.pickle_sheet'+request.user.username, 'wb') as token:
                    pickle.dump(creds, token)
            os.remove('decrypted_credentials.json')
            service = build('sheets', 'v4', credentials=creds)
            spread_sheet_id_decrypted = decrypt(spread_sheet_id_encrypted)
            # Call the Sheets API
            result = service.spreadsheets().values().get(
            spreadsheetId=spread_sheet_id_decrypted, range=SAMPLE_RANGE_NAME).execute()
            values = result.get('values')
            if not values:
                pass
            else:
                for row in values:
                    str_value=''
                    rows = str_value.join(row)
                    #print(rows)
                    file = open('googlesheets.csv','a')
                    file.write(rows)
                file.close()
                df_file = pd.read_csv('googlesheets.csv', encoding = "ISO-8859-1")
                #print(df_file)
                res_df =reduce(lambda left,right: pd.merge(left,right,on=df_file, how='outer'), [df_file])
                #print(res_df.columns.to_list())
                res_json = df_file.to_json(orient='index')
                projectjson, created = ProjectJsonStorage.objects.get_or_create(project=project, js = res_json)
                #print(projectjson)
                os.remove('token.pickle')
                os.remove('googlesheets.csv')
        return redirect('/dashboard/')

class ProjectGoogleSheetsView(View):
    def post(self,request,pk):
        form = SheetDetailsForm(request.POST,request.FILES)
        url_form = SheetUrlForm(request.POST,request.FILES)
        # #print("the form ",url_form)
        if form.is_valid():
            project = Project.objects.get(pk=pk)
            credential=request.FILES["credential"]

            spread_sheet_id=request.POST["spreadsheet_id"]
            name = request.POST['sheet_name']
            data_range =  request.POST["data_range"]
            sheet_details,created = CustomerAPIDetails.objects.get_or_create(name= name,project=project,integration_choice='Google Sheets',credentials=credential,file_id=spread_sheet_id,range=data_range)
            try:

                scope=['htps://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
                file = sheet_details.credentials.open()
                file_content = file.read()
                js_str = json.loads(file_content.decode('utf-8'))
                creadentials = ServiceAccountCredentials.from_json_keyfile_dict(js_str)
                gc = gspread.authorize(creadentials)
                wks = gc.open(spread_sheet_id).sheet1
                data = wks.get_all_records()
                df = pd.DataFrame(data)
            except:
                data={'error':"There is a Error in Reading Sheet"}
                return JsonResponse(data, safe=False)
            data = df_readline(df,0)
            return JsonResponse(data,safe=False)

            
        elif url_form.is_valid():
            #print("in if")
            project = Project.objects.get(pk=pk)
            url = url_form.cleaned_data['url']
            name = request.POST['sheet_url_name']
            cron_frequency = request.POST['cron_frequency']
            header =request.POST.get('header',None)
            if header:
                sheet_details,created = CustomerAPIDetails.objects.get_or_create(name= name,project=project,integration_choice='Google Sheets',sheet_url=url ,range=cron_frequency,sheet_header=int(header))
            else:
                sheet_details,created = CustomerAPIDetails.objects.get_or_create(name= name,project=project,integration_choice='Google Sheets',sheet_url=url ,range=cron_frequency)
            try:
                if header:
                    df = pd.read_html(url,encoding='utf8',index_col=0,header=int(header))
                else:
                    df = pd.read_html(url,encoding='utf8',index_col=0,header=1)

            except:
                data={'error':"There is a Error in Reading Sheet"}
                return JsonResponse(data, safe=False)
            # if header:
            #     df = pd.read_html(url,encoding='utf8',index_col=0,header=int(header))
            # else:
            #     df = pd.read_html(url,encoding='utf8',index_col=0,header=1)
            if header:

                data = df_readline(df[0],int(header)+1)
            else:
                data = df_readline(df[0],1)

            return JsonResponse(data,safe=False)

        else:
            #print("the errors", url_form.errors)
            data={'error':"There is a Error in Reading Sheet"}
            return JsonResponse(data, safe=False)

def df_readline(df,i):
    columns = df.columns.tolist()
    # #print("the columns are ",columns)
    data = {}
    lines = []
    index =len(df.index)
    c_str = ' '
    #print("the read df is",type(df),columns )
    for column in columns:
        c_str = c_str+','+column
    column_list = c_str.replace(' ','',1)
    if index>5:
        for ind in range(i,i+5):
            one= " "
            for col in columns:
                #print("the col",col,ind)
                try:
                    tst = df[col][ind]
                except:
                    tst = df[col][ind+1]
                one = one+','+str(tst)

            lines.append(one.replace(" ", "", 1))
            # #print("the lines are", lines)
        line_1 =lines[0]
        line_2 = lines[1]
        line_3 = lines[2]
        line_4 = lines[3]
        line_5= lines[4]
        data = {'line_1': line_1, 'line_2': line_2, 'line_3': line_3, 'line_4': line_4, 'line_5': line_5,'column_list':column_list}

    elif (index>=4):
        for ind in range(i,i+4):
            one= " "
            for col in columns:
                # #print("the col",df[col][ind])
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
        for ind in range(i,i+3):
            one= " "
            for col in columns:
                # #print("the col",df[col][ind])
                tst = df[col][ind]
                one = one+','+str(tst)
            lines.append(one.replace(" ", "", 1))
            # #print("the lines are", lines)
        line_1 = lines[0]
        line_2 = lines[1]
        line_3 = lines[2]
        line_4  = ''
        line_5 = ''
        data = {'line_1': line_1, 'line_2': line_2, 'line_3': line_3, 'line_4': line_4, 'line_5': line_5,'column_list':column_list}
    elif (index>=2):
        for ind in range(i,i+2):
            one= " "
            for col in columns:
                # #print("the col",df[col][ind])
                tst = df[col][ind]
                one = one+','+str(tst)
            lines.append(one.replace(" ", "", 1))
            # #print("the lines are", lines)
        line_1 = lines[0]
        line_2 = lines[1]
        line_3 = ''
        line_4 = ''
        line_5 = ''
        data = {'line_1': line_1, 'line_2': line_2, 'line_3': line_3, 'line_4': line_4, 'line_5': line_5,'column_list':column_list}

    else:
        for ind in range(i,i+1):
            one= " "
            for col in columns:
                # #print("the col",df[col][ind])
                tst = df[col][ind]
                one = one+','+str(tst)
            lines.append(one.replace(" ", "", 1))
        line_1 = lines[0]
        line_2 = ''
        line_3 = ''
        line_4 = ''
        line_5 = ''
        data ={'line_1':line_1,'line_2':line_2,'line_3':line_3,'line_4':line_4,'line_5':line_5,'column_list':column_list}
    # #print("the lines are",data)

    data={'data':data}
    return data




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
