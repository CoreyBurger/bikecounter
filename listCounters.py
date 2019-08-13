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
urlBase = "http://www.eco-public.com/api/cw6Xk4jW4X4R/publicpage/"
counters=[["CounterID","CounterTitle","Lat","Long","Date"]]
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

#reader in the counter list
if os.path.exists(csvCountersfile):
    counters = pandas.read_csv(csvCountersfile)

newCounters=pandas.DataFrame(columns=['CounterID','CounterTitle','Lat','Long','Date'])

for i in range(101000000,101000500):
    print(i)
    url=urlBase + str(i)

    #try and load the url
    try:
        print(url)
        response = urllib.request.urlopen(url)
    except:
        pass

    #read in the JSON data
    json_data = response.read()
    if json_data.decode('utf-8') == 'Counter null':
        continue

    datapoint = json.loads(json_data)
    
    counter = pandas.DataFrame([[i,datapoint['titre'],datapoint['latitude'],datapoint['longitude'],datapoint['date']]])
    counter.columns=['CounterID','CounterTitle','Lat','Long','Date']
    newCounters = pandas.concat([newCounters,counter])

newCounters['CounterID'].size
counters.merge(newCounters, indicator='id', how='outer', on='CounterID').query('id == "both"')['CounterID'].size
counters.merge(newCounters, indicator='id', how='outer', on='CounterID').query('id == "right_only"').drop('id', 1)
#newCounters.to_csv(workingDir + '\\countersListNew.csv') 
#counters.to_csv(csvCountersfile)