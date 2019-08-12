#! /usr/bin/python
import datetime
import json
import os
import pandas
import urllib.request

#define constants
workingDir = os.getcwd()

stationID ='0012'
yesterdayDate = (datetime.date.today() - datetime.timedelta(1))
yesterday = yesterdayDate.strftime('%Y-%m-%d')
yesterdayYearName = yesterdayDate.strftime("%Y")
urlBase = "http://www.victoriaweather.ca/data/"+yesterdayYearName+'/'

#set the base url
tempUrl=urlBase+'temperature_'+stationID+'_'+yesterday+'.csv'
rainUrl=urlBase+'raintotal_'+stationID+'_'+yesterday+'.csv'

tempData = pandas.read_csv(tempUrl)
rainData = pandas.read_csv(rainUrl)

#get the data needed
#TODO - change to read more midnight on
yesterdayTempMean = round(tempData.iloc[:,5].mean(),1)
yesterdayTotalRain = round(rainData.iloc[:,5].max(),1)

#read in the weather data
weatherData = pandas.read_csv('weatherData'+stationID+'.csv')

#append yesterday's data
todayData = pandas.Series([yesterday,yesterdayTempMean,yesterdayTotalRain],index=['Date','Temp','Rain'])
weatherData = weatherData.append(todayData,ignore_index=True)

#write out the data
weatherData.to_csv('weatherData'+stationID+'.csv', index=False)