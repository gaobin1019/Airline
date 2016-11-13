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

from model import *

@app.route('/webhook', methods=['POST'])
def webhook():
    data = ""+AirInfo.query.filter(AirInfo.flightNumber=="522").first()
    print("data")

    print(getattr(data,"airline"))
    print(type(getattr(data,"airline")))
    res = {
        "speech":getattr(data,"airline"),
        "displayText": getattr(data,"airline"),
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
