"""Module that collects some useful plotting functions."""

import plotly
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from operator import add, sub
from bson.objectid import ObjectId
import numpy as np

import db_utils

SWITCHER = {
        1: "deck",
        2: "accelerometerComplete",
        3: "accelerometerComplete",
        4: "deckShort1600"
    }


def DownloadTraces(db_client, db_name, coll_name, structureID, group, sensorType, axis=None):
    """Download a set of traces for plotting purposes"""

    coll = db_client[db_name][coll_name]
    query = {
        "structureID": ObjectId(structureID),
        "group": ObjectId(group),
        "type": SWITCHER.get(sensorType)
        }

    if sensorType in [2,3]:
        query.update({"axis": axis.upper()})

    cursor = coll.find(query).sort("date",1)
        
    fdd = list(cursor)
    labels = [trace['label'] for trace_block in fdd for trace in trace_block['traces']]

    ftraces = {label: [] for label in set(labels)}
    giornitraces = {label: [] for label in set(labels)}

    for trace_block in fdd:
        for trace in trace_block['traces']:
            ftraces[trace['label']].append(trace['freq_value'])
            giornitraces[trace['label']].append(trace_block['date'])

    fclustermodali = [np.mean(ftraces[key]) for key in ftraces.keys() if key !=-1]

    return ftraces, giornitraces, fclustermodali
    

def DownloadTracesAndShapes(db_client, db_name, coll_name, structureID, group, sensorType, axis=None):
    """Download a set of traces for plotting purposes"""

    coll = db_client[db_name][coll_name]
    query = {
        "structureID": ObjectId(structureID),
        "group": ObjectId(group),
        "type": SWITCHER.get(sensorType)
        }

    if sensorType in [2,3]:
        query.update({"axis": axis.upper()})

    cursor = coll.find(query).sort("date",1)
        
    fdd = list(cursor)
    labels = [trace['label'] for trace_block in fdd for trace in trace_block['traces']]

    ftraces = {label: [] for label in set(labels)}
    giornitraces = {label: [] for label in set(labels)}
    modalshapetraces = {label: [] for label in set(labels)}

    for trace_block in fdd:
        for trace in trace_block['traces']:
            ftraces[trace['label']].append(trace['freq_value'])
            giornitraces[trace['label']].append(trace_block['date'])
            modalshapetraces[trace['label']].append(trace['shape_value'])

    fclustermodali = [np.mean(ftraces[key]) for key in ftraces.keys() if key !=-1]
    modalshapeclustermodali = [np.mean(modalshapetraces[key], axis=0) for key in ftraces.keys() if key!=-1]

    return ftraces, giornitraces, modalshapetraces, fclustermodali, modalshapeclustermodali
    


def PlotTraces(ftraces, fcentrali, fclustermodali, alldays,
                giornitraces, dbName, axis, groupName,
                structureID, dftraces=None, boundaries=False):

    color_list = plotly.colors.qualitative.Plotly
    color_list.extend(color_list)

    fig = go.Figure()

    for key in ftraces.keys():
        if key != -1:

            fig.add_trace(go.Scatter(x=giornitraces[key], y=ftraces[key], mode='lines+markers',
                                        name=f'Trace {key}: {fclustermodali[key]:.5f} Hz', connectgaps=True,
                                        marker=dict(size=6, color=color_list[key]), line=dict(width=2.5),
                                        hovertemplate='<b>Day:</b>: %{x} <br>' + '<b>Freq:</b>: %{y:.2f} <br>'
                                    ))
        else:
            fig.add_trace(go.Scatter(x=giornitraces[-1], y=ftraces[-1], mode='markers', name='outliers',
                                    marker=dict(size=6, color='grey'),
                                    hovertemplate='<b>Day:</b>: %{x} <br>' + '<b>Freq:</b>: %{y:.2f} <br>'))  

    if boundaries:
        for key in ftraces.keys():
            if key != -1:
                upper = list(map(add, fcentrali[key], dftraces[key]))
                lower = list(map(sub, fcentrali[key], dftraces[key]))
                fig.add_trace(go.Scatter(x=alldays,
                                            name = f"Lower limit {fclustermodali[key]:.5f} Hz",
                                            y=lower,
                                            mode='lines',
                                            opacity=0.1,
                                            connectgaps=True,
                                            legendgroup='Boundaries',
                                            marker=dict(size=6, color = color_list[key]),
                                            line =dict(color=color_list[key], dash='dash'),
                                            showlegend=True          
                                            )
                                )
                fig.add_trace(go.Scatter(x=alldays,
                                            y=upper,
                                            name = f"Upper limit {fclustermodali[key]:.5f} Hz",
                                            mode='lines',
                                            opacity=0.1,
                                            legendgroup='Boundaries',
                                            legendgrouptitle_text='Boundaries',
                                            connectgaps=True,
                                            marker=dict(size=4, color = color_list[key]),
                                            line =dict(color=color_list[key], dash='dash',),
                                            fill = 'tonexty',
                                            showlegend=True
                                            )
                                )

    fig.update_layout(title=f"Tracking - {dbName} - {axis} axis - {structureID} - group {groupName}",
                        xaxis_title='Days', yaxis_title=f'Modal frequencies {axis} [Hz]')
    fig.show()


def DownloadInitializationTraces(dbClient, dbName, structureID, group, sensorType, axis, initialization_days, num_sensori, local_or_prod, coll_name):
    """
    Download traces (and their mean values) of a 14-day initialization period from any db 
    (it can be used both for plotting purposes and to skip the init calculations)
    """
    switcher = {
        1: "deck",
        2: "accelerometerComplete",
        3: "accelerometerComplete",
        4: "deckShort1600"
    }
    
    if local_or_prod=='local':
        customerDb = dbClientLocal[str(dbName)]
    else:
        customerDb = dbClient[str(dbName)]  # db di produzione
    
    fddCollection = customerDb[coll_name]

    if sensorType in [2,3]:
        # breakpoint()
        fddCursor = fddCollection.find({"structureID": ObjectId(structureID), "group": ObjectId(group) ,"type": switcher.get(sensorType), "axis": axis.upper()}).sort("date",1)
    elif sensorType==4:
        fddCursor = fddCollection.find({"structureID": ObjectId(structureID), "group": ObjectId(group) ,"type": switcher.get(sensorType)}).sort("date",1)
    else:
        fddCursor = fddCollection.find({"structureID": ObjectId(structureID), "group": ObjectId(group) }).sort("date",1)
    fdd = list(fddCursor)

    if initialization_days == False: #scarica tutta la serie di tracce

        labels = []
        # Cerco le label uniche
        for tracesBlock in fdd:
            for singleTrace in tracesBlock['traces']:
                labels.append(singleTrace['label'])
        # Inizializzo un array per label
        ftraces = {k: [] for k in set(labels)}
        modalshapetraces = {k: [] for k in set(labels)}
        giornitraces = {k: [] for k in set(labels)}

 
        # Appendo tutti i valori label per label
        for tracesBlock in fdd:
            for singleTrace in tracesBlock['traces']:
                ftraces[singleTrace['label']].append(singleTrace['freq_value'])
                if sensorType==3:
                    modalshapetraces[singleTrace['label']].append(singleTrace['shape_value'])
                giornitraces[singleTrace['label']].append(tracesBlock['date'])

        f1 = []
        shape1 = []

        if sensorType==3:

            for key in list(ftraces.keys()):
                if (key != -1):
                    media = np.mean(ftraces[key])
                    f1.append(media)
                    shapemedia = np.zeros(np.shape(modalshapetraces[key][0])[0])
                    for m in range (np.shape(shapemedia)[0]):
                        points = []
                        for j in range(np.shape(ftraces[key])[0]):
                            points.append(modalshapetraces[key][j][m])
                        shapemedia[m] = np.mean(points)
                    shape1.append(list(shapemedia))  
            fclustermodali = f1
            modalshapeclustermodali = shape1

        else:
            for key in list(ftraces.keys()):
                if (key != -1):
                    media = np.mean(ftraces[key])
                    f1.append(media)
            fclustermodali = f1
            modalshapeclustermodali = None

    else: #intialization_days != False

        print(f"Downloading {axis} axis init traces from {local_or_prod} db")
        key_eui_order = 'ShapeEUIorder' if sensorType==3 else 'EUIorder'
        
        fdd_initialization = []
        giorno = 1
        while (giorno <= initialization_days): 
            #print(f" ****** [ giorno {giorno}] ******* TypeSensor {sensorType}, AXIS {axis}")
            sensorsEuis_new = fdd[giorno-1][key_eui_order]

            if (num_sensori != np.shape(sensorsEuis_new)[0]):
                giorno = giorno + 1
                initialization_days = initialization_days + 1
                continue
            else:
                fdd_initialization.append(fdd[giorno-1])
                giorno = giorno + 1

            # Cerco le label uniche
            labels = [singleTrace['label'] for tracesBlock in fdd_initialization for singleTrace in tracesBlock['traces']]
            # Inizializzo un array per label
            ftraces = {k: [] for k in set(labels)}
            modalshapetraces = {k: [] for k in set(labels)}
            giornitraces = {k: [] for k in set(labels)}
    
            
            # Appendo tutti i valori label per label
            for tracesBlock in fdd_initialization:
                for singleTrace in tracesBlock['traces']:
                    ftraces[singleTrace['label']].append(singleTrace['freq_value'])
                    if sensorType==3:
                        modalshapetraces[singleTrace['label']].append(singleTrace['shape_value'])
                    giornitraces[singleTrace['label']].append(tracesBlock['date'])

            f1 = []
            shape1 = []
            
            if sensorType==3:

                for key in list(ftraces.keys()):
                    if (key != -1):
                        media = np.mean(ftraces[key])
                        f1.append(media)  
                        shapemedia = np.zeros(np.shape(modalshapetraces[key][0])[0])
                        for m in range (np.shape(shapemedia)[0]):
                            points = []
                            for j in range(np.shape(ftraces[key])[0]):
                                points.append(modalshapetraces[key][j][m])
                            shapemedia[m] = np.mean(points)
                        shape1.append(list(shapemedia))  
                fclustermodali = f1
                modalshapeclustermodali = shape1
            
            else:

                for key in list(ftraces.keys()):
                    if (key != -1):
                        media = np.mean(ftraces[key])
                        f1.append(media)  
                        
                fclustermodali = f1
                modalshapeclustermodali = None

    return ftraces,modalshapetraces, giornitraces, fclustermodali, modalshapeclustermodali


def DownloadPeakVector(dbClient, dbName, structureID, group, sensorType, axis,
            num_sensori, track, initialization_days, local_or_prod, coll_name):
    """
    Download the freqVector and the modalShapeVector from a db
    """
    switcher = {
        1: "deck",
        2: "accelerometerComplete",
        3: "accelerometerComplete",
        4: "deckShort1600"
    }
    
    customerDb = dbClient[str(dbName)] if local_or_prod=='prod' else dbClientLocal[str(dbName)] 
    fddCollection = customerDb[coll_name]

    if sensorType in [2,3]:

        if local_or_prod=='prod':
            fddCursor = fddCollection.find({"structureID": ObjectId(structureID), "group": ObjectId(group), 
                                            "type": switcher.get(sensorType), "axis": axis.upper()}).sort("date",1)
        else:
            fddCursor = fddCollection.find({"structureID": ObjectId(structureID), "group": ObjectId(group),
                                        "type": switcher.get(sensorType), "axis": axis.upper()}).sort("date",1)

    elif sensorType == 4:

        if local_or_prod=='prod':
            fddCursor = fddCollection.find({"structureID": ObjectId(structureID), "group": ObjectId(group),
                                            "type": switcher.get(sensorType)}).sort("date",1)
        else:
            fddCursor = fddCollection.find({"structureID": ObjectId(structureID), "group": ObjectId(group),
                                        "type": switcher.get(sensorType)}).sort("date",1)

    else:

        if local_or_prod=='prod':
            fddCursor = fddCollection.find({"structureID": ObjectId(structureID), "group": ObjectId(group),
                                           }).sort("date",1)
        else:
            fddCursor = fddCollection.find({"structureID": ObjectId(structureID), "group": ObjectId(group),
                                           }).sort("date",1)

    fdd = list(fddCursor)
    modalFreq = []
    modalshape_cluster = []
    trueListDate = []
    shapeEuiOrderList = []
    total_time_days = []

    #pdb.set_trace()
    key_eui_order = "ShapeEUIorder" if sensorType==3 else "EUIorder"

    if not track: #download only 14 days

        print(f"Downloading {axis} axis peaks from {local_or_prod} db ({initialization_days} days)")
        giorno = 1
        while (giorno <= initialization_days): 
            #print(f" ****** [ giorno {giorno}] ******* AXIS {axis}")
            sensorsEuis_new = fdd[giorno-1][key_eui_order]
            if (num_sensori != np.shape(sensorsEuis_new)[0]):
                giorno += 1
                initialization_days += 1
                continue

            else:
                trueListDate.append(fdd[giorno-1]['date'])
                modalFreq.append(fdd[giorno-1]['freqVector'])
                total_time_days.append(fdd[giorno-1]['TotalTime'])
                if sensorType==3:
                    modalshape_cluster.append(fdd[giorno-1]['modalshapeVector'])
                giorno += 1

    else:          #from day 15 onwards

        print(f"Downloading {axis} axis peaks from {local_or_prod} db ({len(fdd)-initialization_days} days)")
        giorno = initialization_days + 1

        while giorno <= len(fdd):
                trueListDate.append(fdd[giorno-1]['date'])
                modalFreq.append(fdd[giorno-1]['freqVector'])
                total_time_days.append(fdd[giorno-1]['TotalTime'])
                if sensorType==3:
                    modalshape_cluster.append(fdd[giorno-1]['modalshapeVector'])
                shapeEuiOrderList.append(fdd[giorno-1][key_eui_order])
                giorno += 1

    return modalFreq, modalshape_cluster,trueListDate, shapeEuiOrderList, total_time_days, fdd[-1]['fSample'] if sensorType==3 else None





def DownloadInitializationTraces(dbClient, dbName, structureID, group, sensorType, axis, initialization_days, num_sensori, local_or_prod, coll_name):
    """
    Download traces (and their mean values) of a 14-day initialization period from any db 
    (it can be used both for plotting purposes and to skip the init calculations)
    """
    switcher = {
        1: "deck",
        2: "accelerometerComplete",
        3: "accelerometerComplete",
        4: "deckShort1600"
    }
    
    if local_or_prod=='local':
        customerDb = dbClientLocal[str(dbName)]
    else:
        customerDb = dbClient[str(dbName)]  # db di produzione
    
    fddCollection = customerDb[coll_name]

    if sensorType in [2,3]:
        # breakpoint()
        fddCursor = fddCollection.find({"structureID": ObjectId(structureID), "group": ObjectId(group) ,"type": switcher.get(sensorType), "axis": axis.upper()}).sort("date",1)
    elif sensorType==4:
        fddCursor = fddCollection.find({"structureID": ObjectId(structureID), "group": ObjectId(group) ,"type": switcher.get(sensorType)}).sort("date",1)
    else:
        fddCursor = fddCollection.find({"structureID": ObjectId(structureID), "group": ObjectId(group) }).sort("date",1)
    fdd = list(fddCursor)

    if initialization_days == False: #scarica tutta la serie di tracce

        labels = []
        # Cerco le label uniche
        for tracesBlock in fdd:
            for singleTrace in tracesBlock['traces']:
                labels.append(singleTrace['label'])
        # Inizializzo un array per label
        ftraces = {k: [] for k in set(labels)}
        modalshapetraces = {k: [] for k in set(labels)}
        giornitraces = {k: [] for k in set(labels)}

 
        # Appendo tutti i valori label per label
        for tracesBlock in fdd:
            for singleTrace in tracesBlock['traces']:
                ftraces[singleTrace['label']].append(singleTrace['freq_value'])
                if sensorType==3:
                    modalshapetraces[singleTrace['label']].append(singleTrace['shape_value'])
                giornitraces[singleTrace['label']].append(tracesBlock['date'])

        f1 = []
        shape1 = []

        if sensorType==3:

            for key in list(ftraces.keys()):
                if (key != -1):
                    media = np.mean(ftraces[key])
                    f1.append(media)
                    shapemedia = np.zeros(np.shape(modalshapetraces[key][0])[0])
                    for m in range (np.shape(shapemedia)[0]):
                        points = []
                        for j in range(np.shape(ftraces[key])[0]):
                            points.append(modalshapetraces[key][j][m])
                        shapemedia[m] = np.mean(points)
                    shape1.append(list(shapemedia))  
            fclustermodali = f1
            modalshapeclustermodali = shape1

        else:
            for key in list(ftraces.keys()):
                if (key != -1):
                    media = np.mean(ftraces[key])
                    f1.append(media)
            fclustermodali = f1
            modalshapeclustermodali = None

    else: #intialization_days != False

        print(f"Downloading {axis} axis init traces from {local_or_prod} db")
        key_eui_order = 'ShapeEUIorder' if sensorType==3 else 'EUIorder'
        
        fdd_initialization = []
        giorno = 1
        while (giorno <= initialization_days): 
            #print(f" ****** [ giorno {giorno}] ******* TypeSensor {sensorType}, AXIS {axis}")
            sensorsEuis_new = fdd[giorno-1][key_eui_order]

            if (num_sensori != np.shape(sensorsEuis_new)[0]):
                giorno = giorno + 1
                initialization_days = initialization_days + 1
                continue
            else:
                fdd_initialization.append(fdd[giorno-1])
                giorno = giorno + 1

            # Cerco le label uniche
            labels = [singleTrace['label'] for tracesBlock in fdd_initialization for singleTrace in tracesBlock['traces']]
            # Inizializzo un array per label
            ftraces = {k: [] for k in set(labels)}
            modalshapetraces = {k: [] for k in set(labels)}
            giornitraces = {k: [] for k in set(labels)}
    
            
            # Appendo tutti i valori label per label
            for tracesBlock in fdd_initialization:
                for singleTrace in tracesBlock['traces']:
                    ftraces[singleTrace['label']].append(singleTrace['freq_value'])
                    if sensorType==3:
                        modalshapetraces[singleTrace['label']].append(singleTrace['shape_value'])
                    giornitraces[singleTrace['label']].append(tracesBlock['date'])

            f1 = []
            shape1 = []
            
            if sensorType==3:

                for key in list(ftraces.keys()):
                    if (key != -1):
                        media = np.mean(ftraces[key])
                        f1.append(media)  
                        shapemedia = np.zeros(np.shape(modalshapetraces[key][0])[0])
                        for m in range (np.shape(shapemedia)[0]):
                            points = []
                            for j in range(np.shape(ftraces[key])[0]):
                                points.append(modalshapetraces[key][j][m])
                            shapemedia[m] = np.mean(points)
                        shape1.append(list(shapemedia))  
                fclustermodali = f1
                modalshapeclustermodali = shape1
            
            else:

                for key in list(ftraces.keys()):
                    if (key != -1):
                        media = np.mean(ftraces[key])
                        f1.append(media)  
                        
                fclustermodali = f1
                modalshapeclustermodali = None

    return ftraces,modalshapetraces, giornitraces, fclustermodali, modalshapeclustermodali

if __name__=='__main__':
    import pymongo
    dbClientLocal = pymongo.MongoClient("127.0.0.1", 27017) 

    ftraces, giornitraces, fclustermodali = DownloadTraces(
        db_client=dbClientLocal,
        db_name = 'deck_sveco',
        coll_name='fdd_def',
        structureID='6183ec3f5c580e131f45ac37',
        group = "62e252a3b694b0ac5818c0e5",
        sensorType=3,
        axis='X'
    )


    PlotTraces(
        ftraces, None, fclustermodali, None, giornitraces, '', '', '', ''
    )