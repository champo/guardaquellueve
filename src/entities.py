from google.appengine.ext import db

class Location(db.Model):
	station = db.StringProperty(required=True)
	name = db.StringProperty(required=True)
	timezone = db.IntegerProperty(required=True, default=0)

	forecast = db.StringProperty()
	next_rain_datetime = db.DateTimeProperty()
	last_broadcast_rain = db.BooleanProperty(default=False)
	changed_prediction = db.BooleanProperty(default=False)


class User(db.Model):
	screen_name = db.StringProperty(required=True)
	location = db.ReferenceProperty(Location)
	active = db.BooleanProperty(default=True)
