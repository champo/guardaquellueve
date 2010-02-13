from google.appengine.ext import db

class Location(db.Model):
	station = db.StringProperty(required=True)
	name = db.StringProperty(required=True)
	prediction = db.StringProperty()
	timezone = db.IntegerProperty(required=True, default=0)

class User(db.Model):
	screen_name = db.StringProperty(required=True)
	location = db.ReferenceProperty(Location)
