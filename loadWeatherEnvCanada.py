#! /usr/bin/python
import datetime
import json
import os
#import pandas
import urllib.request
import time

#define constants
workingDir = os.getcwd()
print(workingDir)

stationID ='114'
# yesterdayDate = (datetime.date.today() - datetime.timedelta(1))
# yesterday = yesterdayDate.strftime('%Y-%m-%d')
# yesterdayYearName = yesterdayDate.strftime("%Y")
# yesterdayMonth = yesterdayDate.month
# yesterdayDay = yesterdayDate.day
# yesterdayYear = yesterdayDate.year
urlBase = "https://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID="
#&Year=${year}&Month=${month}&Day=14&timeframe=2&submit= Download+Data

#download the data
for year in range(2015,2022):
    weatherURL = urlBase + stationID + "&Year=" + str(year) + "&Month=1&Day=14&timeframe=2&submit=Download+Data"
    print(weatherURL)
    try:
        urllib.request.urlretrieve(weatherURL,stationID + '-' + str(year) + '.csv')
    except:
        pass