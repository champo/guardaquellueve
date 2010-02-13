import logging
import datetime

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

import util
import tweepy

from entities import Location, User


class RainNotification(webapp.RequestHandler):

	def _format_message(location):
		raise NotImplementedError()

	def _get_locations():
		raise NotImplementedError()

	def get(self):

		rainy_places = self._get_locations()
		twitter = tweepy.API(auth_handler=tweepy.BasicAuthHandler('guardaquellueve', 'panchito123'))
		now = datetime.datetime.utcnow()

		logging.debug([location.name for location in rainy_places])
		for rainy_place in rainy_places:
			users = User.all().filter('location =', rainy_place)
			message = self._format_message(rainy_place)

			for user in users:
				twitter.send_direct_message(screen_name=user.screen_name, text=message)

			rainy_place.last_broadcast_made = now

		db.put(rainy_places)


class HourlyNotification(RainNotification):

	def _format_message(self, location):

		if location.changed_prediction and (location.last_broadcaste_made is not Null or location.last_broadcast_made > location.next_rain_datetime):
			return "Sorry titan, sigue lloviendo en %s" % (location.name, )

		return "Va a llover en una horita o dos en %s" % (location.name, )

	def _get_locations(self):
		time_limit = datetime.datetime.utcnow() + datetime.timedelta(hours=3)

		return list(Location.all() \
				.filter('next_rain_datetime <', time_limit) \
				.filter('next_rain_datetime >', datetime.datetime.utcnow()))


class DailyNotification(RainNotification):

	def _format_message(self, location):

		day = ['domingo', 'lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado'][location.next_rain_datetime.weekday()]

		return u"Parece que el %s llueve en %s" % (day, location.name)

	def _get_locations(self):
		min_time = datetime.datetime.utcnow() + datetime.timedelta(days=1)

		return list(Location.all().filter('next_rain_datetime >', min_time))

def main():
	logging.getLogger().setLevel(logging.DEBUG)
	application = webapp.WSGIApplication([
		('/cron/notify/daily', DailyNotification),
		('/cron/notify/hourly', HourlyNotification)
		], debug=True)
	run_wsgi_app(application)

if __name__=="__main__":
	main()
