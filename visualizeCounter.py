#! /usr/bin/python
import json
import altair
import pandas

data = pandas.read_csv='counts-100117730.csv'

heatmap = altair.Chart(data).transform_timeunit(
    year='year(Date)'
).transform_filter(
    altair.FieldGTPredicate(field='year',gt='2014')
).mark_rect().encode(
    altair.X('hours(Date):O'),
    altair.Y('year:O'),
    altair.Color('mean(Count):Q')
)

chart = heatmap
   
chart.save('altairTest.json')