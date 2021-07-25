import requests
import mysql.connector
import nbt
#Python
import gzip
import json
import time
import io
import base64
import os
import numpy
from random import randint
global mydb
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="CURSE OF BINDING",
  database="skyblockUsers"
)
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
  encoded = json_data.encode('utf-8')
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
def writeJson(fileName, data):
  with open(fileName, 'w') as userWriteData:
    json.dump(data, userWriteData)
def readJson(fileName):
  with open(fileName, 'r') as userReadData:
    return(json.load(userReadData))
def getConfig():
  global config
  config = readJson("config.json")

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

def addProfileUserRow(mycursor,i, profiles, uuid):
  global config
  global mydb
  global adds
  #notes
  notes = ""
  profile_id = str(profiles['profiles'][i]['profile_id'])
  if len(list(profiles['profiles'][i]['members'].keys())) <= 50:
    members = str(list(profiles['profiles'][i]['members'].keys())).replace("\'","").replace("[","").replace("]","").replace(" ","")
  else:
    members = str(list(profiles['profiles'][i]['members'].keys())[0:50]).replace("\'","").replace("[","").replace("]","").replace(" ","")
    notes += "Over 50 members. "
  # dungeon_teammate
  if 'dungeons' in profiles['profiles'][i]['members'][uuid] and 'dungeon_types' in profiles['profiles'][i]['members'][uuid]['dungeons']:
    dungeon_teammates = []
    dungeon_types = list(profiles['profiles'][i]['members'][uuid]['dungeons']['dungeon_types'].keys())
    for o in range(len(dungeon_types)):
      if 'best_runs' in profiles['profiles'][i]['members'][uuid]['dungeons']['dungeon_types'][dungeon_types[o]]:
        for j in profiles['profiles'][i]['members'][uuid]['dungeons']['dungeon_types'][dungeon_types[o]]['best_runs']:
          profiles['profiles'][i]['members'][uuid]['dungeons']['dungeon_types'][dungeon_types[o]]['best_runs'][j]
          for q in range(len(profiles['profiles'][i]['members'][uuid]['dungeons']['dungeon_types'][dungeon_types[o]]['best_runs'][j])):
            if 'teammates' in profiles['profiles'][i]['members'][uuid]['dungeons']['dungeon_types'][dungeon_types[o]]['best_runs'][j][q]:
              for p in range(len(profiles['profiles'][i]['members'][uuid]['dungeons']['dungeon_types'][dungeon_types[o]]['best_runs'][j][q]['teammates'])):
                if profiles['profiles'][i]['members'][uuid]['dungeons']['dungeon_types'][dungeon_types[o]]['best_runs'][j][q]['teammates'][p] not in dungeon_teammates and profiles['profiles'][i]['members'][uuid]['dungeons']['dungeon_types'][dungeon_types[o]]['best_runs'][j][q]['teammates'][p] != '':
                  dungeon_teammates.append(profiles['profiles'][i]['members'][uuid]['dungeons']['dungeon_types'][dungeon_types[o]]['best_runs'][j][q]['teammates'][p])
    dungeon_teammates = str(dungeon_teammates).replace("\'","").replace("[","").replace("]","").replace(" ","")
  else:
    dungeon_teammates = None
  #coin_purse
  if 'coin_purse' in profiles['profiles'][i]['members'][uuid]:
    coin_purse = int(profiles['profiles'][i]['members'][uuid]['coin_purse'])
  else:
    coin_purse = 0 
  #banking
  if 'banking' in profiles['profiles'][i]['members'][uuid]:
    bank = int(profiles['profiles'][i]['members'][uuid]['banking']['balance'])
  else:
    bank = 0
  # inv_armor
  if 'inv_armor' in profiles['profiles'][i]['members'][uuid]:
    inv_armor = decode_data(profiles['profiles'][i]['members'][uuid]['inv_armor']['data'])
    if inv_armor['i'][0] == {}and inv_armor['i'][1] == {} and inv_armor['i'][2] == {}and inv_armor['i'][3] == {}:
      inv_armor = None
    else:
      inv_armor = str(encodeJsonData(listOfNbtToJson(inv_armor)))[2:-1]
  else:
    inv_armor = None
  #ender_chest_contents
  if 'ender_chest_contents' in profiles['profiles'][i]['members'][uuid]:
    ender_chest_contents = str(encodeJsonData(listOfNbtToJson(decode_data(profiles['profiles'][i]['members'][uuid]['ender_chest_contents']['data']))))[2:-1]
  else:
    ender_chest_contents = None
  #wardrobe_contents
  if 'wardrobe_contents' in profiles['profiles'][i]['members'][uuid]:
    wardrobe_contents = str(encodeJsonData(listOfNbtToJson(decode_data(profiles['profiles'][i]['members'][uuid]['wardrobe_contents']['data']))))[2:-1]
  else:
    wardrobe_contents = None
  #personal_vault_contents
  if 'personal_vault_contents' in profiles['profiles'][i]['members'][uuid]:
    personal_vault_contents = str(encodeJsonData(listOfNbtToJson(decode_data(profiles['profiles'][i]['members'][uuid]['personal_vault_contents']['data']))))[2:-1]
  else:
    personal_vault_contents = None
  #inv_contents
  if 'inv_contents' in profiles['profiles'][i]['members'][uuid]:
    inv_contents = str(encodeJsonData(listOfNbtToJson(decode_data(profiles['profiles'][i]['members'][uuid]['inv_contents']['data']))))[2:-1]
  else:
    inv_contents = None
  if 'backpack_contents' in profiles['profiles'][i]['members'][uuid]:
    uncompressed_backpack_contents = []
    for p in (profiles['profiles'][i]['members'][uuid]['backpack_contents']):
      uncompressed_backpack_contents.append(listOfNbtToJson(decode_data(profiles['profiles'][i]['members'][uuid]['backpack_contents'][p]['data'])))
    backpack_contents = str(encodeJsonData(uncompressed_backpack_contents))[2:-1]
  else:
    backpack_contents = None
  #first_join
  if 'first_join' in profiles['profiles'][i]['members'][uuid]:
    first_join = int(profiles['profiles'][i]['members'][uuid]['first_join'])//1000
  else:
    first_join = None
  #last_save
  if 'last_save' in profiles['profiles'][i]['members'][uuid]:
    last_save = int(profiles['profiles'][i]['members'][uuid]['last_save'])//1000
  else:
    last_save = None
  #pets
  if 'pets' in profiles['profiles'][i]['members'][uuid] and profiles['profiles'][i]['members'][uuid]['pets'] != []:
    pets = str(encodeJsonData(profiles['profiles'][i]['members'][uuid]['pets']))[2:-1]
  else:
    pets = None
  #inserting row
  # print(f"`{profile_id}`, `{uuid}`, `{members}`, `{dungeon_teammates}`, {coin_purse}, {bank}, `{inv_armor}`, `{ender_chest_contents}`, `{wardrobe_contents}`, `{personal_vault_contents}`, `{inv_contents}`, `{backpack_contents}`, `{first_join}`, `{last_save}`, `{notes}`, `{pets_content}`")
  if coin_purse < 50000 and bank == 0 and inv_armor == None and ender_chest_contents == None and wardrobe_contents == None and personal_vault_contents == None and inv_contents == None and backpack_contents == None:
    pass
  else:
    sql_command = "INSERT INTO tempNames(profile_id, player_id) VALUES('%s','%s')" % (profile_id, uuid)
    mycursor.execute(sql_command)
    sql_command = "INSERT INTO sbData0821(profile_id, player_id, members, dungeon_teammates, coin_purse, bank, inv_armor, ender_chest_contents, wardrobe_contents, personal_vault_contents, inv_contents, backpack_contents, first_join, last_save, notes, pets_contents) VALUES('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s', '%s')" % (profile_id, uuid, members, dungeon_teammates, coin_purse, bank, inv_armor, ender_chest_contents, wardrobe_contents, personal_vault_contents, inv_contents, backpack_contents, first_join, last_save, notes, pets)
    mycursor.execute(sql_command)
    mydb.commit()
    adds += 1

def remakeTable():
  global mydb
  mycursor = mydb.cursor() 
  mycursor.execute("DROP TABLE sbData0821")
  mycursor.execute("DROP TABLE tempNames")
  mycursor.execute("CREATE TABLE tempNames(id INT(8), profile_id VARCHAR(36) NOT NULL, player_id VARCHAR(36))")
  mycursor.execute("CREATE TABLE sbData0821(id INT(8) UNSIGNED AUTO_INCREMENT PRIMARY KEY, profile_id VARCHAR(36) NOT NULL, player_id VARCHAR(36) NOT NULL, members MEDIUMTEXT, dungeon_teammates MEDIUMTEXT, coin_purse BIGINT(20),  bank BIGINT(20), inv_armor MEDIUMTEXT, ender_chest_contents MEDIUMTEXT, wardrobe_contents MEDIUMTEXT, personal_vault_contents MEDIUMTEXT, inv_contents MEDIUMTEXT, backpack_contents MEDIUMTEXT, first_join INT(255), last_save INT(255), notes VARCHAR(2500), pets_contents MEDIUMTEXT)")
def wipeTable():
  global mydb
  mycursor = mydb.cursor()
  mycursor.execute("DELETE FROM sbData0821 WHERE TRUE")
  mydb.commit()

def addUser(uuid):
  global errors
  global adds
  global config
  global mydb
  # try:
  # try:
  # a = time.time()
  profilesStr = requests.get("https://api.hypixel.net/skyblock/profiles?key=" + config["apiKey"] + "&uuid="+uuid)
  try:
    profiles = profilesStr.json()
  except:
    print("https://api.hypixel.net/skyblock/profiles?key=" + config["apiKey"] + "&uuid="+uuid)
    print(str(profilesStr))
    return()
  # except:
  #   errors.append(uuid)
  #   print("hi")
  #   print()
  #   return()
  # b = time.time()
  if profiles['success'] == True and "profiles" in profiles and profiles["profiles"] != None:
    # c = time.time()
    mycursor = mydb.cursor()
    mycursor.execute(f"SELECT profile_id FROM tempNames WHERE player_id = '{uuid}'")
    result = list(mycursor.fetchall())
    # d = time.time()
    existingProfiles = []
    # processingTimes = []
    for j in range(len(result)):
      existingProfiles.append(str(result[j][0]))
    for i in range(len(profiles['profiles'])):
      # f = time.time()
      if profiles['profiles'][i]['profile_id'] not in existingProfiles and uuid in profiles['profiles'][i]['members'] and 'last_save' in profiles['profiles'][i]['members'][uuid]:
        if 1601510401000 < int(profiles['profiles'][i]['members'][uuid]['last_save']):
          addProfileUserRow(mydb.cursor(),i, profiles, uuid)
      # g = time.time()
      # processingTimes.append(str(g-f))
    # print("api time: " + str(b-a) + "s, db time: " + str(d-c) + "s processing times " + str(processingTimes))
def scanToDb():
  global adds
  global errors
  global config
  global mydb
  adds = 0
  errors = []
  startName = str(input("Enter start name index: "))
  i = int(startName)
  getConfig()
  totalTime = 0
  totalCompletedNames = 0
  totalTimePredict = 0
  mycursor = mydb.cursor()
  sql_command = "SELECT COUNT(*) FROM names"
  mycursor.execute(sql_command)
  totalNames = mycursor.fetchall()
  print("Starting processing/scanning of " + str(totalNames) + " names")
  # Start
  numberOfNames = len(totalNames)
  while i in range(numberOfNames):
    startTimePredict = time.time()
    startTime = time.time()
    mycursor.execute("SELECT player_id FROM names WHERE `id` = %i" % (i))
    uuid = mycursor.fetchall()
    addUser(uuid)
    endTime = time.time()
    # api cooldown
    totalTime += endTime-startTime
    excessWaitTime = config["apiCooldown"]-(endTime-startTime)
    if excessWaitTime > 0:
      waitTime = excessWaitTime
      time.sleep(waitTime)
    totalCompletedNames += 1
    endTimePredict = time.time()
    totalTimePredict += endTimePredict-startTimePredict
    if i%2500 == 0:
      print("Average time " + str(round(totalTime/totalCompletedNames,3)))
      print("Actual average time " + str(round(totalTimePredict/totalCompletedNames, 3)))
      print(str(adds) + " new names/rows in code")
      mycursor = mydb.cursor()
      mycursor.execute("SELECT COUNT(*) FROM sbData0821")
      result = mycursor.fetchall()
      print(str(result) + " names/rows in db")
      print(str(len(errors)) + " errors")
      print("Name " + str(i) + " (" + uuid + ").\n")
      writeJson("errors.json", errors)
    i += 1
question = int(input("Add to/wipe db? 1/2: "))
if question == 1:
  scanToDb()
elif question == 2:
  num = randint(0,1000000)
  question = int(input("enter num to confirm: " + str(num)))
  if question == num:
    num = randint(0,1000000)
    question = int(input("enter num to confirm again: " + str(num)))
    if question == num:
      if question == num:
        question = str(input("Are you really sure? enter code: "))
        if question == "confirm hostname":
          remakeTable()
        else:
          print("False")
      else:
        print("False")
    else:
      print("False")
else:
  print("error, not option")
# uuid = "1a7afa96c270429ea63c7eb3db928834".replace("-","")
# addUser(mydb, uuid)
# wipeTable(mydb)