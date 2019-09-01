#! /usr/bin/python
import datetime
import json
import os
import pandas
import urllib.request
import time

#define constants
workingDir = os.getcwd()

stationID ='0012'
stationIDint = int(stationID)
yesterdayDate = (datetime.date.today() - datetime.timedelta(1))
yesterday = yesterdayDate.strftime('%Y-%m-%d')
yesterdayYearName = yesterdayDate.strftime("%Y")
yesterdayMonth = yesterdayDate.month
yesterdayDay = yesterdayDate.day
yesterdayYear = yesterdayDate.year
urlBase = "http://www.victoriaweather.ca/data/"+yesterdayYearName+'/'
primeURLBase = "http://www.victoriaweather.ca/data.php?field="

#set the base url
tempUrl=urlBase+'temperature_'+stationID+'_'+yesterday+'.csv'
rainUrl=urlBase+'raintotal_'+stationID+'_'+yesterday+'.csv'

#prime the csv creation tool
primeStationDetails = '&id=' +  str(stationIDint) + '&year=' + str(yesterdayYear) + '&month=' + str(yesterdayMonth) + '&day=' + str(yesterdayDay) + '&notable=1'
tempPrimeURL = primeURLBase + 'temperature' + primeStationDetails
rainPrimeURL = primeURLBase + 'raintotal' + primeStationDetails

try:
    urllib.request.urlopen(tempPrimeURL)
except:
    pass

try:
    urllib.request.urlopen(rainPrimeURL)
except:
    pass

#give the system time to generate the CSVs
time.sleep(2)

#read the csv from the URL
tempData = pandas.read_csv(tempUrl)
rainData = pandas.read_csv(rainUrl)

#get the data needed
yesterdayTempMean = round(tempData.iloc[:,5].mean(),1)
yesterdayTotalRain = round(rainData.iloc[1:,5].max(),1)

#read in the weather data
weatherData = pandas.read_csv('weatherData'+stationID+'.csv')

#append yesterday's data
todayData = pandas.Series([yesterday,yesterdayTempMean,yesterdayTotalRain],index=['Date','Temp','Rain'])
weatherData = weatherData.append(todayData,ignore_index=True)

#write out the data
weatherData.to_csv('weatherData'+stationID+'.csv', index=False)