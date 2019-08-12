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
#100000000-100063472
#100105000-100160000

#reader in the counter list
if os.path.exists(csvCountersfile):
    counters = pandas.read_csv(csvCountersfile)

newCounters=pandas.DataFrame(columns=['CounterID','CounterTitle','Lat','Long','Date'])

for i in range(100126835,100126836):
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

counters.merge(newCounters, indicator='id', how='outer', on='CounterID').query('id == "right_only"').drop('id', 1)
#newCounters.to_csv(workingDir + '\\countersListNew.csv') 
#counters.to_csv(csvCountersfile)