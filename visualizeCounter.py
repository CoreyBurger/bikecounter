#! /usr/bin/python
import json
import altair
import pandas
import datetime
import bs4
import os
import csv
import statistics

#define constants
workingDir = os.getcwd()
yesterday = datetime.date.today() - datetime.timedelta(1)
yesterday = yesterday.strftime('%Y-%m-%d')
yesterdayDay = (datetime.date.today() - datetime.timedelta(1)).day
yesterdayMonth = (datetime.date.today() - datetime.timedelta(1)).month
yesterdayMonthName =  (datetime.date.today() - datetime.timedelta(1)).strftime("%B")

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
dailyRankAll = dailyCount.loc[dailyCount['Count']>yesterdayCount]['Count'].size+1
dailyRankThisYear=dailyCount.loc[dailyCount.index.year==datetime.datetime.now().year].loc[dailyCount['Count']>yesterdayCount]['Count'].size+1

ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n//10%10!=1)*(n%10<4)*n%10::4])
print(ordinal(dailyRankThisYear))

#craft the string for yeserday
countString ="Yesterday saw " + str(yesterdayCount) + " bike rides, the " + str(ordinal(dailyRankThisYear)) + " busiest day of " + (datetime.date.today() - datetime.timedelta(1)).strftime('%Y') +  " and " + str(ordinal(dailyRankAll)) + " busiest overall."

#add monthly & yearly cumulative total
YearlyCumSum = dailyCount.groupby(dailyCount.index.to_period('y')).cumsum()
YearlyCumSum.rename(columns={'Count':'YearlyCumSum'}, inplace=True)
dailyCount['MonthlyCumSum'] = dailyCount.groupby(dailyCount.index.to_period('m')).cumsum()
dailyCount = pandas.merge(dailyCount,YearlyCumSum,on='Date')

#write that list out to a csv file
dailyCount.to_csv(countExportFile)

#resample to monthly count
monthlyCount = data.resample('M',on='Date').sum()
monthlyCount['Month'] = monthlyCount.index
monthlyCount = monthlyCount.loc[monthlyCount['Month'] >= '2015-01-31']

#Pull out the current month
currentMonth = pandas.DataFrame(dailyCount.loc[dailyCount.index.month==yesterdayMonth])

#check if we are ahead of behind of the average monthly cumulative sum

yesterdayMonthCumSumMean=statistics.mean(dailyCount.loc[(dailyCount.index.month==yesterdayMonth) & (dailyCount.index.day==yesterdayDay)].MonthlyCumSum)
yesterdayMonthlyCumSum=pandas.DataFrame(dailyCount.loc[dailyCount.index==yesterday]).MonthlyCumSum[0]
yesterdayMonChange=(yesterdayMonthlyCumSum-yesterdayMonthCumSumMean)/yesterdayMonthCumSumMean

if yesterdayMonChange<-0.05:
    monthlyCountString='less busy than'
elif yesterdayMonChange>0.05:
    monthlyCountString='busier than'
else:
    monthlyCountString='about as busy same as'

MonthlyCountString=  yesterdayMonthName +  " is " + monthlyCountString + " average"

#Create daily heatmap
heatmap = altair.Chart(dailyCount).mark_rect().encode(
    altair.X('day(Day):O'),
    altair.Y('Day:O', timeUnit='year'),
    altair.Color('mean(Count):Q')
).properties(width=200,height=300)

#Create monthly cumulative line chart
monthlyLine = altair.Chart(currentMonth).mark_line(stroke='#f304d3').encode(
    altair.X('date(Day):O'),
    altair.Y('MonthlyCumSum', axis=altair.Axis(title='Monthly Cumulative Sum')),
    altair.Color('Day:O', timeUnit='year')  
).transform_filter(
    altair.FieldEqualPredicate(timeUnit='year',field='Day',equal=datetime.date.today().year)
).properties(width=200,height=200)

monthlyLineAvg = altair.Chart(currentMonth).mark_line(color='grey',strokeDash=[8,8]).encode(
    altair.X('date(Day):O'),
    altair.Y('mean(MonthlyCumSum)'),
).properties(width=200,height=200)

monthlyLineBand = altair.Chart(currentMonth).mark_errorband(extent='stdev',color='grey').encode(
    altair.X('date(Day):O'),
    altair.Y('MonthlyCumSum'),
).properties(width=200,height=200)

MonthlyChart = monthlyLineBand + monthlyLine + monthlyLineAvg

#Create yearlycumulative line chart
#TODO fix, not working correctly
yearlyLine = altair.Chart(dailyCount).mark_line().encode(
    altair.X('Day:O', timeUnit='month'),
    altair.Y('YearlyCumSum', axis=altair.Axis(title='Yearly Cumulative Sum')),
    altair.Color('Day:O', timeUnit='year')  
).properties(width=200,height=200)

chart = altair.hconcat(heatmap,MonthlyChart,yearlyLine)

#open the HTML doc
with open (workingDir + '\\counterVisual.html') as counterPage:
    page = bs4.BeautifulSoup(counterPage)

#write out the map
page.find(id='counterMap').find('script').string.replace_with(mapHTML)

#write out the yesterday string
page.find(id="counterName").find('p').string.replace_with(countString)

#write out the first data
testV1spec = "var testV1Spec =" + chart.to_json() + "; vegaEmbed('#vis1', testV1Spec); "
page.find(id='vis1').find('script').string.replace_with(testV1spec)

#write out the HTML
pageStr = bs4.BeautifulSoup.prettify(page)
with open (workingDir + '\\counterVisual.html',"w") as counterPage:
    counterPage.write(pageStr)