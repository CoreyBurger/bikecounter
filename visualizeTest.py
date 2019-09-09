#! /usr/bin/python
import json
import altair
import pandas
import datetime
import bs4
import os
import csv
import statistics
import locale

#define constants
#TODO Clean up to removal duplicate calls for yesterday
workingDir = os.getcwd()
yesterdayDate = datetime.date.today() - datetime.timedelta(1)
yesterday = yesterdayDate.strftime('%Y-%m-%d')
yesterdayDay = yesterdayDate.day
yesterdayDayName = yesterdayDate.strftime("%A")
yesterdayWeekNum = int(yesterdayDate.strftime("%W"))
yesterdayDayOfWeek = yesterdayDate.weekday()
yesterdayMonth = yesterdayDate.month
yesterdayMonthName =  yesterdayDate.strftime("%B")
yesterdayYear= yesterdayDate.year
yesterdayYearName = yesterdayDate.strftime("%Y")
locale.setlocale(locale.LC_ALL, 'en_CA')
ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n//10%10!=1)*(n%10<4)*n%10::4])

#read in counters list
counterList  = pandas.read_csv('counters.csv',parse_dates=['FirstDate','FirstFullYear'])

#load data
countFile = "counts-" + str(counterList['CounterID'][0]) + "-export.csv"
dailyCount = pandas.read_csv(countFile, parse_dates=['Date']).set_index('Date')

dailyCount.loc[(dailyCount['WeekNum']==yesterdayWeekNum) & (dailyCount['Weekday']==yesterdayDayOfWeek)]

#Mean of weekly cumulative sum to this day of prior weeks
statistics.mean(dailyCount['WeeklyCumSum'].loc[(dailyCount['WeekNum']==yesterdayWeekNum) & (dailyCount['Weekday']==yesterdayDayOfWeek)])

# monthlyCount = dailyCount[['Date','Count']].resample('M',on='Date').sum()
# monthlyCount['Month'] = monthlyCount.index

# monthlyMerge = pandas.merge(monthlyCount,monthlyCount,left_on=[monthlyCount['Month'].dt.year,monthlyCount['Month'].dt.month],right_on=[monthlyCount['Month'].dt.year-1,monthlyCount['Month'].dt.month])
# monthlyMerge['YoYChange']=monthlyMerge['Count_y']-monthlyMerge['Count_x']
# monthlyCount = pandas.merge(monthlyCount,monthlyMerge[['Month_y','YoYChange']],left_on=monthlyCount['Month'],right_on=monthlyMerge['Month_y'])
# monthlyCount = monthlyCount.drop(columns=['Month_y'])
# #drop the current month, as it is partial
# monthlyCount = monthlyCount[(monthlyCount['Month'].dt.month<yesterdayMonth) | (monthlyCount['Month'].dt.year<yesterdayYear)]

# #Year over year by Month
# testVisual = altair.Chart(monthlyCount).mark_bar().encode(
#     altair.X('yearmonth(Month):T', axis=altair.Axis(title='Months')),
#     altair.Y('YoYChange:Q', axis=altair.Axis(title='Year over Year Change')),
#     color=altair.condition(
#         altair.datum.YoYChange > 0,
#         altair.value("green"),  # The positive color
#         altair.value("darkgrey")  # The negative color
#     )
# ).properties(width=200,height=200)

#Count of days, by year and binned to 500
# testVisual = altair.Chart(dailyCount).mark_circle().encode(
#     altair.X('Temp:Q', bin=altair.Bin(step=2)), #
#     altair.Y('Date:O', timeUnit='year'),
#     altair.Size('count(Count):O')#,
#     #altair.Color('mean(Count):Q')
# ).properties(width=200,height=200)

#Temp by count by year
# testVisual = altair.Chart(dailyCount).mark_circle().encode(
#     altair.X('Temp:Q', bin=altair.Bin(step=5)), 
#     altair.Y('Date:O', timeUnit='year'),
#     altair.Color('mean(Count):Q'),
#     altair.Size('count(Count):Q'),
#     altair.Tooltip('mean(Count)',format=',.0f')
# ).properties(width=200,height=200)

##Count of days by binned by 1000s
# testVisual = altair.Chart(dailyCount).mark_bar().encode(
#     altair.X('Date:O', timeUnit='year', axis=altair.Axis(title=None,domainWidth=0,labelAngle=0,tickWidth=0)), 
#     altair.Y('count(Count):Q',sort='descending', axis=altair.Axis(title='Days by Total Bikes',domainWidth=0)),
#     altair.Color('Count:Q', bin=True)
#     #altair.Size('count(Count):Q'),
#     #altair.Tooltip('mean(Count)',format=',.0f')
# ).transform_filter(
#     altair.FieldLTPredicate(field='DayOfYear',lt=datetime.datetime.today().timetuple().tm_yday)
# ).properties(width=200,height=200
# ).configure_axis(
#     grid=False
# ).configure_view(
#     strokeWidth=0
# ).configure_legend(
#     labelBaseline='top'
# )

testVisual.save('testVisual.json')