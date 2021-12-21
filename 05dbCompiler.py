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
    json_data = json.dumps(uncompressed, indent=2)
    # Convert to bytes
    encoded = json_data.encode("utf-8")
    # Compress
    compressed = gzip.compress(encoded)
    final = base64.b64encode(compressed)
    return(final)
def decodeJsonData(compressed):
    #decode
    nonb64 = base64.b64decode(compressed)
    #decompress
    uncompressed = gzip.decompress(nonb64)
    #json
    jsonData = json.loads(uncompressed)
    return(jsonData)
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
mycursor = mydb.cursor()
# mycursor.execute("SELECT * FROM sbData0521 WHERE `id` = %i" % (20))
# data = list(mycursor.fetchall()[0])
# print(len(data))
# print(str(encodeJsonData(nbtToJson(decode_data(data[6])['i'])))[2:-1])
mycursor.execute("DROP TABLE sbData")
mydb.commit()
mycursor.execute("CREATE TABLE sbData(id INT(8) UNSIGNED AUTO_INCREMENT PRIMARY KEY, profile_id VARCHAR(36) NOT NULL, player_id VARCHAR(36) NOT NULL, profile_members MEDIUMTEXT, dungeon_teammates MEDIUMTEXT, coin_purse BIGINT(20),  bank BIGINT(20), inv_armor_contents MEDIUMTEXT, ender_chest_contents MEDIUMTEXT, wardrobe_contents MEDIUMTEXT, personal_vault_contents MEDIUMTEXT, inv_contents MEDIUMTEXT, backpack_contents MEDIUMTEXT, pets_contents MEDIUMTEXT, first_join INT(255), last_save INT(255), month_indexed text(20))")
mydb.commit()
mycursor.execute("SELECT MAX(`id`) FROM sbData0521")
userCount = int(mycursor.fetchall()[0][0])
print(userCount)
userNum = 501
a = time.time()
while userNum <= userCount:
    mycursor.execute("SELECT * FROM sbData0521 WHERE `id` = %i" % (userNum))
    userData = mycursor.fetchall()
    if len(userData) == 1:
        data = list(userData[0])
        if data[6] != 'None':
            data[6] = str(encodeJsonData(nbtToJson(decode_data(data[6])['i'])))[2:-1]
        if data[7] != 'None':
            data[7] = str(encodeJsonData(nbtToJson(decode_data(data[7])['i'])))[2:-1]
        if data[8] != 'None':
            data[8] = str(encodeJsonData(nbtToJson(decode_data(data[8])['i'])))[2:-1]
        if data[9] != 'None':
            data[9] = str(encodeJsonData(nbtToJson(decode_data(data[9])['i'])))[2:-1]
        if data[10] != 'None':
            data[10] = str(encodeJsonData(nbtToJson(decode_data(data[10])['i'])))[2:-1]
        sql_command = "INSERT INTO sbData(profile_id, player_id, profile_members, dungeon_teammates, coin_purse,  bank, inv_armor_contents, ender_chest_contents, wardrobe_contents, personal_vault_contents, inv_contents, backpack_contents, pets_contents, first_join, last_save, month_indexed) VALUES('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s', '%s')" % (data[1], data[2], data[3], '', data[4],  data[5], data[6], data[7], data[8], data[9], data[10], 'None', 'None', data[11], data[12], '05/21')
        mycursor.execute(sql_command)
        mydb.commit()
    else:
        print(userCount)
    if userNum%5000 == 0:
        b = time.time()
        print("Average time: " + str((b-a)/userNum) + ", User number: " + str(userNum) + "/" + str(userCount))
    userNum+=1