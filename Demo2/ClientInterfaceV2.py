import streamlit as st
from moduleFileClient import registerClient, loginClient

clientInsertForm1 = st.empty()
clientForm = clientInsertForm1.form(key="Something", clear_on_submit=True)
username = clientForm.text_input('Username')
password = clientForm.text_input('Password')
# doctorOptions = retriveDoctor("client")
# doctorOptions.append("Walk in")
# doctor = clientForm.selectbox("Which doctor are you here for?", doctorOptions)
# appointed = clientForm.checkbox("Have you made an appointment before-hand?", value=False)
clientRegister = clientForm.form_submit_button("Resigter")
clientLogin = clientForm.form_submit_button("Login")

clientMainGUI = st.empty()
lineUp = st.empty()
guiCancel = st.empty()

if clientRegister:
    result = registerClient(username, password)
    if result:
        st.success("Registered")
    else:
        st.error("Someone already used that name")

if clientLogin:
    result = loginClient(username, password)
    if result:
        st.success("Welcome back, {}. What would you like to do today?".format(username))
        clientInsertForm1.empty()

        mainGUI = clientMainGUI.form(key="mainGUI", clear_on_submit=False)
        lineUp = mainGUI.form_submit_button("Line Up")
        guiCancel = mainGUI.form_submit_button("Cancel or Log out")

    else:
        st.error("There is no patient with that name OR the password is incorrect")

if lineUp:
    st.success("Working")

if guiCancel:
    st.success("Working")