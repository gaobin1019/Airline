from app import db
#table schema for airplain infomations
class AirInfo(db.Model):
    flightNumber = db.Column(db.Integer,primary_key=True)
    airline = db.Column(db.String(80),unique=False)
    departureCity = db.Column(db.String(120),unique=False)
    departureTime = db.Column(db.String(120),unique=False)
    arrivalCity = db.Column(db.String(120),unique=False)
    arrivalTime = db.Column(db.String(120),unique=False)
    status = db.Column(db.String(120),unique=False)

    def __init__(self,flightNumber,airline,departureCity,departureTime,arrivalCity,arrivalTime,status):
        self.flightNumber = flightNumber
        self.airline = airline
        self.departureCity = departureCity
        self.departureTime = departureTime
        self.arrivalCity = arrivalCity
        self.arrivalTime = arrivalTime
        self.status = status

    #print "My name is %s and weight is %d kg!" % ('Zara', 21)
    def __repr__(self):
        return '<flightNumber %d,airline %s>' % (self.username,self.airline)
