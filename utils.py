import hashlib
import pycksum
import sys
import csv
from coreapp.models import ProjectUser
from django.contrib.auth.models import User,Group,Permission
import pandas as pd
import logging
from datetime import datetime

def read_in_chunks(file_object, chunk_size=1024):
    """Lazy function (generator) to read a file piece by piece.
    Default chunk size: 1k."""
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data

def listgenerator(l):
    for i in l:
        yield i

def linereadgen(lines):
    for line in lines[:5]:
        yield line
        
class ReadFileLines:
    def __init__(self,files):
        self.files = files

    def read_file_content(self):
        files = self.files
        # #print("files are ",files)
        files_length = len(files)
        # #print("file length is",files_length)
        
        final_data_dict = {}
        count=1
        # read_f = listgenerator(files)
        # logging.info("the info data "+str(files))   
        i=1
        # while i<=len(files):
        

        #     f = next(read_f)
        #     logging.info("file"+str(f)+str(i)+str(len(files)))
        #     i+=1
        for f_name,f  in files.items():

            file_name=f_name
        
            if f :

                # #print("file size",file_size ,"kb")
                final_data_dict[file_name] ={}
                file_type = file_name.split('.')
                if f_name.endswith('.csv'):
                    # logging.info("file read start time while pandas read "+str(datetime.now()))
                    # df = pd.read_csv(f, nrows=6)
                    # logging.info("the data "+str(type(df)))
                    # content = df.to_string(index = False) 
                    # content = bytes(content, 'utf-8')
                   # logging.info("file read end time while pandas read "+str(datetime.now()))
                    # logging.info("file read end time while chunks"+str(datetime.now()))
                    logging.info("file read start time while chunks"+str(datetime.now()))
                    content=''
                    for piece in read_in_chunks(f):
                        content+=piece
                        lines = content.splitlines()
                        if len(lines)>5:
                            break

                    # if f.multiple_chunks(chunk_size=0.3):
                    #     condition = True
                    #     for chunk in f.chunks():
                    #         content+=chunk.decode("utf-8") 
                    #         lines = content.splitlines()
                    #         if len(lines)>5:
                    #             break
                    # else:
                    #     content = f.read().decode("utf-8")

                    # del f
                    logging.info("file read end time while chunks"+str(datetime.now()))


                        
                 
                    
                    # logging.info("file read start time while total file "+str(datetime.now()))

                    # content = f.read()

                    # logging.info("file read end time while total file"+str(datetime.now()))
                                                                
                    final_data_dict[file_name]['csv'] = True
                    final_data_dict[file_name]['file_no'] = count
                    acepted_format =True
                elif f_name.endswith('.xls') or file_type[-1] == f.name.endswith('.xlsx'):
                    df = pd.read_excel(f,nrows=10)
                    content = df.to_string(index = False) 
                    #print("thr type ",type(content))
                    content = bytes(content, 'utf-8')
                    acepted_format =True
                    final_data_dict[file_name]['csv'] = False
                    final_data_dict[file_name]['file_no'] = count
                else:
                    final_data_dict[file_name]['csv'] = False
                    final_data_dict[file_name]['file_no'] = count
                    acepted_format =False
                if not acepted_format:
                    data ={'error_msg':'We accept only  csv,xls,xlxs'}
                    return data
                lines = content.splitlines()

                some_array = []
                # try:
                #     some_array.append(content)
                #     file_check_sum = pycksum.cksum(some_array)
                # except:
                #     #print("type of content ",type(content))
                #     str_byte = bytes(content, 'utf-8')
                #     #print("type of str",str_byte)
                #     logging.info("the content is"+str(str_byte))
                #     some_array.append(str_byte)
                #     logging.info("the content is"+str(some_array))
                #     file_check_sum = pycksum.cksum(str_byte)

                final_data_dict[file_name]['file_check_sum'] = 0
                
                i=1
                data={}
                condition= True
                line_read = linereadgen(lines)
                while condition:
                    try:

                        line= next(line_read)
                    except StopIteration:
                        condition = False
                    
                    
                    if i<=5:
                        line_byte = line
                        #print("the read line",type(line_byte))
                        try:

                            line_str = line_byte.decode("utf-8")
                        except:
                            line_str = line_byte
                        
                        data['line_'+str(i)] = str(line_str)
                        i=i+1


                final_data_dict[file_name]['data']= data
                
                # file_check_sum = 0
                #print("Checksum:", file_check_sum, "for the file", file_name)
                # #print("file read in check sum fumction", content)
                count=count+1
                
        del files
        logging.info(
            "the filnam data "+str(final_data_dict))
        data={'file_content':final_data_dict}
        #print("the final data of function",data)
        return data

"""
how to execute:
    python simple_test.py

how to code:
        x = CsvValidate('good_comma.csv')
        if x.handle_delimiter():
            #print("VALIDATING::")
            x.validate()

    #print(x.describe) if you want to know what it contains

    Example Output:
    {'file': 'good_comma.csv', 'delimiter': '|', 'row_count': 4, 'column_count': 3, 'format_good': True, 'is_csv_validated': True}
"""
class CsvValidate():
    def __init__(self, f):
        self.describe = {}
        self.describe['file'] = f
        #print("CSV file:", self.describe['file'])
        self.describe['delimiter']         = ','
        self.describe['row_count']         = -1
        self.describe['column_count']      = -1
        self.describe['format_good']       = True

    # def handle_delimiters(self, d=None):
    #     if d:
    #         self.describe['delimiter']   = d
    #     return
    #
    #     data = open(self.csvfile).readlines()
    #     possible_delimiters = ['\t', ',', ':', ';']
    #     for dl in possible_delimiters:
    #         lines = [x.split(dl) for x in data]
    #         no_newlines = [line for line in lines if len(line) > 1]
    #         return all(len(line) == 4 for line in no_newlines)

    def handle_delimiter(self, d=None):
        possible_delimiters = ['\t', ',', ';', '.', ':', '|', '-', '#']
        # possible_delimiters = ['|']
        if d:
            self.describe['delimiter'] = d
            possible_delimiters = [d,]

        data = open(self.describe['file']).readlines()
        self.describe['row_count'] = len(data)

        for dl in possible_delimiters:
            #print("\nDealing with:", dl)
            self.describe['format_good']       = True
            self.describe['column_count']      = -1
            for line in data[:50]: # first 50 lines
                lineContains = line.split(dl)
                columns = len(lineContains)  #calculate elements
                # #print("Columns ", columns, " with delimiter", dl, 'and string:', lineContains)
                if self.describe['column_count'] == -1:
                    self.describe['column_count'] = columns
                if self.describe['column_count'] != columns:
                    self.describe['format_good'] = False
                if self.describe['column_count'] < 2:
                    self.describe['format_good'] = False
            #print("For", dl, "Data is:", self.describe)
            if self.describe['format_good']:
                if self.describe['column_count'] > 1:
                    self.describe['delimiter'] = dl
                    return True
        return False

    def validate(self):
        with open(self.describe['file']) as csvfile:
            data = csv.reader(csvfile, delimiter=self.describe['delimiter'])
            if self.describe['row_count'] != len(list(data)):
                self.describe['is_csv_validated'] = False
                self.describe['error'] = 'Row count is not matching'
                return self.describe['is_csv_validated']

            for r, row in enumerate(data):
                if self.describe['column_count'] != len(list(row)):
                    self.describe['is_csv_validated'] = False
                    self.describe['error'] = 'Column count for the '+ str(r) + ' row is not matching'
                    return self.describe['is_csv_validated']
        self.describe['is_csv_validated'] = True

##############################################################

# x = CsvValidate('good_comma.csv')
# if x.handle_delimiter():
#     #print("VALIDATING::")
#     x.validate()
#     #print(x.describe)        



class ProjectPermissionGroupCreate:
    '''class to create an project permission groups'''
    def __init__(self,project):
        self.project=project

    def _read_perm(self,group):
        project_read = Permission.objects.get(codename='view_project')
        projectendpoint_read = Permission.objects.get(codename='view_projectendpoint')
        projectdashboard_read = Permission.objects.get(codename='view_projectdashboard')
        projectquery_read = Permission.objects.get(codename='view_projectquery')
        projectmetadata_read = Permission.objects.get(codename='view_projectmetadata')
        projectjsonstorage_read = Permission.objects.get(codename='view_projectjsonstorage')

        group.permissions.add(project_read)
        group.permissions.add(projectdashboard_read)
        group.permissions.add(projectendpoint_read)
        group.permissions.add(projectquery_read)
        group.permissions.add(projectmetadata_read)
        group.permissions.add(projectjsonstorage_read)
    
    def _write_perm(self,group):
        self._read_perm(group)
        project_create = Permission.objects.get(codename='add_project')
        projectendpoint_create = Permission.objects.get(codename='add_projectendpoint')
        projectdashboard_create = Permission.objects.get(codename='add_projectdashboard')
        projectquery_create = Permission.objects.get(codename='add_projectquery')
        # projectmetadata_create = Permission.objects.get(codename='add_projectmetadata')
        projectjsonstorage_create = Permission.objects.get(codename='add_projectjsonstorage')
        project_change = Permission.objects.get(codename='change_project')
        projectendpoint_change = Permission.objects.get(codename='change_projectendpoint')
        projectdashboard_change = Permission.objects.get(codename='change_projectdashboard')
        projectquery_change = Permission.objects.get(codename='change_projectquery')
        # projectmetadata_change = Permission.objects.get(codename='change_projectmetadata')
        projectjsonstorage_change = Permission.objects.get(codename='change_projectjsonstorage')

        group.permissions.add(project_create)
        group.permissions.add(projectdashboard_create)
        group.permissions.add(projectendpoint_create)
        group.permissions.add(projectquery_create)
        group.permissions.add(projectjsonstorage_create)

        group.permissions.add(project_change)
        group.permissions.add(projectdashboard_change)
        group.permissions.add(projectendpoint_change)
        group.permissions.add(projectquery_change)
        group.permissions.add(projectjsonstorage_change)
    

    def _delete_perm(self,group):
        self._write_perm(group)
        project_delete = Permission.objects.get(codename='delete_project')
        projectendpoint_delete = Permission.objects.get(codename='delete_projectendpoint')
        projectdashboard_delete = Permission.objects.get(codename='delete_projectdashboard')
        projectquery_delete = Permission.objects.get(codename='delete_projectquery')
        # projectmetadata_delete = Permission.objects.get(codename='delete_projectmetadata')
        # projectjsonstorage_delete = Permission.objects.get(codename='delete_projectjsonstorage')

        group.permissions.add(project_delete)
        group.permissions.add(projectdashboard_delete)
        group.permissions.add(projectendpoint_delete)
        group.permissions.add(projectquery_delete)
    
    
    def _admin_perm(self,group):
        self._delete_perm(group)


    def group_create(self,name):

        project = self.project
        group, create  = Group.objects.get_or_create(name=name)
        splited_name = name.split('_')
        if splited_name[-1] == 'Admin':
            self._admin_perm(group)
        elif splited_name[-1] == 'Delete':
            self._delete_perm(group)
        elif splited_name[-1] == 'Write':
            self._write_perm(group)
        elif splited_name[-1] == 'Read':
            self._read_perm(group)
        return "sucess"