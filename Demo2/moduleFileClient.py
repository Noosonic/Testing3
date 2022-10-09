import streamlit as st
import csv
from datetime import datetime, date, time
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

def uploadData():
    deleteData()
    data = []
    headers = []
    with open(fileName) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                for header in row:
                    headers.append(header)
                line_count += 1
            else:
                obj = {}
                for idx, item in enumerate(row):
                    obj[headers[idx]] = item
                data.append(obj)
                line_count += 1
        print(f'Processed {line_count} lines.')

    for batched_data in batch_data(data, 499):
        batch = store.batch()
        for data_item in batched_data:
            doc_ref = store.collection(collection_name).document()
            batch.set(doc_ref, data_item)
        batch.commit()

    print('Done')

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

def uploadDoctor():
    deleteDoctor()
    data = []
    headers = []
    with open(doctorFileName) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                for header in row:
                    headers.append(header)
                line_count += 1
            else:
                obj = {}
                for idx, item in enumerate(row):
                    obj[headers[idx]] = item
                data.append(obj)
                line_count += 1
        print(f'Processed {line_count} lines.')

    for batched_data in batch_data(data, 499):
        batch = store.batch()
        for data_item in batched_data:
            doc_ref = store.collection(doctorFileName).document()
            batch.set(doc_ref, data_item)
        batch.commit()

    print('Done')

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

# ---------------------------------------------------------------------------------------------

st.title("Hello patient. Please enter this form to line up.")

insertForm = st.empty()
form = insertForm.form(key="TestForm1", clear_on_submit=True)
doctor = form.selectbox("Which doctor are you here for?", retriveDoctor("client"))
appointed = form.checkbox("Have you made an appointment before-hand?", value=False)

submit_button = form.form_submit_button(label="Submit")

if submit_button:
    output = addQueueV2(doctor, appointed)
    globalOutput = output
    insertForm.empty()
    setTime6 = datetime.now().timestamp()
    currentTime6 = datetime.now().timestamp()
    while (currentTime6 - setTime6) < 5:
        currentTime6 = datetime.now().timestamp()
    uploadData()
    st.success("Thank you for lining up. Your Queue Number is {}.\nPlease screenshot it until your queue has been called.".format(output))
    initial_Pending = False
    current_Status = retriveData(output)
    previous = -1
    setTime2 = datetime.now().timestamp() - 60
    delay = 60
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
                    setTime3 = datetime.now().timestamp() - 60
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
                    updateData(output, "Pending3")
                elif status == "Pending3":
                    current = datetime.now().timestamp()
                    time_remains = (360 - (current - previous))
                    st.warning("You queue has been called. You have less than 1 minute left.")
                    setTime4 = datetime.now().timestamp() - 60
                    while time_remains > 0 and current_Status == status:
                        currentTime4 = datetime.now().timestamp()
                        if (currentTime4 - setTime4) > delay:
                            setTime4 = datetime.now().timestamp()
                            current = datetime.now().timestamp()
                            time_remains = (360 - (current - previous))
                            status = retriveData(output)
                    current_Status = status
                    updateData(output, "Pending4")
                elif status == "Pending4":
                    st.warning("5 minutes have passed. Please meet the doctor immediately before your queue get skipped.")
                    current_Status = status
                    setTime5 = datetime.now().timestamp() - 60
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
