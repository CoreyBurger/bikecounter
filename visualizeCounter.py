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
workingDir = os.getcwd()
yesterday = datetime.date.today() - datetime.timedelta(1)
yesterday = yesterday.strftime('%Y-%m-%d')
yesterdayDay = (datetime.date.today() - datetime.timedelta(1)).day
yesterdayMonth = (datetime.date.today() - datetime.timedelta(1)).month
yesterdayMonthName =  (datetime.date.today() - datetime.timedelta(1)).strftime("%B")
yesterdayYearName = (datetime.date.today() - datetime.timedelta(1)).strftime("%Y")
locale.setlocale(locale.LC_ALL, 'en_CA')

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
yesterdayCount = locale.format_string("%d", dailyCount.loc[dailyCount['Day']==yesterday]['Count'][0], grouping=True)

#determine rank
dailyRankAll = dailyCount.loc[dailyCount['Count']>yesterdayCount]['Count'].size+1
dailyRankThisYear=dailyCount.loc[dailyCount.index.year==datetime.datetime.now().year].loc[dailyCount['Count']>yesterdayCount]['Count'].size+1

ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n//10%10!=1)*(n%10<4)*n%10::4])
print(ordinal(dailyRankThisYear))

#craft the string for yeserday
countString ="Yesterday saw " + yesterdayCount + " bike rides, the " + str(ordinal(dailyRankThisYear)) + " busiest day of " + (datetime.date.today() - datetime.timedelta(1)).strftime('%Y') +  " and " + str(ordinal(dailyRankAll)) + " busiest overall."

#add monthly & yearly cumulative total
YearlyCumSum = dailyCount.groupby(dailyCount.index.to_period('y')).cumsum()
YearlyCumSum.rename(columns={'Count':'YearlyCumSum'}, inplace=True)
dailyCount['MonthlyCumSum'] = dailyCount.groupby(dailyCount.index.to_period('m')).cumsum()
dailyCount = pandas.merge(dailyCount,YearlyCumSum,on='Date')

#add day of the year
dailyCount['DayOfYear'] = dailyCount['Day'].dt.dayofyear

#write that list out to a csv file
dailyCount.to_csv(countExportFile)

#resample to monthly count
monthlyCount = data.resample('M',on='Date').sum()
monthlyCount['Month'] = monthlyCount.index
monthlyCount = monthlyCount.loc[monthlyCount['Month'] >= '2015-01-31']

#Pull out the current month
currentMonth = pandas.DataFrame(dailyCount.loc[dailyCount.index.month==yesterdayMonth])

#check if we are ahead of behind of the average monthly cumulative sum
#TODO genericize the function to deal with both yearly & monthly
yesterdayMonthCumSumMean=statistics.mean(dailyCount.loc[(dailyCount.index.month==yesterdayMonth) & (dailyCount.index.day==yesterdayDay)].MonthlyCumSum)
yesterdayMonthlyCumSum=pandas.DataFrame(dailyCount.loc[dailyCount.index==yesterday]).MonthlyCumSum[0]
yesterdayMonChange=(yesterdayMonthlyCumSum-yesterdayMonthCumSumMean)/yesterdayMonthCumSumMean

if yesterdayMonChange<-0.05:
    monthlyCountString='less busy than'
elif yesterdayMonChange>0.05:
    monthlyCountString='busier than'
else:
    monthlyCountString='about as busy same as'

monthlyCountString=  yesterdayMonthName +  " is " + monthlyCountString + " average, with " + locale.format_string("%d", yesterdayMonthlyCumSum, grouping=True) + " rides so far this month"

#Check if we are ahead of last year
#TODO - deal with leap years
yesterdayYearlyCumSum=pandas.DataFrame(dailyCount.loc[dailyCount.index==yesterday]).YearlyCumSum[0]
lastyearYearlyCumSum=pandas.DataFrame(dailyCount.loc[dailyCount.index==(datetime.date.today() - datetime.timedelta(365)).strftime('%Y-%m-%d')]).YearlyCumSum[0]
yesterdayYearChange = (yesterdayYearlyCumSum-lastyearYearlyCumSum)/yesterdayYearlyCumSum

if yesterdayYearChange<-0.05:
    yearlyCountString='less busy than'
elif yesterdayYearChange>0.05:
    yearlyCountString='busier than'
else:
    yearlyCountString='about as busy same as'

yearlyCountString =  yesterdayYearName +  " is " + yearlyCountString + " last year, with " + locale.format_string("%d", yesterdayYearlyCumSum, grouping=True) + " rides so far this year"

#Determine busiest day and month
highestCountDayString=dailyCount[dailyCount['Count']==dailyCount['Count'].max()]['Day'][0].strftime('%A %B %d, %Y')

highestCountDayString = "The busiest day ever was " + highestCountDayString

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
yearlyLine = altair.Chart(dailyCount).mark_line().encode(
    altair.X('DayOfYear:O'),
    altair.Y('YearlyCumSum', axis=altair.Axis(title='Yearly Cumulative Sum')),
    altair.Color('Day:O', timeUnit='year')
).properties(width=200,height=200)

#Create daily heatmap
heatmap = altair.Chart(dailyCount).mark_rect().encode(
    altair.X('day(Day):O'),
    altair.Y('Day:O', timeUnit='year'),
    altair.Color('mean(Count):Q')
).properties(width=200,height=200)

#open the HTML doc
with open (workingDir + '\\counterVisual.html') as counterPage:
    page = bs4.BeautifulSoup(counterPage)

#write out the map
page.find(id='counterMap').find('script').string.replace_with(mapHTML)

#write out the yesterday string
page.find(id="counterName").find('p').string.replace_with(countString)

#write out the monthly data
monthlySpec = "var monthlySpec =" + MonthlyChart.to_json() + "; vegaEmbed('#visMonthly', monthlySpec); "
page.find(id='visMonthly').find('script').string.replace_with(monthlySpec)
page.find(id="monthlyText").find('p').string.replace_with(monthlyCountString)

#write out yearly data
yearlySpec = "var yearlySpec =" + yearlyLine.to_json() + "; vegaEmbed('#visYearly', yearlySpec); "
page.find(id='visYearly').find('script').string.replace_with(yearlySpec)
page.find(id="yearlyText").find('p').string.replace_with(yearlyCountString)

#write out overall data
overallSpec = "var overallSpec =" + heatmap.to_json() + "; vegaEmbed('#visOverall', overallSpec); "
page.find(id='visOverall').find('script').string.replace_with(overallSpec)
page.find(id="overallText").find('p').string.replace_with(highestCountDayString)

#write out the HTML
pageStr = bs4.BeautifulSoup.prettify(page)
with open (workingDir + '\\counterVisual.html',"w") as counterPage:
    counterPage.write(pageStr)