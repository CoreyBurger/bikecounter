#! /usr/bin/python
import json
import altair
import pandas
import datetime
import bs4
import os
import csv

#define constants
workingDir = os.getcwd()
yesterday = datetime.date.today() - datetime.timedelta(1)
yesterday = yesterday.strftime('%Y-%m-%d')

#load data
countFile = "counts-100117730.csv"
countExportFile = "counts-100117730-export.csv"
data = pandas.read_csv(countFile,parse_dates=['Date'])

#setup counter map
mapHTML ="var countmap = L.map('counterMap').setView([48.432613, -123.3782], 15);var marker = L.marker([48.432613, -123.37829]).addTo(countmap);var background = L.tileLayer.provider('Stamen.Toner').addTo(countmap);"

#resample to daily count
dailyCount = data.resample('D',on='Date').sum()
dailyCount['Day'] = dailyCount.index
dailyCount = dailyCount.loc[dailyCount['Day'] >= '2015-01-01']

#get yesterdays count   
yesterdayCount = dailyCount.loc[dailyCount['Day']==yesterday]['Count'][0]

#determine rank
dailyRank = dailyCount.loc[dailyCount['Count']>yesterdayCount]['Count'].size+1

#add monthly & yearly cumulative total
dailyCount['MonthlyCumSum'] = dailyCount.groupby(dailyCount.index.to_period('m')).cumsum()
#dailyCount['YearlyCumSum'] = dailyCount.groupby(dailyCount.index.to_period('y')).cumsum()

#write that list out to a csv file
#dailyCount.to_csv(countExportFile)

#resample to monthly count
monthlyCount = data.resample('M',on='Date').sum()
monthlyCount['Month'] = monthlyCount.index
monthlyCount = monthlyCount.loc[monthlyCount['Month'] >= '2015-01-31']

#Pull out the current month
currentMonth = pandas.DataFrame(dailyCount.loc[dailyCount.index.month==datetime.datetime.now().month])

#Create daily heatmap
heatmap = altair.Chart(dailyCount).mark_rect().encode(
    altair.X('day(Day):O'),
    altair.Y('Day:O', timeUnit='year'),
    altair.Color('mean(Count):Q')
).properties(width=300,height=300)

#Create monthly cumulative line chart
monthlyLine = altair.Chart(currentMonth).mark_line().encode(
    altair.X('date(Day):O'),
    altair.Y('MonthlyCumSum', axis=altair.Axis(title='Monthly Cumulative Sum')),
    altair.Color('Day:O', timeUnit='year')  
).properties(width=400,height=300)

monthlyLineAvg = altair.Chart(currentMonth).mark_line(color='grey').encode(
    altair.X('date(Day):O'),
    altair.Y('mean(MonthlyCumSum)'),
).properties(width=400,height=300)

monthlyLineBand = altair.Chart(currentMonth).mark_errorband(extent='stdev',color='grey').encode(
    altair.X('date(Day):O'),
    altair.Y('MonthlyCumSum'),
).properties(width=400,height=300)

#chart = altair.hconcat(heatmap,monthlyLine,monthlyLineAvg)
chart = monthlyLineBand + monthlyLine + monthlyLineAvg

#open the HTML doc
with open (workingDir + '\\counterVisual.html') as counterPage:
    page = bs4.BeautifulSoup(counterPage)

#write out the map
page.find(id='counterMap').find('script').string.replace_with(mapHTML)

#write out the first data
testV1spec = "var testV1Spec =" + chart.to_json() + "; vegaEmbed('#vis1', testV1Spec); "
page.find(id='vis1').find('script').string.replace_with(testV1spec)

#write out the HTML
pageStr = bs4.BeautifulSoup.prettify(page)
with open (workingDir + '\\counterVisual.html',"w") as counterPage:
    counterPage.write(pageStr)