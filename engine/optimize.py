import os
import sys
import json
from functools import reduce, partial
import pandas as pd
from coreapp.models import ProjectIndex, Project,ProjectJsonStorage,ProjectMetaData
import json
from datetime import datetime, timedelta
from django.db.models import Q,F

def index_optimize(start_date,pk,end_date=None):
    '''function to return the filtered json storage objects to optimize the time'''

    project = Project.objects.get(pk=pk)
    js_stotages = []
    # print("single dump of the data")
    if start_date and end_date:
        project_meta,created = ProjectMetaData.objects.get_or_create(project=project)
        if project_meta.date_column_name:
            date_field = project_meta.date_column_name
        else:
            date_field = None
        from_date = start_date
        to_date = end_date
        # indexes = ProjectIndex.objects.get(project=project)
        project_jsons = ProjectJsonStorage.objects.filter(project=project)
        # if date_field:
        #     indexes = ProjectIndex.objects.filter(Q(project=project)&(Q(start_date__range=(from_date, to_date)) | Q(end_date__range=(from_date, to_date)) ))
        # else:
        #     indexes = ProjectIndex.objects.filter(Q(project=project)&(Q(created__range=(from_date, to_date)) ))
        # print("the lengt of project index is ", len(indexes))
        # # if len(indexes)<= 0:
            
        # #     indexes = ProjectIndex.objects.filter(Q(project=project))

        dfs  = []
            
        for ind in project_jsons:
            json_st = json.loads(ind.js)
            # print("appended the df")
            json_df = pd.DataFrame(json_st)
            transposed_df = json_df.transpose()
            # print("appended the df")

            columns = transposed_df.columns.to_list()
            # print("appended the df")

            dfs.append(transposed_df)
            # print("appended the df",dfs)



        # print("concate the dfs")
        res_df = pd.concat(dfs)
        

        res_df[date_field] = pd.to_datetime(res_df[date_field])
        mask = (res_df[date_field] > from_date) & (res_df[date_field] <= to_date)

        res_df = res_df.loc[mask]
        # print("the resulted dataframe is from the optimizer",res_df)

        # print("optimizer time after",datetime.now())
        return res_df
    elif start_date:
        # print("only start data indexer")
        # print(" optimizer time before",datetime.now())
        project_meta,created = ProjectMetaData.objects.get_or_create(project=project)
        if project_meta.date_column_name:
            date_field = project_meta.date_column_name
        else:
            date_field = None

        to_date = datetime.now().date()
        from_date = start_date
        # print("from date amd to date",from_date, to_date)
        project_jsons = ProjectJsonStorage.objects.filter(project=project)
        # if date_field:
        #     indexes = ProjectIndex.objects.filter(Q(project=project)& Q(start_date__gte = from_date) )
        
        # else:
        #     indexes = ProjectIndex.objects.filter(Q(project=project)&(Q(created__range=(from_date, to_date)) ))
        # print("the length of indexer is ", len(indexes))
        # print("picking only the relevent jsons fo r query",indexes)
        # if len(indexes)<= 0:
            
        #     indexes = ProjectIndex.objects.filter(Q(project=project))
        #         # print("picking only the relevent jsons fo r query",indexes)
            
        dfs  = []
        for ind in project_jsons:
            json_st = json.loads(ind.js)
            json_df = pd.DataFrame(json_st)
            transposed_df = json_df.transpose()
            columns = transposed_df.columns.to_list()
            dfs.append(transposed_df)
        res_df = pd.concat(dfs)
        res_df[date_field] = pd.to_datetime(res_df[date_field])

        try:
            mask = (res_df[date_field] > from_date) 
            res_df = res_df.loc[mask]
            # print("else in optimizer time after",datetime.now())
            return res_df
        except:
            res_df= "Error"
            # print("else in optimizer time after",datetime.now())
            return res_df


    elif end_date:
    
        project_meta,created = ProjectMetaData.objects.get_or_create(project=project)
        if project_meta.date_column_name:
            date_field = project_meta.date_column_name
        else:
            date_field = None
        # print("th tet")
        to_date = end_date
        # print("the test")

        project_jsons = ProjectJsonStorage.objects.filter(project=project)
        # if date_field:

        #     indexes = ProjectIndex.objects.filter(Q(project=project) & Q(end_date__lte = to_date ))
        # else:
        #     indexes = ProjectIndex.objects.filter(Q(project=project) & Q(created__lte=to_date))
        # print("the length of indexer is ", len(indexes))
        # print("picking only the relevent jsons fo r query",indexes)
        # if len(indexes)<= 0:
            
        #     indexes = ProjectIndex.objects.filter(Q(project=project))
        #         # print("picking only the relevent jsons fo r query",indexes)
            
        dfs  = []
        for ind in project_jsons:
                # print("the matched results",ind.json_storage.js)

            json_st = json.loads(ind.js)
            json_df = pd.DataFrame(json_st)
            transposed_df = json_df.transpose()
            columns = transposed_df.columns.to_list()
            dfs.append(transposed_df)
        res_df = pd.concat(dfs)
        res_df[date_field] = pd.to_datetime(res_df[date_field])

        try:
            mask = (res_df[date_field] > from_date) 
            res_df = res_df.loc[mask]
            # print("else in optimizer time after",datetime.now())
            return res_df
        except:
            res_df= "Error"
            # print("else in optimizer time after",datetime.now())
            return res_df

    else:
        # print("else in optimizer time before",datetime.now())
        json_storage = ProjectJsonStorage.objects.filter(project=project)
        project_meta = ProjectMetaData.objects.get(project=project)
        if project_meta.date_column_name:
            date_field = project_meta.date_column_name
        else:
            date_field = None
            
        dfs  = []
        for ind in json_storage:
            # print("the matched results",ind.json_storage.js)

            json_st = json.loads(ind.js)
            json_df = pd.DataFrame(json_st)
            transposed_df = json_df.transpose()
            columns = transposed_df.columns.to_list()
            dfs.append(transposed_df)
        res_df = pd.concat(dfs)
        if date_field:

            res_df[date_field] = pd.to_datetime(res_df[date_field])
            
        # print("final results ",res_df)
        # print("else in optimizer time after",datetime.now())
        return res_df

def optimize_data(project,date_field):
    # project = Project.objects.get(pk=pk)
    json_storage = ProjectJsonStorage.objects.values_list('js').filter(project=project)
    # json_storage = ProjectJsonStorage.objects.filter(project=project)
    
    # project_meta = ProjectMetaData.objects.get(project=project)
    # if project_meta.date_column_name:
    #     date_field = project_meta.date_column_name
    # else:
    #     date_field = None
           
    dfs  = []
    for ind in json_storage:
        json_st = json.loads(ind[0])
        json_df = pd.DataFrame(json_st)
        transposed_df = json_df.transpose()
        columns = transposed_df.columns.to_list()
        dfs.append(transposed_df)
    res_df = pd.concat(dfs)
    if date_field:

        res_df[date_field] = pd.to_datetime(res_df[date_field])
            
    # print("final results ",res_df)
    # print("else in optimizer time after",datetime.now())
    return res_df


class ProjectJsonAlter:

    def __init__(self,jsons_meta):
        self.jsons_meta = jsons_meta


    def claculate_rows_columns(self):
        jsons_meta = self.jsons_meta
        rows = 0
        columns = 0
        for json_meta in jsons_meta:
            if json_meta.columns > columns  :
                columns = json_meta.columns

            
            rows = rows+json_meta.rows
        data={'rows':rows,'columns':columns}
        return data
    
    def dataframe_head_tail(self):
        jsons_meta = self.jsons_meta
        head_json  = jsons_meta[0].head_json
        json_st = json.loads(head_json)
        json_df = pd.DataFrame(json_st)
        res_df = json_df.transpose()
        return res_df






