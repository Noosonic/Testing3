import csv
from DatabaseSystem import *

def resetDoctor():
    writeFile = open("DoctorList.csv", 'w', newline="")
    writer1 = csv.writer(writeFile)
    writer1.writerow(["Doctor Name", "Password"])
    writeFile.close()
    deleteDoctor()

def register(name, password):
    # readFile = open("DoctorList.csv", "r")
    # reader = csv.reader(readFile)
    reader = retriveDoctor("client")
    for row in reader:
        if row == name:
            return False
    # readFile.close()

    appendFile = open("DoctorList.csv", 'a', newline="")
    writer2 = csv.writer(appendFile)
    writer2.writerow([name, password])
    appendFile.close()
    return True

def login(name, password):
    listing = retriveDoctor("doctor")
    for row in listing:
        if (row[0] == name) and (row[1] == password):
            return True
    return False