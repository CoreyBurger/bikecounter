#! /usr/bin/python
import json
import altair
import pandas
import datetime

data = pandas.read_csv=("counts-100117730.csv")

heatmap = altair.Chart(data).mark_rect().encode(
    altair.X('hours(Date):O'),
    altair.Y('Date:O', timeUnit='year'),
    altair.Color('mean(Count):Q')
)

chart = heatmap
   
chart.save('bikecounter/altairTest.json')