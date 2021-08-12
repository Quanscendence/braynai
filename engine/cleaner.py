import os
import io
import sys
import json
from functools import reduce, partial
import pandas as pd
import csv
import numpy as np
import logging
from datetime import datetime


class FillNan:
    '''class to fill NAN with 0'''

    def __init__(self,df):
        self.df = df
        


    def fillnan_with_0(self,column):
        '''function to fill NAN with 0'''

        df = self.df
        df[column].fillna(0, inplace=True)
        # #print("nan filled df 0",df)

        return df
    def fillnan_with_previous_value(self,column):
        '''function to fill NAN with previous value'''

        df = self.df
        df[column].fillna(method='ffill')
        # #print("nan filled df ",df)

        return df
    def fillnan_with_None_value(self,column):
        '''function to fill NAN with None value'''

        df = self.df
        df[column].fillna('None', inplace=True)
        # #print("nan filled df ",df)

        return df
    def drop_row(self,column):
        '''function to drop row'''

        df = self.df
        # #print("nan  non dropped  ",df)
        print("before",df)
        df[column].dropna(subset=column)
        print("df",df)
        # #print("nan   dropped",df[column].isnull().sum())

        return df
    def time_series_drop_row(self,l):
        '''function to drop row'''
        df = self.df
        # #print("nan  non dropped  ",df)
        column= l[0]
        # #print("the column is",column)
        # #print("NAT ount before drop",df[column].isnull().sum())
        # df[l].replace({'NaT': 'NaN'}, inplace=True)
        df.dropna(subset=l,inplace=True)
        # #print("NAT count after drop",df[column].isnull().sum())

        return df
        

    # def fillnan_with_mean(self,df):
    #     '''function to fill NAN with mean of cloumn'''
    #
    #
    #     df.fillna(0, inplace=True)
    #
    #     return df

def dataframe_to_json(data_frames,file1_column):
    # #print(" called dataframe" )
    res_df =reduce(lambda left,right: pd.merge(left,right,on=file1_column, how ='inner'), data_frames)
    # #print(res_df.columns.to_list())
    res_json = res_df.to_json(orient='index')
    # #print("res json ",res_json)
    # #print("suc.ess in json " )
    return res_json

def json_to_json():
    pass

'''
class to read file as pandas dataframe'''  
class FileReader:
    def __init__(self):
        pass
    def readfile(self,files,files_separators,files_heders):
        all_dfs = {}
        for file_name, file in files.items():
            # logging.info("final files "+str(files))
            file_str = file_name.split('.')
            if file_str[-1] == 'csv':
                separator = files_separators[file_name]
                headers= files_heders[file_name]
                logging.info("the start time for read df in upload"+str(datetime.now()))
                df = self.read_csv(file,separator,headers)
                logging.info("the end time for read df in upload"+str(datetime.now())+str(df.empty))
               
                if df.empty:
                    logging.error("the utf error")
                    all_dfs={'Error':"Please Convert csv to utf-8 format"}
                    return all_dfs
                else:
                    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '').str.replace('.', '_').str.replace(',','_').str.replace('/','_').str.replace(':','').str.replace(':','')
                    all_dfs[file_name]=df
            elif file_str[-1] == 'xls' or file_str[-1] == 'xlsx':
                headers= files_heders[file_name]
                separator = files_separators[file_name]
                df = self.read_excel(file,separator,headers)
                ##print("typeof df",type(df))
                df_empty = df.empty
                ##print("the empty df", df_empty)
                if df_empty:
                    all_dfs={'Error':"Please Convert csv to utf-8 format"}
                    return all_dfs
                else:
                    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '').str.replace('.', '_').str.replace(',','_').str.replace('/','_').str.replace(':','').str.replace(':','')
                    all_dfs[file_name]=df
            else:
                all_dfs={'Error':"NonFormat"}
                return all_dfs
            del df
        
        return all_dfs
                
    def read_csv(self,file,separator,header):
        if header['header_status'] == "yes":
            
            # ##print("the delemeter",separator,file)
            
            try:
                header = int(header['file_header_row'])-1

                # df_object = pd.read_csv(file,sep=separator,header=header,encoding = "utf-8", iterator=True)
                df = pd.read_csv(file,sep=separator,header=header,encoding = "utf-8")

                # reader = pd.read_csv('tmp.sv', sep=separator,header=header,encoding = "utf-8", chunksize=1000)
                # df = pd.DataFrame()
                # for chunk in pd.read_csv(file,sep=separator,header=header,encoding = "utf-8", chunksize=1000):
                #     df = pd.concat([df, chunk], ignore_index=True)

            except:
                df=pd.DataFrame()
                return df
            

            columns = df.columns.tolist()
            return df
        elif header['header_status'] == 'no':
            
            # #print("columns names",header['columns'])
            file_columns =header['columns'].split(',') 
            
            try:
                df = pd.read_csv(file,sep=separator,names=file_columns,encoding = "utf-8")
            except:
                df=pd.DataFrame()
                return df
            type(df)
            columns = df.columns.tolist()
            return df

    def read_excel(self,file,separator,header):
        #print("the data",header['header_status'])

        if  header['header_status'] == "yes":
            header = int(header['file_header_row'])-1
            df = pd.read_excel(file,header=header, encoding='utf-8')
            df_columns = df.columns.tolist()
            return df
        elif header['header_status'] == "no":
            file_columns =header['columns'].split(',')
            df = pd.read_excel(file,names=file_columns, encoding='utf-8')
            columns = df.columns.tolist()
            return df
        else:
            df = pd.read_excel(file, encoding='utf-8')
            #print("the df is",df)
            return df

    def readfile_with_schema(self,files,files_separators,files_heders):
        all_dfs = {}
        project_schema_dict = {}
        for file_name, file in files.items():
            schema = {}
            file_str = file_name.split('.')
            if file_str[-1] == 'csv':
                separator = files_separators[file_name]
                header= files_heders[file_name]
                logging.info("the data"+str(header)+str(separator))
                if header['header_status'] == "yes":
                    schema['file_name']= str(file)
                    schema['csv'] = True
                    schema['delemeter'] = separator
                    
                    # #print("the delemeter",separator)
                    
                    try:
                        header = int(header['file_header_row'])-1
                        df = pd.read_csv(file,delimiter=separator,header=header, encoding ="ISO-8859-1")
                    except:
                        data={'error':"Please Convert csv to utf-8 format"}
                        
                        return data
                    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '').str.replace('.', '_').str.replace(',','_').str.replace('/','_')
                    df_colums = df.columns.tolist()
                    columns = ''
                    for c in df_colums:
                        columns = columns+','+c
                    columns = columns[1:]
                    schema['columns']=columns
                    all_dfs[file_name]=df
                    project_schema_dict[file_name]=schema
                    logging.info("the df head test"+str(df.head()))
                elif header['header_status'] == 'no':
                    schema['file_name']= str(file)
                    schema['csv']=True
                    schema['delemeter']=separator
                    file_columns =header['columns'].split(',') 
                    try:

                        df = pd.read_csv(file,delimiter=separator,names=file_columns)
                    except:
                        data={'error':"Please Convert csv to utf-8 format"}
                        
                        return data
                    
                    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '').str.replace('.', '_').str.replace(',','_').str.replace('/','_')
                    df_colums = df.columns.tolist()
                    columns = ''
                    for c in df_colums:
                        columns = columns+','+c
                    columns = columns[1:]
                    schema['columns']=columns
                    all_dfs[file_name]=df
                    project_schema_dict[file_name]=schema
            elif file_str[-1] == 'xls' or file_str[-1] == 'xlsx':
                separator = files_separators[file_name]
                header= files_heders[file_name]
                if  header['header_status'] == "yes":
                    schema['file_name']= str(file)
                    schema['csv']=False
                    schema['delemeter']=''
                    header = int(header['file_header_row'])-1
                    df = pd.read_excel(file,header=header, encoding='utf-8')
                    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '').str.replace('.', '_').str.replace(',','_').str.replace('/','_')
                    df_columns = df.columns.tolist()
                    
                    columns = ''
                    for c in df_columns:
                        columns = columns+','+c
                    columns = columns[1:]
                    schema['columns']=columns
                    project_schema_dict[file_name]=schema
                    all_dfs[file_name]=df
                elif header['header_status'] == "no":
                    schema['file_name']= str(file)
                    schema['csv']=False

                    schema['delemeter']=''
                    file_columns =file_columns.split(',')
                    df = pd.read_excel(file,names=header['columns'], encoding='utf-8')
                    df_columns = df.columns.tolist()
                    
                    columns = ''
                    for c in df_colums:
                        columns = columns+','+c
                    columns = columns[1:]
                    schema['columns']=columns
                    all_dfs[file_name]=df
                    project_schema_dict[file_name]=schema
            else:
                
                data={'error':"wrong format"}
                return data
        #print("the final scema is",schema)
        data = {'all_dfs':all_dfs,'schema':project_schema_dict}
        return data


'''class to check and combine the file columns'''
class ColumnCombine:
    def __init__(self):
        pass
    def list_combine(self,dfs):
        ''' function to check is here common columns or not if not return error'''
        all_columns = []
        for df  in dfs:
            
            columns = df.columns.tolist()
            for c in columns:
                if c  not in all_columns:
                    all_columns.append(c)
        
        return all_columns


    def time_series_dict_combine(self,dfs,request):
        '''function to check is here common columns or not if not retun error'''
        all_columns = {}
        test_columns =[]
        
            
        for key, value  in dfs.items():
            df = value 
            df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '').str.replace('.', '_').str.replace(',','_').str.replace('/','_').str.replace(':','')
            columns = df.columns.tolist()
            missing_data=None
            for c in columns:
                try:
                    cu =  c+'_select'
                    missing_data = request.POST[cu]
                    
                except:
                    pass
                if missing_data and missing_data == 'delete_column':
                    pass
                else:
                    all_columns[key+'._:'+c] = key+':'+c
                    test_columns.append(c)
                
        common_columns = list(dict.fromkeys(test_columns))
        if  len(dfs) == 1:
            return all_columns

        if len(test_columns)<=0 or not  len(common_columns)<len(test_columns):
            data ={'Error':"files cannot be murged there are no common  columns"}
            return data
        else:
            return all_columns
    def relation_dict_combine(self,dfs,request):
        '''function to check is here common columns or not if not retun error'''
        all_columns = {}
        test_columns=[]
        for key, value  in dfs.items():
            df = value 
            df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '').str.replace('.', '_').str.replace(',','_').str.replace('/','_').str.replace(':','')
            columns = df.columns.tolist()

            for c in columns:
                missing_data = None
                try:
                    cu =  c+'_select'
                    missing_data = request.POST[cu]
                    
                except:
                    pass
                if missing_data and missing_data == 'delete_column':
                    pass
                    
                else:
                    all_columns[key+'._:'+c] = key+':'+c
                    test_columns.append(c)
                
                
        common_columns = list(dict.fromkeys(test_columns))
        if len(dfs) == 1:
            return all_columns
        if len(test_columns)<=0 or not  len(common_columns)<len(test_columns):
            data ={'Error':"files cannot be murged there is no common   columns"}
            return data
        else:
            return all_columns
    def relation_dict_combine_add_on(self,dfs):
        '''function to check is here common columns or not if not retun error'''
        all_columns = {}
        test_columns=[]
        for key, value  in dfs.items():
            df = value 
            df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '').str.replace('.', '_').str.replace(',','_').str.replace('/','_').str.replace(':','')
            columns = df.columns.tolist()
            for c in columns:
                
                all_columns[key+'._:'+c] = key+':'+c
                test_columns.append(c)
        common_columns = list(dict.fromkeys(test_columns))
        if len(dfs) == 1:
            return all_columns
        else:
            return all_columns
            

    def list_combine_with_datatype(self,dfs):
        ''' function to check is here common columns or not if not return error'''
        all_columns = {}
        column_nan = {}
        for key, value  in dfs.items():
            df = value 
            df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '').str.replace('.', '_').str.replace(',','_').str.replace('/','_').str.replace(':','')
            columns = df.columns.tolist()
            for c in columns:
                count = str(df[c].isnull().sum())
                column_nan[c]= count
                if df.dtypes[c] == np.int64:
                    all_columns[c] = 0
                elif df.dtypes[c] == np.float64:
                    all_columns[c] = 0.0
                elif df.dtypes[c] == np.object:
                    all_columns[c] = "None"
                elif df.dtypes[c] == np.bool:
                    all_columns[c] = "None"
                elif np.issubdtype(df[c].dtype, np.datetime64):
                    all_columns[c] = "None"

        data = {'all_columns':all_columns,'column_nan':column_nan}
       
        return data
    def list_combine_with_datatype_integration(self,dfs,columns):
        ''' function to check is here common columns or not if not return error'''
        all_columns = {}
        column_nan = {}
        for value in dfs:
            df = value 
            df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '').str.replace('.', '_').str.replace(',','_').str.replace('/','_').str.replace(':','')
            
            for c in columns:
                count = str(df[c].isnull().sum())
                column_nan[c]= count
                if df.dtypes[c] == np.int64:
                    all_columns[c] = 0
                elif df.dtypes[c] == np.float64:
                    all_columns[c] = 0.0
                elif df.dtypes[c] == np.object:
                    all_columns[c] = "None"
        data = {'all_columns':all_columns,'column_nan':column_nan}
       
        return data

'''class to identify the wether the given relation primarykey column is duplicated or not'''
class CheckPrimarykey:
    def __init__(self):
        pass

    def primarykey_check(self,dfs,primarykey,foreignkey):
        '''function to check the chosen primery key is duplicated or not'''
        primary_key_df =dfs[primarykey['file']] 
        primary_column = primarykey['column']
        foreign_key_df =dfs[foreignkey['file']] 
        foreign_column = foreignkey['column']
        l = [primary_column]
        # #print("dfs",dfs)
        colum_count = primary_key_df[primary_column].count()
        duplicate_removed = primary_key_df.drop_duplicates(subset=l,inplace=True)
        duplicate_removed_count  = primary_key_df[primary_column].count()
        primay_column_dtype = primary_key_df.dtypes[primary_column]  
        foreign_column_dtype = foreign_key_df.dtypes[foreign_column]
        # #print(primay_column_dtype,foreign_column_dtype)
        if primay_column_dtype == foreign_column_dtype:
            pass
        if duplicate_removed_count == colum_count:
            # #print(duplicate_removed_count,colum_count)

            p_key = True
        else:
            #print(duplicate_removed_count,colum_count)
            p_key = False 
        return p_key
                

'''class to delete the column from the  dataframe'''
class DeleteColumn:
    def __init__(self,df):
        self.df = df

    def delete_column(self,l):
        df = self.df
        df.drop(columns=l,inplace=True)
        return df

class SchmaCheck:
    def __init__(self,files):
        pass

    def schema_check(self,files,project,project_schema,meta_data):
        
        all_dfs = {}
        schema_dict = project_schema.schema


        error=False
        for file in files:
            schema={}
            file_name = str(file)
            
            file_name = str(file)
            file_name_str = file_name.split('.')
            #print("file_name",file_name_str)
            
            if file_name_str[-1] == 'csv':
                df = pd.read_csv(file,encoding = "utf-8")
                df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '').str.replace('.', '_').str.replace(',','_').str.replace('/','_')

                df_colums = df.columns.tolist()
                columns = ''
                for c in df_colums:
                    columns = columns+','+c
                columns = columns[1:]
                

                
                schema['columns']=columns
                schema['file_name']= str(file)
                schema['csv'] = True
                schema['delemeter'] = ','
                if file_name in schema_dict.keys():
                    schema_dict[file_name]['columns'] = columns
                else:
                    schema_dict[file_name] = schema



                meta_columns = meta_data.columns['columns']
                #print("the meta columns are",meta_columns,columns)
                
                    
                all_dfs[file_name]=df
                

                
            
            elif file_name_str[-1] == 'xlsx':
                df = pd.read_excel(file, encoding='utf-8')
                df.columns =  df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '').str.replace('.', '_').str.replace(',','_').str.replace('/','_')
                df_colums = df.columns.to_list()
                columns = df.columns.to_list()
                columns = ''
                for c in df_colums:
                    columns = columns+','+c
                columns = columns[1:]
                schema['columns']=columns
                schema['file_name']= str(file)
                schema['csv']=False
                schema['delemeter']=''
                if file_name in schema_dict.keys():
                    schema_dict[file_name]['columns'] = columns
                else:
                    schema_dict[file_name] = schema

                
                all_dfs[file_name]=df
            
        if error:
            data={'error':"schema not matching"}
            return data
        else:
            data={'all_df':all_dfs,'schema_dict':schema_dict}
            return data





                
        




