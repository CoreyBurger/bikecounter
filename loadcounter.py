#! /usr/bin/python
import csv
from datetime import datetime,date, timedelta
import json
import urllib.request
import os

#define constants
workingDir = os.getcwd()
urlBase = "http://www.eco-public.com/api/cw6Xk4jW4X4R/data/periode/"


#reader in the counter list
with open(workingDir + '\\counters.csv') as csvCountersfile:
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
            yesterday = date.today() - timedelta(1)
            lastDate = datetime.date(datetime.strptime(countsExport[-1][1][0:10],'%Y-%m-%d')) + timedelta(1)
            #check the two dates, yesterday and the largest date found, return the largest date if not the same as yesterday
            startDate = lastDate if lastDate != yesterday else yesterday
            #convert both dates to the correct format
            yesterday = yesterday.strftime('%Y%m%d')
            startDate = startDate.strftime('%Y%m%d')
        counts=[]
    else:
        counts=[["Count","Date"]]
        startDate = i[2]

    #create the url base with the start date
    url=urlBase + i[1] + "?begin=" + startDate + "&end=" + yesterday + "&step=2"

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

    #write that list out to a csv file
    with open(csvExportName, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(counts)