import nbt
import requests
import mysql.connector
#Python
import gzip
import json
import time
import base64
import io
import os
import numpy
def decode_data(compressed):
  # b = time.time()
  iobite = io.BytesIO(base64.b64decode(compressed))
  # c = time.time()
  uncompressed = nbt.nbt.NBTFile(fileobj = iobite)
  # d = time.time()
  # print(" iobytes: " + str(c-b) + " nbt: " + str(d-c))
  return(uncompressed)
def encodeJsonData(uncompressed):
  # Convert to JSON
  a = time.time()
  json_data = json.dumps(uncompressed, indent=2)
  # Convert to bytes
  b = time.time()
  encoded = json_data.encode('utf-8')
  # Compress
  c = time.time()
  compressed = gzip.compress(encoded)
  d = time.time()
  final = base64.b64encode(compressed)
  print("cast Json" + str(b-a) + "encode to binary" + str(c-b) +"gzip: " + str(d-c) + "json to binary: " + str(b-a))
  return(final)
def decodeJsonData(compressed):
  a = time.time()
  #decode
  nonb64 = base64.b64decode(compressed)
  #decompress
  b = time.time()
  uncompressed = gzip.decompress(nonb64)
  #json
  c = time.time()
  jsonData = json.loads(uncompressed)
  d = time.time()
  print("b64: " + str(b-a) + "ungzip: " + str(c-b) + "binary to json: " + str(d-c))
  return(jsonData)

def writeJson(fileName, data):
  with open(fileName, 'w') as userWriteData:
    json.dump(data, userWriteData)
def readJson(fileName):
  with open(fileName, 'r') as userReadData:
    return(json.load(userReadData))
def tagValueToJson(data):
  if type(data) in [nbt.nbt.TAG_Byte,nbt.nbt.TAG_Short,nbt.nbt.TAG_Int,nbt.nbt.TAG_Long]:
    newData = int(str(data))
  elif type(data) in [nbt.nbt.TAG_Float,nbt.nbt.TAG_Double]:
    newData = float(str(data))
  elif type(data) in [nbt.nbt.TAG_String]:
    newData = str(data)
  elif type(data) in [nbt.nbt.TAG_Byte_Array,nbt.nbt.TAG_Int_Array,nbt.nbt.TAG_Long_Array]:
    newData = []
    for i in range(len(data)):
      newData.append(int(data[i]))
  else:
    print(type(data))
  return(newData)
def tagListToJson(data):
  newData = []
  for i in range(len(data)):
    if type(data[i]) == nbt.nbt.TAG_Compound:
      newData.append(tagCompoundToJson(data[i]))
    elif type(data[i]) == nbt.nbt.TAG_List:
      newData.append(tagListToJson(data[i]))
    else:
      newData.append(tagValueToJson(data[i]))
  return(newData)
def tagCompoundToJson(data):
  newData = {}
  for i in range(len(data.keys())):
    if type(data[data.keys()[i]]) == nbt.nbt.TAG_Compound:
      newData[data.keys()[i]] = tagCompoundToJson(data[data.keys()[i]])
    elif type(data[data.keys()[i]]) == nbt.nbt.TAG_List:
      newData[data.keys()[i]] = tagListToJson(data[data.keys()[i]])   
    else:
      newData[data.keys()[i]] = tagValueToJson(data[data.keys()[i]])
  return(newData)
def nbtToJson(data):
  if type(data) == nbt.nbt.TAG_Compound:
    newData = tagCompoundToJson(data)
  elif type(data) == nbt.nbt.TAG_List:
    newData= tagListToJson(data)   
  else:
    newData= tagValueToJson(data)
  return(newData)
def listOfNbtToJson(data):
  newList = []
  for i in range(len(data)):
    newList.append(nbtToJson(data[i]))
  return(newList)
print("start")
# mydb = mysql.connector.connect(
#   host="192.168.1.104",
#   port="3306",
#   user="root",
#   password="CURSE OF BINDING",
#   database="skyblockUsers"
# )

profiles = requests.get("https://api.hypixel.net/skyblock/profiles?key=d16dc479-a24f-4c10-98b1-77b14d7fccfa&uuid=1a7afa96c270429ea63c7eb3db928834").json()
# print(listOfNbtToJson(decode_data(profiles['profiles'][1]['members']['1a7afa96c270429ea63c7eb3db928834']['inv_contents']['data']))[0][0].keys())
for j in range(36):
  slotData = listOfNbtToJson(decode_data(profiles['profiles'][1]['members']['1a7afa96c270429ea63c7eb3db928834']['inv_contents']['data']))[0][j]
  if slotData != {}:
    if slotData['id'] == 397:
      if 'tag' in slotData:
        #skyblockId
        if 'ExtraAttributes' in slotData['tag'] and 'id' in slotData['tag']['ExtraAttributes']:
            skyblockId = str(slotData['tag']['ExtraAttributes']['id'])
        else:
            skyblockId = None
      print(str(j) + " <-Yes->" + str(slotData['id']) + ":")
      print(slotData.keys())
      print(str(skyblockId)+"\n")
    else:
      print(str(j) + " <-No->" + str(slotData['id']))