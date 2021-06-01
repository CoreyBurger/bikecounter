#! /usr/bin/python
import csv
from datetime import datetime,date, timedelta
import json
import urllib.request
import os
import pandas

#define constants
workingDir = os.getcwd()

#urlBase = "http://www.eco-public.com/api/cw6Xk4jW4X4R/data/periode/"
urlBase = "https://www.eco-visio.net/api/aladdin/1.0.0/pbl/publicwebpage/data/"
urlEnd = "&domain=4828&withNull=true"
yesterdayDate = date.today() - timedelta(1)
yesterday = yesterdayDate.strftime('%Y%m%d')
todayDate = date.today().strftime('%Y%m%d')

#reader in the counter list
#TODO - change to a Pandas dataframe
with open(workingDir + '\\countersToVisualize.csv') as csvCountersfile:
    csvCountersReader = csv.reader(csvCountersfile, delimiter=',')
    next(csvCountersReader)
    counters = list(csvCountersReader)

#iterate through the counters
for i in counters:
    print('Reading ',i[0])
    csvExportName = workingDir + '\\counts-' + i[1] + '.csv'

    #check for existing file, if found, append only yesterday, otherwise the full amount
    if os.path.isfile(csvExportName)==True:
        with open(csvExportName) as csvCountsFile:
            #read in the CSV file, figure out the last date and use that to start the reading
            csvExportReader = csv.reader(csvCountsFile,delimiter=',')
            next(csvExportReader)
            countsExport = list(csvExportReader)
            #define our dates
            lastDate = datetime.date(datetime.strptime(countsExport[-1][1][0:10],'%Y-%m-%d')) + timedelta(1)
            #check the two dates, yesterday and the largest date found, return the largest date if not the same as yesterday
            startDate = lastDate if lastDate != yesterday else yesterday
            #convert both dates to the correct format
            startDate = startDate.strftime('%Y%m%d')
        counts=[]
    else:
        counts=[["Count","Date"]]
        startDate = i[2]

    #create the url base with the start date
    

    if i[5] == 'BikeOnly':
        url=urlBase + i[1] + "?begin=" + startDate + "&end=" + todayDate + "&step=2" + urlEnd + "&t=" + i[6]
        #try and load the url
        try:
            print(url)
            response = urllib.request.urlopen(url)
        except:
            pass

        #read in the JSON data
        json_data = response.read()
        datapoints = json.loads(json_data)

        #for each data point, read it into a list
        for datapoint in datapoints:
            if datapoint['comptage'] is None:
                continue
            #countdatetime = datetime.strptime(datapoint['date'],'%Y-%m-%d %H:%M:%S.%f')
            count = [datapoint['comptage'], datapoint['date']]
            counts.append(count)
    elif i[5] == 'PedAndBike':
        counts3=[]
        counts4=[]

        url3=urlBase + i[8] + "?begin=" + startDate + "&end=" + todayDate + "&step=2" + urlEnd + "&t=" + i[6]
        url4=urlBase + i[9] + "?begin=" + startDate + "&end=" + todayDate + "&step=2" + urlEnd + "&t=" + i[6]
        try:
            print(url)
            response3 = urllib.request.urlopen(url3)
            response4 = urllib.request.urlopen(url4)
        except:
            pass

        #read in the JSON data
        json_data3 = response3.read()
        datapoints3 = json.loads(json_data3)

        json_data4 = response4.read()
        datapoints4 = json.loads(json_data4)

        #for each data point, read it into a list
        for datapoint in datapoints3:
            if datapoint['comptage'] is None:
                continue
            #countdatetime = datetime.strptime(datapoint['date'],'%Y-%m-%d %H:%M:%S.%f')
            count = [datapoint['comptage'], datapoint['date']]
            counts3.append(count)
        
        #for each data point, read it into a list
        for datapoint in datapoints4:
            if datapoint['comptage'] is None:
                continue
            #countdatetime = datetime.strptime(datapoint['date'],'%Y-%m-%d %H:%M:%S.%f')
            count = [datapoint['comptage'], datapoint['date']]
            counts4.append(count)
        
        #combine the two
        countsAll = [j + k for j, k in zip(counts3, counts4)]
        for count in countsAll:
            countAppend = [count[0]+count[2],count[1]] 
            counts.append(countAppend)
        
    #write that list out to a csv file
    with open(csvExportName, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(counts)