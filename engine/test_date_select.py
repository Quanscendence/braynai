import os
import sys
import datetime
import numpy as np
import pandas as pd

from random import randrange, randint
from statistics import mean, median
import re

class Aggregator():
    def __init__(self):
        pass

    def many_to_one(self, func, values=[]):
        print(values)
        if func == 'max':
            return max(values)
        elif func == 'min':
            return min(values)
        elif func == 'mean' or func == 'avg':
            return mean(values)

class TimeManage():
    """
    Deals only with the dataframes that contains a column dedicated for date/time series
    The input can be in string format.
    This sets the platform for date based Aggregator
    """
    df = pd.DataFrame()

    def __init__(self, df):
        """
        constructor expecting a dataframe with valid dates/times
        """
        self.df = df
        self.min_interval_in_seconds = 99999999999



    def keyword_based_date_range_selection(self, keyword,keyword_value, aggfunc={},date_column=None, date_column_format="%Y-%m-%d %H:%M:%S", custom=[],grouping_colums=[],where=None):
        """
        this will create a subset of df
        # TODO:
        """
        expected_interval_for_aggregation_in_seconds = 0
        # working code with  converion of date limits commenting the below section for the testing of pivot tables and grouper below this section
        # need to use reg exp but there is problem with separating kewa_value ex:10min should be separated as 10 min
        # if keyword == 'custom':
        #     print("Currently not supported")
        #     exit()
        #
        # elif 'min' in keyword:
        #     expected_seconds = 60
        #     expected_interval_for_aggregation_in_seconds = expected_seconds*keyword_value
        # elif 'hour' in keyword:
        #     expected_seconds = 60*60
        #     expected_interval_for_aggregation_in_seconds = expected_seconds*keyword_value
        # elif 'day' in keyword:
        #     expected_seconds = 60*60*24
        #     expected_interval_for_aggregation_in_seconds = expected_seconds*keyword_value
        # elif 'week' in keyword:
        #     expected_seconds = 60*60*24*7
        #     expected_interval_for_aggregation_in_seconds = expected_seconds*keyword_value
        # elif 'month' in keyword:
        #     expected_seconds = 60*60*24*30
        #     expected_interval_for_aggregation_in_seconds = expected_seconds*keyword_value



        #uniquify  the date column from the dataframe



        # #now get the min_interval_in_seconds of the user
        # min_seconds = self.get_min_interval_in_seconds(date_column=date_column,format_of_date=date_column_format)
        #
        # print("the minimum interval seconds is", min_seconds)
        # print("expected_interval_for_aggregation_in_seconds", expected_interval_for_aggregation_in_seconds)
        # #compare the min_seconds and expected_interval_for_aggregation_in_seconds if min_seconds is greated than expected_inteval then as for now its error result_df.
        #
        # if expected_interval_for_aggregation_in_seconds > min_seconds:
        #     #calculating the range to split the dataframe
        #     range = int(expected_interval_for_aggregation_in_seconds/min_seconds)
        #     #split the dataframr into multipldf based on range
        #     splited_dfs = self.split_df_to_many(range)
        #
        #     date_value = []
        #     aggregation_value = []
        #     #here we get splited df according to range
        #     for df in splited_dfs:
        #         print("splited dfs ",df)
        #         value_df = df.iloc[:,value_column]
        #         # print("the value list is ",value_df)
        #         aggregation = Aggregator()
        #         #apply aggregation on each chucnk of divrded dataframe
        #         aggregation_result = aggregation.many_to_one(func,value_df)
        #         d = self.df.iloc[:,date_column]
        #         date_name = d.name
        #         print("the date name",date_name)
        #         #append the first vale o date field into date_value list
        #         date_value.append(df[date_name].iloc[0])
        #         #append the result of aggregation class into  aggregation_value list
        #         aggregation_value.append(aggregation_result)
        #     d = self.df.iloc[:,date_column]
        #     date_name = d.name
        #     v = self.df.iloc[:,value_column]
        #     value_name = v.name
        #
        #     #generate the dict from both date_value list and aggregation_value list
        #     frame = {date_name:date_value,value_name:aggregation_value}
        #     #create a result dataframe
        #     result_df = pd.DataFrame(frame)
        #     print("the results dataframe is ", result_df)
        #
        #     print("the expected range is",range)
        #
        # else:
        #     print("-F- the interval  range supporting is not found")
        #     exit()

        # todo
        # use self.df
        #print(self.df.iloc[0:range,1])
        # resulted_array = []
        # for v in self.df.iloc[0:range,value_column]:
        #     resulted_array.append(v)
        #
        #
        # agg = Aggregator()
        # return agg.many_to_one(func, resulted_array)


        # craeting the below  section for the testing of pivot table and grouper methods.
        df = self.df
        if aggfunc:
            if len(aggfunc)>0:

                for column, value in aggfunc.items():
                    # print("the converting column name is",  column)
                    try:
                        df[column] = df[column].astype(float)
                    except:
                        result_df="Error"


                    # print("the converted column name is",df.dtypes)
        #Todo should convert the numerical columns to numbered datatype]
        #for testing purpose e manually converted it


        # print("the  keyword  is ",keyword)
        # print("the date column is ",date_column)
        # print("the grouping_colums is ",grouping_colums)
        # print("the value column is ",value_column)
        # print("the aggrigation function is ",aggfunc)
        # print("in project query frequency",keyword)
        if keyword:

            if keyword == 'custom':
                # print("Currently not supported")
                exit()

            elif 'min' in keyword:
                expected_freq = 'M'
                # print("the date column is ",date_column)
                if where and aggfunc  and grouping_colums :
                    
                    try:
                        result_df = df.pivot_table(index= grouping_colums,columns =pd.Grouper(freq=expected_freq,key=date_column),fill_value=0,aggfunc=aggfunc,)
                        result_df = result_df.stack().reset_index()
                    except:
                        result_df="Error"
                elif not  where and aggfunc  and grouping_colums :
                    
                    try:
                        result_df = df.pivot_table(index= grouping_colums,columns =pd.Grouper(freq=expected_freq,key=date_column),fill_value=0,aggfunc=aggfunc,)
                        result_df = result_df.stack().reset_index()
                    except:
                        result_df="Error"
                elif where and aggfunc and not  grouping_colums:
                    try:
                        result_df = df.pivot_table(columns =pd.Grouper(freq=expected_freq,key=date_column),fill_value=0,aggfunc=aggfunc,)
                        # print("new type of query",result_df)
                        pv_df = result_df.transpose()
                        result_df = pv_df.reset_index()
                    except:
                        result_df="Error"
                elif not where and aggfunc and not  grouping_colums:
                    try:
                        result_df = df.pivot_table(columns =pd.Grouper(freq=expected_freq,key=date_column),fill_value=0,aggfunc=aggfunc,)
                        # print("new type of query",result_df)
                        pv_df = result_df.transpose()
                        result_df = pv_df.reset_index()
                    except:
                        result_df="Error"

                elif where and  grouping_colums  and not aggfunc:
                    try:
                        # print("year just grouping")
                        grouping_colums.append(date_column)
                        grouped_df =df.groupby(grouping_colums)
                        result_df = pd.DataFrame(grouped_df.size().reset_index(name = "Count"))
                    except:
                        result_df="Error"
                elif not where and  grouping_colums  and not aggfunc:
                    try:
                        # print("year just grouping")
                        grouping_colums.append(date_column)
                        grouped_df =df.groupby(grouping_colums)
                        result_df = pd.DataFrame(grouped_df.size().reset_index(name = "Count"))
                    except:
                        result_df="Error"

                elif where and expected_freq:
                    try:
                        # print("only frequency")
                        s_df = df.groupby(pd.Grouper(freq=expected_freq,key=date_column))
                        result_df = pd.DataFrame(s_df.size().reset_index(name = "Count"))
                        
                    except:
                        result_df="Error"
                elif not  where and expected_freq:
                    try:
                        # print("only frequency")
                        s_df = df.groupby(pd.Grouper(freq=expected_freq,key=date_column))
                        result_df = pd.DataFrame(s_df.size().reset_index(name = "Count"))
                        
                    except:
                        result_df="Error"


            elif 'hour' in keyword:
                expected_freq = 'H'
                # print("the date column is ",date_column)
                if where and aggfunc  and grouping_colums :
                    
                    try:
                        result_df = df.pivot_table(index= grouping_colums,columns =pd.Grouper(freq=expected_freq,key=date_column),fill_value=0,aggfunc=aggfunc,)
                        result_df = result_df.stack().reset_index()
                    except:
                        result_df="Error"
                elif not  where and aggfunc  and grouping_colums :
                    
                    try:
                        result_df = df.pivot_table(index= grouping_colums,columns =pd.Grouper(freq=expected_freq,key=date_column),fill_value=0,aggfunc=aggfunc,)
                        result_df = result_df.stack().reset_index()
                    except:
                        result_df="Error"
                elif where and aggfunc and not  grouping_colums:
                    try:
                        result_df = df.pivot_table(columns =pd.Grouper(freq=expected_freq,key=date_column),fill_value=0,aggfunc=aggfunc,)
                        # print("new type of query",result_df)
                        pv_df = result_df.transpose()
                        result_df = pv_df.reset_index()
                    except:
                        result_df="Error"
                elif not where and aggfunc and not  grouping_colums:
                    try:
                        result_df = df.pivot_table(columns =pd.Grouper(freq=expected_freq,key=date_column),fill_value=0,aggfunc=aggfunc,)
                        # print("new type of query",result_df)
                        pv_df = result_df.transpose()
                        result_df = pv_df.reset_index()
                    except:
                        result_df="Error"

                elif where and  grouping_colums  and not aggfunc:
                    try:
                        # print("year just grouping")
                        grouping_colums.append(date_column)
                        grouped_df =df.groupby(grouping_colums)
                        result_df = pd.DataFrame(grouped_df.size().reset_index(name = "Count"))
                    except:
                        result_df="Error"
                elif not where and  grouping_colums  and not aggfunc:
                    try:
                        # print("year just grouping")
                        grouping_colums.append(date_column)
                        grouped_df =df.groupby(grouping_colums)
                        result_df = pd.DataFrame(grouped_df.size().reset_index(name = "Count"))
                    except:
                        result_df="Error"

                elif where and expected_freq:
                    try:
                        # print("only frequency")
                        s_df = df.groupby(pd.Grouper(freq=expected_freq,key=date_column))
                        result_df = pd.DataFrame(s_df.size().reset_index(name = "Count"))
                        
                    except:
                        result_df="Error"
                elif not  where and expected_freq:
                    try:
                        # print("only frequency")
                        s_df = df.groupby(pd.Grouper(freq=expected_freq,key=date_column))
                        result_df = pd.DataFrame(s_df.size().reset_index(name = "Count"))
                        
                    except:
                        result_df="Error"
            elif 'week' in keyword:
                expected_freq = 'W'
                # print("the date column is ",date_column)
                if where and aggfunc  and grouping_colums :
                    
                    try:
                        result_df = df.pivot_table(index= grouping_colums,columns =pd.Grouper(freq=expected_freq,key=date_column),fill_value=0,aggfunc=aggfunc,)
                        result_df = result_df.stack().reset_index()
                    except:
                        result_df="Error"
                elif not  where and aggfunc  and grouping_colums :
                    
                    try:
                        result_df = df.pivot_table(index= grouping_colums,columns =pd.Grouper(freq=expected_freq,key=date_column),fill_value=0,aggfunc=aggfunc,)
                        result_df = result_df.stack().reset_index()
                    except:
                        result_df="Error"
                elif where and aggfunc and not  grouping_colums:
                    try:
                        result_df = df.pivot_table(columns =pd.Grouper(freq=expected_freq,key=date_column),fill_value=0,aggfunc=aggfunc,)
                        # print("new type of query",result_df)
                        pv_df = result_df.transpose()
                        result_df = pv_df.reset_index()
                    except:
                        result_df="Error"
                elif not where and aggfunc and not  grouping_colums:
                    try:
                        result_df = df.pivot_table(columns =pd.Grouper(freq=expected_freq,key=date_column),fill_value=0,aggfunc=aggfunc,)
                        # print("new type of query",result_df)
                        pv_df = result_df.transpose()
                        result_df = pv_df.reset_index()
                    except:
                        result_df="Error"

                elif where and  grouping_colums  and not aggfunc:
                    try:
                        # print("year just grouping")
                        grouping_colums.append(date_column)
                        grouped_df =df.groupby(grouping_colums)
                        result_df = pd.DataFrame(grouped_df.size().reset_index(name = "Count"))
                    except:
                        result_df="Error"
                elif not where and  grouping_colums  and not aggfunc:
                    try:
                        # print("year just grouping")
                        grouping_colums.append(date_column)
                        grouped_df =df.groupby(grouping_colums)
                        result_df = pd.DataFrame(grouped_df.size().reset_index(name = "Count"))
                    except:
                        result_df="Error"

                elif where and expected_freq:
                    try:
                        # print("only frequency")
                        s_df = df.groupby(pd.Grouper(freq=expected_freq,key=date_column))
                        result_df = pd.DataFrame(s_df.size().reset_index(name = "Count"))
                        
                    except:
                        result_df="Error"
                elif not  where and expected_freq:
                    try:
                        # print("only frequency")
                        s_df = df.groupby(pd.Grouper(freq=expected_freq,key=date_column))
                        result_df = pd.DataFrame(s_df.size().reset_index(name = "Count"))
                        
                    except:
                        result_df="Error"

            elif 'day' in keyword:
                expected_freq = 'D'
                # print("the date column is ",date_column)
                if where and aggfunc  and grouping_colums :
                    
                    try:
                        result_df = df.pivot_table(index= grouping_colums,columns =pd.Grouper(freq=expected_freq,key=date_column),fill_value=0,aggfunc=aggfunc,)
                        result_df = result_df.stack().reset_index()
                    except:
                        result_df="Error"
                elif not  where and aggfunc  and grouping_colums :
                    
                    try:
                        result_df = df.pivot_table(index= grouping_colums,columns =pd.Grouper(freq=expected_freq,key=date_column),fill_value=0,aggfunc=aggfunc,)
                        result_df = result_df.stack().reset_index()
                    except:
                        result_df="Error"
                elif where and aggfunc and not  grouping_colums:
                    try:
                        result_df = df.pivot_table(columns =pd.Grouper(freq=expected_freq,key=date_column),fill_value=0,aggfunc=aggfunc,)
                        # print("new type of query",result_df)
                        pv_df = result_df.transpose()
                        result_df = pv_df.reset_index()
                    except:
                        result_df="Error"
                elif not where and aggfunc and not  grouping_colums:
                    try:
                        result_df = df.pivot_table(columns =pd.Grouper(freq=expected_freq,key=date_column),fill_value=0,aggfunc=aggfunc,)
                        # print("new type of query",result_df)
                        pv_df = result_df.transpose()
                        result_df = pv_df.reset_index()
                    except:
                        result_df="Error"

                elif where and  grouping_colums  and not aggfunc:
                    try:
                        # print("year just grouping")
                        grouping_colums.append(date_column)
                        grouped_df =df.groupby(grouping_colums)
                        result_df = pd.DataFrame(grouped_df.size().reset_index(name = "Count"))
                    except:
                        result_df="Error"
                elif not where and  grouping_colums  and not aggfunc:
                    try:
                        # print("year just grouping")
                        grouping_colums.append(date_column)
                        grouped_df =df.groupby(grouping_colums)
                        result_df = pd.DataFrame(grouped_df.size().reset_index(name = "Count"))
                    except:
                        result_df="Error"

                elif where and expected_freq:
                    try:
                        # print("only frequency")
                        s_df = df.groupby(pd.Grouper(freq=expected_freq,key=date_column))
                        result_df = pd.DataFrame(s_df.size().reset_index(name = "Count"))
                        
                    except:
                        result_df="Error"
                elif not  where and expected_freq:
                    try:
                        # print("only frequency")
                        s_df = df.groupby(pd.Grouper(freq=expected_freq,key=date_column))
                        result_df = pd.DataFrame(s_df.size().reset_index(name = "Count"))
                        
                    except:
                        result_df="Error"
            elif 'month' in keyword:
                expected_freq = 'M'
                # print("the date column is ",date_column)
                if where and aggfunc  and grouping_colums :
                    
                    try:
                        result_df = df.pivot_table(index= grouping_colums,columns =pd.Grouper(freq=expected_freq,key=date_column),fill_value=0,aggfunc=aggfunc,)
                        result_df = result_df.stack().reset_index()
                    except:
                        result_df="Error"
                elif not  where and aggfunc  and grouping_colums :
                    
                    try:
                        result_df = df.pivot_table(index= grouping_colums,columns =pd.Grouper(freq=expected_freq,key=date_column),fill_value=0,aggfunc=aggfunc,)
                        result_df = result_df.stack().reset_index()
                    except:
                        result_df="Error"
                elif where and aggfunc and not  grouping_colums:
                    try:
                        result_df = df.pivot_table(columns =pd.Grouper(freq=expected_freq,key=date_column),fill_value=0,aggfunc=aggfunc,)
                        # print("new type of query",result_df)
                        pv_df = result_df.transpose()
                        result_df = pv_df.reset_index()
                    except:
                        result_df="Error"
                elif not where and aggfunc and not  grouping_colums:
                    try:
                        result_df = df.pivot_table(columns =pd.Grouper(freq=expected_freq,key=date_column),fill_value=0,aggfunc=aggfunc,)
                        # print("new type of query",result_df)
                        pv_df = result_df.transpose()
                        result_df = pv_df.reset_index()
                    except:
                        result_df="Error"

                elif where and  grouping_colums  and not aggfunc:
                    try:
                        # print("year just grouping")
                        grouping_colums.append(date_column)
                        grouped_df =df.groupby(grouping_colums)
                        result_df = pd.DataFrame(grouped_df.size().reset_index(name = "Count"))
                    except:
                        result_df="Error"
                elif not where and  grouping_colums  and not aggfunc:
                    try:
                        # print("year just grouping")
                        grouping_colums.append(date_column)
                        grouped_df =df.groupby(grouping_colums)
                        result_df = pd.DataFrame(grouped_df.size().reset_index(name = "Count"))
                    except:
                        result_df="Error"

                elif where and expected_freq:
                    try:
                        # print("only frequency")
                        s_df = df.groupby(pd.Grouper(freq=expected_freq,key=date_column))
                        result_df = pd.DataFrame(s_df.size().reset_index(name = "Count"))
                        
                    except:
                        result_df="Error"
                elif not  where and expected_freq:
                    try:
                        # print("only frequency")
                        s_df = df.groupby(pd.Grouper(freq=expected_freq,key=date_column))
                        result_df = pd.DataFrame(s_df.size().reset_index(name = "Count"))
                        
                    except:
                        result_df="Error"
            elif 'year' in keyword:
                expected_freq = 'Y'
                # print("year just grouping",grouping_colums)
                # print("the date column is ",date_column)
                if where and aggfunc  and grouping_colums :
                    
                    try:
                        result_df = df.pivot_table(index= grouping_colums,columns =pd.Grouper(freq=expected_freq,key=date_column),fill_value=0,aggfunc=aggfunc,)
                        result_df = result_df.stack().reset_index()
                    except:
                        result_df="Error"
                elif not  where and aggfunc  and grouping_colums :
                    
                    try:
                        result_df = df.pivot_table(index= grouping_colums,columns =pd.Grouper(freq=expected_freq,key=date_column),fill_value=0,aggfunc=aggfunc,)
                        result_df = result_df.stack().reset_index()
                    except:
                        result_df="Error"
                elif where and aggfunc and not  grouping_colums:
                    try:
                        result_df = df.pivot_table(columns =pd.Grouper(freq=expected_freq,key=date_column),fill_value=0,aggfunc=aggfunc,)
                        # print("new type of query",result_df)
                        pv_df = result_df.transpose()
                        result_df = pv_df.reset_index()
                    except:
                        result_df="Error"
                elif not where and aggfunc and not  grouping_colums:
                    try:
                        result_df = df.pivot_table(columns =pd.Grouper(freq=expected_freq,key=date_column),fill_value=0,aggfunc=aggfunc,)
                        # print("new type of query",result_df)
                        pv_df = result_df.transpose()
                        result_df = pv_df.reset_index()
                    except:
                        result_df="Error"

                elif where and  grouping_colums  and not aggfunc:
                    try:
                        # print("year just grouping")
                        grouping_colums.append(date_column)
                        grouped_df =df.groupby(grouping_colums)
                        result_df = pd.DataFrame(grouped_df.size().reset_index(name = "Count"))
                    except:
                        result_df="Error"
                elif not where and  grouping_colums  and not aggfunc:
                    try:
                        # print("year just grouping")
                        grouping_colums.append(date_column)
                        grouped_df =df.groupby(grouping_colums)
                        result_df = pd.DataFrame(grouped_df.size().reset_index(name = "Count"))
                    except:
                        result_df="Error"

                elif where and expected_freq:
                    try:
                        # print("only frequency")
                        s_df = df.groupby(pd.Grouper(freq=expected_freq,key=date_column))
                        result_df = pd.DataFrame(s_df.size().reset_index(name = "Count"))
                        
                    except:
                        result_df="Error"
                elif not  where and expected_freq:
                    try:
                        # print("only frequency")
                        s_df = df.groupby(pd.Grouper(freq=expected_freq,key=date_column))
                        result_df = pd.DataFrame(s_df.size().reset_index(name = "Count"))
                        
                    except:
                        result_df="Error"
            elif 'quarterly' in keyword:
                expected_freq = 'Q'
                # print("the date column is ",date_column)
                if where and aggfunc  and grouping_colums :
                    
                    try:
                        result_df = df.pivot_table(index= grouping_colums,columns =pd.Grouper(freq=expected_freq,key=date_column),fill_value=0,aggfunc=aggfunc,)
                        result_df = result_df.stack().reset_index()
                    except:
                        result_df="Error"
                elif not  where and aggfunc  and grouping_colums :
                    
                    try:
                        result_df = df.pivot_table(index= grouping_colums,columns =pd.Grouper(freq=expected_freq,key=date_column),fill_value=0,aggfunc=aggfunc,)
                        result_df = result_df.stack().reset_index()
                    except:
                        result_df="Error"
                elif where and aggfunc and not  grouping_colums:
                    try:
                        result_df = df.pivot_table(columns =pd.Grouper(freq=expected_freq,key=date_column),fill_value=0,aggfunc=aggfunc,)
                        # print("new type of query",result_df)
                        pv_df = result_df.transpose()
                        result_df = pv_df.reset_index()
                    except:
                        result_df="Error"
                elif not where and aggfunc and not  grouping_colums:
                    try:
                        result_df = df.pivot_table(columns =pd.Grouper(freq=expected_freq,key=date_column),fill_value=0,aggfunc=aggfunc,)
                        # print("new type of query",result_df)
                        pv_df = result_df.transpose()
                        result_df = pv_df.reset_index()
                    except:
                        result_df="Error"

                elif where and  grouping_colums  and not aggfunc:
                    try:
                        # print("year just grouping")
                        grouping_colums.append(date_column)
                        grouped_df =df.groupby(grouping_colums)
                        result_df = pd.DataFrame(grouped_df.size().reset_index(name = "Count"))
                    except:
                        result_df="Error"
                elif not where and  grouping_colums  and not aggfunc:
                    try:
                        # print("year just grouping")
                        grouping_colums.append(date_column)
                        grouped_df =df.groupby(grouping_colums)
                        result_df = pd.DataFrame(grouped_df.size().reset_index(name = "Count"))
                    except:
                        result_df="Error"

                elif where and expected_freq:
                    try:
                        # print("only frequency")
                        s_df = df.groupby(pd.Grouper(freq=expected_freq,key=date_column))
                        result_df = pd.DataFrame(s_df.size().reset_index(name = "Count"))
                        
                    except:
                        result_df="Error"
                elif not  where and expected_freq:
                    try:
                        # print("only frequency")
                        s_df = df.groupby(pd.Grouper(freq=expected_freq,key=date_column))
                        result_df = pd.DataFrame(s_df.size().reset_index(name = "Count"))
                        
                    except:
                        result_df="Error"
            else:
                print("else in project query")
                if where  and  aggfunc and grouping_colums :
                    result_df = df.pivot_table(index= grouping_colums ,aggfunc=aggfunc)
                    # print("the df without time grouper frequency and arregation",result_df)
                    result_df = result_df.reset_index()
                        
                    try:
                        result_df = df.pivot_table(index= grouping_colums ,aggfunc=aggfunc)
                        # print("the df without time grouper frequency and arregation",result_df)
                        result_df = result_df.reset_index()
                    except:
                        result_df="Error"
                elif not where  and  aggfunc and grouping_colums :
                    result_df = df.pivot_table(index= grouping_colums ,aggfunc=aggfunc)
                    print("the df without time grouper frequency and arregation",result_df)
                    result_df = result_df.reset_index()
                    print("after reset index",result_df)
                        
                    try:
                        result_df = df.pivot_table(index= grouping_colums ,aggfunc=aggfunc)
                        print("the df without time grouper frequency and arregation",result_df)
                        result_df = result_df.reset_index()
                        print("after reset index",result_df)
                    except:
                        result_df="Error"
                elif where and grouping_colums and not aggfunc:
                    grouped_df = df.groupby(grouping_colums)
                    result_df = pd.DataFrame(grouped_df.size().reset_index(name = "Count"))
                    try:
                        grouped_df = df.groupby(grouping_colums)
                        result_df = pd.DataFrame(grouped_df.size().reset_index(name = "Count"))
                    except:
                        result_df="Error"
                elif not where and grouping_colums and not aggfunc:
                    grouped_df = df.groupby(grouping_colums)
                    result_df = pd.DataFrame(grouped_df.size().reset_index(name = "Count"))
                    try:
                        grouped_df = df.groupby(grouping_colums)
                        result_df = pd.DataFrame(grouped_df.size().reset_index(name = "Count"))
                    except:
                        result_df="Error"
                        
                elif aggfunc and not grouping_colums:
                    print("its agrigation with no grouping")
                    try:
                        result_df="Error"
                    except:
                        result_df="Error"
                
                
        
        
        else:
            if where  and  aggfunc and grouping_colums :
                    
                        
                try:
                    result_df = df.pivot_table(index= grouping_colums ,aggfunc=aggfunc)
                    # print("the df without time grouper frequency and arregation",result_df)
                    result_df = result_df.reset_index()
                except:
                    result_df="Error"
            elif not where  and  aggfunc and grouping_colums :
                    
                        
                try:
                    result_df = df.pivot_table(index= grouping_colums ,aggfunc=aggfunc)
                    print("the df without time grouper frequency and arregation",result_df)
                    result_df = result_df.reset_index()
                    print("after reset index",result_df)
                except:
                    result_df="Error"
            elif where and grouping_colums and not aggfunc:
                   
                try:
                    grouped_df = df.groupby(grouping_colums)
                    result_df = pd.DataFrame(grouped_df.size().reset_index(name = "Count"))
                except:
                    result_df="Error"
            elif not where and grouping_colums and not aggfunc:
                   
                try:
                    grouped_df = df.groupby(grouping_colums)
                    result_df = pd.DataFrame(grouped_df.size().reset_index(name = "Count"))
                except:
                    result_df="Error"
                        
            elif where and aggfunc and not grouping_colums:
                    
                try:
                    result_df="Error"
                except:
                    result_df="Error"
            elif not where and aggfunc and not grouping_colums:
                   
                try:
                    result_df="Error"
                except:
                    result_df="Error"
        # print("the result data head", result_df)
        # print("the grouper column is ",grouping_colums)
        # print("the resulted dataframe is from the pivot table",result_df)
        return result_df

    def no_time_series_pivot_table(self, aggfunc={},date_column=None, date_column_format="%Y-%m-%d %H:%M:%S", custom=[],grouping_colums=[]):
        '''this to create sub set of non timeseriesd df'''
        df = self.df
        if aggfunc:
            if len(aggfunc)>0:

                for column, value in aggfunc.items():
                    # print("the converting column name is",  column)
                    try:
                        df[column] = df[column].astype(float)
                    except:
                        result_df="Error"
        if aggfunc and grouping_colums :
            
            try:
                result_df = df.pivot_table(index= grouping_colums,aggfunc=aggfunc)
            except:
                result_df="Error"
        elif aggfunc and not grouping_colums :
            
            try:
                result_df="Error"
            except:
                result_df="Error"
        
        elif grouping_colums and not aggfunc :
        
            try:
                grouped_df = df.groupby(grouping_colums)
                result_df = pd.DataFrame(grouped_df.size().reset_index(name = "Count"))
            except:
                result_df="Error"
        elif grouping_colums :
            # print("the result ",grouping_colums)
            try:

                grouped_df = df.groupby(grouping_colums)
                result_df = pd.DataFrame(grouped_df.size().reset_index(name = "Count"))
                # print("type of groper",type(result_df))
            except:
                    result_df="Error"

        return result_df








    def gen_test(self):
        """
        generating a self test case
        """
        count = 500
        dates = []
        value = []
        now = datetime.datetime.now()
        # print(now)
        for i in range(count):
            some_date = now - datetime.timedelta(
                                days=randrange(30),
                                hours=randrange(20),
#                                minutes=randrange(60),
#                                seconds=randrange(60),
                                )
            some_value = randint(1, 9999)
            dates.append(some_date.strftime("%Y-%m-%d %H:%M:%S"))
            value.append(some_value)
        d = {'Time':dates, 'Value':value}
        return pd.DataFrame(d)

    def print(self):
        """
        printing the generated self test case
        """
        df = self.gen_test()
        # print(df)
        df.to_csv('some_dated_file.csv', index=False)
        return df


    def split_df_to_many(self,range):
        '''
        here we split the main df into chunks based on the range
        '''
        split_data = self.df
        # print(len(split_data.index))
        no_of_splits = int(len(split_data.index)/range)
        end_range = range
        dfs = []
        start_range = 0
        while end_range<=len(split_data):
            df = split_data.iloc[start_range:end_range]
            dfs.append(df)
            start_range = start_range+range
            end_range = end_range+range
        return dfs



    def uniquified(self, d):
        """
        please uniquify the dates and send back
        """
        print("the value befour conversion",d)
        df_unique = d.drop_duplicates()

        print("after conversion",df_unique)


        return df_unique

    def get_min_interval_in_seconds(self, date_column=0, format_of_date="%Y-%m-%d %H:%M:%S"):
        """
        get the minimum time interval so that we can control the end user options
        # TODO: dates should be uniquified; else the minimum value will be zero!
        """
        print("the date column is the",date_column)
        d = self.df.iloc[:,date_column]
        # print(divided_d)
        d = self.uniquified(d)
        print("the data after duplicate remove",type(d))


        total_date_count = d.size
        delta = self.min_interval_in_seconds
        date  = enumerate(d)
        print("the enumarated date is",date)





        for i, v in enumerate(d):
            print("inside the for ",i, v)
            next = i+1
            if next != total_date_count:
                print("inside the if")
                print(">>Date:", d[i], "Format", format_of_date)
                this_date = datetime.datetime.strptime(d[i],    format_of_date)
                next_date = datetime.datetime.strptime(d[next], format_of_date)
                x = abs(next_date - this_date).total_seconds()
                print("this date",this_date,"nextdate" ,next_date,"the x value", x)
                if (x < delta):
                    delta = x
        self.min_interval_in_seconds = delta
        return delta

'''
Main Section - Play around
'''

######################################################
# df = pd.DataFrame()
# t = TimeManage(df)
# gen_df = t.print()
######################################################
# actual = TimeManage(gen_df)
# print("New input:", actual.df)
# min_seconds = actual.get_min_interval_in_seconds()
# print("Min interval in seconds:", min_seconds)
# agg_value = actual.keyword_based_date_range_selection('avg','hours', 3)
# print(agg_value)

''''''
