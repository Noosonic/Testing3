import streamlit as st
import csv
from datetime import datetime, date
import firebase_admin
from firebase_admin import credentials, firestore

fileName = str(date.today())
fileName = fileName + ".csv"

if not firebase_admin._apps:
    cred = credentials.Certificate("Demo2/certificate.json")
    app = firebase_admin.initialize_app(cred)

store = firestore.client()

collection_name = fileName

doctorFileName = "DoctorList.csv"

def batch_data(iterable, n=1):
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx:min(ndx + n, l)]

def deleteData():
    docs = store.collection(collection_name).get()
    for doc in docs:
        key = doc.id
        store.collection(collection_name).document(key).delete()

def uploadData(data, naming):
    store.collection(collection_name).document(naming).set(data)

def retriveData(type):
    data = []

    docs = store.collection(collection_name).get()
    for doc in docs:
        data.append(doc.to_dict())

    if type == "ID":
        IDs = []
        for each in data:
            IDs.append(each["Queue ID"])
        return IDs
    elif type == "All":
        return data
    else:
        for each in data:
            if (type == each["Queue ID"]):
                return each["Status"]

def updateData(QueueID, newStatus):
    docs = store.collection(collection_name).get()
    for doc in docs:
        key = doc.id
        temp = doc.to_dict()
        if QueueID == temp["Queue ID"]:
            store.collection(collection_name).document(key).update({"Status":newStatus})
            break

def deleteDoctor():
    docs = store.collection(doctorFileName).get()
    for doc in docs:
        key = doc.id
        store.collection(doctorFileName).document(key).delete()

def uploadDoctor(doctor, naming):
    store.collection(doctorFileName).document(naming).set(doctor)

def retriveDoctor(caller):
    data = []

    docs = store.collection(doctorFileName).get()
    for doc in docs:
        data.append(doc.to_dict())

    if caller == "client":
        doctorNames = []
        for each in data:
            doctorNames.append(each["Doctor Name"])
        return doctorNames
    elif caller == "doctor":
        doctorInfo = []
        for each in data:
            doctorInfo.append([each["Doctor Name"], each["Password"]])
        return doctorInfo

# ---------------------------------------------------------------------------------

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

    uploadDoctor({"Doctor Name": name, "Password": password}, name)
    return True

def login(name, password):
    listing = retriveDoctor("doctor")
    for row in listing:
        if (row[0] == name) and (row[1] == password):
            return True
    return False

# ----------------------------------------------------------------------------------------------

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
    subQueue = {"Doctor Name": doctor, "Queue ID": name, "Appointed": str(appointed), "Time": rightNow.strftime("%H:%M:%S"), "Status": "Waiting"}
    uploadData(subQueue, name)

def callQueue(queueNumber):
    data = retriveData("All")
    for each in data:
        if queueNumber == each["Queue ID"]:
            return each

# ---------------------------------------------------------------------------------------------

st.title("Hello Doctor. Please enter this registration to continue.")

insertForm2 = st.empty()
form2 = insertForm2.form(key="TestForm2", clear_on_submit=True)
nameInsert = form2.text_input("Doctor\'s Name")
passwordInsert = form2.text_input("Password")
registerSubmit = form2.form_submit_button("Register")
loginSubmit = form2.form_submit_button("Login")

if registerSubmit:
    result = register(nameInsert, passwordInsert)
    if result:
        st.success("Registered")
    else:
        st.error("Someone already used that name")

if loginSubmit:
    result = login(nameInsert, passwordInsert)
    if result:
        st.success("Welcome back, {}".format(nameInsert))
    else:
        st.error("There is no doctor with that name OR the password is incorrect")

callForm = st.empty()
form3 = callForm.form(key="TestForm3", clear_on_submit=False)
callingID = form3.selectbox("Queue ID", retriveData("ID"))
checkingSubmit = form3.form_submit_button("Check Information")
callingSubmit = form3.form_submit_button("Call Patient")
unCallSubmit = form3.form_submit_button("Uncall Patient")
CompleteSubmit = form3.form_submit_button("Finish Meeting")

reportPoster = st.empty()

if checkingSubmit:
    called = callQueue(callingID)
    report1 = reportPoster.text_area("Patient\'s Information:", "QueueID: {}\nTime: {}\nDoctor: {}\nAppointed: {}\nStatus: {}".format(str(called["Queue ID"]), str(called["Time"]), str(called["Doctor Name"]), str(called["Appointed"]), str(called["Status"])), height=155)

if callingSubmit:
    called = callQueue(callingID)
    updateData(called["Queue ID"], "Pending1")

if unCallSubmit:
    called = callQueue(callingID)
    updateData(called["Queue ID"], "Waiting")

if CompleteSubmit:
    called = callQueue(callingID)
    updateData(called["Queue ID"], "Complete")