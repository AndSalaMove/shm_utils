"""Module to handle connection with the db"""
import sys
sys.path.append("..")

from bson.objectid import ObjectId
from socket import socket
import numpy as np
from pymongo import MongoClient
from sshtunnel import SSHTunnelForwarder
import settings

def getFreePort():
    with socket() as s:
        s.bind(('', 0))
        port = s.getsockname()[1]
        print(port)
        return port


class MongoManager:
    __instance = None
    @staticmethod
    def getInstance():
        if MongoManager.__instance == None:
            MongoManager()
        return MongoManager.__instance
    def __init__(self):
        if (settings.LOCATION == "local"):
            pickedPort = getFreePort()
            server = SSHTunnelForwarder(
                (settings.IP_EC2, 22),
                ssh_username="ubuntu",
                ssh_pkey=settings.SSH_PKEY,
                remote_bind_address=(settings.REMOTE_BIND_ADDRESS, 27017),
                local_bind_address=('0.0.0.0', pickedPort)
            )
            # start ssh tunnel
            server.start()
            MongoManager.__instance = MongoClient("127.0.0.1", pickedPort, username=settings.USERNAME_DB,
                                                    password=settings.PWD_DB, tls=True, tlsCAFile=settings.SSL_CA_CERTS,
                                                    tlsAllowInvalidHostnames=True, directConnection=True, retryWrites = False)
        else:
            MongoManager.__instance = MongoClient(settings.MONGO_URL)
        # TODO aggiugnere parametreo al costruttore per la connessione al db locale


dbClient = MongoManager.getInstance()

def findCustomers() -> list:
    """
    Find the requested customer. Return db cursor for the given customer(s)

    :param customer: Name of the customer
    :param single: Set to True if you are looking for a single customer

    :return: List of found customer(s)
    """

    global_db = dbClient["global"]
    collection = global_db["users"]

    customer_cursor = collection.find({"username": {"$ne": "admin"}, "$or": [{"type":{"$exists": False}},{"type":"standard"}]})

    return list(customer_cursor)


def findStructures(dbName: str) -> list:
    """
    Find and return list of structures for a given customer

    :param dbName: Name of the db (usually deck_something)
    :param structureID: String represeting the ID of the structure

    :return: List of mongo documents relative to the structure(s) found
    """
    customerDb = dbClient[dbName]
    collection = customerDb["structures"]

    structures_cursor = collection.find({})

    return list(structures_cursor)


def findSensors(customerDb) -> list:
    """
    Find and return the list of sensors for a given structure
    """
    mycol = customerDb["structures"]
    structure = mycol.find_one()
    eui_list = list(map(lambda x: x['eui'], structure['sensors']))
    return eui_list


def findSensorType(dbName,group,structure):
    customerDb = dbClient[str(dbName)]

    sensor_type = False
    if (np.shape(group["devices"])[0] == 0):
        return sensor_type

    else:
        eui = group["devices"][0]["eui"]
        for i in range (np.shape(structure['sensors'])[0]):
            if (structure['sensors'][i]['eui'] == eui):
                type = structure['sensors'][i]['type']    
                if (type == 'accelerometer'):
                    rev = structure['sensors'][i]['rev']
                    if (rev == '3.0'):
                        sensor_type = 3
                    else:
                        sensor_type = 2
                elif (type == 'deck'):
                    mycol = customerDb["vibrations"]
                    event = list(mycol.find({"eui": eui, "payload.dati.1599": { "$exists": True },
                                "payload.dati.2999": { "$exists": False }}).limit(1))
                    if (np.shape(event)[0] == 0):
                        sensor_type = 1
                    else:
                        sensor_type = 4
                break
                    
        return sensor_type



