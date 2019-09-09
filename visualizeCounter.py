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
counterList  = pandas.read_csv('counters.csv',parse_dates=['FirstDate','FirstFullYear'], dtype={'VictoriaWeatherStation': str})
counterName = counterList['CounterName'][0]
counterStartDate = counterList['FirstDate'][0]

#load data
countFile = "counts-" + str(counterList['CounterID'][0]) + ".csv"
countExportFile = "counts-" + str(counterList['CounterID'][0]) + "-export.csv"
countData = pandas.read_csv(countFile,parse_dates=['Date'])
specialDateFile = "specialDates.csv"
specialDateData = pandas.read_csv(specialDateFile,parse_dates=['Date'])
weatherData = pandas.read_csv('weatherData'+counterList['VictoriaWeatherStation'][0]+'.csv',parse_dates=['Date']).set_index('Date')

#setup counter map
mapHTML ="var countmap = L.map('counterMap').setView([48.432613, -123.3782], 15);var marker = L.marker([48.432613, -123.37829]).addTo(countmap);var background = L.tileLayer.provider('Stamen.Toner').addTo(countmap);"

#resample to daily count
dailyCount = countData.resample('D',on='Date').sum()

#determine total rides
totalRides = dailyCount['Count'].sum()

#remove all data from partial years
dailyCount = dailyCount.loc[dailyCount.index >= counterList['FirstFullYear'][0]]

#add columns for weekly, monthly, and yearly cumulative total, plus weekday and day of the year
YearlyCumSum = dailyCount.groupby(dailyCount.index.to_period('y')).cumsum()
YearlyCumSum.rename(columns={'Count':'YearlyCumSum'}, inplace=True)
MonthlyCumSum = dailyCount.groupby(dailyCount.index.to_period('m')).cumsum()
MonthlyCumSum.rename(columns={'Count':'MonthlyCumSum'}, inplace=True)
WeeklyCumSum = dailyCount.groupby(dailyCount.index.strftime('%y%W')).cumsum()
WeeklyCumSum.rename(columns={'Count':'WeeklyCumSum'}, inplace=True)
dailyCount = pandas.merge(dailyCount,YearlyCumSum,on='Date')
dailyCount = pandas.merge(dailyCount,MonthlyCumSum,on='Date')
dailyCount = pandas.merge(dailyCount,WeeklyCumSum,on='Date')
dailyCount['WeekNum']=dailyCount.index.strftime('%W')
dailyCount['Weekday']=dailyCount.index.dayofweek 
dailyCount['DayOfYear'] = dailyCount.index.dayofyear

#append weather data to dailyCount
dailyCount = pandas.merge(dailyCount,weatherData,on=['Date'])

#write that list out to a csv file
dailyCount.to_csv(countExportFile)

#get yesterdays count   
yesterdayCount = dailyCount.loc[dailyCount.index==yesterday]['Count'][0]
yesterdayCountString = locale.format_string("%d",yesterdayCount, grouping=True)

#determine daily rank
dailyRankAll = dailyCount.loc[dailyCount['Count']>yesterdayCount]['Count'].size+1
dailyRankThisYear=dailyCount.loc[dailyCount.index.year==datetime.datetime.now().year].loc[dailyCount['Count']>yesterdayCount]['Count'].size+1
dailyRankDayOnly=dailyCount.loc[dailyCount.index.dayofweek==yesterdayDate.weekday()].loc[dailyCount['Count']>yesterdayCount]['Count'].size+1

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
    specialDateStringYesterday = "Yesterday was " + specialDateData[specialDateData['Date']==yesterdayDate].Event.iloc[0] + ""
except IndexError as error:
    specialDateStringYesterday = None

#craft the string for yesterday
countString ="Yesterday saw " + yesterdayCountString + " bike rides,"
countStringYearlyRank = "".join(filter(None,("...", dailyRankThisYear,"busiest day of ",yesterdayYearName)))
countStringDayRank = "".join(filter(None,("...", dailyRankDayOnly,"busiest ",yesterdayDayName)))
countStringOverallRank = "".join(filter(None,("...", dailyRankAll,"busiest day overall")))

#resample to monthly count
monthlyCount = countData.resample('M',on='Date').sum()
monthlyCount['Month'] = monthlyCount.index
monthlyCount = monthlyCount.loc[monthlyCount['Month'] >= '2015-01-31']

#Pull out the current month
currentMonth = pandas.DataFrame(dailyCount.loc[dailyCount.index.month==yesterdayMonth])

#check if we are ahead or behind the average monthly cumulative sum
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

monthIsWas = "was" if datetime.date.today().day==1 else "is"

monthlyCountString=  yesterdayMonthName +  " " + monthIsWas + " " + monthlyCountString + " average, with " + locale.format_string("%d", yesterdayMonthlyCumSum, grouping=True) + " rides so far this month"

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

yearIsWas = "was" if (datetime.date.today().day==1 and datetime.date.today().month==1) else "is"

yearlyCountString =  yesterdayYearName +  " " + yearIsWas + " " + yearlyCountString + " last year, with " + locale.format_string("%d", yesterdayYearlyCumSum, grouping=True) + " rides so far this year (compared to " + locale.format_string("%d", lastyearYearlyCumSum, grouping=True) + " rides this time last year)"

#Determine how many of the top 10 days were this year
numHighestDays = len(dailyCount.sort_values('Count',ascending=False).head(10)[dailyCount.sort_values('Count',ascending=False).head(10).index.year==yesterdayYear])
numHighestDaysString = str(numHighestDays) + " of the top 10 busiest days have been in " + yesterdayYearName

#Determine total counts since beginning of counter
totalCountString = "Since " + counterList['FirstDate'][0].strftime('%A, %b %d, %Y') + " there have been " + locale.format_string("%d", totalRides, grouping=True) + " rides past the counter"
 
#Determine busiest day and month
highestCountDay = dailyCount[dailyCount['Count']==dailyCount['Count'].max()].index[0]
highestCountDayString=highestCountDay.strftime('%A %B %d, %Y')
highestCountMonth=monthlyCount[monthlyCount['Count']==monthlyCount['Count'].max()]['Month'][0]
highestCountMonthString = "The busiest month ever was " + highestCountMonth.strftime('%B %Y')

#Check if the highest day was anything special
try:
    specialDateStringHighest = "(" + specialDateData[specialDateData['Date']==highestCountDay].Event.iloc[0] + ")"
except IndexError as error:
    specialDateStringHighest = None

highestCountDayString = " ".join(filter(None,("The busiest day ever was",highestCountDayString,specialDateStringHighest)))

#Determine weather stats
dailyCount[dailyCount.index.year==datetime.datetime.now().year].loc[dailyCount['Rain']==0]['Rain'].size
#Days of sunshine
#Avg Temp

#reset index to allow use in altair
dailyCount = dailyCount.reset_index()
currentMonth = currentMonth.reset_index()

#Create monthly cumulative line chart
monthlyLine = altair.Chart(currentMonth).mark_line(stroke='#f304d3').encode(
    altair.X('date(Date):T', axis=altair.Axis(title='Day of the Month')),
    altair.Y('MonthlyCumSum', axis=altair.Axis(title='Total Bikes'), scale=altair.Scale(domain=(0,100000))),
    altair.Color('Date:O', timeUnit='year', legend=altair.Legend(title='Year'))  
).transform_filter(
    altair.FieldEqualPredicate(timeUnit='year',field='Date',equal=datetime.date.today().year)
).properties(width=200,height=200)

monthlyLineAvg = altair.Chart(currentMonth).mark_line(color='grey',strokeDash=[8,8]).encode(
    altair.X('date(Date):T', axis=altair.Axis(title='')),
    altair.Y('mean(MonthlyCumSum)', axis=altair.Axis(title='')),
).properties(width=200,height=200)

monthlyLineBand = altair.Chart(currentMonth).mark_errorband(extent='stdev',color='grey').encode(
    altair.X('date(Date):T', axis=altair.Axis(title='')),
    altair.Y('MonthlyCumSum', axis=altair.Axis(title='')),
).properties(width=200,height=200)

MonthlyChart = monthlyLineBand + monthlyLine + monthlyLineAvg

#Daily mean
dailyMean = altair.Chart(dailyCount).mark_line().encode(
    altair.X('month(Date):T', axis=altair.Axis(title='Months')),
    altair.Y('mean(Count):Q', axis=altair.Axis(title='Average Bikes per Day')),
    altair.Color('Date:O', timeUnit='year', legend=altair.Legend(title='Year'))  
).properties(width=200,height=200)

#Create yearlycumulative line chart
yearlyLine = altair.Chart(dailyCount).mark_line().encode(
    altair.X('DayOfYear:O'),
    altair.Y('YearlyCumSum', axis=altair.Axis(title='Total Bikes')),
    altair.Color('Date:O', timeUnit='year',sort='descending')  
).properties(width=200,height=200)

nearest = altair.selection(type='single', nearest=True, on='mouseover',fields=['DayOfYear'], empty='none')

# Transparent selectors across the chart. This is what tells us
# the x-value of the cursor
selectors = altair.Chart(dailyCount).mark_point().encode(
    x='DayOfYear:O',
    opacity=altair.value(0)
).add_selection(
    nearest
)

# Draw text labels near the points, and highlight based on selection
text = yearlyLine.mark_text(align='left', dx=5,dy=-5).encode(
    text=altair.condition(nearest, 'YearlyCumSum', altair.value(' ')),
    x=altair.value(200)
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
    altair.X('day(Date):O', axis=altair.Axis(title='Day of the Week')),
    altair.Y('Date:O', timeUnit='year', axis=altair.Axis(title='Year')),
    altair.Color('mean(Count):Q', legend=altair.Legend(title='Mean Total Bikes')),
    altair.Tooltip('mean(Count)',format=',.0f')
).properties(width=200,height=200)

# heatmapText = altair.Chart(dailyCount).mark_text().encode(
#     altair.X('day(Date):O', axis=altair.Axis(title='Day of the Week')),
#     altair.Y('Date:O', timeUnit='year', axis=altair.Axis(title='Year')),
#     altair.Text('mean(Count)',format=',.0f')
# )
# heatmap = heatmap + heatmapText

heatmap.save('overallTest.json')

#Visual temperature with count volumes
tempCount = altair.Chart(dailyCount).mark_rect().encode(
    altair.X('Temp:Q', bin=True),
    altair.Y('Date:O', timeUnit='year'),
    altair.Color('mean(Count):Q'),
    altair.Tooltip('mean(Count)',format=',.0f')
).properties(width=200,height=200)

#open the HTML doc  
with open (workingDir + '\\counterVisualTemplate.html') as counterPage:
    page = bs4.BeautifulSoup(counterPage)

#write out the map
page.find(id='counterMap').find('script').string.replace_with(mapHTML)

#write out the counter name
page.find('title').string.replace_with(counterName)
page.find(id="counterName").find('h1').string.replace_with(counterName)

#write out the yesterday string
page.find(id="counterName").find('p').string.replace_with(countString)
page.find(id="counterName").find('li').string.replace_with(countStringYearlyRank)
page.find(id="counterName").find('li').find_next_sibling().string.replace_with(countStringDayRank)
page.find(id="counterName").find('li').find_next_sibling().find_next_sibling().string.replace_with(countStringOverallRank)
if specialDateStringYesterday is not None:
    page.find(id="counterName").find('p').find_next_sibling().find_next_sibling().string.replace_with(specialDateStringYesterday)

#write out the monthly data
monthlySpec = "var monthlySpec =" + MonthlyChart.to_json() + "; vegaEmbed('#visMonthly', monthlySpec); "
dailyMeanSpec = "var dailyMeanSpec =" + dailyMean.to_json() + "; vegaEmbed('#visMonthly2', dailyMeanSpec); "
page.find(id='visMonthly').find('script').string.replace_with(monthlySpec)
page.find(id='visMonthly2').find('script').string.replace_with(dailyMeanSpec)
page.find(id="monthlyText").find('p').string.replace_with(monthlyCountString)

#write out yearly data
yearlySpec = "var yearlySpec =" + yearlyLineCombined.to_json() + "; vegaEmbed('#visYearly', yearlySpec); "
page.find(id='visYearly').find('script').string.replace_with(yearlySpec)
page.find(id="yearlyText").find('p').string.replace_with(yearlyCountString)
page.find(id="yearlyText").find('li').string.replace_with(numHighestDaysString)

#write out overall data
overallSpec = "var overallSpec =" + heatmap.to_json() + "; vegaEmbed('#visOverall', overallSpec); "
page.find(id='visOverall').find('script').string.replace_with(overallSpec)
page.find(id="overallText").find('p').string.replace_with(totalCountString)
page.find(id="overallText").find('li').string.replace_with(highestCountDayString)
page.find(id="overallText").find('li').find_next_sibling().string.replace_with(highestCountMonthString)

#write out the weather data
weatherSpec = "var weatherSpec =" + tempCount.to_json() + "; vegaEmbed('#visWeather', weatherSpec); "
page.find(id='visWeather').find('script').string.replace_with(weatherSpec)

#write out the HTML
pageStr = bs4.BeautifulSoup.prettify(page)
with open (workingDir + '\\counterVisual.html',"w") as counterPage:
    counterPage.write(pageStr)