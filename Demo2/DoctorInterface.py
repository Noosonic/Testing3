import streamlit as st
from moduleFile import *

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
        uploadDoctor()
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