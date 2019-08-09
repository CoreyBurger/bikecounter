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
dailyCount = pandas.read_csv(countFile, parse_dates=['Date'])

monthlyCount = dailyCount[['Date','Count']].resample('M',on='Date').sum()
monthlyCount['Month'] = monthlyCount.index

monthlyMerge = pandas.merge(monthlyCount,monthlyCount,left_on=[monthlyCount['Month'].dt.year,monthlyCount['Month'].dt.month],right_on=[monthlyCount['Month'].dt.year-1,monthlyCount['Month'].dt.month])
monthlyMerge['YoYChange']=monthlyMerge['Count_y']-monthlyMerge['Count_x']

monthlyCount = pandas.merge(monthlyCount,monthlyMerge[['Month_y','YoYChange']],left_on=monthlyCount['Month'],right_on=monthlyMerge['Month_y'])
monthlyCount = monthlyCount.drop(columns=['Month_y'])
#drop the current month, as it is partial
monthlyCount = monthlyCount[(monthlyCount['Month'].dt.month<yesterdayMonth) | (monthlyCount['Month'].dt.year<yesterdayYear)]

testVisual = altair.Chart(monthlyCount).mark_bar().encode(
    altair.X('yearmonth(Month):T', axis=altair.Axis(title='Months')),
    altair.Y('YoYChange:Q', axis=altair.Axis(title='Year over Year Change')),
    color=altair.condition(
        altair.datum.YoYChange > 0,
        altair.value("steelblue"),  # The positive color
        altair.value("orange")  # The negative color
    )
).properties(width=200,height=200)

#Daily mean
# testVisual = altair.Chart(countFile).mark_line().encode(
#     altair.X('month(Date):T', axis=altair.Axis(title='Months')),
#     altair.Y('mean(Count):Q', axis=altair.Axis(title='Average Bikes per Day')),
#     altair.Color('Date:O', timeUnit='year', legend=altair.Legend(title='Year'))  
# ).properties(width=200,height=200)

testVisual.save('testVisual.json')