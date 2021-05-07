#! /usr/bin/python
import datetime
import json
import os
import pandas
import urllib.request
import time

#define constants
workingDir = os.getcwd()
print(workingDir)

stationID ='114'
yesterdayDate = (datetime.date.today() - datetime.timedelta(1))
todayDate = datetime.date.today()
yesterdayYear = yesterdayDate.year
urlBase = "https://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID="
#&Year=${year}&Month=${month}&Day=14&timeframe=2&submit= Download+Data

#read in the current weather data
weatherDataFile = 'weatherData'+stationID+'.csv'
if os.path.isfile(weatherDataFile)==True:
    weatherData = pandas.read_csv(weatherDataFile)
    weatherData["Date"] = pandas.to_datetime(weatherData["Date"]).dt.date
    maxDate = weatherData["Date"].max()
else:
    weatherDate=["Date","Temp","Rain"]
    maxDate = datetime.datetime.strptime('2015-01-01','%Y-%m-%d').dt.date

#download the data
for year in range(weatherData["Date"].max().year,yesterdayYear+1):
    weatherURL = urlBase + stationID + "&Year=" + str(year) + "&Month=1&Day=14&timeframe=2&submit=Download+Data"
    print(weatherURL)
    try:
        stationData = stationID + '-' + str(year) + '.csv'
        urllib.request.urlretrieve(weatherURL,stationData)
        #read back in new data
        newWeatherData = pandas.read_csv(stationData)
        newWeatherData["Date/Time"] = pandas.to_datetime(newWeatherData["Date/Time"]).dt.date

        #append the new data to the existing data
        newData = newWeatherData.loc[(newWeatherData["Date/Time"]>maxDate) & (newWeatherData["Date/Time"]<todayDate),["Date/Time","Mean Temp (°C)","Total Precip (mm)"]].rename(columns={"Date/Time": "Date", "Mean Temp (°C)": "Temp","Total Precip (mm)":"Rain"})
        weatherData = weatherData.append(newData,ignore_index=True)

        #write out the data
        weatherData.to_csv(weatherDataFile, index=False)

    except:
        pass