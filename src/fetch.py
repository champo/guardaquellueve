import logging
import datetime

from google.appengine.ext import webapp, db
from google.appengine.ext.webapp.util import run_wsgi_app

from entities import Location, User
from weather.utils import get_next_rainy_day

class FetchForecast(webapp.RequestHandler):
	def get(self):
		places = list(Location.all())

		for place in places:
			forecast = get_next_rainy_day(place.station, place.timezone)
			if not forecast and place.next_rain_datetime:
				place.forecast = "It will not rain in the next week!"
				place.next_rain_datetime = None
				place.changed_prediction = True
			if forecast and forecast[1] != place.forecast:
				logging.debug("Updating forecast of %s to %s"%(place.station, str(forecast)))
				place.forecast = forecast[1]
				place.next_rain_datetime = forecast[0]
				place.changed_prediction = True

		db.put(places)

def main():
	application = webapp.WSGIApplication([
		('/cron/fetch', FetchForecast)
		], debug=True)
	run_wsgi_app(application)

if __name__ == "__main__":
	main()