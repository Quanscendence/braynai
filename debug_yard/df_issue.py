#######################################################
import pandas as pd
import numpy as np
from pandas.tseries.offsets import BDay
from datetime import timedelta

begin = pd.datetime(2013,1,1)
end = pd.datetime(2013,2,20)

dtrange = pd.date_range(begin, end)

p1 = np.random.rand(len(dtrange)) + 5
p2 = np.random.rand(len(dtrange)) + 10

df = pd.read_csv('BIT_August2019.csv')
# df

#######################################################
# series = df.iloc[:,0]
# single_col_df = series.to_frame()
# single_col_df.set_index()
# pd.unique(single_col_df)

# df = df.iloc[:0]

# # df = df.set_index('Day')
# # # df
# # # l=5
# # # n=15
# # # d= df.index.day - np.clip((df.index.day-1) // l, 0,n )*l - 1
# # # d
# # df['date'] = df.Clicks.resample('5min').ffill()
# df

#######################################################
import pandas as pd
import numpy as np
from pandas.tseries.offsets import BDay
from datetime import timedelta

begin = pd.datetime(2013,1,1)
end = pd.datetime(2013,2,20)

dtrange = pd.date_range(begin, end)

p1 = np.random.rand(len(dtrange)) + 5
p2 = np.random.rand(len(dtrange)) + 10

df = pd.read_csv('E:/projects/DSAAA/folder_a/Pivot Queries/BIT_ADS_sep18-sep19.csv')
df['Day']= pd.to_datetime(df['Day'])

g = df.groupby(pd.Grouper(key='Day', freq='M'))
df['Day']= pd.to_datetime(df['Day'])
df.pivot_table(index=pd.Grouper(freq='M',key='Day'),values=['Clicks'], fill_value=0,aggfunc={'Clicks':'sum',})
df['Day_of_Week'] = df['Day'].dt.day_name()
week = ['Wednesday','Tuesday','Monday','Friday','Thursday']
weekend = ['Saturday','Sunday']
week_day =['Monday']
df_q = df.query("Day_of_Week==['Monday']")
l=[]
l.append(pd.Grouper(freq='M',key='Day'))
g = ['Day_of_Week']
g.insert(0,l[0])
# print(g)


d = df_q.pivot_table(index=g,columns='Campaign', values=['Clicks'], fill_value=0,aggfunc={'Clicks':'sum',})
# print(d)
# print(d.transpose())
# new_df = d.transpose()
# new_df
print("the df is ",d)
# new_df.columns = new_df.columns.get_level_values(0)
d.columns = d.columns.to_series().str.join('_')
print("the first level columns",d.columns)

#######################################################
# expecpected output is the i need to get the other two columns  Day and Day_of_week
# ex: i have to get the  the columns Campaign, Clicks, Day and Day_of_Week form the below table.

# Campaign               Thai- Singapore -Cruise Unbeatable Europe_Aug_Sept2019
# Day        Day_of_Week
# 2018-09-30 Monday                            0                              0
# 2018-10-31 Monday                            0                              0
# 2018-11-30 Monday                           39                              0
# 2018-12-31 Monday                           34                              0
# 2019-01-31 Monday                            0                              0
# 2019-02-28 Monday                            0                              0
# 2019-03-31 Monday                            0                              0
# 2019-04-30 Monday                            0                              0
# 2019-05-31 Monday                            0                              0
# 2019-06-30 Monday                            0                              0
# 2019-07-31 Monday                            0                              0
# 2019-08-31 Monday                            0                              0
# 2019-09-30 Monday                            0                            100

#out put shoul be similar to this :['Campaign','Day','Day_of_Week','Clicks'].

#######################################################


#######################################################
#######################################################
#######################################################
#######################################################
#######################################################
