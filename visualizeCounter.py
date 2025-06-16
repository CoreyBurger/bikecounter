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
import numpy

#define constants
#TODO Clean up to removal duplicate calls for yesterday
workingDir = os.getcwd()
todayYear = datetime.date.today().strftime('%Y')
yesterdayDate = datetime.date.today() - datetime.timedelta(1)
yesterday = yesterdayDate.strftime('%Y-%m-%d')
try:
    yesterdayLastYear = yesterdayDate.replace(year=datetime.date.today().year-1).strftime('%Y-%m-%d')
except ValueError:
    yesterdayLastYear = yesterdayDate.replace(year=datetime.date.today().year-1, day=yesterdayDate-1).strftime('%Y-%m-%d')
yesterdayDay = yesterdayDate.day
yesterdayDayName = yesterdayDate.strftime("%A")
yesterdayMonth = yesterdayDate.month
yesterdayMonthName =  yesterdayDate.strftime("%B")
yesterdayYear= yesterdayDate.year
yesterdayYearName = yesterdayDate.strftime("%Y")
locale.setlocale(locale.LC_ALL, 'en_CA')
ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n//10%10!=1)*(n%10<4)*n%10::4])

#load weather data
#weatherData = pandas.read_csv('weatherData'+counterList['VictoriaWeatherStation'][0]+'.csv',parse_dates=['Date']).set_index('Date')
weatherData = pandas.read_csv('weatherData114.csv',parse_dates=['Date']).set_index('Date')

#read in counters list
counterList  = pandas.read_csv('countersToVisualize.csv',parse_dates=['FirstDate','FirstFullYear'], dtype={'VictoriaWeatherStation': str})

for index,row in counterList.iterrows():
    #only visualize if visualize is set to 1 and FirstFullYear less than current year
    if row[['Visualize']].iloc[0]==1 and (row[['FirstDate']].iloc[0].strftime('%Y') is not None and row[['FirstDate']].iloc[0].strftime('%Y') < todayYear):
        print(row[['CounterID']].iloc[0])
        counterName = row[['CounterName']].iloc[0]
        print(counterName)
        counterStartDate = row[['FirstDate']].iloc[0]
        print(counterStartDate)

        #load data
        countFile = "counts-" + str(row[['CounterID']].iloc[0]) + ".csv"
        countExportFile = "counts-" + str(row[['CounterID']].iloc[0]) + "-export.csv"
        countData = pandas.read_csv(countFile,parse_dates=['Date'])
        specialDateFile = "specialDates.csv"
        specialDateData = pandas.read_csv(specialDateFile,parse_dates=['Date'])
        firstFullYear = row[['FirstDate']].iloc[0].strftime('%Y')

        #setup counter map
        mapHTML ="var countmap = L.map('counterMap').setView([" + row[['Location']].iloc[0] + "], 15);var marker = L.marker(["  + row[['Location']].iloc[0] +  "]).addTo(countmap);var background = L.tileLayer.provider('CyclOSM').addTo(countmap);"

        #resample to daily count
        dailyCount = countData.resample('D',on='Date').sum()

        #resample to hourly count
        hourlyCount = countData.resample('h',on='Date').sum()
        hourlyCount['Hour'] = hourlyCount.index.hour
        hourlyCount['Year'] = hourlyCount.index.year
        hourlyCount['DayoftheWeek'] = hourlyCount.index.dayofweek
        
        #determine total rides
        totalRides = dailyCount['Count'].sum()

        #remove all data from partial years
        dailyCount = dailyCount.loc[dailyCount.index >= row[['FirstFullYear']].iloc[0]]
        hourlyCount = hourlyCount.loc[hourlyCount.index >= row[['FirstFullYear']].iloc[0]]

        #add columns for weekly, monthly, and yearly cumulative total, plus weekday and day of the year
        YearlyCumSum = dailyCount.groupby(dailyCount.index.to_period('Y')).cumsum()
        YearlyCumSum.rename(columns={'Count':'YearlyCumSum'}, inplace=True)
        MonthlyCumSum = dailyCount.groupby(dailyCount.index.to_period('M')).cumsum()
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
        #print(dailyCount.loc[dailyCount.index==yesterday]['Count'][0])
        try:  
            yesterdayCount = dailyCount.loc[dailyCount.index==yesterday]['Count'].iloc[0]
        except IndexError as error:
            continue
        
        yesterdayCountString = locale.format_string("%d",yesterdayCount, grouping=True)

        #determine daily rank
        dailyRankAll = dailyCount.loc[dailyCount['Count']>yesterdayCount]['Count'].size+1
        dailyRankThisYear=dailyCount.loc[dailyCount.index.year==yesterdayYear].loc[dailyCount['Count']>yesterdayCount]['Count'].size+1
        dailyRankDayOnly=dailyCount.loc[dailyCount.index.dayofweek==yesterdayDate.weekday()].loc[dailyCount['Count']>yesterdayCount]['Count'].size+1
        dailyRankMonthOnly=dailyCount.loc[dailyCount.index.month==yesterdayMonth].loc[dailyCount['Count']>yesterdayCount]['Count'].size+1

        #TODO = genericize
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

        if dailyRankMonthOnly==1:
            dailyRankMonthOnly=None
        else:
            dailyRankMonthOnly = str(ordinal(dailyRankMonthOnly)) + " "

        #Check if yesterday was anything special
        try:
            specialDateStringYesterday = "Yesterday was " + specialDateData[specialDateData['Date']==yesterdayDate].Event.iloc[0] + ""
        except IndexError as error:
            specialDateStringYesterday = None

        #craft the string for yesterday
        countString ="Yesterday saw " + yesterdayCountString + " bike rides,"
        countStringYearlyRank = "".join(filter(None,("...", dailyRankThisYear,"busiest day of ",yesterdayYearName)))
        countStringMonthlyRank = "".join(filter(None,("...", dailyRankMonthOnly,"busiest day in ",yesterdayMonthName)))
        countStringDayRank = "".join(filter(None,("...", dailyRankDayOnly,"busiest ",yesterdayDayName)))
        countStringOverallRank = "".join(filter(None,("...", dailyRankAll,"busiest day overall")))

        #resample to monthly count
        monthlyCount = countData.resample('ME',on='Date').sum()
        monthlyCount['Month'] = monthlyCount.index
        monthlyCount = monthlyCount.loc[monthlyCount['Month'] >= '2015-01-31']

        #Pull out the current month
        currentMonth = pandas.DataFrame(dailyCount.loc[dailyCount.index.month==yesterdayMonth])

        #check if we are ahead or behind the average monthly cumulative sum
        #TODO genericize the function to deal with both yearly & monthly
        yesterdayMonthCumSumMean=numpy.nanmean(dailyCount.loc[(dailyCount.index.month==yesterdayMonth) & (dailyCount.index.day==yesterdayDay)].MonthlyCumSum)
        yesterdayMonthlyCumSum=pandas.DataFrame(dailyCount.loc[dailyCount.index==yesterday]).MonthlyCumSum.iloc[0]
        lastyearMonthlyCumSum=pandas.DataFrame(dailyCount.loc[dailyCount.index==yesterdayLastYear]).MonthlyCumSum.iloc[0]
        yesterdayMonChange=(yesterdayMonthlyCumSum-yesterdayMonthCumSumMean)/yesterdayMonthCumSumMean

        #compare this year to average
        if yesterdayMonChange<-0.05:
            monthlyCountString='less busy than'
        elif yesterdayMonChange>0.05:
            monthlyCountString='busier than'
        else:
            monthlyCountString='about as busy as'

        monthIsWas = "was" if datetime.date.today().day==1 else "is"

        monthlyCountString=  yesterdayMonthName +  " " + monthIsWas + " " + monthlyCountString + " average, with " + locale.format_string("%d", yesterdayMonthlyCumSum, grouping=True) + " rides so far this month, as compared to " + locale.format_string("%d", lastyearMonthlyCumSum, grouping=True) + " last year and " + locale.format_string("%d", yesterdayMonthCumSumMean, grouping=True) + " on average" 

        #TODO - deal with leap years
        yesterdayYearlyCumSum=dailyCount[dailyCount.index==yesterday]['YearlyCumSum'].iloc[0]
        lastyearYearlyCumSum=dailyCount[dailyCount.index==(datetime.date.today() - datetime.timedelta(365)).strftime('%Y-%m-%d')]['YearlyCumSum'].iloc[0]
        yesterdayYearChange = (yesterdayYearlyCumSum-lastyearYearlyCumSum)/yesterdayYearlyCumSum

        if yesterdayYearChange<-0.05:
            yearlyCountString='less busy than'
        elif yesterdayYearChange>0.05:
            yearlyCountString='busier than'
        else:
            yearlyCountString='about as busy as'

        yearIsWas = "was" if (datetime.date.today().day==1 and datetime.date.today().month==1) else "is"

        yearlyCountString =  yesterdayYearName +  " " + yearIsWas + " " + yearlyCountString + " last year, with " + locale.format_string("%d", yesterdayYearlyCumSum, grouping=True) + " rides so far this year (compared to " + locale.format_string("%d", lastyearYearlyCumSum, grouping=True) + " rides this time last year)"

        #Determine how many of the top 10 days were this year
        numHighestDays = len(dailyCount.sort_values('Count',ascending=False).head(10)[dailyCount.sort_values('Count',ascending=False).head(10).index.year==yesterdayYear])
        numHighestDaysString = str(numHighestDays) + " of the top 10 busiest days have been in " + yesterdayYearName

        #Determine total counts since beginning of counter
        totalCountString = "Since " + row[['FirstDate']].iloc[0].strftime('%A, %b %d, %Y') + " there have been " + locale.format_string("%d", totalRides, grouping=True) + " rides past the counter"

        #Show day of the year
        dayofYearString = 'Today is the ' + str(ordinal(dailyCount.loc[dailyCount.index==yesterday]['DayOfYear'].iloc[0])) + ' day of the year'
                
        #Determine busiest day and month
        highestCountDay = dailyCount[dailyCount['Count']==dailyCount['Count'].max()].index[0]
        highestCountDayString=highestCountDay.strftime('%A %B %d, %Y')
        highestCountMonth=monthlyCount[monthlyCount['Count']==monthlyCount['Count'].max()]['Month'].iloc[0]
        highestCountMonthString = "The busiest month ever was " + highestCountMonth.strftime('%B %Y')

        #Check if the highest day was anything special
        try:
            specialDateStringHighest = "(" + specialDateData[specialDateData['Date']==highestCountDay].Event.iloc[0] + ")"
        except IndexError as error:
            specialDateStringHighest = None

        highestCountDayString = " ".join(filter(None,("The busiest day ever was",highestCountDayString,specialDateStringHighest)))

        #Determine weather stats
        
        #Yesterday's weather
        yesterdayTemp = dailyCount.loc[dailyCount.index==yesterday]['Temp'].iloc[0]
        yesterdayTempRainString = "Yesterday was an average of " + str(yesterdayTemp) + " C with "

        yesterdayRain = dailyCount.loc[dailyCount.index==yesterday]['Rain'].iloc[0]
        if yesterdayRain > 0:
            yesterdayRainString = str(yesterdayRain) + "mm of rain"
        elif yesterdayRain == 0:
            yesterdayRainString = "no rain"
        else:
            yesterdayRainString = "unknown precipitation"

        yesterdayTempRainString += yesterdayRainString
        
        #Days without rain
        daysWithoutRainString = "There have been " + str(dailyCount[dailyCount.index.year==yesterdayYear].loc[dailyCount['Rain']==0]['Rain'].size) + " days without rain this year"

        #Avg Temp
        currentMonthlyTempMean = numpy.nanmean(dailyCount.loc[(dailyCount.index.month==yesterdayMonth) & (dailyCount.index.day<=yesterdayDay) & (dailyCount.index.year==yesterdayYear)].Temp)      
        averageMonthlyTempMean = numpy.nanmean(dailyCount.loc[(dailyCount.index.month==yesterdayMonth) & (dailyCount.index.day<=yesterdayDay)].Temp)
        monthlyTempMeanChange = (currentMonthlyTempMean-averageMonthlyTempMean)/currentMonthlyTempMean

        yesterdayTempChangeString =yesterdayMonthName + ' has had an average temperature of ' + str(round(currentMonthlyTempMean,1)) + ' C'
        if monthlyTempMeanChange<-0.05:
            yesterdayTempChangeString+=' (colder than the average of ' + str(round(averageMonthlyTempMean,1)) + " C)"
        elif monthlyTempMeanChange>0.05:
            yesterdayTempChangeString+=' (warmer than the average of ' + str(round(averageMonthlyTempMean,1)) + " C)"
        else:
            yesterdayTempChangeString+=' (similar to the average of ' + str(round(averageMonthlyTempMean,1)) + " C)"

        #Avg Rain
        currentMonthlyRainTotal = numpy.nansum(dailyCount.loc[(dailyCount.index.month==yesterdayMonth) & (dailyCount.index.day<=yesterdayDay) & (dailyCount.index.year==yesterdayYear)].Rain)      
        averageMonthlyRainTotal = numpy.nansum(dailyCount.loc[(dailyCount.index.month==yesterdayMonth) & (dailyCount.index.day<=yesterdayDay)].Rain)/(int(todayYear)-int(firstFullYear)+1)
        if averageMonthlyRainTotal >0:
            monthlyRainTotalChange = (currentMonthlyRainTotal-averageMonthlyRainTotal)/averageMonthlyRainTotal
        else:
            monthlyRainTotalChange = 0
        
        # print(currentMonthlyRainTotal)
        # print(averageMonthlyRainTotal)
        # print((int(todayYear)-int(firstFullYear)+1))
        # print(monthlyRainTotalChange) 

        yesterdayRainTotalString =yesterdayMonthName + ' had a total rainfall of ' + str(round(currentMonthlyRainTotal,1)) + ' mm'
        if monthlyRainTotalChange>0.05:
            yesterdayRainTotalString+=' (wetter than the average of ' + str(round(averageMonthlyRainTotal,1)) + " mm)"
        elif monthlyRainTotalChange<-0.05:
            yesterdayRainTotalString+=' (drier than the average of ' + str(round(averageMonthlyRainTotal,1)) + " mm)"
        else:
            yesterdayRainTotalString+=' (similar to the average of ' + str(round(averageMonthlyRainTotal,1)) + " mm)"

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
            altair.Y('mean(Count):Q', axis=altair.Axis(title='Average Bikes per Day'), scale=altair.Scale(domain=(0,4000))),
            altair.Color('Date:O', timeUnit='year', legend=altair.Legend(title='Year'))  
        ).properties(width=200,height=200)

        #Create yearlycumulative line chart
        yearlyLine = altair.Chart(dailyCount).mark_line().encode(
            altair.X('DayOfYear:O'),
            altair.Y('YearlyCumSum', axis=altair.Axis(title='Total Bikes')),
            altair.Color('Date:O', timeUnit='year')
        ).properties(width=200,height=200)

        #TODo - Fix this
        #nearest = altair.selection(type='single', nearest=True, on='mouseover',fields=['DayOfYear'], empty='none')

        # Transparent selectors across the chart. This is what tells us
        # the x-value of the cursor
        selectors = altair.Chart(dailyCount).mark_point().encode(
            x='DayOfYear:O',
            opacity=altair.value(0)
        # ).add_selection(
        #     nearest
        )

        # Draw text labels near the points, and highlight based on selection
        # text = yearlyLine.mark_text(align='left', dx=5,dy=-5).encode(
        #     text=altair.condition(nearest, 'YearlyCumSum', altair.value(' ')),
        #     x=altair.value(200)
        # )

        # Draw a rule at the location of the selection
        # rules = altair.Chart(dailyCount).mark_rule(color='gray').encode(
        #     x='DayOfYear:O',
        # ).transform_filter(
        #     nearest
        # )

        yearlyLineCombined = altair.layer(
                yearlyLine,selectors#,rules,text
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
            altair.X('Temp:Q', bin=True, axis=altair.Axis(title='Temperature')),
            altair.Y('Date:O', timeUnit='year', axis=altair.Axis(title='Year')),
            altair.Color('mean(Count):Q', legend=altair.Legend(title='Mean Total Bikes')),
            altair.Tooltip('mean(Count)',format=',.0f')
        ).properties(width=200,height=200)

        #open the HTML doc  
        with open (workingDir + '\\counterVisualTemplate.html') as counterPage:
            page = bs4.BeautifulSoup(counterPage, features="html.parser")

        #write out the map
        page.find(id='counterMap').find('script').string.replace_with(mapHTML)

        #write out the counter name
        page.find('title').string.replace_with(counterName)
        page.find(id="counterName").find('h1').string.replace_with(counterName)

        #write out the yesterday string
        #TODO cleanup to walk through list of li
        page.find(id="counterName").find('p').string.replace_with(countString)
        page.find(id="counterName").find('li').string.replace_with(countStringYearlyRank)
        page.find(id="counterName").find('li').find_next_sibling().string.replace_with(countStringMonthlyRank)
        page.find(id="counterName").find('li').find_next_sibling().find_next_sibling().string.replace_with(countStringDayRank)
        page.find(id="counterName").find('li').find_next_sibling().find_next_sibling().find_next_sibling().string.replace_with(countStringOverallRank)
        if specialDateStringYesterday is not None:
            page.find(id="counterName").find('p').find_next_sibling().find_next_sibling().find_next_sibling().string.replace_with(specialDateStringYesterday)

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
        page.find(id="yearlyText").find('li').find_next_sibling().string.replace_with(dayofYearString)

        #write out overall data
        overallSpec = "var overallSpec =" + heatmap.to_json() + "; vegaEmbed('#visOverall', overallSpec); "
        page.find(id='visOverall').find('script').string.replace_with(overallSpec)
        page.find(id="overallText").find('p').string.replace_with(totalCountString)
        page.find(id="overallText").find('li').string.replace_with(highestCountDayString)
        page.find(id="overallText").find('li').find_next_sibling().string.replace_with(highestCountMonthString)

        #write out the weather data
        weatherSpec = "var weatherSpec =" + tempCount.to_json() + "; vegaEmbed('#visWeather', weatherSpec); "
        page.find(id='visWeather').find('script').string.replace_with(weatherSpec)
        page.find(id="weatherText").find('p').string.replace_with(yesterdayTempRainString)
        page.find(id="weatherText").find('li').string.replace_with(daysWithoutRainString)        
        page.find(id="weatherText").find('li').find_next_sibling().string.replace_with(yesterdayTempChangeString)
        page.find(id="weatherText").find('li').find_next_sibling().find_next_sibling().string.replace_with(yesterdayRainTotalString)

        #write out the HTML
        pageStr = bs4.BeautifulSoup.prettify(page)
        with open (workingDir + '\\counterVisual-' + str(row[['CounterID']].iloc[0]) + '.html',"w") as counterPage:
            counterPage.write(pageStr)