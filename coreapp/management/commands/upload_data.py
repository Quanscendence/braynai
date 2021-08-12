from django.core.management.base import BaseCommand
from django.utils import timezone
import os
import sys
import random
from datetime import datetime, timedelta
from functools import reduce, partial
from django.core.mail import send_mail
from django.core import mail
import pandas as pd
from django.contrib.auth.models import User
from engine import cleaner, optimize, query
from django.db.models import Q
import json
from coreapp.models import Project, ProjectType, ProjectJsonStorage,ProjectIndex,ProjectQuery,ProjectMetaData,IndustryChoices

class Command(BaseCommand):
    help = 'Upload the pre Defined data'

    def handle(self, *args, **kwargs):
        # user_list = ['vatsa@realmimpex.com','deepa@realmimpex.com','nag@realmimpex.com','ranjitha@realmimpex.com','vijeth@realmimpex.com','vishwa@realmimpex.com']
        # for user in user_list:
        #     if ProjectType.objects.filter().exists():
        #         ID=str(ProjectType.objects.latest('id').id)
        #         project_id=ID
        #     else:
        #         project_id='001'
        #     industry_name = IndustryChoices.objects.get(Industry_name='TELECOMMUNICATIONS')
        #     project_type,created =ProjectType.objects.get_or_create(type='Visualization',industry_name=industry_name,data_title="UFC-FightHDf-1993 to 2019",data_description="Testing Query Process",expected_ans="good response time",project_id=project_id)

        #     login_user=User.objects.get(username=user)
        #     print(login_user)
        #     # project,created=Project.objects.get_or_create(type=project_type,title="UFCFD-2019",admin_user=login_user)
        #     # time = timezone.now().strftime('%X')
        #     # self.stdout.write("It's now %s" % time)
        #     # folder_a =os.listdir('folder_a')
        #     # time_series = 'date'
        #     # if time_series:
        #     #     metadata, create = ProjectMetaData.objects.get_or_create(project=project,date_column_name=time_series,date_format='%m/%d/%Y')
            

        #     # file1_path = 'E:/projects/DSAAA/dsaas/folder_a/data.csv'
        #     # print("file1_path:",file1_path)
        #     # file1_df = pd.read_csv(file1_path,error_bad_lines=False,encoding="ISO-8859-1")

        #     # obj = cleaner.FillNan()
        #     # no_NAN_df = obj.fillnan_with_0(file1_df)

        #     # if time_series:
        #     #     print("date series")

        #     #     no_NAN_df.set_index('date')


        #     # res_json = no_NAN_df .to_json(orient='index')



        #     # projectjson, created = ProjectJsonStorage.objects.get_or_create(project=project, js = res_json)
        #     # print(projectjson.pk)
        #     # if time_series:
        #     #     no_NAN_df[time_series]= pd.to_datetime(no_NAN_df[time_series])
        #     #     no_NAN_df.sort_values(time_series, inplace=True)
        #     #     print(no_NAN_df)
        #     #     end_date = no_NAN_df.date.iloc[0]
        #     #     start_date= no_NAN_df.date.iloc[-1]
        #     #     project_index, created = ProjectIndex.objects.get_or_create(project=project,json_storage=projectjson,start_date=start_date,end_date=end_date)
        #     #     print(project_index)


        #     project,created=Project.objects.get_or_create(type=project_type,title="BIT-Add-Data",admin_user=login_user)
        #     time = timezone.now().strftime('%X')
        #     self.stdout.write("It's now %s" % time)
        #     folder_a =os.listdir('folder_a')
        #     time_series = 'Day'
        #     if time_series:
        #         metadata, create = ProjectMetaData.objects.get_or_create(project=project,date_column_name=time_series,date_format='%m/%d/%Y')
        #     for file1 in folder_a:

        #         file1_path = 'folder_a/'+file1
        #         print("file1_path:",file1_path)
        #         file1_df = pd.read_csv(file1_path,error_bad_lines=False,encoding="ISO-8859-1")

        #         obj = cleaner.FillNan()
        #         no_NAN_df = obj.fillnan_with_0(file1_df)

        #         if time_series:
        #             print("date series")

        #             no_NAN_df.set_index(time_series)


        #         res_json = no_NAN_df .to_json(orient='index')



        #         projectjson, created = ProjectJsonStorage.objects.get_or_create(project=project, js = res_json)
        #         print(projectjson.pk)
        #         if time_series:
        #             no_NAN_df[time_series]= pd.to_datetime(no_NAN_df[time_series])
        #             no_NAN_df.sort_values(time_series, inplace=True)
        #             print(no_NAN_df)
        #             start_date = no_NAN_df.Day.iloc[0]
        #             end_date  = no_NAN_df.Day.iloc[-1]
        #             project_index, created = ProjectIndex.objects.get_or_create(project=project,json_storage=projectjson,start_date=start_date,end_date=end_date)
        #             print(project_index)
        
        ID=str(ProjectType.objects.latest('id').id)
        project_id=ID
        industry_name = IndustryChoices.objects.get(Industry_name='TELECOMMUNICATIONS')
        project_type,created =ProjectType.objects.get_or_create(type='Visualization',industry_name=industry_name,data_title="Shopping Data",data_description="Testing Query Process",expected_ans="good response time",project_id=project_id)

        login_user=User.objects.get(username='vatsa@realmimpex.com')
        print(login_user)
        project,created=Project.objects.get_or_create(type=project_type,title="Shopping",admin_user=login_user)
        time = timezone.now().strftime('%X')
        self.stdout.write("It's now %s" % time)
        folder_a =os.listdir('folder_a')
        time_series = 'Date'
        if time_series:
            metadata, create = ProjectMetaData.objects.get_or_create(project=project,date_column_name=time_series,date_format='%m/%d/%Y')
        

        file1_path = 'E:/projects/DSAAA/brayn/test_shopping/ROTATION_of_products01.01.2018-09.01.2019.csv'
        file2_path = 'E:/projects/DSAAA/brayn/test_shopping/SELL_1.csv'
        file3_path = 'E:/projects/DSAAA/brayn/test_shopping/Day_sell_24_12_18.csv'

        print("file1_path:",file1_path)
        file1_df = pd.read_csv(file1_path,error_bad_lines=False,encoding="ISO-8859-1")
        file2_df = pd.read_csv(file2_path,error_bad_lines=False,encoding="ISO-8859-1")
        file3_df = pd.read_csv(file3_path,error_bad_lines=False,encoding="ISO-8859-1")
        print("the df are ready")
        merge_2df =reduce(lambda left,right: pd.merge(left,right,on=['PKod','Pgroup','Pname'], how='outer'), [file1_df,file2_df])
        print(merge_2df['Date'])
        res_df =reduce(lambda left,right: pd.merge(left,right,on='Date', how='outer'), [file3_df,merge_2df])
        end = '1.12.2019'
        res_df ['Date'].fillna(end, inplace=True)
        res_df ['PKod'].fillna(1111, inplace=True)
        res_df ['Pgroup'].fillna('Nagroup', inplace=True)
        res_df ['Pname'].fillna('NoName', inplace=True)
        
        res_df.fillna(method='ffill', inplace=True)
        
        print("thejson is ready",res_df['Date'])
        # obj = cleaner.FillNan()
        # no_NAN_df = obj.fillnan_with_0(file1_df)

        if time_series:
            print("date series")

            res_df.set_index('Date')


        res_json = res_df.to_json(orient='index')
        print("converted into json-storage") 



        projectjson, created = ProjectJsonStorage.objects.get_or_create(project=project, js = res_json)
        print(projectjson.pk)
        if time_series:

            

            res_df[time_series]= pd.to_datetime(res_df[time_series])
            
            sort_df = res_df.sort_values(time_series)
            
            print(res_df)
            end_date = sort_df.Date.iloc[-1]
            start_date= sort_df.Date.iloc[0]
            project_index, created = ProjectIndex.objects.get_or_create(project=project,json_storage=projectjson,start_date=start_date,end_date=end_date)
            # print(project_index)

