import streamlit as st
from datetime import datetime, date
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
settingFileName = "Setting.csv"

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

def uploadClient(doctor, naming):
    store.collection(clientFileName).document(naming).set(doctor)

def retriveClient():
    data = []

    docs = store.collection(clientFileName).get()
    for doc in docs:
        data.append(doc.to_dict())

    return data

# ---------------------------------------------------------------------------------

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

# ---------------------------------------------------------------------------------------------

st.title("Hello patient. Please enter this form to line up.")

insertForm = st.empty()
form = insertForm.form(key="TestForm1", clear_on_submit=False)
username = form.text_input("Username")
password = form.text_input("Password")
doctor = form.selectbox("Which doctor are you here for?", retriveDoctor("client"))
appointed = form.checkbox("Have you made an appointment before-hand? (This mean you walk in)", value=False)

register_button = form.form_submit_button("Resigter")
submit_button = form.form_submit_button(label="Line up")
check_queue = form.form_submit_button("Check Queue ID")

if register_button:
    result = registerClient(username, password)
    if result:
        st.success("Registered")
    else:
        st.error("Someone already used that name")

if check_queue:
    output = retriveClientData(username, password)
    if output == "False1":
        st.error("There is no user with that name or Incorrect password")
    elif output == "False2":
        st.warning("You have not line up yet.")
    else:
        st.success("Your Queue Number is {}".format(output))

if submit_button:
    output = addQueueV2(username, password, doctor, appointed)
    if output == "No user":
        st.error("User not found")
    elif output == "Wrong Password":
        st.error("There is no user with that name or Incorrect password")
    else:
        globalOutput = output
        setTime6 = datetime.now().timestamp()
        currentTime6 = datetime.now().timestamp()
        st.success("Thank you for lining up. Your Queue Number is {}.\nPlease screenshot it until your queue has been called.".format(output))
        while (currentTime6 - setTime6) < 5:
            currentTime6 = datetime.now().timestamp()
        
        initial_Pending = False
        current_Status = retriveData(output)
        previous = -1
        delay = 60
        setTime2 = datetime.now().timestamp() - delay
        while True:
            currentTime2 = datetime.now().timestamp()
            if (currentTime2 - setTime2 > delay):
                setTime2 = datetime.now().timestamp()
                status = retriveData(output)
                if current_Status != status:
                    current_Status = status
                    if status == "Waiting":
                        st.info("Your queue has not been called yet. Please wait until called.")
                    elif status == "Pending1":
                        previous = datetime.now().timestamp()
                        initial_Pending = True
                        current_Status = status
                        updateData(output, "Pending2")
                    elif status == "Pending2":
                        current = datetime.now().timestamp()
                        time_remains = (360 - (current - previous))
                        current_waiting = -1
                        setTime3 = datetime.now().timestamp() - delay
                        while (time_remains // 60) > 1 and current_Status == status:
                            currentTime3 = datetime.now().timestamp()
                            if (currentTime3 - setTime3) > delay:
                                setTime3 = datetime.now().timestamp()
                                current = datetime.now().timestamp()
                                time_remains = (360 - (current - previous))
                                if ((time_remains // 60 < 6) and (time_remains // 60 > 1)) and (time_remains // 60 != current_waiting):
                                    current_waiting = (time_remains // 60)
                                    st.warning("You queue has been called. You have {} minutes left.".format(str(time_remains // 60)))
                                status = retriveData(output)
                        current_Status = status
                        if (retriveData(output) != "Complete") and (retriveData(output) != "Waiting"):
                            updateData(output, "Pending3")
                    elif status == "Pending3":
                        current = datetime.now().timestamp()
                        time_remains = (360 - (current - previous))
                        st.warning("You queue has been called. You have less than 1 minute left.")
                        setTime4 = datetime.now().timestamp() - delay
                        while time_remains > 0 and current_Status == status:
                            currentTime4 = datetime.now().timestamp()
                            if (currentTime4 - setTime4) > delay:
                                setTime4 = datetime.now().timestamp()
                                current = datetime.now().timestamp()
                                time_remains = (360 - (current - previous))
                                status = retriveData(output)
                        current_Status = status
                        if (retriveData(output) != "Complete") and (retriveData(output) != "Waiting"):
                            updateData(output, "Pending4")
                    elif status == "Pending4":
                        st.warning("5 minutes have passed. Please meet the doctor immediately before your queue get skipped.")
                        current_Status = status
                        setTime5 = datetime.now().timestamp() - delay
                        while current_Status == status:
                            currentTime5 = datetime.now().timestamp()
                            if (currentTime5 - setTime5) > delay:
                                setTime5 = datetime.now().timestamp()
                                status = retriveData(output)
                    elif status == "Complete":
                        st.success("Thank you for coming to meet the doctor today. Have a nice day!")
                        break                
                    else:
                        st.error("Something is wrong with the system. Please contact the staff for the moment.")
                        break
