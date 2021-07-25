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
mycursor = mydb.cursor()
mycursor.execute("DROP TABLE names")
mycursor.execute("CREATE TABLE names(id INT(8), player_id VARCHAR(36) NOT NULL)")
for l in range(15):
    print(str(l), "started")
    file = readJson("names/" + str(hex(l))[2:] + ".json")
    a = time.time()
    for i in range(len(file)):
        file[i]
        sql_command = "INSERT INTO names(player_id) VALUES('%s')" % (file[i].replace('-',''))
        mycursor.execute(sql_command)
        mydb.commit()
    b = time.time()
    print(str(hex(l))[2:], "ended")
    print("average time:", str((b-a)/i))
    sql_command = "SELECT COUNT(*) FROM names"
    mycursor.execute(sql_command)
    print("total count is:", str(mycursor.fetchall()), "\n")