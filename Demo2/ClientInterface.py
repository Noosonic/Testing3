import streamlit as st
from moduleFile import *
from datetime import time

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
    st.success("Thank you for lining up. Your Queue Number is {}.\nPlease screenshot it until your queue has been called.".format(output))
    uploadData()
    initial_Pending = False
    current_Status = retriveData(output)
    previous = -1
    setTime2 = time.time() - 60
    delay = 60
    while True:
        currentTime2 = time.time()
        if (currentTime2 - setTime2 > delay):
            setTime2 = time.time()
            status = retriveData(output)
            if current_Status != status:
                current_Status = status
                if status == "Waiting":
                    st.info("Your queue has not been called yet. Please wait until called.")
                elif status == "Pending1":
                    previous = int(time.time())
                    initial_Pending = True
                    current_Status = status
                    updateData(output, "Pending2")
                elif status == "Pending2":
                    current = int(time.time())
                    time_remains = (360 - (current - previous))
                    current_waiting = -1
                    setTime3 = time.time() - 60
                    while (time_remains // 60) > 1 and current_Status == status:
                        currentTime3 = time.time()
                        if (currentTime3 - setTime3) > delay:
                            setTime3 = time.time()
                            current = int(time.time())
                            time_remains = (360 - (current - previous))
                            if ((time_remains // 60 < 6) and (time_remains // 60 > 1)) and (time_remains // 60 != current_waiting):
                                current_waiting = (time_remains // 60)
                                st.warning("You queue has been called. You have {} minutes left.".format(str(time_remains // 60)))
                            status = retriveData(output)
                    current_Status = status
                    updateData(output, "Pending3")
                elif status == "Pending3":
                    current = int(time.time())
                    time_remains = (360 - (current - previous))
                    st.warning("You queue has been called. You have less than 1 minute left.")
                    setTime4 = time.time() - 60
                    while time_remains > 0 and current_Status == status:
                        currentTime4 = time.time()
                        if (currentTime4 - setTime4) > delay:
                            setTime4 = time.time()
                            current = int(time.time())
                            time_remains = (360 - (current - previous))
                            status = retriveData(output)
                    current_Status = status
                    updateData(output, "Pending4")
                elif status == "Pending4":
                    st.warning("5 minutes have passed. Please meet the doctor immediately before your queue get skipped.")
                    current_Status = status
                    setTime5 = time.time() - 60
                    while current_Status == status:
                        currentTime5 = time.time()
                        if (currentTime5 - setTime5) > delay:
                            setTime5 = time.time()
                            status = retriveData(output)
                elif status == "Complete":
                    st.success("Thank you for coming to meet the doctor today. Have a nice day!")
                    break                
                else:
                    st.error("Something is wrong with the system. Please contact the staff for the moment.")
                    break
