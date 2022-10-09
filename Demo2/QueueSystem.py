import csv
from datetime import datetime
from datetime import date
from DatabaseSystem import retriveData, deleteData

fileName = str(date.today())
fileName = fileName + ".csv"

def resetQueueV2():
    file = open(fileName, "w", newline="")
    writer = csv.writer(file)
    writer.writerow(["Doctor Name", "Queue ID", "Appointed", "Time", "Status"])
    file.close()
    deleteData()

def addQueueV2(doctor, appointed):
    retrivingData = retriveData("All")
    amount = len(retrivingData) + 1
    name = "Q" + str(amount)
    rightNow = datetime.now()
    subQueue = [doctor, name, str(appointed), rightNow.strftime("%H:%M:%S"), "Waiting"]
    file = open(fileName, 'a', newline="")
    writer = csv.writer(file)
    writer.writerow(subQueue)
    file.close()
    return name

def callQueue(queueNumber):
    data = retriveData("All")
    for each in data:
        if queueNumber == each["Queue ID"]:
            return each