"""Module with models to depurate traces."""

import plotly
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from operator import add, sub
from bson.objectid import ObjectId
import numpy as np
import pymongo
from pymongo import MongoClient

import datetime as dtt
from datetime import datetime, timedelta

import db_utils

SWITCHER = {
        1: "deck",
        2: "accelerometerComplete",
        3: "accelerometerComplete",
        4: "deckShort1600"
    }

def DownloadTemperatures(db_client: MongoClient, db_name):


    coll = db_client[db_name]['temperatures']

    print("Downloading temperatures...")
    tmps = list(coll.aggregate([
            {"$group": {
                "_id": { "date": {'$dateToString': { 'format': "%Y-%m-%d", 'date': "$date", }},
                       #  "eui": "$eui"
                },
                "avg_temperature": {"$avg": "$temperature" },
                "min_temperature": {"$min": "$temperature" },
                "max_temperature": {"$max": "$temperature" },
            }},
            {"$sort": { "_id.date":1} }
            ]))

    days = sorted(set([datetime.strptime(d['_id']['date'], '%Y-%m-%d') for d in tmps]))
    temp_max = [doc['max_temperature'] for doc in tmps]
    temp_min = [doc['min_temperature'] for doc in tmps]
    temp_avg = [doc['avg_temperature'] for doc in tmps]

    return days, temp_max, temp_min, temp_avg


def PlotTemperatures(days, temp_max, temp_min, temp_avg):

    fig = go.Figure()

    fig.add_trace(go.Scatter(x = days, y=temp_max, name='Max Temperature', mode='lines+markers'))
    fig.add_trace(go.Scatter(x = days, y=temp_min, name='Min Temperature', mode='lines+markers'))
    fig.add_trace(go.Scatter(x = days, y=temp_avg, name='Avg Temperature', mode='lines+markers'))

    fig.update_layout(title="Temperatures",  xaxis_title='Days', yaxis_title='Temperature [°C]')

    fig.show()

if __name__=='__main__':

    db_client = db_utils.MongoManager.getInstance()
    
    days, tmax, tmin, tavg = DownloadTemperatures(
         db_client,
        'deck_sveco',
        '6183ec3f5c580e131f45ac37',
        '63172499a46181b32d20d51d',
        3,
        ['0080E11500289CDE'],
    )

    PlotTemperatures(days, tmax, tmin, tavg)