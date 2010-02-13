from google.appengine.ext import db

class Location(db.Model):
	station = db.StringProperty(required=True)
	name = db.StringProperty(required=True)
	timezone = db.IntegerProperty(required=True, default=0)

	forecast = db.???()
	next_rain_datetime = db.????()
	last_broadcast_made = db.????()
	changed_prediction = db.BOOLIANO()


class User(db.Model):
	screen_name = db.StringProperty(required=True)
	location = db.ReferenceProperty(Location)
