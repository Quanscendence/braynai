from django.test import TestCase
import os
import sys
import random
from datetime import datetime, timedelta
from functools import reduce, partial
from django.core.mail import send_mail
from django.core import mail
import pandas as pd
from . models import Project, ProjectType, ProjectJsonStorage,ProjectIndex,ProjectQuery,ProjectMetaData,IndustryChoices
from django.contrib.auth.models import User
from engine import cleaner, optimize, query, date_selector
from django.db.models import Q
import json
import ast



# def date_series_file_generation(row,file):
#     ''' this is to genetrate the date series files'''

#     # testcase with date increments as IDs

#     #---------------------------
#     # can be changed
#     #--------------------------
#     rows    = row
#     indexes = file # can try: 500000
#     begin_date = datetime.now() - timedelta(hours=99999)
#     #--------------------------


#     c     = 1

#     fa = ''
#     fb = ''

#     print("begin date:", begin_date)
#     this_date = begin_date


#     def get_rdm_str(i, r=10):
#         n1 = round(random.uniform(0, r), 3)
#         n2 = round(random.uniform(0, r), 3)
#         n3 = round(random.uniform(1, r*2), 3)
#         n4 = round(random.uniform(1, r*3), 3)

#         pk = round(random.uniform(1, 10))

#         return str(i)+", "+str(pk)+", "+str(n1)+", "+str(n2)+", "+str(n3)+", "+str(n4)


#     for i in range(indexes):
#         if (i % rows) == 0:
#             filea = 'folder_date_a/file_a_'+str(c)+'.csv'
#             fileb = 'folder_date_b/file_b_'+str(c)+'.csv'
#             c = c+1

#             if fa:
#                 fa.close()
#             if fb:
#                 fb.close()

#             fa = open(filea, 'w')
#             fb = open(fileb, 'w')

#             fa.write("DateTime, r_no, attr1, attr2, attr3, attr4\n")
#             sa = get_rdm_str(this_date)
#             fa.write(sa+'\n')

#             fb.write("DateTime, r_no, attr5, attr6, attr7, attr8\n")
#             sb = get_rdm_str(this_date)
#             fb.write(sb+'\n')
#         else:
#             this_date += timedelta(hours=1)
#             sa = get_rdm_str(this_date, 50)
#             fa.write(sa+'\n')

#             sb = get_rdm_str(this_date, 100)
#             fb.write(sb+'\n')
#     print("End Date:", this_date)
#     return "sucess"



# def id_series_file_generation(row,file):
#     ''' this is to genetrate the ID series files'''


#     # testcase without date field

#     #---------------------------
#     # can be changed
#     #--------------------------
#     rows    = row
#     indexes = file # can try: 500000
#     #--------------------------


#     c     = 1

#     fa = ''
#     fb = ''
#     fc = ''


#     def get_rdm_str(i, r=10):
#         n1 = round(random.uniform(0, r), 3)
#         n2 = round(random.uniform(0, r), 3)
#         n3 = round(random.uniform(1, r*2), 3)
#         n4 = round(random.uniform(1, r*3), 3)
#         return str(i)+", "+str(n1)+", "+str(n2)+", "+str(n3)+", "+str(n4)


#     for i in range(indexes):
#         if (i % rows) == 0:
#             filea = 'folder_a/file_a_'+str(c)+'.csv'
#             fileb = 'folder_b/file_b_'+str(c)+'.csv'
#             filec = 'folder_c/file_c_'+str(c)+'.csv'

#             c = c+1

#             if fa:
#                 fa.close()
#             if fb:
#                 fb.close()
#             if fc:
#                 fc.close()

#             fa = open(filea, 'w')
#             fb = open(fileb, 'w')
#             fc = open(filec, 'w')


#             fa.write("ID, attr1, attr2, attr3, attr4\n")
#             sa = get_rdm_str(i)
#             fa.write(sa+'\n')

#             fb.write("ID, attr5, attr6, attr7, attr8\n")
#             sb = get_rdm_str(i)
#             fb.write(sb+'\n')


#             fc.write("ID, attr5, attr6, attr7, attr8\n")
#             sc = get_rdm_str(i)
#             fc.write(sc+'\n')
#         else:
#             sa = get_rdm_str(i, 50)
#             fa.write(sa+'\n')

#             sb = get_rdm_str(i, 100)
#             fb.write(sb+'\n')

#             sc = get_rdm_str(i, 100)
#             fc.write(sc+'\n')
#     return "sucess"


# def create_project(title,description,project_title):
#     '''this function will create project'''
#     ID=str(77)
#     project_id=ID
#     industry_name, created = IndustryChoices.objects.get_or_create(Industry_name='TELECOMMUNICATIONS')

#     project_type,created =ProjectType.objects.get_or_create(type='Visualization',industry_name=industry_name,data_title="BIT Add Month wise Data",data_description="Testing Query Process",expected_ans="good response time",project_id=project_id)

#     login_user,created=User.objects.get_or_create(username='vishwa@therealm.in',email= 'vishwa@therealm.in',)
#     login_user.set_password('someuser')
#     login_user.save()
#     print(login_user)
#     project,created=Project.objects.get_or_create(type=project_type,title=project_title,admin_user=login_user)
#     return project

# def upload_date_series_data():
#     ''' this function is to upload  the date series data'''
#     folder_a =os.listdir('folder_a')
#     begin = datetime.now()
#     print("start time uploadind date series",begin )
#     f = open('log.txt','w')
#     begin_str = str(begin)
#     f.write("start time uploadind Id series:"+begin_str)
#     project = create_project('Date Series Data Test','BIT Date seriesed data','Date Series Data Test')
#     print("project for date series dat is created")
#     time_series = 'Day'
#     if time_series:
#         metadata, create = ProjectMetaData.objects.get_or_create(project=project,date_column_name=time_series,date_format='%m/%d/%Y')
#         date_column= metadata.date_column_name
#         date_format= metadata.date_format





#     for file1 in folder_a:

#         file1_path = 'folder_a/'+file1

#         file1_df = pd.read_csv(file1_path,encoding="ISO-8859-1")
#         # print(file1_df.columns.to_list())



#         obj = cleaner.FillNan()
#         no_NAN_df = obj.fillnan_with_0(file1_df)
#         # print(file1_df)
#         if time_series:
#             print("date series")

#             no_NAN_df.set_index(time_series)
#         res_json = no_NAN_df .to_json(orient='index')
#         projectjson, created = ProjectJsonStorage.objects.get_or_create(project=project, js = res_json)

#         if time_series:
#             no_NAN_df[time_series]= pd.to_datetime(no_NAN_df[time_series])
#             no_NAN_df.sort_values(time_series, inplace=True)

#             start_date = no_NAN_df.Day.iloc[0]
#             end_date  = no_NAN_df.Day.iloc[-1]
#             project_index, created = ProjectIndex.objects.get_or_create(project=project,json_storage=projectjson,start_date=start_date,end_date=end_date)

#     end = datetime.now()
#     # print("time taken to  uploade date series",end-begin )
#     # print('time to test the query on date seri data:')
#     begin = datetime.now()
#     begin_str = str(begin)
#     total = str(end-begin)
#     f.write("time taken to  uploade date series data:"+total)
#     f.write("starting test on loading   the data from 200 uploades ")
#     # print("start time  merge and query on given inputs:",begin_str )
#     #define the date range you need to
#     fdate ='09/10/2018'
#     tdate = '08/20/2019'
#     combined_df = optimize.index_optimize(fdate,project.pk,tdate,)
#     # print("the dataframe is ",combined_df)
#     combined_df['Clicks'] = combined_df['Clicks'].astype(float)
#     combined_df['Impressions'] = combined_df['Impressions'].astype(float)
#     # print("type of the value is ",type('Clicks'))
#     value_column = combined_df.columns.get_loc('Clicks')
#     print("the value is", value_column)
#     date_column = str(date_column)
#     # print("the data value is ",type(date_column))

#     date_column =combined_df.columns.get_loc(date_column)
#     actual = date_selector.TimeManage(combined_df)
#     keyword = 'week'
#     keyword_value = 1


#     df = actual.keyword_based_date_range_selection('mean',keyword=keyword,keyword_value=keyword_value, date_column=date_column, value_column=value_column, custom=[],date_column_format=date_format)






#     # s_time = datetime.now()
#     # where_q_1 = "Campaign == ['Explore Europe','Hongkong_Tour','Leads-Singapore','Dubai Tour Package','Leads-SMT Package','SMT_MAY-JUN_2019','Bali_Reg','SMT']"
#     # where_q_1_operator = '&'
#     # where_q_2 = 'Clicks>=100'
#     # gropupby= ['Campaign']
#     # aggregation_str = "{'Clicks':'mean','Impressions':'mean'}"
#     # aggregation = ast.literal_eval(aggregation_str)
#     #
#     # where_query = where_q_1+where_q_1_operator+where_q_2
#     # #creating the object for where clause class
#     # filter = query.WhereClouse()
#     # filter_res = filter.filter_data(combined_df,where_query)
#     #
#     # #creating the object for group clause class
#     #
#     # grouping = query.GroupBY()
#     # grouping_res = grouping.data_group(filter_res,gropupby)
#     #
#     #
#     # # crfeating an object to date aggregation class to apply both sampling the grouped data and aggregation
#     # sample_data = query.DateAggregator()
#     # # date control is  monthly based
#     # sample_monthly_res = sample_data.get_new_df_with_date_control(grouping_res,'Day','M')
#     #
#     # sample_monthly_agg_res = sample_data.many_to_one(aggregation,sample_monthly_res)
#     # print("the data with monthly aggrigated",sample_monthly_agg_res)
#     # # date control is  weekly based
#     # sample_weekly_res = sample_data.get_new_df_with_date_control(grouping_res,'Day','W')
#     # sample_weekly_agg_res = sample_data.many_to_one(aggregation,sample_weekly_res)
#     # print("the data with weekly aggrigated",sample_monthly_agg_res)
#     # # date control is  10days  based
#     # sample_10d_res = sample_data.get_new_df_with_date_control(grouping_res,'Day','10D')
#     # sample_10d_agg_res = sample_data.many_to_one(aggregation,sample_10d_res)
#     # print("the data with 10d aggrigated",sample_10d_agg_res)
#     #
#     # # date control is  week days   aggrigated excluding friday and sunday
#     # sample_Weekdays_res = sample_data.get_new_df_with_date_control(grouping_res,'Day','3B')
#     # sample_Weekdays_agg_res = sample_data.many_to_one(aggregation,sample_Weekdays_res)
#     # print("the data with Weekdays aggrigated",sample_Weekdays_agg_res)

#     # # TODO: need to write customized week days aggrigation like only  someday or only somedays

#     return "sucess"

# def upload_id_series_data():
#     ''' this function is to upload  the date series data'''
#     folder_a =os.listdir('folder_a')
#     folder_b =os.listdir('folder_b')
#     folder_c =os.listdir('folder_c')
#     f = open('log.txt','w')
#     begin = datetime.now()
#     begin_str = str(begin)
#     f.write("start time uploadind Id series:"+begin_str)


#     print("start time uploadind Id series",begin )
#     project = create_project('ID Series Data Test','files and uploads','ID Series Data Test')


#     for (file1, file2,file3 ) in zip(folder_a, folder_b,folder_c):

#         file1_path = 'folder_a/'+file1
#         file2_path = 'folder_b/'+file2
#         file3_path = 'folder_c/'+file3
#         file1_df = pd.read_csv(file1_path,encoding="ISO-8859-1")
#         file2_df = pd.read_csv(file2_path,encoding="ISO-8859-1")
#         file3_df = pd.read_csv(file3_path,encoding="ISO-8859-1")

#         res_df =reduce(lambda left,right: pd.merge(left,right,on='ID', how='outer'), [file1_df,file2_df,file3_df])
#         print("befour nan fill:",res_df)

#         obj = cleaner.FillNan()
#         no_NAN = obj.fillnan_with_0(res_df)
#         res_json = no_NAN .to_json(orient='index')




#         projectjson, created = ProjectJsonStorage.objects.get_or_create(project=project, js = res_json)
#         print(projectjson.pk)
#     end = datetime.now()
#     print("time taken to  uploade Id series",end-begin )
#     total = str(end-begin)
#     f.write("time taken to  uploade Id series data:"+total)

#     print("starting test on loading   the data from  uploades ")
#     f.write("starting test on loading   the data from  uploades ")

#     begin = datetime.now()
#     print("time start",begin)
#     from_date ='2008-03-30 08:33:27.008631'
#     to_date = '2010-06-19 05:33:27.008631'
#     from_date = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S.%f')
#     to_date = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S.%f')
#     indexes = ProjectIndex.objects.filter(project=project)
#     js_stotages = []

#     indexes = ProjectIndex.objects.filter.filter(Q(project=project)&(Q(start_date<=from_date) | Q(end_date<=from_date) | Q(start_date<=to_date) | Q(end_date<=to_date)))
#     print("the matched results",indexes)
#     return "sucess"

# class TestDataStorage(TestCase):
#     ''' this class is to run test on datastorage'''
#     def test_data_storage(self):
#         ''' this function is to call file generation, file upload, and loading time testing'''
#         list_rows = [500]
#         list_files = [100000]


#         for row, file in zip(list_rows,list_files):

#             # self.assertEqual(date_series_file_generation(row,file), 'sucess')
#             # self.assertEqual(id_series_file_generation(row,file), 'sucess')
#             self.assertEqual(upload_date_series_data(),'sucess')
#             # self.assertEqual(upload_id_series_data(),'sucess')

#             f = open('log.txt','w')
#             f.write('--------------------------------------------End-----------------------------------------')
#             f.close()
