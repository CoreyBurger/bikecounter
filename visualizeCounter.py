#! /usr/bin/python
import json
import altair
import pandas
import datetime
import bs4
import os

#define constants
workingDir = os.getcwd()
yesterday = datetime.date.today() - datetime.timedelta(1)
yesterday = yesterday.strftime('%Y-%m-%d')

#load data
countFile = "counts-100117730.csv"
data = pandas.read_csv(countFile,parse_dates=['Date'])

#resample to daily count
dailyCount = data.resample('D',on='Date').sum()
dailyCount['Day'] = dailyCount.index
dailyCount = dailyCount.loc[dailyCount['Day'] >= '2015-01-01']

#get yesterdays count   
yesterdayCount = dailyCount.loc[dailyCount['Day']==yesterday]['Count'][0]

#determine rank
dailyRank = dailyCount.loc[dailyCount['Count']>yesterdayCount]['Count'].size+1

heatmap = altair.Chart(dailyCount).mark_rect().encode(
    altair.X('day(Day):O'),
    altair.Y('Day:O', timeUnit='year'),
    altair.Color('mean(Count):Q')
)

chart = heatmap

#open the HTML doc   
with open (workingDir + '\\counterVisual.html') as counterPage:
    page = bs4.BeautifulSoup(counterPage)

#write out the first data
testV1spec = "var testV1Spec =" + chart.to_json() + "; vegaEmbed('#vis1', testV1Spec); "
page.find(id='vis1script').string.replace_with(testV1spec)

#write out the HTML
page = bs4.BeautifulSoup.prettify(page)
with open (workingDir + '\\counterVisual.html',"w") as counterPage:
    counterPage.write(page)