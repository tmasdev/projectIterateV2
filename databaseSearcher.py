import mysql.connector
import nbt
#Python
from random import randint
import json
import time
import gzip
import base64
import io
def decode_data(compressed):
    iobite = io.BytesIO(base64.b64decode(compressed))
    uncompressed = nbt.nbt.NBTFile(fileobj = iobite)
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

def autoSaveLocation(index):
    writeJson("autoSaveIndex.json", [index])
def autoLoadIndex():
    return(readJson("autoSaveIndex.json")[0])

def saveItem(str(profileId), str(playerid), skyblockId, itemName,location):
    global mydb
    mycursor = mydb.cursor()
    sql_command = "INSERT INTO foundItems" + str(config['monthIndexed']) + "(profile_id, player_id, item_id, item, item_location) VALUES('%s','%s','%s','%s','%s')" % (str(profileId), str(playerid), skyblockId, itemName,location)
    mycursor.execute(sql_command)
    mydb.commit()

def filterSlot(slotData,location):
    global mydb
    global config
    global exoticCodesTable
    global nonExoticCodes
    global playerid
    global profileId
    global month_indexed
    if 'tag' in slotData:
        #skyblockId
        if 'ExtraAttributes' in slotData['tag'] and 'id' in slotData['tag']['ExtraAttributes']:
            skyblockId = str(slotData['tag']['ExtraAttributes']['id'])
        else:
            skyblockId = None
        if 'display' in slotData['tag']:
            #itemName
            if 'Name' in slotData['tag']['display']:
                itemName = slotData['tag']['display']['Name']
            else:
                itemName = None
            #itemLore
            if 'Lore' in slotData['tag']['display']:
                itemLore = slotData['tag']['display']['Lore']
            else:
                itemLore = None
        else:
            itemLore = None
            itemName = None
    else:
        skyblockId = None
        itemLore = None
        itemName = None
    # numericId
    numericId = str(slotData['id'])
    #leatherColor: leatherColorHex:
    if numericId in ["298","299","300","301"] and 'tag' in slotData and 'display' in slotData['tag'] and 'color' in slotData['tag']['display']:
        leatherColor = str(slotData['tag']['display']['color'])
        leatherColorHex = str(hex(int(leatherColor)))[2:]
    else:
        leatherColor = None
        leatherColorHex = None
    #itemSlotCount:
    if 'count' in slotData:
        itemSlotCount = slotData['count']
    else:
        itemSlotCount = None

    #Variables:(All str unless otherwise specified)
    #profileId :The profile's id
    #playerId :The player's uuid
    #skyblockId :The item's skyblock id: CHESTPLATE_OF_THE_PACK
    #numericId :Old numeric minecraft item id: 298
    #leatherColor :Denary color of leather: 3124528 OR None (if item isn't leather)
    #leatherColorHex :Hex color of leather (string): FFAAFF OR None (if item isn't leather)
    #location : Where the item was found/scanned: enderchest OR inventory
    #itemLore : The item's lore
    #itemName :The displayed name of the item: [lvl 1] Enderman
    #itemSlotCount :How many of the item are in the slot: 1-64
    #saveItem(str(profileId), str(playerid), skyblockId, itemName,location): saves item to database 
    
    #Start code block

    if skyblockId == "POTION":
        #Dungeon Splash
        if "Dungeon" in itemName and "Splash Potion" in itemName:
            saveItem(str(profileId), str(playerid), skyblockId, itemName,location)
    elif skyblockId == "PET":
        if 'tag' in slotData:
            if 'ExtraAttributes' in slotData['tag']:
                if 'petInfo' in slotData['tag']['ExtraAttributes']:
                    petInfo = json.loads(slotData['tag']['ExtraAttributes']['petInfo'])
                    filterPetSlot(petInfo, location, month_indexed)
                else:
                    print("\'petInfo\' not in \'ExtraAttributes\'... hmm.")
                    if 'originTag' in slotData['tag']['ExtraAttributes']:
                        if slotData['tag']['ExtraAttributes']['originTag'] == 'UNKNOWN':
                            print("Unknown pet : " + str(playerid) + " : " + str(location))
                            saveItem(str(profileId), str(playerid), "PET", "unknown_pet",location)
                        else:
                            print("Not \'originTag\' == \'UNKNOWN\' ")
                            print(str(playerid) + " : " + str(location) + " : " + str(slotData) + "\n")
                    else:
                        print("No origin tag.")
                        print(str(playerid) + " : " + str(location) + " : " + str(slotData) + "\n")
            else:
                print("\'ExtraAttributes\' not in \'ExtraAttributes\'... hmm.")
                print(str(playerid) + " : " + str(location) + " : " + str(slotData) + "\n")
        else:
            print("\'tag\' not in pet data... hmm.")
            print(str(playerid) + " : " + str(location) + " : " + str(slotData) + "\n")

        #End code block

def filterArmorSlot(slotData,location,month_indexed):
    pass

def filterPetSlot(slotData,location,month_indexed):
    global mydb
    global config
    global playerid
    global profileId
    #cursed pets
    if slotData['tier'] in ['COMMON','UNCOMMON','RARE'] and slotData['type'] in ['SKELETON_HORSE', 'BLAZE', 'PIGMAN', 'SNOWMAN', 'WITHER_SKELETON']:
        print("Found Cursed Pet : " + str(playerid) + " : " + str(location) + " : " + str(slotData) + "\n")
        mycursor = mydb.cursor()
        sql_command = "INSERT INTO foundItems(profile_id, player_id, item_id, item, item_location, month_indexed) VALUES('%s','%s','%s','%s','%s','%s')" % (str(profileId), str(playerid), "PET", "cursed_" + str(slotData['type']),location, month_indexed)
        mycursor.execute(sql_command)
        mydb.commit()

def exoticSearchSlot(slotData,location, month_indexed):
    global mydb
    global config
    global exoticCodesTable
    global nonExoticCodes
    global playerid
    global profileId
    try:
        if str(slotData['id']) == "298" and 'tag' in  slotData and 'ExtraAttributes' in slotData['tag'] and 'color' in slotData['tag']['display']:
            if str(slotData['tag']['ExtraAttributes']['id']) in exoticCodesTable["Helmet"]:
                if int(str(slotData['tag']['display']['color'])) != exoticCodesTable["Helmet"][str(slotData['tag']['ExtraAttributes']['id'])]:
                    if int(str(slotData['tag']['display']['color'])) not in nonExoticCodes:
                        mycursor = mydb.cursor()
                        sql_command = "INSERT INTO exoticProfiles(profile_id, player_id, item_id, item_color, item_location, month_indexed) VALUES('%s','%s','%s','%s','%s','%s')" % (str(profileId), playerid, str(slotData['tag']['ExtraAttributes']['id']),str(slotData['tag']['display']['color']),location,month_indexed)
                        mycursor.execute(sql_command)
                        mydb.commit()
        elif str(slotData['id']) == "299" and 'tag' in  slotData and 'ExtraAttributes' in slotData['tag'] and 'color' in slotData['tag']['display']:
            if str(slotData['tag']['ExtraAttributes']['id']) in exoticCodesTable["Chestplate"]:
                if int(str(slotData['tag']['display']['color'])) != exoticCodesTable["Chestplate"][str(slotData['tag']['ExtraAttributes']['id'])]:
                    if int(str(slotData['tag']['display']['color'])) not in nonExoticCodes:
                        mycursor = mydb.cursor()
                        sql_command = "INSERT INTO exoticProfiles(profile_id, player_id, item_id, item_color, item_location, month_indexed) VALUES('%s','%s','%s','%s','%s','%s')" % (str(profileId), playerid, str(slotData['tag']['ExtraAttributes']['id']),str(slotData['tag']['display']['color']),location,month_indexed)
                        mycursor.execute(sql_command)
                        mydb.commit()
        elif str(slotData['id']) == "300" and 'tag' in  slotData and 'ExtraAttributes' in slotData['tag'] and 'color' in slotData['tag']['display']:
            if str(slotData['tag']['ExtraAttributes']['id']) in exoticCodesTable["Leggings"]:
                if int(str(slotData['tag']['display']['color'])) != exoticCodesTable["Leggings"][str(slotData['tag']['ExtraAttributes']['id'])]:
                    if int(str(slotData['tag']['display']['color'])) not in nonExoticCodes:
                        mycursor = mydb.cursor()
                        sql_command = "INSERT INTO exoticProfiles(profile_id, player_id, item_id, item_color, item_location, month_indexed) VALUES('%s','%s','%s','%s','%s','%s')" % (str(profileId), playerid, str(slotData['tag']['ExtraAttributes']['id']),str(slotData['tag']['display']['color']),location,month_indexed)
                        mycursor.execute(sql_command)
                        mydb.commit()
        elif str(slotData['id']) == "301" and 'tag' in  slotData and 'ExtraAttributes' in slotData['tag'] and 'color' in slotData['tag']['display']:
            if str(slotData['tag']['ExtraAttributes']['id']) in exoticCodesTable["Boots"]:
                if int(str(slotData['tag']['display']['color'])) != exoticCodesTable["Boots"][str(slotData['tag']['ExtraAttributes']['id'])]:
                    if int(str(slotData['tag']['display']['color'])) not in nonExoticCodes:
                        mycursor = mydb.cursor()
                        sql_command = "INSERT INTO exoticProfiles(profile_id, player_id, item_id, item_color, item_location, month_indexed) VALUES('%s','%s','%s','%s','%s','%s')" % (str(profileId), playerid, str(slotData['tag']['ExtraAttributes']['id']),str(slotData['tag']['display']['color']),location, month_indexed)
                        mycursor.execute(sql_command)
                        mydb.commit()
                        # print(sql_command)
    except:
        print(slotData)
        exit()

def searchUser(userData):
    global exoticSearch
    global playerid
    global profileId
    global location
    global month_indexed
    month_indexed = userData[16]
    playerid = userData[2]
    profileId = userData[1]
    #inv_armor
    location = "inv_armor"
    if userData[7] != 'None':
        inv_armor = decodeJsonData(userData[7])
        for slot in range(len(inv_armor)):
            if type(inv_armor[slot]) is list:
                for sloter in range(len(inv_armor[slot])):
                    if inv_armor[slot][sloter] != {}:
                        if type(inv_armor[slot][sloter]) is list:
                            continue
                        filterSlot(inv_armor[slot][sloter],location)
                        if exoticSearch:
                            exoticSearchSlot(inv_armor[slot][sloter],location,month_indexed)
    #ender_chest_contents
    location = "ender_chest_contents"
    if userData[8] != 'None':
        ender_chest_contents = decodeJsonData(userData[8])
        for slot in range(len(ender_chest_contents)):
            if type(ender_chest_contents[slot]) is list:
                for sloter in range(len(ender_chest_contents[slot])):
                    if ender_chest_contents[slot][sloter] != {}:
                        if type(ender_chest_contents[slot][sloter]) is list:
                            continue
                        filterSlot(ender_chest_contents[slot][sloter],location)
                        if exoticSearch:
                            exoticSearchSlot(ender_chest_contents[slot][sloter],location,month_indexed)
    #wardrobe_contents
    location = "wardrobe_contents"
    if userData[9] != 'None':
        wardrobe_contents = decodeJsonData(userData[9])
        for slot in range(len(wardrobe_contents)):
            if type(wardrobe_contents[slot]) is list:
                for sloter in range(len(wardrobe_contents[slot])):
                    if wardrobe_contents[slot][sloter] != {}:
                        if type(wardrobe_contents[slot][sloter]) is list:
                            continue
                        filterSlot(wardrobe_contents[slot][sloter],location)
                        if exoticSearch:
                            exoticSearchSlot(wardrobe_contents[slot][sloter],location,month_indexed)
    #personal_vault_contents
    location = "personal_vault_contents"
    if userData[10] != 'None':
        personal_vault_contents = decodeJsonData(userData[10])
        for slot in range(len(personal_vault_contents)):
            if type(personal_vault_contents[slot]) is list:
                for sloter in range(len(personal_vault_contents[slot])):
                    if personal_vault_contents[slot][sloter] != {}:
                        if type(personal_vault_contents[slot][sloter]) is list:
                            continue
                        filterSlot(personal_vault_contents[slot][sloter],location)
                        if exoticSearch:
                            exoticSearchSlot(personal_vault_contents[slot][sloter],location,month_indexed)    
    #inv_contents
    location = "inv_contents"
    if userData[11] != 'None':
        inv_contents = decodeJsonData(userData[11])
        for slot in range(len(inv_contents)):
            if type(inv_contents[slot]) is list:
                for sloter in range(len(inv_contents[slot])):
                    if inv_contents[slot][sloter] != {}:
                        if type(inv_contents[slot][sloter]) is list:
                            continue
                        filterSlot(inv_contents[slot][sloter],location)
                        if exoticSearch:
                            exoticSearchSlot(inv_contents[slot][sloter],location,month_indexed)
            else:
                if inv_contents[slot] != {}:
                    filterSlot(inv_contents[slot],location)
                    if exoticSearch:
                        exoticSearchSlot(inv_contents[slot],location,inv_contents)
    #backpacks
    location = "backpacks"
    if userData[12] != 'None':
        backpacks = decodeJsonData(userData[12])
        for bp in range(len(backpacks)):
            backpack = backpacks[bp][0]
            for slot in range(len(backpack)):
                if backpack[slot] != {}:
                    filterSlot(backpack[slot],location)
                    if exoticSearch:
                        exoticSearchSlot(backpack[slot],location,month_indexed)
    #pets_contents
    location = "pets_contents"
    if userData[13] != 'None':
        pets_contents = decodeJsonData(userData[13])
        for pet in range(len(pets_contents)):
            filterPetSlot(pets_contents[pet], location, month_indexed)
def remakeTable(mycursor):
    mycursor.execute("SHOW TABLES LIKE \'exoticProfiles" + str(config['monthIndexed']) + "\'")
    if len(mycursor.fetchall()) > 0:
        mycursor.execute("DROP TABLE exoticProfiles" + str(config['monthIndexed']))
    mycursor.execute("SHOW TABLES LIKE \'foundItems" + str(config['monthIndexed']) + "\'")
    if len(mycursor.fetchall()) > 0:
        mycursor.execute("DROP TABLE foundItems" + str(config['monthIndexed']))
    mycursor.execute("CREATE TABLE exoticProfiles" + str(config['monthIndexed']) + "(id INT(8) UNSIGNED AUTO_INCREMENT PRIMARY KEY, profile_id VARCHAR(36) NOT NULL, player_id VARCHAR(36) NOT NULL,item_id VARCHAR(64),item_color VARCHAR(8), item_location VARCHAR(64), month_indexed text(20))")
    mycursor.execute("CREATE TABLE foundItems" + str(config['monthIndexed']) + "(id INT(8) UNSIGNED AUTO_INCREMENT PRIMARY KEY, profile_id VARCHAR(36) NOT NULL, player_id VARCHAR(36) NOT NULL,item_id VARCHAR(64),item VARCHAR(256), item_location VARCHAR(64), month_indexed text(20))")
    
def searchDb(index):
    global exoticSearch
    global exoticCodesTable
    global nonExoticCodes
    global mydb
    nonExoticCodes = [6684774, 6684723, 10027084, 13369446, 16711807, 16724889, 16737970, 16751052, 16764133, 16751052, 16737970, 16724889, 16711807, 13369446, 10027084, 6684723, 6684774, 10027161, 13369548, 16711935, 16724991, 16738047, 16751103, 16764159, 15060223, 13408767, 11691775, 10040319, 8323327, 6684876, 4980889, 3342438, 4980889, 6684876, 8323327, 10040319, 11691775, 13408767, 15060223, 16764159, 16751103, 16738047, 16724991, 16711935, 13369548, 10027161, 2031664, 4589662, 5510254, 6102136, 6497149, 6958210, 8274326, 9327014, 10249395, 11040189, 12094409, 13018068, 14270947, 15061485, 15720949, 16577535]
    exoticCodesTable = {
        "Helmet":
        {"TARANTULA_HELMET":0,"FARM_SUIT_HELMET":16776960,"FARM_ARMOR_HELMET":16766720,"SPEEDSTER_HELMET":14744823,"CACTUS_HELMET":65280,"LEAFLET_HELMET":5098573,"MINER_OUTFIT_HELMET":8026468,"MUSHROOM_HELMET":16711680,"EMERALD_ARMOR_HELMET":65280,"PUMPKIN_HELMET":15575606,"GROWTH_HELMET":48640,"ARMOR_OF_MAGMA_HELMET":16749312,"CRYSTAL_HELMET":6684774,"FAIRY_HELMET":6684774},
        "Chestplate":
        {"SUPERIOR_DRAGON_CHESTPLATE":15916817,"WISE_DRAGON_CHESTPLATE":2748649,"YOUNG_DRAGON_CHESTPLATE":14542064,"STRONG_DRAGON_CHESTPLATE":14229057,"UNSTABLE_DRAGON_CHESTPLATE":11670243,"OLD_DRAGON_CHESTPLATE":15787690,"PROTECTOR_DRAGON_CHESTPLATE":10065803,"SHARK_SCALE_CHESTPLATE":11430,"ANGLER_CHESTPLATE":720975,"BAT_PERSON_CHESTPLATE":0,"FARM_SUIT_CHESTPLATE":16776960,"FARM_ARMOR_CHESTPLATE":16766720,"SPEEDSTER_CHESTPLATE":14744823,"CACTUS_CHESTPLATE":65280,"LEAFLET_CHESTPLATE":5098573,"MINER_OUTFIT_CHESTPLATE":8026468,"MUSHROOM_CHESTPLATE":16711680,"GUARDIAN_CHESTPLATE":1143697,"EMERALD_ARMOR_CHESTPLATE":65280,"PUMPKIN_CHESTPLATE":15575606,"OBSIDIAN_CHESTPLATE":0,"LAPIS_ARMOR_CHESTPLATE":255,"CHEAP_TUXEDO_CHESTPLATE":3684408,"FANCY_TUXEDO_CHESTPLATE":3353130,"ELEGANT_TUXEDO_CHESTPLATE":1644825,"GROWTH_CHESTPLATE":48640,"SPOOKY_CHESTPLATE":6316128,"BLAZE_CHESTPLATE":16243251,"ARMOR_OF_MAGMA_CHESTPLATE":16749312,"CRYSTAL_CHESTPLATE":6684774,"FAIRY_CHESTPLATE":6684774,"CHESTPLATE_OF_THE_PACK":16711680,"SPONGE_CHESTPLATE":16768081},
        "Leggings":
        {"SUPERIOR_DRAGON_LEGGINGS":15916817,"WISE_DRAGON_LEGGINGS":2748649,"YOUNG_DRAGON_LEGGINGS":14542064,"STRONG_DRAGON_LEGGINGS":14717977,"UNSTABLE_DRAGON_LEGGINGS":11670243,"OLD_DRAGON_LEGGINGS":15787690,"PROTECTOR_DRAGON_LEGGINGS":10065803,"TARANTULA_LEGGINGS":0,"SHARK_SCALE_LEGGINGS":11430,"ANGLER_LEGGINGS":720975,"BAT_PERSON_LEGGINGS":0,"FARM_SUIT_LEGGINGS":16776960,"FARM_ARMOR_LEGGINGS":16766720,"SPEEDSTER_LEGGINGS":14744823,"CACTUS_LEGGINGS":65280,"LEAFLET_LEGGINGS":5098573,"MINER_OUTFIT_LEGGINGS":8026468,"MUSHROOM_LEGGINGS":16711680,"CREEPER_LEGGINGS":8054828,"EMERALD_ARMOR_LEGGINGS":65280,"PUMPKIN_LEGGINGS":15575606,"MUSIC_PANTS":315347,"LAPIS_ARMOR_LEGGINGS":255,"CHEAP_TUXEDO_LEGGINGS":13092807,"FANCY_TUXEDO_LEGGINGS":13948116,"ELEGANT_TUXEDO_LEGGINGS":16711164,"GROWTH_LEGGINGS":48640,"SPOOKY_LEGGINGS":6316128,"BLAZE_LEGGINGS":16243251,"ARMOR_OF_MAGMA_LEGGINGS":16749312,"CRYSTAL_LEGGINGS":6684774,"FAIRY_LEGGINGS":6684774,"SPONGE_LEGGINGS":16768081},
        "Boots":
        {"SUPERIOR_DRAGON_BOOTS":15883544,"WISE_DRAGON_BOOTS":2748649,"YOUNG_DRAGON_BOOTS":14542064,"STRONG_DRAGON_BOOTS":15782180,"UNSTABLE_DRAGON_BOOTS":11670243,"OLD_DRAGON_BOOTS":15787690,"PROTECTOR_DRAGON_BOOTS":10065803,"SHARK_SCALE_BOOTS":11430,"ANGLER_BOOTS":720975,"SQUID_BOOTS":0,"BAT_PERSON_BOOTS":0,"FARMER_BOOTS":13391104,"FARM_SUIT_BOOTS":16776960,"FARM_ARMOR_BOOTS":16766720,"SPEEDSTER_BOOTS":14744823,"CACTUS_BOOTS":65280,"LEAFLET_BOOTS":5098573,"MINER_OUTFIT_BOOTS":8026468,"MUSHROOM_BOOTS":16711680,"EMERALD_ARMOR_BOOTS":65280,"PUMPKIN_BOOTS":15575606,"LAPIS_ARMOR_BOOTS":255,"CHEAP_TUXEDO_BOOTS":3684408,"FANCY_TUXEDO_BOOTS":3353130,"ELEGANT_TUXEDO_BOOTS":1644825,"GROWTH_BOOTS":48640,"SPOOKY_BOOTS":6316128,"BLAZE_BOOTS":16243251,"ARMOR_OF_MAGMA_BOOTS":16749312,"CRYSTAL_BOOTS":6684774,"FAIRY_BOOTS":6684774,"RANCHERS_BOOTS:":13391104,"SPONGE_BOOTS":16768081}}
    getConfig()
    exoticSearch = config["exoticSearch"]
    mydb = mysql.connector.connect(
        host=config['databaseHost'],
        user=config['databaseUser'],
        password=config['databasePassword'],
        database=config['databaseName'],
    )
    print("connected")
    mycursor = mydb.cursor()
    remakeTable(mycursor)
    mycursor.execute("SELECT MAX(`id`) FROM sbData"+str(config['monthIndexed']))
    maxIds = mycursor.fetchall()[0][0]
    if maxIds == None:
        print("Error: no player data in database table.")
        exit()
    userCount = int(maxIds)
    print(userCount)
    totalDbTime = 0
    times = 0
    totalProcessingTime = 0
    totalTime = 0
    dbTimes = 0 
    userNumber = 0
    totalNewNamesTime = 0
    timesOfTotalNewNamesTime = 0
    while userNumber in range(userCount):
        a = time.time()
        mycursor.execute("SELECT * FROM sbData" + str(config['monthIndexed']) + " WHERE `id` = %i" % (userNumber))
        userData = mycursor.fetchall()
        b = time.time()
        totalDbTime += b-a
        dbTimes += 1
        if len(userData) == 1:
            c = time.time()
            searchUser(userData[0])
            d = time.time()
            totalProcessingTime += d-c
            times += 1
        else:
            pass
        e = time.time()
        totalTime += e-a
        if userNumber%config['updateProgressInteval'] == 0 and userNumber != 0:
            print(str(userNumber) + ". total average: " + str(round(totalTime/userNumber, 5)) + ". processing: " + str(round(totalProcessingTime/times, 5)) + ". dbtime: " + str(round(totalDbTime/userNumber, 5)) + ". ")
        userNumber +=1
    print(str(userNumber) + ". total " + str())
    print("Done.")

print("Start")
searchDb(0)
 # Last updated 14/5/22