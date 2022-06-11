from codecs import xmlcharrefreplace_errors
import mysql.connector
import nbt
from random import randint
#Python
import json
import time
import gzip
import base64
import io
import os
import csv
global mydb
print("start")
def writeJson(fileName, data):
    with open(fileName, "w") as userWriteData:
        json.dump(data, userWriteData)
def readJson(fileName):
    with open(fileName, "r") as userReadData:
        return(json.load(userReadData))
def getConfig():
    global config
    config = readJson("config.json")
getConfig()
mydb = mysql.connector.connect(
    host=config["databaseHost"],
    user=config["databaseUser"],
    password=config["databasePassword"],
    database=config["databaseName"],
    port=config["databasePort"]
)
print("connected")