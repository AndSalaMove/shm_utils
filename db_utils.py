"""Module to handle connection with the db"""
import sys
sys.path.append("..")

from bson.objectid import ObjectId
from socket import socket
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


def retrievedb(myclient, customer):
    rootdb = myclient["global"]
    dbcustomer = rootdb["users"].find_one({"_id": ObjectId(customer)})
    return dbcustomer['dbName']