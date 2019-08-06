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
yesterdayYearName = yesterdayDate.strftime("%Y")
locale.setlocale(locale.LC_ALL, 'en_CA')
ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n//10%10!=1)*(n%10<4)*n%10::4])

#read in counters list
counterList  = pandas.read_csv('counters.csv',parse_dates=['FirstDate','FirstFullYear'])

#load data
countFile = "counts-" + str(counterList['CounterID'][0]) + ".csv"
countExportFile = "counts-" + str(counterList['CounterID'][0]) + "-export.csv"
data = pandas.read_csv(countFile,parse_dates=['Date'])
specialDateFile = "specialDates.csv"
specialDateData = pandas.read_csv(specialDateFile,parse_dates=['Date'])

counterStartDate = counterList['FirstDate'][0]

#setup counter map
mapHTML ="var countmap = L.map('counterMap').setView([48.432613, -123.3782], 15);var marker = L.marker([48.432613, -123.37829]).addTo(countmap);var background = L.tileLayer.provider('Stamen.Toner').addTo(countmap);"

#resample to daily count
dailyCount = data.resample('D',on='Date').sum()
dailyCount['Day'] = dailyCount.index

totalRides = dailyCount['Count'].sum()

#remove all data from partial years
dailyCount = dailyCount.loc[dailyCount['Day'] >= counterList['FirstFullYear'][0]]

#add columns for monthly & yearly cumulative total, plus weekday and day of the year
YearlyCumSum = dailyCount.groupby(dailyCount.index.to_period('y')).cumsum()
YearlyCumSum.rename(columns={'Count':'YearlyCumSum'}, inplace=True)
MonthlyCumSum = dailyCount.groupby(dailyCount.index.to_period('m')).cumsum()
MonthlyCumSum.rename(columns={'Count':'MonthlyCumSum'}, inplace=True)
dailyCount = pandas.merge(dailyCount,YearlyCumSum,on='Date')
dailyCount = pandas.merge(dailyCount,MonthlyCumSum,on='Date')
dailyCount['Weekday']=dailyCount['Day'].dt.dayofweek 
dailyCount['DayOfYear'] = dailyCount['Day'].dt.dayofyear

#write that list out to a csv file
dailyCount.to_csv(countExportFile)

#get yesterdays count   
yesterdayCount = dailyCount.loc[dailyCount['Day']==yesterday]['Count'][0]
yesterdayCountString = locale.format_string("%d",yesterdayCount, grouping=True)

#determine daily rank
dailyRankAll = dailyCount.loc[dailyCount['Count']>yesterdayCount]['Count'].size+1
dailyRankThisYear=dailyCount.loc[dailyCount.index.year==datetime.datetime.now().year].loc[dailyCount['Count']>yesterdayCount]['Count'].size+1
dailyRankDayOnly=dailyCount.loc[dailyCount['Day'].dt.dayofweek==yesterdayDate.weekday()].loc[dailyCount['Count']>yesterdayCount]['Count'].size

if dailyRankAll==1:
    dailyRankAll=None
else:
    dailyRankAll = str(ordinal(dailyRankAll)) + " "

if dailyRankThisYear==1:
    dailyRankThisYear=None
else:
    dailyRankThisYear = str(ordinal(dailyRankThisYear)) + " "

if dailyRankDayOnly==1:
    dailyRankDayOnly=None
else:
    dailyRankDayOnly = str(ordinal(dailyRankDayOnly)) + " "

#Check if yesterday was anything special
try:
    specialDateStringYesterday = "(" + specialDateData[specialDateData['Date']==yesterdayDate].Event.iloc[0] + ")"
except IndexError as error:
    specialDateStringYesterday = None

#craft the string for yesterday
countString ="Yesterday saw " + yesterdayCountString + " bike rides,"
countStringYearlyRank = "".join(filter(None,("...", dailyRankThisYear,"busiest day of ",yesterdayYearName)))
countStringDayRank = "".join(filter(None,("...", dailyRankDayOnly,"busiest ",yesterdayDayName)))
countStringOverallRank = "".join(filter(None,("...", dailyRankAll,"busiest day overall")))

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
yesterdayYearlyCumSum=dailyCount[dailyCount.index==yesterday]['YearlyCumSum'][0]
lastyearYearlyCumSum=dailyCount[dailyCount.index==(datetime.date.today() - datetime.timedelta(365)).strftime('%Y-%m-%d')]['YearlyCumSum'][0]
yesterdayYearChange = (yesterdayYearlyCumSum-lastyearYearlyCumSum)/yesterdayYearlyCumSum

if yesterdayYearChange<-0.05:
    yearlyCountString='less busy than'
elif yesterdayYearChange>0.05:
    yearlyCountString='busier than'
else:
    yearlyCountString='about as busy same as'

yearlyCountString =  yesterdayYearName +  " is " + yearlyCountString + " last year, with " + locale.format_string("%d", yesterdayYearlyCumSum, grouping=True) + " rides so far this year (compared to " + locale.format_string("%d", lastyearYearlyCumSum, grouping=True) + " rides this time last year)"

#Determine total counts since beginning of counter
totalCountString = "Since " + counterList['FirstDate'][0].strftime('%A, %b %d, %Y') + " there have been " + locale.format_string("%d", totalRides, grouping=True) + " rides past the counter"
 
#Determine busiest day and month
highestCountDay = dailyCount[dailyCount['Count']==dailyCount['Count'].max()]['Day'][0]
highestCountDayString=highestCountDay.strftime('%A %B %d, %Y')
highestCountMonth=monthlyCount[monthlyCount['Count']==monthlyCount['Count'].max()]['Month'][0]
highestCountMonthString = "The busiest month ever was " + highestCountMonth.strftime('%B %Y')

#Check if the highest day was anything special
try:
    specialDateStringHighest = "(" + specialDateData[specialDateData['Date']==highestCountDay].Event.iloc[0] + ")"
except IndexError as error:
    specialDateStringHighest = None

highestCountDayString = " ".join(filter(None,("The busiest day ever was",highestCountDayString,specialDateStringHighest)))

#Create monthly cumulative line chart
monthlyLine = altair.Chart(currentMonth).mark_line(stroke='#f304d3').encode(
    altair.X('date(Day):T', axis=altair.Axis(title='Day of the Month')),
    altair.Y('MonthlyCumSum', axis=altair.Axis(title='Total Bikes'), scale=altair.Scale(domain=(0,100000))),
    altair.Color('Day:O', timeUnit='year', legend=altair.Legend(title='Year'))  
).transform_filter(
    altair.FieldEqualPredicate(timeUnit='year',field='Day',equal=datetime.date.today().year)
).properties(width=200,height=200)

monthlyLineAvg = altair.Chart(currentMonth).mark_line(color='grey',strokeDash=[8,8]).encode(
    altair.X('date(Day):T', axis=altair.Axis(title='')),
    altair.Y('mean(MonthlyCumSum)', axis=altair.Axis(title='')),
).properties(width=200,height=200)

monthlyLineBand = altair.Chart(currentMonth).mark_errorband(extent='stdev',color='grey').encode(
    altair.X('date(Day):T', axis=altair.Axis(title='')),
    altair.Y('MonthlyCumSum', axis=altair.Axis(title='')),
).properties(width=200,height=200)

MonthlyChart = monthlyLineBand + monthlyLine + monthlyLineAvg

#Create yearlycumulative line chart
yearlyLine = altair.Chart(dailyCount).mark_line().encode(
    altair.X('DayOfYear:O'),
    altair.Y('YearlyCumSum', axis=altair.Axis(title='Total Bikes')),
    altair.Color('Day:O', timeUnit='year')  
).properties(width=200,height=200)

nearest = altair.selection(type='single', nearest=True, on='mouseover',fields=['DayOfYear'], empty='none')

# Transparent selectors across the chart. This is what tells us
# the x-value of the cursor
selectors = altair.Chart(dailyCount).mark_point().encode(
    x='DayOfYear:O',
    opacity=altair.value(0),
).add_selection(
    nearest
)

# Draw text labels near the points, and highlight based on selection
text = yearlyLine.mark_text(align='left', dx=100,dy=-25).encode(
    text=altair.condition(nearest, 'YearlyCumSum', altair.value(' ')),
)

# Draw a rule at the location of the selection
rules = altair.Chart(dailyCount).mark_rule(color='gray').encode(
    x='DayOfYear:O',
).transform_filter(
    nearest
)

yearlyLineCombined = altair.layer(
        yearlyLine,selectors,rules,text
)

yearlyLineCombined.save('yearlyTest.json')

#Create daily heatmap
heatmap = altair.Chart(dailyCount).mark_rect().encode(
    altair.X('day(Day):O', axis=altair.Axis(title='Day of the Week')),
    altair.Y('Day:O', timeUnit='year', axis=altair.Axis(title='Year')),
    altair.Color('mean(Count):Q', legend=altair.Legend(title='Mean Total Bikes')),
    altair.Tooltip('mean(Count)',format=',.0f')
).properties(width=200,height=200)

heatmap.save('overallTest.json')
#open the HTML doc  
with open (workingDir + '\\counterVisual.html') as counterPage:
    page = bs4.BeautifulSoup(counterPage)

#write out the map
page.find(id='counterMap').find('script').string.replace_with(mapHTML)

#write out the yesterday string
page.find(id="counterName").find('p').string.replace_with(countString)
page.find(id="counterName").find('li').string.replace_with(countStringYearlyRank)
page.find(id="counterName").find('li').find_next_sibling().string.replace_with(countStringDayRank)
page.find(id="counterName").find('li').find_next_sibling().find_next_sibling().string.replace_with(countStringOverallRank)

#write out the monthly data
monthlySpec = "var monthlySpec =" + MonthlyChart.to_json() + "; vegaEmbed('#visMonthly', monthlySpec); "
page.find(id='visMonthly').find('script').string.replace_with(monthlySpec)
page.find(id="monthlyText").find('p').string.replace_with(monthlyCountString)

#write out yearly data
yearlySpec = "var yearlySpec =" + yearlyLineCombined.to_json() + "; vegaEmbed('#visYearly', yearlySpec); "
page.find(id='visYearly').find('script').string.replace_with(yearlySpec)
page.find(id="yearlyText").find('p').string.replace_with(yearlyCountString)

#write out overall data
overallSpec = "var overallSpec =" + heatmap.to_json() + "; vegaEmbed('#visOverall', overallSpec); "
page.find(id='visOverall').find('script').string.replace_with(overallSpec)
page.find(id="overallText").find('p').string.replace_with(totalCountString)
page.find(id="overallText").find('li').string.replace_with(highestCountDayString)
page.find(id="overallText").find('li').find_next_sibling().string.replace_with(highestCountMonthString)


#write out the HTML
pageStr = bs4.BeautifulSoup.prettify(page)
with open (workingDir + '\\counterVisual.html',"w") as counterPage:
    counterPage.write(pageStr)