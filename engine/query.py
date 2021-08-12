import io
import sys
import json
import json
import pandas as pd
from . import optimize
import re
from coreapp.models import ProjectJsonStorage,Project, ProjectMetaData, ProjectQuery
import ast
from engine.date_selector import TimeManage
from datetime import datetime




def subset(pk,frequency,keyword_value,start_date=None,end_date=None,grouping_columns=[],where=None,aggregation=None,date_column=None,date_column_format=None):
    '''this function is to run query on the date series dataset'''
    print()
    project = Project.objects.get(pk=pk)
    project_meta,created = ProjectMetaData.objects.get_or_create(project=project)
    if project_meta.date_column_name:
        date_field = project_meta.date_column_name
        


    # print("before the engine query",datetime.now())
    
    try:
        # print("not Error")
        result_df = optimize.index_optimize(start_date,pk,end_date)
        # print(" not Error data")
        
    except:
        result_df= "Error"
        # print("Error in optimizer" )
        return result_df

    # print("the df columns are ",res_df.columns)
    if where:
        
        try:
            
            results = result_df.query(where)
            
           
        except:
            
                
            msg= "Error"
            print("Error")
            return msg

    else:
        results=result_df

    #creating the object for class to execute the query
    # print("after optimizer",results)
    query_object = TimeManage(results)
    if frequency or aggregation or grouping_columns:
        print("")
        if project_meta.date_column_name:
            date_field = project_meta.date_column_name
        else:
            date_field=None

        if date_field:
            result_df = query_object.keyword_based_date_range_selection(frequency,keyword_value,aggfunc=aggregation,date_column=date_field,date_column_format=date_column_format,grouping_colums=grouping_columns)
        else:
            result_df = query_object.no_time_series_pivot_table(aggfunc=aggregation,date_column=date_field,date_column_format=date_column_format,grouping_colums=grouping_columns)

        try:
            result_empty = result_df.empty

            # print("the dataframe empty",result_empty)
            # print("after the engine query",datetime.now())
            return result_df
        except:
            result_df=  'Error'
            print("error in group")
            # print("after the engine query",datetime.now())
            return result_df
        
    else:
        # print("after the engine query",datetime.now())
        return results

   
    # if start_date and end_date:
    #     new_json=result_df.to_json(orient='index')
    #     update = ProjectQuery.objects.filter(pk=project_query.pk).update(js_storage=new_json)
    



    # if start_date and end_date:
    #     if multiple_query:
    #         print("multiple query called")
    #         res_df = optimize.index_optimize(start_date,pk,end_date,multiple_query)
    #
    #         res_df[date_column] = pd.to_datetime(res_df[date_column])
    #         res_df = res_df.set_index(date_column)
    #
    #     else:
    #         print("no multiple query called")
    #         res_df = optimize.index_optimize(start_date,pk,end_date)
    #         res_df[date_column] = pd.to_datetime(res_df[date_column])
    #         res_df = res_df.set_index(date_column)
    #         print("the mached results indexed with date",res_df)
    #
    #
    #     if columns:
    #         if group:
    #             if where:
    #                 if aggrigation:
    #                     res_df['Clicks'] = res_df['Clicks'].astype(float)
    #                     res_df['Impressions'] = res_df['Impressions'].astype(float)
    #
    #                     print(res_df.columns.to_list())
    #                     df = res_df[columns]
    #                     results = df.query(where)
    #                     print("results",results)
    #
    #                     groupby_res = results.groupby(group).agg(aggrigation)
    #                     groupby_res.sort()
    #
    #
    #                 else:
    #                     print("colums list", columns)
    #                     print(res_df.columns.to_list())
    #                     column_res = res_df[columns]
    #                     df = res_df
    #                     print("after multiple selection",column_res.columns.to_list())
    #                     df = df.query(where)
    #                     groupby_res = df.groupby(group)
    #
    #
    #
    #
    #             elif aggrigation:
    #                 res_df['Clicks'] = res_df['Clicks'].astype(float)
    #                 res_df['Impressions'] = res_df['Impressions'].astype(float)
    #                 print()
    #                 column_res = res_df[columns]
    #                 print()
    #                 groupby_res = column_res.groupby(group).agg(aggrigation)
    #
    #             else:
    #                 print()
    #                 column_res = res_df[columns]
    #                 print()
    #                 groupby_res = column_res.groupby(group)
    #
    #             print("group by results",groupby_res.head(30))
    #             return(groupby_res)
    #         elif where:
    #             if aggrigation:
    #                 res_df['Clicks'] = res_df['Clicks'].astype(float)
    #                 res_df['Impressions'] = res_df['Impressions'].astype(float)
    #                 print("colums list", columns)
    #                 print(res_df.columns.to_list())
    #                 results = df.query(where)
    #                 print("where filter results",results.head(80))
    #                 return(results.agg(aggrigation))
    #             else:
    #
    #                 print("colums list", columns)
    #                 print(res_df.columns.to_list())
    #                 df = res_df
    #                 results = df.query(where)
    #                 print("where filter results",results.head(80))
    #                 return(results)
    #
    #
    #         else:
    #             column_res = res_df[columns]
    #             print(column_res)
    #             return(column_res)
    #     else:
    #         if group:
    #             if where:
    #                 if aggrigation:
    #                     res_df['Clicks'] = res_df['Clicks'].astype(float)
    #                     res_df['Impressions'] = res_df['Impressions'].astype(float)
    #                     df = res_df
    #                     print("after multiple selection",df.columns.to_list())
    #                     results = df.query(where)
    #                     groupby_res = results.groupby(group).agg(aggrigation)
    #
    #
    #                 else:
    #                     column_res = res_df
    #                     print("after multiple selection",column_res.columns.to_list())
    #                     filter = where
    #                     results = df.query(where)
    #                     groupby_res = results.groupby(group)
    #
    #
    #
    #
    #             elif aggrigation:
    #                 res_df['Clicks'] = res_df['Clicks'].astype(float)
    #                 res_df['Impressions'] = res_df['Impressions'].astype(float)
    #                 print()
    #                 column_res = res_df[columns]
    #                 print()
    #                 groupby_res = column_res.groupby(group).agg(aggrigation)
    #
    #             else:
    #                 column_res = res_df
    #                 print()
    #                 groupby_res = column_res.groupby(group)
    #
    #             print("group by results",groupby_res.head(30))
    #             return(groupby_res)
    #         elif where:
    #             if aggrigation:
    #                 res_df['Clicks'] = res_df['Clicks'].astype(float)
    #                 res_df['Impressions'] = res_df['Impressions'].astype(float)
    #                 df = res_df
    #
    #                 results = df.query(where)
    #                 print("where filter results",results.head(30))
    #                 return(final_res.agg(aggrigation))
    #             else:
    #                 res_df['Clicks'] = res_df['Clicks'].astype(float)
    #                 res_df['Impressions'] = res_df['Impressions'].astype(float)
    #                 df = res_df
    #
    #                 results = df.query(where)
    #                 print("where filter results",results.head(30))
    #                 return(results)
    #         else:
    #             return(res_df)
    #
    # if date_column:
    #
    #     if start_date and end_date:
    #         if multiple_query:
    #             print("multiple query called")
    #             res_df = optimize.index_optimize(start_date,pk,end_date,multiple_query)
    #
    #             res_df[date_column] = pd.to_datetime(res_df[date_column])
    #             res_df = res_df.set_index(date_column)
    #
    #         else:
    #             print("no multiple query called")
    #             res_df = optimize.index_optimize(start_date,pk,end_date)
    #             res_df[date_column] = pd.to_datetime(res_df[date_column])
    #             res_df = res_df.set_index(date_column)
    #             print("the mached results indexed with date",res_df)
    #
    #
    #         if columns:
    #             if group:
    #                 if where:
    #                     if aggrigation:
    #                         res_df['Clicks'] = res_df['Clicks'].astype(float)
    #                         res_df['Impressions'] = res_df['Impressions'].astype(float)
    #
    #                         print(res_df.columns.to_list())
    #                         df = res_df[columns]
    #                         results = df.query(where)
    #                         print("results",results)
    #
    #                         groupby_res = results.groupby(group).agg(aggrigation)
    #                         groupby_res.sort()
    #
    #
    #                     else:
    #                         print("colums list", columns)
    #                         print(res_df.columns.to_list())
    #                         column_res = res_df[columns]
    #                         df = res_df
    #                         print("after multiple selection",column_res.columns.to_list())
    #                         df = df.query(where)
    #                         groupby_res = df.groupby(group)
    #
    #
    #
    #
    #                 elif aggrigation:
    #                     res_df['Clicks'] = res_df['Clicks'].astype(float)
    #                     res_df['Impressions'] = res_df['Impressions'].astype(float)
    #                     print()
    #                     column_res = res_df[columns]
    #                     print()
    #                     groupby_res = column_res.groupby(group).agg(aggrigation)
    #
    #                 else:
    #                     print()
    #                     column_res = res_df[columns]
    #                     print()
    #                     groupby_res = column_res.groupby(group)
    #
    #                 print("group by results",groupby_res.head(30))
    #                 return(groupby_res)
    #             elif where:
    #                 if aggrigation:
    #                     res_df['Clicks'] = res_df['Clicks'].astype(float)
    #                     res_df['Impressions'] = res_df['Impressions'].astype(float)
    #                     print("colums list", columns)
    #                     print(res_df.columns.to_list())
    #                     results = df.query(where)
    #                     print("where filter results",results.head(80))
    #                     return(results.agg(aggrigation))
    #                 else:
    #
    #                     print("colums list", columns)
    #                     print(res_df.columns.to_list())
    #                     df = res_df
    #                     results = df.query(where)
    #                     print("where filter results",results.head(80))
    #                     return(results)
    #
    #
    #             else:
    #                 column_res = res_df[columns]
    #                 print(column_res)
    #                 return(column_res)
    #         else:
    #             if group:
    #                 if where:
    #                     if aggrigation:
    #                         res_df['Clicks'] = res_df['Clicks'].astype(float)
    #                         res_df['Impressions'] = res_df['Impressions'].astype(float)
    #                         df = res_df
    #                         print("after multiple selection",df.columns.to_list())
    #                         results = df.query(where)
    #                         groupby_res = results.groupby(group).agg(aggrigation)
    #
    #
    #                     else:
    #                         column_res = res_df
    #                         print("after multiple selection",column_res.columns.to_list())
    #                         filter = where
    #                         results = df.query(where)
    #                         groupby_res = results.groupby(group)
    #
    #
    #
    #
    #                 elif aggrigation:
    #                     res_df['Clicks'] = res_df['Clicks'].astype(float)
    #                     res_df['Impressions'] = res_df['Impressions'].astype(float)
    #                     print()
    #                     column_res = res_df[columns]
    #                     print()
    #                     groupby_res = column_res.groupby(group).agg(aggrigation)
    #
    #                 else:
    #                     column_res = res_df
    #                     print()
    #                     groupby_res = column_res.groupby(group)
    #
    #                 print("group by results",groupby_res.head(30))
    #                 return(groupby_res)
    #             elif where:
    #                 if aggrigation:
    #                     res_df['Clicks'] = res_df['Clicks'].astype(float)
    #                     res_df['Impressions'] = res_df['Impressions'].astype(float)
    #                     df = res_df
    #
    #                     results = df.query(where)
    #                     print("where filter results",results.head(30))
    #                     return(final_res.agg(aggrigation))
    #                 else:
    #                     res_df['Clicks'] = res_df['Clicks'].astype(float)
    #                     res_df['Impressions'] = res_df['Impressions'].astype(float)
    #                     df = res_df
    #
    #                     results = df.query(where)
    #                     print("where filter results",results.head(30))
    #                     return(results)
    #             else:
    #                 return(res_df)
    #
    #     elif start_date:
    #
    #         if multiple_query:
    #             res_df = optimize.index_optimize(start_date,pk,multiple_query)
    #
    #             res_df[date_column] = pd.to_datetime(res_df[date_column])
    #             res_df.set_index(date_column)
    #         else:
    #             res_df = optimize.index_optimize(start_date,pk)
    #
    #             res_df[date_column] = pd.to_datetime(res_df[date_column])
    #             res_df.set_index(date_column)
    #
    #         if columns:
    #             if group:
    #                 if where:
    #                     if aggrigation:
    #                         res_df['Clicks'] = res_df['Clicks'].astype(float)
    #                         res_df['Impressions'] = res_df['Impressions'].astype(float)
    #                         print("colums list", columns)
    #                         print(res_df.columns.to_list())
    #                         df = res_df[columns]
    #                         print("after multiple selection",df.columns.to_list())
    #                         results = df.query(where)
    #                         groupby_res = results.groupby(group).agg(aggrigation)\
    #
    #
    #                     else:
    #                         print("colums list", columns)
    #                         print(res_df.columns.to_list())
    #                         column_res = res_df[columns]
    #                         results = df.query(where)
    #                         groupby_res = results.groupby(group)
    #
    #
    #
    #
    #                 elif aggrigation:
    #                     res_df['Clicks'] = res_df['Clicks'].astype(float)
    #                     res_df['Impressions'] = res_df['Impressions'].astype(float)
    #                     print()
    #                     column_res = res_df[columns]
    #                     print()
    #                     groupby_res = column_res.groupby(group).agg(aggrigation)
    #
    #                 else:
    #                     print()
    #                     column_res = res_df[columns]
    #                     print()
    #                     groupby_res = column_res.groupby(group)
    #
    #                 print("group by results",groupby_res.head(30))
    #                 return(groupby_res)
    #             elif where:
    #                 if aggrigation:
    #                     res_df['Clicks'] = res_df['Clicks'].astype(float)
    #                     res_df['Impressions'] = res_df['Impressions'].astype(float)
    #                     print("colums list", columns)
    #                     print(res_df.columns.to_list())
    #                     df = res_df[columns]
    #
    #                     results = df.query(where)
    #                     print("where filter results",results.head(30))
    #                     return(final_res.agg(aggrigation))
    #                 else:
    #                     print("colums list", columns)
    #                     print(res_df.columns.to_list())
    #                     df = res_df[columns]
    #
    #                     results = df.query(where)
    #                     print("where filter results",results.head(30))
    #                     return(final_res)
    #
    #
    #             else:
    #                 column_res = res_df[columns]
    #                 print(column_res)
    #                 return(column_res)
    #         else:
    #             if group:
    #                 if where:
    #                     if aggrigation:
    #                         res_df['Clicks'] = res_df['Clicks'].astype(float)
    #                         res_df['Impressions'] = res_df['Impressions'].astype(float)
    #                         df = res_df
    #                         print("after multiple selection",df.columns.to_list())
    #                         results = df.query(where)
    #                         groupby_res = results.groupby(group).agg(aggrigation)
    #
    #
    #                     else:
    #                         column_res = res_df
    #                         print("after multiple selection",column_res.columns.to_list())
    #                         filter = where
    #                         results = df.query(where)
    #                         groupby_res = results.groupby(group)
    #
    #
    #
    #
    #                 elif aggrigation:
    #                     res_df['Clicks'] = res_df['Clicks'].astype(float)
    #                     res_df['Impressions'] = res_df['Impressions'].astype(float)
    #                     print()
    #                     column_res = res_df[columns]
    #                     print()
    #                     groupby_res = column_res.groupby(group).agg(aggrigation)
    #
    #                 else:
    #                     column_res = res_df
    #                     print()
    #                     groupby_res = column_res.groupby(group)
    #
    #                 print("group by results",groupby_res.head(30))
    #                 return(groupby_res)
    #             elif where:
    #                 if aggrigation:
    #                     res_df['Clicks'] = res_df['Clicks'].astype(float)
    #                     res_df['Impressions'] = res_df['Impressions'].astype(float)
    #                     df = res_df
    #
    #                     results = df.query(where)
    #                     print("where filter results",results.head(30))
    #                     return(final_res.agg(aggrigation))
    #                 else:
    #                     df = res_df
    #
    #                     results = df.query(where)
    #                     print("where filter results",results.head(30))
    #                     return(final_res)
    #             else:
    #                 return(res_df)
    #
    #     else:
    #         json_storage = ProjectJsonStorage.objects.filter(project=project)
    #         dfs  = []
    #         for ind in json_storage:
    #             # print("the matched results",ind.json_storage.js)
    #
    #             json_st = json.loads(ind.js)
    #             json_df = pd.DataFrame(json_st)
    #             transposed_df = json_df.transpose()
    #             columns = transposed_df.columns.to_list()
    #             dfs.append(transposed_df)
    #         res_df = pd.concat(dfs)
    #         res_df[date_column] = pd.to_datetime(res_df[date_column])
    #         res_df.set_index(date_column)
    #
    #         if columns:
    #             if group:
    #                 if where:
    #                     if aggrigation:
    #                         res_df['Clicks'] = res_df['Clicks'].astype(float)
    #                         res_df['Impressions'] = res_df['Impressions'].astype(float)
    #                         print("colums list", columns)
    #                         print(res_df.columns.to_list())
    #                         df = res_df[columns]
    #                         print("after multiple selection",df.columns.to_list())
    #
    #                         results = df.query(where)
    #                         groupby_res = results.groupby(group).agg(aggrigation)
    #
    #
    #                     else:
    #                         print("colums list", columns)
    #                         print(res_df.columns.to_list())
    #                         column_res = res_df[columns]
    #                         print("after multiple selection",column_res.columns.to_list())
    #                         filter = where
    #                         df = res_df
    #                         results = df.query(where)
    #                         print("where_query",results)
    #                         groupby_res = results.groupby(group)
    #
    #
    #
    #
    #                 elif aggrigation:
    #                     res_df['Clicks'] = res_df['Clicks'].astype(float)
    #                     res_df['Impressions'] = res_df['Impressions'].astype(float)
    #                     print()
    #                     column_res = res_df[columns]
    #                     print()
    #                     groupby_res = column_res.groupby(group).agg(aggrigation)
    #
    #                 else:
    #                     print()
    #                     column_res = res_df[columns]
    #                     print()
    #                     groupby_res = column_res.groupby(group)
    #
    #                 print("group by results",groupby_res.head(30))
    #                 return(groupby_res)
    #             elif where:
    #                 if aggrigation:
    #                     df=res_df
    #                     df = res_df
    #
    #                     results = df.query(where)
    #                     print("where filter results",results.head(30))
    #                     return(results.agg(aggrigation))
    #                 else:
    #
    #                     df=res_df
    #                     df = res_df
    #
    #                     results = df.query(where)
    #                     print("where filter results",results.head(30))
    #                     return(results)
    #             else:
    #                 column_res = res_df[columns]
    #                 print(column_res)
    #                 return(column_res)
    #         else:
    #             if group:
    #                 if where:
    #                     if aggrigation:
    #                         res_df['Clicks'] = res_df['Clicks'].astype(float)
    #                         res_df['Impressions'] = res_df['Impressions'].astype(float)
    #
    #                         df = res_df
    #                         print("after multiple selection",df.columns.to_list())
    #                         results = df.query(where)
    #                         groupby_res = results.groupby(group).agg(aggrigation)
    #
    #
    #                     else:
    #                         column_res = res_df
    #                         print("after multiple selection",column_res.columns.to_list())
    #                         results = df.query(where)
    #                         groupby_res = results.groupby(group)
    #
    #
    #
    #
    #                 elif aggrigation:
    #                     res_df['Clicks'] = res_df['Clicks'].astype(float)
    #                     res_df['Impressions'] = res_df['Impressions'].astype(float)
    #                     print()
    #                     column_res = res_df[columns]
    #                     print()
    #                     groupby_res = column_res.groupby(group).agg(aggrigation)
    #
    #                 else:
    #                     column_res = res_df
    #                     print()
    #                     groupby_res = column_res.groupby(group)
    #
    #                 print("group by results",groupby_res.head(30))
    #                 return(groupby_res)
    #             elif where:
    #                 if aggrigation:
    #                     res_df['Clicks'] = res_df['Clicks'].astype(float)
    #                     res_df['Impressions'] = res_df['Impressions'].astype(float)
    #                     df = res_df
    #
    #                     results = df.query(where)
    #                     print("where filter results",results.head(30))
    #                     return(results.agg(aggrigation))
    #                 else:
    #
    #
    #                     df = res_df
    #
    #                     results = df.query(where)
    #                     print("where filter results",results.head(30))
    #                     return(results)
    #             else:
    #                 return(res_df)
    # else:
    #     print("theelse part ")
    #     json_storage = ProjectJsonStorage.objects.filter(project=project)
    #     dfs  = []
    #     for ind in json_storage:
    #         # print("the matched results",ind.json_storage.js)
    #
    #         json_st = json.loads(ind.js)
    #         json_df = pd.DataFrame(json_st)
    #         transposed_df = json_df.transpose()
    #         columns = transposed_df.columns.to_list()
    #         dfs.append(transposed_df)
    #     res_df = pd.concat(dfs)
    #
    #     if columns:
    #         if group:
    #             if where:
    #                 if aggrigation:
    #                     res_df['Clicks'] = res_df['Clicks'].astype(float)
    #                     res_df['Impressions'] = res_df['Impressions'].astype(float)
    #                     print("colums list", columns)
    #                     print(res_df.columns.to_list())
    #                     df = res_df[columns]
    #                     print("after multiple selection",df.columns.to_list())
    #
    #                     results = df.query(where)
    #                     groupby_res = results.groupby(group).agg(aggrigation)
    #
    #
    #                 else:
    #                     print("colums list", columns)
    #                     print(res_df.columns.to_list())
    #                     column_res = res_df[columns]
    #                     print("after multiple selection",column_res.columns.to_list())
    #                     filter = where
    #                     df = res_df
    #                     results = df.query(where)
    #                     print("where_query",results)
    #                     groupby_res = results.groupby(group)
    #
    #
    #
    #
    #             elif aggrigation:
    #                 res_df['Clicks'] = res_df['Clicks'].astype(float)
    #                 res_df['Impressions'] = res_df['Impressions'].astype(float)
    #                 print()
    #                 column_res = res_df[columns]
    #                 print()
    #                 groupby_res = column_res.groupby(group).agg(aggrigation)
    #
    #             else:
    #                 print()
    #                 column_res = res_df[columns]
    #                 print()
    #                 groupby_res = column_res.groupby(group)
    #
    #             print("group by results",groupby_res.head(30))
    #             return(groupby_res)
    #         elif where:
    #             df=res_df
    #             df = res_df
    #
    #             results = df.query(where)
    #             print("where filter results",results.head(30))
    #             return(results)
    #         else:
    #             column_res = res_df[columns]
    #             print(column_res)
    #             return(column_res)
    #     else:
    #         if group:
    #             if where:
    #                 if aggrigation:
    #
    #                     df = res_df
    #                     print("after multiple selection",df.columns.to_list())
    #                     results = df.query(where)
    #                     groupby_res = results.groupby(group).agg(aggrigation)
    #
    #
    #                 else:
    #                     column_res = res_df
    #                     print("after multiple selection",column_res.columns.to_list())
    #                     results = df.query(where)
    #                     groupby_res = results.groupby(group)
    #
    #
    #
    #
    #             elif aggrigation:
    #                 print()
    #                 column_res = res_df[columns]
    #                 print()
    #                 groupby_res = column_res.groupby(group).agg(aggrigation)
    #
    #             else:
    #                 column_res = res_df
    #                 print()
    #                 groupby_res = column_res.groupby(group)
    #
    #             print("group by results",groupby_res.head(30))
    #             return(groupby_res)
    #         elif where:
    #
    #             df = res_df
    #
    #             results = df.query(where)
    #             print("where filter results",results.head(30))
    #             return(results)



def Subset_with_df(df,project,frequency,keyword_value,start_date=None,end_date=None,grouping_columns=[],where=None,aggregation=None,date_column=None,date_field=None):
    '''this function is to run query on the date series dataset'''
   
    # project = Project.objects.get(pk=pk)
    # project_meta,created = ProjectMetaData.objects.get_or_create(project=project)
    # if project_meta.date_column_name:
    #     date_field = project_meta.date_column_name
    # else:
    #     date_field=None
    
    if start_date and end_date:
        from_date = start_date
        to_date = end_date
        mask = (df[date_field] > from_date) & (df[date_field] <= to_date)
        result_df = df.loc[mask]
    elif start_date and not end_date:
        to_date = datetime.now().date()
        from_date = start_date
        mask = (df[date_field] > from_date) & (df[date_field] <= to_date)
        result_df = df.loc[mask]
    else:
        result_df=df



    # print("the df columns are ",res_df.columns)
    if where:
        
        try:
            
            results = result_df.query(where)
            
           
        except:
            
                
            msg= "Error"
            # print("Error")
            return msg

    else:
        results=result_df

    #creating the object for class to execute the query
    # print("after optimizer",results)
    query_object = TimeManage(results)
    if frequency or aggregation or grouping_columns:
        # print("")
        # if project_meta.date_column_name:
        #     date_field = project_meta.date_column_name
        # else:
        #     date_field=None

        if date_field:
            result_df = query_object.keyword_based_date_range_selection(frequency,keyword_value,aggfunc=aggregation,date_column=date_field,date_column_format=date_field,grouping_colums=grouping_columns)
        else:
            result_df = query_object.no_time_series_pivot_table(aggfunc=aggregation,date_column=date_field,date_field=date_field,grouping_colums=grouping_columns)

        try:
            result_empty = result_df.empty

            # print("the dataframe empty",result_empty)
            # print("after the engine query",datetime.now())
            return result_df
        except:
            result_df=  'Error'
            # print("error in group")
            # print("after the engine query",datetime.now())
            return result_df
        
    else:
        # print("after the engine query",datetime.now())
        return results










class WhereClouse:
    '''this is the class  used to filter the data based on user requirements'''
    def __init__(self):
        pass

    def filter_data(self,df,query_set):
        '''fuction to execute the given query'''
        filter_result_df = df.query(query_set)
        return filter_result_df


class GroupBY:
    '''this is an class to execute all grouping of data or results from WhereClouse'''
    def __init__(self):
        pass

    def data_group(self,df,group):
        '''function to group the where_query results or group the data on given statment'''
        group_results_df = df.groupby(group)
        return group_results_df


class Aggregator():
    def _init_(self):
        pass

    def independent_value_modify(self, value, function, param=[]):
        """
        Example: independent_value_modify(33.5, integer)
                    returns 34
                independent_value_modify(33.5, floor)
                    returns 33
                independent_value_modify(33.56789, precision, [2,])
                    return 33.57
        """
        if function == 'round':
            return int(value)
        elif function == 'floor':
            return floor(value)
        elif function == 'precision':
            return precision(value, param)

    def dependent_value_modify (self, value,condition, reference=[]):
        # i think we will have a use case of this one .. but can't think of anything now
        pass

    def type_conversion(self, value, convert_to='str'):
        if convert_to == 'str':
            return str(value)
        elif convert_to == 'int':
            return int(value)
        # else:
        #     exec("convert_to(value)") # this is wrong syntax and should be fixed.

    def many_to_one(self, function, df):
        # if function == 'mean':
        #     return array.mean()
        # elif function == 'median':
        #     return array.median()
        # elif function == 'max':
        #     return array.max()
        # elif function == 'min':
        #     return array.min()
        new_df =df.agg(function)

        return new_df




class DateAggregator(Aggregator):
    def _init_(self):
        pass
    def get_new_df_with_date_control(self, current_df, date_column,function):
        # new_df = pd.DataFrame()
        new_df = current_df.resample(function)
        # split into year, month, date, day_of_week, hour, min, sec
        return new_df
