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
    """
    data = AirInfo.query.filter(AirInfo.flightNumber=="522").first()
    print("data")

    print(getattr(data,"airline"))
    print(type(getattr(data,"airline")))
    """


    req = request.get_json(silent=True, force=True)
    print("request")
    print(json.dumps(req,indent=4))

    if req.get("result").get("action") != "showInfoByFlightNumber":
        return{}
    flightNum = req.get("result").get("parameters").get("flightNumber")

    data = AirInfo.query.filter(AirInfo.flightNumber == flightNum).first()
    airline = getattr(data,"airline")
    dc = getattr(data,"departureTime")
    s = getattr(data,"status")

    speech = "Flight Info for" + flightNum + " Airline " + airline
             + " departure City " + dc + " arrival time " + " status " +s

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


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print "Starting app on port %d" % port

    app.run(debug=False, port=port, host='0.0.0.0')
