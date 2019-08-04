#! /usr/bin/python
import csv
from datetime import datetime,date,timedelta,time
import json
import urllib.request
import os

#define constants
workingDir = os.getcwd()
urlBase = "http://www.eco-public.com/api/cw6Xk4jW4X4R/publicpage/"
counters=[["CounterID","CounterTitle","Lat","Long","Date"]]

#100150000
#100000000,100000001

for i in range(100117730,100117732):
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

    counter = [i,datapoint['titre'],datapoint['latitude'],datapoint['longitude'],datapoint['date']]
    counters.append(counter)