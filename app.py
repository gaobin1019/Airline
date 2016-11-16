#!/usr/bin/env python

import urllib
import json
import os

from flask import Flask
from flask import request
from flask import make_response
from flask_sqlalchemy import SQLAlchemy

# Flask app should start in global layout
app = Flask(__name__)

#config
app.config.from_object(os.environ['APP_SETTINGS'])

#create a db object  I'll manually enter data into database for this project.
db = SQLAlchemy(app)

#don't know why * works but AirInfo not, todo .....
from model import *

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    print("request")
    print(json.dumps(req,indent=4))

    speech = processRequest(req)

    res = {
        "speech":speech,
        "displayText": speech,
        "source": "airline database"
    }
    res = json.dumps(res, indent=4)
    print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

#request as json object,return output as string,return error prompt if no action found.
#a lot of thing to factor and improve. todo
def processRequest(req):
    action = req.get("result").get("action")
    if action == "showInfoByFlightNumber":
        flightNum = req.get("result").get("parameters").get("flightNumber")

        try:
            data = AirInfo.query.filter(AirInfo.flightNumber == flightNum).first()
        except:
            db.session.rollback()
        airline = getattr(data,"airline")
        dc = getattr(data,"departureCity")
        s = getattr(data,"status")

        speech = "Flight Info for" + flightNum + ": " + airline + " Airline, " +\
                dc +" departure City, " +  " status " +s
        return speech
    elif action == "showFlightDepartTimeByAirline":
        airlineName = req.get("result").get("parameters").get("airlineName")
        cityName = req.get("result").get("parameters").get("cityName")

        rowList =[]
        try:
            rowList = AirInfo.query.filter(AirInfo.airline == airlineName).\
                                filter(AirInfo.departureCity==cityName).all()
        except:
            db.session.rollback()
        departTimeStr= ""
        for row in rowList:
            departTimeStr += getattr(row,"departureTime") + ","

        speech = "Airline "+airlineName+" to "+cityName+" is scheduled at: "+departTimeStr
        return speech
    elif action == "showDestinationsByCityAndAirline":
        airlineName = req.get("result").get("parameters").get("airlineName")
        cityName = req.get("result").get("parameters").get("fromCity")
        rowList=[]
        try:
            rowList = AirInfo.query.filter(AirInfo.airline == airlineName).\
                                filter(AirInfo.departureCity==cityName).all()
        except:
            db.session.rollback()
        arrivalCity=""
        for row in rowList:
            arrivalCity += getattr(row,"arrivalCity") + ","

        speech = "Airline "+airlineName+" from "+cityName+" has destination: "+arrivalCity
        return speech
    elif action == "showFlightsByArrivalTime":
        arrivalCity = req.get("result").get("parameters").get("cityName")
        landTime = req.get("result").get("parameters").get("landTime")
        allRows = AirInfo.query.all()
        beforeTimeFlight = []
        for row in allRows:
            if processTime(getattr(row,"arrivalTime")) < processTime(landTime) and \
                                        getattr(row,"arrivalCity") == arrivalCity:

                beforeTimeFlight.append(str(getattr(row,"flightNumber")))


        if not beforeTimeFlight:
            speech = "No flight will arrive in "+arrivalCity+" before "+landTime
        else:
            speech = "Flight number"+','.join(beforeTimeFlight) + " will arrive in "+arrivalCity+" before "+landTime
        return speech

    else:
        return "Action:" + action + " not found"

#input "12:00:00" output  as integer as minutes passed in a day
#input from database "4:20 PM"
def processTime(timeIn):
    if "M" in timeIn:
        tempList = timeIn.split(":")
        if tempList[1].split(" ")[1] == "AM":
            return int(tempList[0])*60 + int(tempList[1].split(" ")[0])
        else:
            return int(tempList[0])*60 + int(tempList[1].split(" ")[0]) + 12*60
    else:
        tempList = timeIn.split(":")
        return int(tempList[0])*60+int(tempList[1])






if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print "Starting app on port %d" % port

    app.run(debug=False, port=port, host='0.0.0.0')
