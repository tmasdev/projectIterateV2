import mysql.connector
import time
import json
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="CURSE OF BINDING",
  database="skyblockUsers"
)
def readJson(fileName):
    with open(fileName, 'r') as userReadData:
        return(json.load(userReadData))

# mycursor = mydb.cursor()
# mycursor.execute("ALTER TABLE namesList ADD `id` INT NOT NULL AUTO_INCREMENT")
# mydb.commit()
# sql_command = "SELECT COUNT(*) FROM names"
# mycursor.execute(sql_command)
# print("total count is:", str(list(mycursor.fetchall()[0])[0]), "\n")
# for l in range(15):
#     print(str(l), "started")
#     file = readJson("names/" + str(hex(l))[2:] + ".json")
#     a = time.time()
#     for i in range(len(file)):
#         file[i] = file[i].replace("-","")
#     k = 20
# while k in range(len(file)):
#     namesBlock = []
#     for q in range(20):
#         namesBlock.append(file[k-q])
#     namesBlock = str(namesBlock).replace("[","(").replace("]",")").replace("\', \'", "\'), (\'")
#     sql_command = "INSERT INTO names(player_id) VALUES %s" % (namesBlock)
#     # print(sql_command)
#     # exit()
#     mycursor.execute(sql_command)
#     mydb.commit()
#     sql_command = "SELECT COUNT(*) FROM names"
#     mycursor.execute(sql_command)
#     print("total count is:", str(list(mycursor.fetchall()[0])[0]), "\n")
#     k+=20
#     b = time.time()
#     print(str(hex(l))[2:], "ended")
#     print("average time:", str((b-a)/i))
#     sql_command = "SELECT COUNT(*) FROM names"
#     mycursor.execute(sql_command)
#     print("total count is:", str(list(mycursor.fetchall()[0])[0]), "\n")