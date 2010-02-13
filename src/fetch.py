import logging
import datetime

from google.appengine.ext import webapp, db
from google.appengine.ext.webapp.util import run_wsgi_app

from entities import Location, User
from weather.utils import get_next_rainy_day

class FetchForecast(webapp.RequestHandler):
	def get(self):
		places = Location.all()

		for place in places:
			forecast = get_next_rainy_day(place.station, place.timezone)
			if not forecast:
				place.prediction = "It will not rain in the next week!"
			else:
				if forecast[0] != place.forecast:
					place.forecast = forecast[1]
					place.next_rain_datetime = forecast[0]
					place.changed_prediction = True

		db.put(places)

def main():
	application = webapp.WSGIApplication([
		('/cron/fetch', FetchForecast)
		], debug=True)
	run_wsgi_application(application)

if __name__ == "__main__":
	main()