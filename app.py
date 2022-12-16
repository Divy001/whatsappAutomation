from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from pymongo import MongoClient
from datetime import datetime
import certifi

# cluster = MongoClient("mongodb+srv://divy:divy@cluster0.asioc.mongodb.net/?retryWrites=true&w=majority")
cluster = MongoClient("mongodb+srv://hcpwire:hcpwire@cluster0.osnlh.mongodb.net/test",
                      tls=True, tlsAllowInvalidCertificates=True)
# mongodb+srv://hcpwire:hcpwire@cluster0.osnlh.mongodb.net/test
db = cluster["retail-corporate-testing"]
users = db["ppmcs"]
appointments = db["appointments"]

app = Flask(__name__)


# data = users.find_one({},{"_id":0, "patientName":1,"patientPhone":1, "patientAddress":1, "patientPincode":1})
# print(data["patientName"])


@app.route("/", methods=["get")
def hello():
    return "<h1 style='color:blue'>Hello There!</h1>"

@app.route("/", methods=["get", "post"])
def reply():
    text = request.form.get("Body")
    number = request.form.get("From")
    # print(number)
    number = number.replace("whatsapp:", "")
    number = number[3:]
    response = MessagingResponse()
    findNum = {"patientPhone": number}
    # data = users.find(findNum, {"_id": 0, "patientName": 1, "patientPhone": 1, "patientAddress": 1, "patientPincode": 1})
    data = users.find_one(findNum,
                          {"_id": 0, "patientName": 1, "patientPhone": 1, "patientAddress": 1, "patientPincode": 1})

    name = data.get("patientName")
    mobile = data.get("patientPhone")
    address = data.get("patientAddress")
    pincode = data.get("patientPincode")

    user = users.find_one(findNum)
    appointment = appointments.find_one({"number": mobile})
    day = appointment.get("day")
    timeSlot1 = appointment.get("timeSlot")
    # print(appointment["status"])
    # print(appointment)

    # print(user)
    # user = "true"
    # if bool(user) == False:
    if "hi" in text:
        response.message("Hey, Type 'book' to Proceed Further.")
    if "book" in text:
        response.message(
            f" Hi  ! You're required to undergo a Pre-Policy Health Check(PPHC) as a part of your policy purchase with ACKO Insurance.\nFor next steps, we will help you with your booking for the PPHC. Kindly confirm/update the below information we've received from ACKO, to plan and confirm your PPHC.\n \n Name: {name} \n Mobile Number: {mobile} \n Address: {address} \n Pincode: {pincode}\n\n\n ➡️What would you like to do? \n\n 1️⃣Update These Details. \n 2️⃣Keep These Details.\n 3️⃣Customer Support Number")
        if bool(appointment) == False:
            appointments.insert_one(
                {"number": mobile, "status": "main", "messages": []})
        else:
            appointments.update_one({"number": mobile}, {
                                    "$push": {"messages": {"text": text, "date": datetime.now()}}})

    elif appointment["status"] == "main":
        try:
            global option
            option = int(text)
            print("option" + option)
        except:
            print("exceptMain")
            # except:
            #response.message("Enter A Valid Response", option)
            # return str(response)
        if option == 1:
            response.message("Lets *Update* Your Details!")
            appointments.update_one({"number": number}, {
                                    "$set": {"status": "updating"}})
            response.message(
                "Which details would you like to *Change*? \n Reply with the number of your choice.(For example, if you would like to change your first name, reply with the number 1) \n 1️⃣ *Name* \n 2️⃣ *Mobile Number* \n 3️⃣ *Address* \n 4️⃣ *Pincode*")
        if option == 2:
            appointments.update_one({"number": number}, {
                                    "$set": {"status": "confirm"}})
            response.message(
                f"Thanks *{name}*! Your details have been saved 😀👍")
            response.message(
                "Your details for conducting the  Pre-Policy Medical Check required for your health insurance requirement with Acko has been updated. Would you like to proceed with the booking? \n Kindly enter '1' to proceed or '2' to remind you later.\n\n 1. Yes, proceed. \n 2. Remind me later")
        if option == 3:
            response.message(
                "Thanks for Choosing To Contact Us on +919448920370")

    elif appointment["status"] == "updating":
        try:
            option = int(text)
        except:
            print("exceptUpdating")
        if option == 1:
            response.message("Please reply with your name.")
            appointments.update_one({"number": number}, {
                                    "$set": {"status": "updatingName"}})
        if option == 2:
            response.message(
                "Please reply with your active mobile number for our team to reach you(intended test taker) at")
            appointments.update_one({"number": number}, {
                                    "$set": {"status": "updatingMob"}})
        if option == 3:
            response.message(
                "Update your *Full Address* here. \n\n (enter : house no/flat no., floor, number, street, area, landmark)")
            appointments.update_one({"number": number}, {
                                    "$set": {"status": "updatingAddress"}})
        if option == 4:
            response.message("Enter your location Pin-code to update:")
            appointments.update_one({"number": number}, {
                                    "$set": {"status": "updatingPincode"}})

    elif appointment["status"] == "updatingName":
        users.update_one(findNum, {"$set": {"patientName": text}})
        appointments.update_one({"number": number}, {
                                "$set": {"status": "updateagain"}})
        response.message(
            "👍🏻Got it! \n Would you like to change any other details? \n\n Type 'Yes' or 'No' \n 1️⃣ Yes. \n 2️⃣ No.")

    elif appointment["status"] == "updatingMob":
        users.update_one(findNum, {"$set": {"patientPhone": text}})
        appointments.update_one({"number": number}, {
                                "$set": {"status": "updateagain"}})
        response.message(
            "👍🏻Got it! \n Would you like to change any other details? \n\n Type 'Yes' or 'No' \n 1️⃣ Yes. \n 2️⃣ No.")

    elif appointment["status"] == "updatingAddress":
        users.update_one(findNum, {"$set": {"patientAddress": text}})
        appointments.update_one({"number": number}, {
                                "$set": {"status": "updateagain"}})
        response.message(
            "👍🏻Got it! \n Would you like to change any other details? \n\n Type 'Yes' or 'No' \n 1️⃣ Yes. \n 2️⃣ No.")

    elif appointment["status"] == "updatingPincode":
        users.update_one(findNum, {"$set": {"patientPincode": text}})
        appointments.update_one({"number": number}, {
                                "$set": {"status": "updateagain"}})
        response.message(
            "👍🏻Got it! \n Would you like to change any other details? \n\n Type 'Yes' or 'No' \n 1️⃣ Yes. \n 2️⃣ No.")

    elif appointment["status"] == "updateagain":
        if option == 1:
            response.message(
                "Which details would you like to *Change*? \n Reply with the number of your choice.(For example, if you would like to change your first name, reply with the number 1) \n 1️⃣. *Name* \n 2️⃣. *Mobile Number* \n 3️⃣. *Address* \n 4️⃣. *Pincode*")
            appointments.update_one({"number": number}, {
                                    "$set": {"status": "updating"}})
        if option == 2:
            response.message(
                f"Thanks *{name}*! Your details have been saved 😀👍")
            appointments.update_one({"number": number}, {
                                    "$set": {"status": "confirm"}})
            response.message(
                "Your details for conducting the  Pre-Policy Medical Check required for your health insurance requirement with Acko has been updated. Would you like to proceed with the booking? \n Kindly enter '1' to proceed or '2' to remind you later.\n\n 1. Yes, proceed. \n 2. Remind me later")
        else:
            response.message("Enter A Valid Response")

    elif appointment["status"] == "confirm":
        try:
            option = int(text)
        except:
            response.message("Enter A Valid Response")
            return str(response)
        if option == 1:
            response.message(
                "Kindly select a day that suits you for your next appointment.")

            response.message(
                "What day of the week will you prefer? \n Kindly enter '1' for Monday or '2' for Tuesday etc. \n1. Monday \n2. Tuesday \n3. Wednesday \n4. Thursday \n5. Friday \n6. Saturday \n7. Sunday")
            appointments.update_one({"number": number}, {
                                    "$set": {"status": "appointment"}})
        if option == 2:
            response.message("We will Remind You Later to book Appointment.")

    elif appointment["status"] == "appointment":
        try:
            option = int(text)
        except:
            response.message("Enter A Valid Response")
            return str(response)
        if 1 <= option <= 7:
            days = ["Monday", "Tuesday", "Wednesday",
                    "Thursday", "Friday", "Saturday", "Sunday"]
            selectedDay = days[option-1]
            appointments.update_one({"number": number}, {
                                    "$set": {"status": "timeSlot"}})
            appointments.update_one({"number": number}, {
                                    "$set": {"day": selectedDay}})
            response.message("Pick your slot timing preference \n You pick the slot for morning (7:00 a.m. - 12:00 p.m), afternoon (12:00 p.m. -  5:00 p.m) or evening (5:00 p.m. - 7:00 p.m) \n Kindly note: Fasting related tests are advised for morning \n 1️⃣ MORNING \n 2️⃣ AFTERNOON \n 3️⃣ EVENING")

    elif appointment["status"] == "timeSlot":
        try:
            option = int(text)
        except:
            response.message("Enter A Valid Response")
            return str(response)
        if 1 <= option <= 3:
            timeSlot = ["Morning", "Afternoon", "Evening"]
            selectedTimeSlot = timeSlot[option-1]
            appointments.update_one({"number": number}, {
                                    "$set": {"timeSlot": selectedTimeSlot}})
            response.message(
                f"Your Test Booking Plan: \n Great, *{name}*! Your booking has been captured for *{day}* *{selectedTimeSlot}*.")
            appointments.update_one({"number": number}, {
                                    "$set": {"status": "confirmAppointment"}})
            response.message(
                "Booking Summary \n To proceed, *Confirm* your test or choose *Update* to update details \n 1️⃣ Confirm \n 2️⃣ Update Appointment ")

    elif appointment["status"] == "confirmAppointment":
        try:
            option = int(text)
        except:
            response.message("Enter A Valid Response")
            return str(response)
        if option == 1:
            appointments.update_one({"number": number}, {
                                    "$set": {"status": "main"}})
            response.message(
                "Congratulations! Your booking is captured. Our operations team will confirm your booking in the next 60 minutes👍")
        if option == 2:
            appointments.update_one({"number": number}, {
                                    "$set": {"status": "appointment"}})
            response.message(
                "What day of the week will you prefer? \n Kindly enter '1' for Monday or '2' for Tuesday etc. \n1. Monday \n2. Tuesday \n3. Wednesday \n4. Thursday \n5. Friday \n6. Saturday \n7. Sunday")

    return str(response)


if __name__ == "__main__":
    app.run()
