#! /usr/bin/python
import csv
from datetime import datetime,date,timedelta,time
import json
import urllib.request
import os
import pandas
import itertools

#define constants
workingDir = os.getcwd()
#urlBase = "http://www.eco-public.com/api/cw6Xk4jW4X4R/publicpage/"
urlBase = 'https://www.eco-visio.net/api/aladdin/1.0.0/pbl/publicwebpage/'
#counters=[["CounterID","CounterTitle","Lat","Long","Date","DateChecked"]]
csvCountersfile=workingDir + '\\countersList.csv'

#Ranges checked
#99999500 -100000000
#100000000-100064000
#100068500-100070000
#100079500-100080500
#100105000-100162157
#100180000-100180500
#100190000-100190500
#100200000-100200500
#100210000-100210500
#100220000-100220500
#100300000-100300500
#100400000-100400500

#These appear to be directional data for counters in the above ranges
#101000000-101000000

#read in the counter list
if os.path.exists(csvCountersfile):
    counters = pandas.read_csv(csvCountersfile)

newCounters=pandas.DataFrame(columns=['CounterID','CounterTitle','Lat','Long','Date','DateChecked'])

for i in range(300040000,300045000):
    print(i)
    url=urlBase + str(i) + '?withNull=true'

    #try and load the url
    try:
        print(url)
        response = urllib.request.urlopen(url)
    except:
        pass

    #read in the JSON data
    json_data = response.read()
    if json_data.decode('utf-8') == 'Counter null':
        counter = pandas.DataFrame([[i,'No Counter','','','',datetime.today().strftime('%Y/%m/%d')]])
    else:
        datapoint = json.loads(json_data)
        counter = pandas.DataFrame([[i,datapoint['titre'],datapoint['latitude'],datapoint['longitude'],datapoint['date'],datetime.today().strftime('%Y/%m/%d')]])
    counter.columns=['CounterID','CounterTitle','Lat','Long','Date','DateChecked']
    newCounters = pandas.concat([newCounters,counter])

#check for new counters
counters.merge(newCounters, indicator='id', how='outer', on='CounterID').query('id == "right_only"').query('CounterTitle_y!="No Counter"')

#list of duplicated counters
counters.merge(newCounters, indicator='id', how='outer', on='CounterID').query('id == "both"')

#merge the two lists, then sort
completeCounters = pandas.concat([counters,newCounters],ignore_index=True).sort_values(['CounterID'])

#write out the data
completeCounters.to_csv(workingDir + '\\countersList.csv',index=False)