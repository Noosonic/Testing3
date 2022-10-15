import streamlit as st
import csv
from datetime import datetime, date, time
import firebase_admin
from firebase_admin import credentials, firestore

fileName = str(date.today())
fileName = fileName + ".csv"

if not firebase_admin._apps:
    cred = credentials.Certificate("certificate.json")
    app = firebase_admin.initialize_app(cred)

store = firestore.client()

collection_name = fileName

doctorFileName = "DoctorList.csv"
clientFileName = "ClientList.csv"

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

def retrivePatients(doctor):
    data = retriveData("All")
    subData = []
    for each in data:
        if each["Doctor Name"] == doctor or each["Doctor Name"] == "Walk in":
            subData.append(each["Queue ID"])
    return subData

def deleteClient():
    docs = store.collection(clientFileName).get()
    for doc in docs:
        key = doc.id
        store.collection(clientFileName).document(key).delete()

def uploadClient(doctor, naming):
    store.collection(clientFileName).document(naming).set(doctor)

def retriveClient():
    data = []

    docs = store.collection(clientFileName).get()
    for doc in docs:
        data.append(doc.to_dict())

    return data

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

# ---------------------------------------------------------------------------------

def resetClient():
    writeFile = open("DoctorList.csv", 'w', newline="")
    writer1 = csv.writer(writeFile)
    writer1.writerow(["Doctor Name", "Password"])
    writeFile.close()
    deleteClient()

def registerClient(name, password):
    # readFile = open("DoctorList.csv", "r")
    # reader = csv.reader(readFile)
    reader = retriveClient()
    for row in reader:
        if row == name:
            return False
    # readFile.close()

    uploadClient({"Client Name": name, "Password": password}, name)
    return True

def loginClient(name, password):
    listing = retriveClient()
    for row in listing:
        if (row[0] == name) and (row[1] == password):
            return True
    return False

def retriveClientData(name, password):
    checker = loginClient(name, password)
    if checker:
        data = retriveData("All")
        for each in data:
            if each["Username"] == name:
                return each["Queue ID"]
        return str("False2")
    else:
        return str("False1")

# ----------------------------------------------------------------------------------------------

def resetQueueV2():
    file = open(fileName, "w", newline="")
    writer = csv.writer(file)
    writer.writerow(["Doctor Name", "Queue ID", "Appointed", "Time", "Status"])
    file.close()
    deleteData()

def addQueueV2(username, password, doctor, appointed):
    retrivingUser = retriveClient()
    for each in retrivingUser:
        if (username == each["Client Name"]):
            if (password == each["Password"]):
                amount = len(retriveData("All")) + 1
                name = "Q" + str(amount)
                rightNow = datetime.now()
                if appointed == False:
                    doctor = "Walk in"
                subQueue = {"Username": username, "Password": password, "Doctor Name": doctor, "Queue ID": name, "Appointed": str(appointed), "Time": rightNow.strftime("%H:%M:%S"), "Status": "Waiting"}
                uploadData(subQueue, name)
                return name
            else:
                return "Wrong Password"
    return "No user"

def callQueue(queueNumber):
    data = retriveData("All")
    for each in data:
        if queueNumber == each["Queue ID"]:
            return each

# ---------------------------------------------------------------------------------------------

if "DoctorName" not in st.session_state:
    st.session_state.DoctorName = "Unknown"

def initiatGlobalVariables():
    global Docusername
    global Docpassword
    global registerButton
    global loginButton
    global BackButton
    global patientList
    global CheckPatient
    global CallPatient
    global UncallPatient
    global Complete

initiatGlobalVariables()

st.title("Hello Doctor. Please enter this form to continue")

doctorInsertForm = st.empty()
doctorForm = doctorInsertForm.form(key="DoctorOnly", clear_on_submit=False)

Docusername = doctorForm.text_input("Username")

Docpassword = doctorForm.text_input("Password")


registerButton = doctorForm.form_submit_button("Register")

loginButton = doctorForm.form_submit_button("Login")

BackButton = doctorForm.form_submit_button("Log out")

if registerButton:
    output = register(Docusername, Docpassword)
    if output:
        st.success("You have successfully signed up. Please re-enter the form again to login")
    else:
        st.error("Someone already used that username")

if loginButton:
    output = login(Docusername, Docpassword)
    if output:
        st.session_state.DoctorName = Docusername
        st.success("Welcome back, {}".format(Docusername))
    else:
        st.error("Either the username doesn\'t exist or the password is inccorect")

if BackButton:
    st.session_state.DoctorName = "Unknown"


st.title("Doctor Main Page")

patientCallForm = st.empty()
patientForm = patientCallForm.form("PatientCall", clear_on_submit=False)

patientList = patientForm.selectbox("Select a Queue", retrivePatients(st.session_state.DoctorName))


CheckPatient = patientForm.form_submit_button("Check Information")

CallPatient = patientForm.form_submit_button("Call Patient")

UncallPatient = patientForm.form_submit_button("Uncall Patient")

Complete = patientForm.form_submit_button("Finish")

if CheckPatient:
    QueueNumber = callQueue(patientList)
    st.text("Patient\'s Information\nQueue ID: {}\nPatient\'s Name: {}\nDoctor: {}\nTime: {}\nAppointed: {}\nStatus: {}".format(QueueNumber["Queue ID"], QueueNumber["Username"], QueueNumber["Doctor Name"], QueueNumber["Time"], QueueNumber["Appointed"], QueueNumber["Status"]))

if CallPatient:
    updateData(patientList, "Pending1")
    st.success("Calling. Please wait for at least 10 minutes")
            
if UncallPatient:
    updateData(patientList, "Waiting")
    st.success("Cancelling")

if Complete:
    updateData(patientList, "Complete")
    st.success("Finishing up the meeting...")