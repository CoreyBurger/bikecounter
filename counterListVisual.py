#! /usr/bin/python
import csv
from datetime import datetime,date,timedelta,time
import json
import urllib.request
import os
import pandas
import itertools
import altair


#define constants
workingDir = os.getcwd()
urlBase = "http://www.eco-public.com/api/cw6Xk4jW4X4R/publicpage/"
csvCountersfile=workingDir + '\\countersList.csv'

#read in the counter list
if os.path.exists(csvCountersfile):
    counters = pandas.read_csv(csvCountersfile)

counterList = altair.Chart(counters).mark_point(clip=True).encode(
    altair.X('CounterID:Q',scale=altair.Scale(domain=(100000000,100153370))),
    altair.Y('Date:T',scale=altair.Scale(domain=('2009-01-01','2020-12-31'))),
    altair.Tooltip('CounterTitle:N')
)

counterList.save('counterList.json')

counters.query('CounterTitle!="No Counter"')