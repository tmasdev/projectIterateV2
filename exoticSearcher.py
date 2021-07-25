import mysql.connector
#Python
import csv
def saveExoticProfilesToCsv():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="CURSE OF BINDING",
        database="skyblockUsers"
    )
    mycursor = mydb.cursor()
    mycursor.execute("SELECT MAX(`id`) FROM exoticProfiles")
    userCount = int(mycursor.fetchall()[0][0])
    print(userCount)
    i = 1
    exoticProfiles = []
    while i in range(userCount+1):
        mycursor.execute("SELECT * FROM exoticProfiles WHERE id = %i" % (i))
        data = mycursor.fetchall()[0]
        exoticProfiles.append([data[0], data[1],data[2],data[3],hex(int(data[4])),data[5]])
        # print(exoticProfiles)
        i+=1
    file = open('exoticProfiles.csv', 'w')
    with file:
        write = csv.writer(file)
        write.writerows(exoticProfiles)
saveExoticProfilesToCsv()