from google.appengine.ext import db

class Outcode(db.Model):
  outcode = db.StringProperty(required=True)
  lat_long = db.GeoPtProperty()
  
class Postcode(db.Model):
  postcode = db.StringProperty(required=True)
  lat_long = db.GeoPtProperty()

class GP(db.Model):
  name = db.StringProperty()
  address = db.StringProperty()
  postcode = db.StringProperty()
  lat_long = db.GeoPtProperty()
  
class TrainStation(db.Model):
  name = db.StringProperty()
  lat_long = db.GeoPtProperty()
  
class Supermarket(db.Model):
  name = db.StringProperty()
  address = db.StringProperty()
  postcode = db.StringProperty()
  lat_long = db.GeoPtProperty()

class School(db.Model):
  name = db.StringProperty()
  address = db.StringProperty()
  postcode = db.StringProperty()
  lat_long = db.GeoPtProperty()

  
