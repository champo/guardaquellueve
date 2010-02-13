from google.appengine.ext import db

class User(db.Model):
	screen_name = db.StringProperty(required=True)
	location = db.ReferenceProperty(Location)

class Location(db.Model):
	station = db.StringProperty(required=True)
	name = db.StringProperty(required=True)
