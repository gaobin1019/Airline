#!/usr/bin/env python

import urllib
import json
import os
import datetime

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
        departureCity = getattr(data,"departureCity")
        departureTime = getattr(data,"departureTime")
        arrivalCity = getattr(data,"arrivalCity")
        arrivalTime = getattr(data,"arrivalTime")
        status = getattr(data,"status")

        speech = airline + " " + flightNum + " from " + departureCity + " will depart at " + \
                departureTime + ", will arrive " + arrivalCity + " at " + arrivalTime + \
                ", status " + status + "."
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
    #arrive between
    elif action == "showFlightsLandingBetweenTimes":
        arrivalCity = req.get("result").get("parameters").get("cityName")
        startTime = req.get("result").get("parameters").get("startTime")
        endTime = req.get("result").get("parameters").get("endTime")
        allRows = AirInfo.query.all()
        betweenTimeFlight = []
        for row in allRows:
            if processTime(getattr(row,"arrivalTime")) < processTime(endTime) and \
                           processTime(getattr(row,"arrivalTime")) > processTime(startTime) and \
                           getattr(row,"arrivalCity") == arrivalCity:

                betweenTimeFlight.append(str(getattr(row,"flightNumber")))

        if not betweenTimeFlight:
            speech = "No flight will arrive in "+arrivalCity+" between "+startTime+" and "+endTime
        else:
            speech = "Flight number"+','.join(betweenTimeFlight) + \
                    " will arrive in "+arrivalCity+" between "+startTime+" and "+endTime
        return speech
    elif action == "showFlightDepartTimeByCity":
        departCityName = req.get("result").get("parameters").get("cityName")
        rowList =[]
        try:
            rowList = AirInfo.query.filter(AirInfo.departureCity==departCityName).all()
        except:
            db.session.rollback()
        flightNumberStr= ""
        for row in rowList:
            flightNumberStr += str(getattr(row,"flightNumber")) + ","

        speech = "flightNumber "+flightNumberStr+" will depart from "+departCityName
        return speech
    #depart after
    elif action == "showFlightsByDepartureTime":
        departlCity = req.get("result").get("parameters").get("cityName")
        departTime = req.get("result").get("parameters").get("departTime")
        allRows = AirInfo.query.all()
        afterTimeFlight = []
        for row in allRows:
            if processTime(getattr(row,"departureTime")) > processTime(departTime) and \
                                        getattr(row,"departureCity") == departlCity:

                afterTimeFlight.append(str(getattr(row,"flightNumber")))

        if not afterTimeFlight:
            speech = "No flight will depart from "+departlCity+" after "+departTime
        else:
            speech = "Flight number"+','.join(afterTimeFlight) + \
                    " will depart from "+departlCity+" after "+departTime
        return speech
    #depart between
    elif action == "showFlightsBetweenTimes":
        departCity = req.get("result").get("parameters").get("cityName")
        startTime = req.get("result").get("parameters").get("startTime")
        endTime = req.get("result").get("parameters").get("endTime")
        allRows = AirInfo.query.all()
        betweenTimeFlight = []
        for row in allRows:
            if processTime(getattr(row,"departureTime")) < processTime(endTime) and \
                           processTime(getattr(row,"departureTime")) > processTime(startTime) and \
                           getattr(row,"departureCity") == departCity:

                betweenTimeFlight.append(str(getattr(row,"flightNumber")))

        if not betweenTimeFlight:
            speech = "No flight will arrive in "+departCity+" between "+startTime+" and "+endTime
        else:
            speech = "Flight number"+','.join(betweenTimeFlight) + \
                    " will depart from "+departCity+" between "+startTime+" and "+endTime
        return speech
    elif action == "showCitiesWithFlights":
        allRows = AirInfo.query.all()
        allCityStr = ""
        for row in allRows:
            if getattr(row,"departureCity") not in allCityStr:
                allCityStr += getattr(row,"departureCity")+","
        speech = "You can depart from "+allCityStr
        return speech
    elif action == "showFlightsByCity":
        departCity = req.get("result").get("parameters").get("cityName")
        rowList=[]
        try:
            rowList = AirInfo.query.filter(AirInfo.departureCity == departCity).all()
        except:
            db.session.rollback()
        arrivalCity=""
        for row in rowList:
            if getattr(row,"arrivalCity") not in arrivalCity:
                arrivalCity += getattr(row,"arrivalCity") + ","

        speech = departCity+" can fly to "+arrivalCity
        return speech
    elif action == "showFlightsByCityAndAirline":
        departCity = req.get("result").get("parameters").get("cityName")
        airlineName = req.get("result").get("parameters").get("airlineName")
        rowList=[]
        try:
            rowList = AirInfo.query.filter(AirInfo.departureCity == departCity) \
                                    .filter(AirInfo.airline == airlineName).all()
        except:
            db.session.rollback()
        flightNumberStr=""
        for row in rowList:
            flightNumberStr += str(getattr(row,"flightNumber")) + ","

        if flightNumberStr == "":
            speech = "No flight depart from "+departCity+" on "+airlineName
        else:
            speech = flightNumberStr+" depart from "+departCity+" on "+airlineName
        return speech
    elif action == "showFlightDepartTime":
        flightNumber = req.get("result").get("parameters").get("flightNumber")
        rowList=[]
        try:
            rowList = AirInfo.query.filter(AirInfo.flightNumber == int(flightNumber)).all()
        except:
            db.session.rollback()

        departTime = ""
        if rowList:
            departTime = getattr(rowList[0],"departureTime")
        speech = departTime
        return speech

    elif action == "showFlightLandTime":
        flightNumber = req.get("result").get("parameters").get("flightNumber")
        rowList=[]
        try:
            rowList = AirInfo.query.filter(AirInfo.flightNumber == int(flightNumber)).all()
        except:
            db.session.rollback()

        landTime = ""
        if rowList:
            landTime = getattr(rowList[0],"arrivalTime")
        speech = landTime
        return speech
    elif action == "showFlightsByAirline":
        airlineName = req.get("result").get("parameters").get("airlineName")
        rowList=[]
        try:
            rowList = AirInfo.query.filter(AirInfo.airline == airlineName).all()
        except:
            db.session.rollback()

        flightNumber = ""
        for row in rowList:
            flightNumber += str(getattr(row,"flightNumber")) +","
        speech = "Flight Number: "+flightNumber
        return speech
    elif action == "showFlightsByStatus":
        statusName = req.get("result").get("parameters").get("statusName")
        statusName = statusName.title()
        rowList=[]
        try:
            rowList = AirInfo.query.filter(AirInfo.status == statusName).all()
        except:
            db.session.rollback()

        flightNumber = ""
        for row in rowList:
            flightNumber += str(getattr(row,"flightNumber")) +","
        speech = "Flight Number: "+flightNumber+" are "+statusName
        return speech
    elif action == "showStatusByAirline":
        airlineName = req.get("result").get("parameters").get("airlineName")
        rowList=[]
        try:
            rowList = AirInfo.query.filter(AirInfo.airline == airlineName).all()
        except:
            db.session.rollback()

        status = []
        flightNumber = []
        for row in rowList:
            flightNumber.append(str(getattr(row,"flightNumber")))
            status.append(getattr(row,"status"))
        speech = ""
        for i in range(len(status)):
            speech += "Flight number "+flightNumber[i]+" "+status[i]+"."
        return speech
    #next flight between city
    elif action == "showNextFlightBetweenCities":
        fromCity = req.get("result").get("parameters").get("fromCity")
        toCity = req.get("result").get("parameters").get("toCity")
        rowList=[]
        try:
            rowList = AirInfo.query.filter(AirInfo.departureCity == fromCity) \
                                        .filter(AirInfo.arrivalCity == toCity).all()
        except:
            db.session.rollback()
        minimum = 99999
        nextRow = {}
        for row in rowList:
            if processTime(getattr(row,"departureTime")) < minimum:
                minimum = processTime(getattr(row,"departureTime"))
                nextRow = row
            else:
                continue
        nextFlight = str(getattr(nextRow,"flightNumber"))

        speech = "Next flight from "+fromCity+" to "+toCity+" is "+nextFlight+"."
        return speech
    #when does next flight arrive at $city
    elif action == "showNextFlightArrivalTime":
        cityName = req.get("result").get("parameters").get("cityName")
        rowList=[]
        try:
            rowList = AirInfo.query.filter(AirInfo.arrivalCity == cityName).all()
        except:
            db.session.rollback()
        minimum = 99999
        nextRow = {}
        for row in rowList:
            if processTime(getattr(row,"arrivalTime")) < minimum:
                minimum = processTime(getattr(row,"arrivalTime"))
                nextRow = row
            else:
                continue
        nextArrivalTime = getattr(nextRow,"arrivalTime")

        speech = "Next arrival in "+cityName+" will be "+nextArrivalTime+"."
        return speech
    elif action == "countFlightsLandingByAirline":
        airlineName = req.get("result").get("parameters").get("airlineName")
        rowList=[]
        try:
            rowList = AirInfo.query.filter(AirInfo.airline == airlineName).all()
        except:
            db.session.rollback()

        speech = airlineName+" operates "+str(len(rowList))+" flights."
        return speech
    elif action == "countFlightsLandingByCity":
        cities = req.get("result").get("parameters").get("cities")
        rowList=[]
        try:
            rowList = AirInfo.query.filter(AirInfo.arrivalCity == cities).all()
        except:
            db.session.rollback()

        speech = str(len(rowList))+" flights are landing in "+cities+"."
        return speech
    #next arrive flight between city
    elif action == "showFlightsBetweenCity":
        timeNow = datetime.datetime.strftime(datetime.datetime.now(), '%H:%M:%S')
        fromCity = req.get("result").get("parameters").get("fromCity")
        toCity = req.get("result").get("parameters").get("toCity")
        rowList=[]
        try:
            rowList = AirInfo.query.filter(AirInfo.departureCity == fromCity) \
                                        .filter(AirInfo.arrivalCity == toCity).all()
        except:
            db.session.rollback()
        minimum = 99999
        nextRow = {}
        for row in rowList:
            if processTime(getattr(row,"arrivalTime"))-processTime(timeNow) < minimum:
                minimum = processTime(getattr(row,"arrivalTime"))-processTime(timeNow)
                nextRow = row
            else:
                continue
        nextFlight = str(getattr(nextRow,"flightNumber"))

        speech = "Next flight arriving "+toCity+" from "+fromCity+" is "+nextFlight+"."
        return speech
    #next arrive flight between city before $time
    elif action == "showFlightArriveByTimeCity":
        time = req.get("result").get("parameters").get("time")
        fromCity = req.get("result").get("parameters").get("fromCity")
        toCity = req.get("result").get("parameters").get("toCity")
        rowList=[]
        try:
            rowList = AirInfo.query.filter(AirInfo.departureCity == fromCity) \
                                        .filter(AirInfo.arrivalCity == toCity).all()
        except:
            db.session.rollback()
        flightNumber = ""
        for row in rowList:
            if processTime(getattr(row,"arrivalTime")) > processTime(time):
                flightNumber += str(getattr(row,"flightNumber")) + ","
            else:
                continue
        if flightNumber != "":
            speech = "Flight "+flightNumber+"will arrive "+toCity+" from "+fromCity+" before "+ \
                    time+"."
        else:
            speech = "No flight will arrive "+toCity+" from "+fromCity+" before "+ \
                    time+"."

        return speech
    #Which flights have arrived in Atlanta?
    elif action == "showArrivedByCity":
        cityName = req.get("result").get("parameters").get("cityName")
        rowList=[]
        try:
            rowList = AirInfo.query.filter(AirInfo.arrivalCity == cityName) \
                                .filter(AirInfo.status == "Landed").all()
        except:
            db.session.rollback()

        flightNumber = ""
        for row in rowList:
            flightNumber += (str(getattr(row,"flightNumber")))

        if flightNumber != "":
            speech = flightNumber+" has arrived in "+cityName
        else:
            speech = "No flight has arrived in "+cityName+"yet"
        return speech
    #Has flight 679 arrived?
    elif action == "showArrivedByFlight":
        flightNumber = req.get("result").get("parameters").get("flightNumber")
        rowList=[]
        try:
            rowList = AirInfo.query.filter(AirInfo.flightNumber == int(flightNumber)) \
                                    .filter(AirInfo.status == "Landed").all()
        except:
            db.session.rollback()

        if not rowList:
            speech = "Flight "+flightNumber+" has not arrived yet."
        else:
            speech = "Yes, it arrived."
        return speech

    #What flights are delayed between Portland and New York?
    elif action == "showDelayedBetween":
        cityOne = req.get("result").get("parameters").get("cityOne")
        cityTwo = req.get("result").get("parameters").get("cityTwo")

        rowList=[]
        try:
            listOne= AirInfo.query.filter(AirInfo.departureCity == cityOne) \
                                    .filter(AirInfo.arrivalCity == cityTwo) \
                                    .filter(AirInfo.status.contains("Delayed")).all()
            listTwo = AirInfo.query.filter(AirInfo.departureCity == cityTwo) \
                                    .filter(AirInfo.arrivalCity == cityOne) \
                                    .filter(AirInfo.status.contains("Delayed")).all()
            rowList = listOne+listTwo
        except:
            db.session.rollback()

        flightNumber = ""
        for row in rowList:
            flightNumber += (str(getattr(row,"flightNumber")))

        if not rowList:
            speech = "No flight is delayed between "+cityOne+" and "+cityTwo+"."
        else:
            speech = "Flight "+flightNumber+"is delayed between "+cityOne+" and "+cityTwo+"."
        return speech

    #Is flight 679 delayed?
    elif action == "showDelayedByFlight":
        flightNumber = req.get("result").get("parameters").get("flightNumber")
        rowList=[]
        try:
            rowList = AirInfo.query.filter(AirInfo.flightNumber == int(flightNumber)) \
                                    .filter(AirInfo.status.contains("Delayed")).all()
        except:
            db.session.rollback()

        if not rowList:
            speech = "Flight "+flightNumber+" it not delayed."
        else:
            speech = "Yes, it delayed,"+getattr(rowList[0],"status")+"."
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
        else:#it's ugly, toto...
            if tempList[0] == "12":
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
