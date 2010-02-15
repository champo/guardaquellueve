from google.appengine.ext import webapp, db

from entities import Location
from weather.utils import get_next_rainy_day

class FetchLocationForecast(webapp.RequestHandler):
	def post(self):
		place = Location.get(self.request.get('location_key'))
		forecast = get_next_rainy_day(place.station, place.timezone)
		if not forecast and place.next_rain_datetime:
			place.forecast = "It will not rain in the next week!"
			place.next_rain_datetime = None
			place.changed_prediction = True
		if forecast and forecast[0] != place.next_rain_datetime:
			logging.debug("Updating forecast of %s to %s"%(place.station, str(forecast)))
			place.forecast = forecast[1]
			place.next_rain_datetime = forecast[0]
			place.changed_prediction = True
		db.put(place)

def main():
	application = webapp.WSGIApplication([
		('/task/fetch_location', FetchLocationForecast)
		], debug=True)
	run_wsgi_app(application)

if __name__ == "__main__":
	main()
