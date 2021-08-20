# import mysql.connector
# #Python
# import csv
# def saveExoticProfilesToCsv():
#     mydb = mysql.connector.connect(
#         host="localhost",
#         user="root",
#         password="CURSE OF BINDING",
#         database="skyblockUsers"
#     )
#     mycursor = mydb.cursor()
#     mycursor.execute("SELECT MAX(`id`) FROM exoticProfiles")
#     userCount = int(mycursor.fetchall()[0][0])
#     print(userCount)
#     i = 1
#     exoticProfiles = []
#     while i in range(userCount+1):
#         mycursor.execute("SELECT * FROM exoticProfiles WHERE id = %i" % (i))
#         data = mycursor.fetchall()[0]
#         exoticProfiles.append([data[0], data[1],data[2],data[3],hex(int(data[4])),data[5]])
#         # print(exoticProfiles)
#         i+=1
#     file = open('exoticProfiles.csv', 'w')
#     with file:
#         write = csv.writer(file)
#         write.writerows(exoticProfiles)
# saveExoticProfilesToCsv()
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
    mycursor.execute("SELECT COUNT(*) FROM namesList")
    userCount = int(mycursor.fetchall()[0][0])
    print(userCount)
    mycursor.execute("SELECT * FROM namesList WHERE id < 5000")
    data = mycursor.fetchall()
    print(data)
    i = 5000
    namesList = []
    while i in range(userCount+5000):
        mycursor.execute("SELECT * FROM namesList WHERE id > %i and id < %i" % (i-5000, i))
        data = mycursor.fetchall()
        for q in range(len(data)):
            namesList.append(list(data[q])[0])
        print(len(namesList))
        # print(exoticProfiles)
        i+=5000
    
    file = open('namesList.csv', 'w')
    with file:
        write = csv.writer(file)
        write.writerows(namesList)
saveExoticProfilesToCsv()