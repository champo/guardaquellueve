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
		all_places = list(Location.all())
		rainy_places = self._get_locations(all_places)
		twitter = tweepy.API(auth_handler=tweepy.BasicAuthHandler('guardaquellueve', 'panchito123'))
		now = datetime.datetime.utcnow()

		logging.debug([location.name for location in rainy_places])
		for places in all_places:
			if place in rainy_places:
				users = User.all().filter('location =', place)
				message = self._format_message(place)
				for user in users:
					twitter.send_direct_message(screen_name=user.screen_name, text=message)
				place.last_broadcast_rain = True
			else:
				place.last_broadcast_rain = False

		db.put(places)


class HourlyNotification(RainNotification):
	def _format_message(self, location):
		if location.last_broadcast_rain:
			return "Sigue lloviendo en %s!" % (location.name, )
		else:
			return "Va a llover en menos de tres horas en %s" % (location.name, )

	def _get_locations(self, location_list):
		max_time = datetime.datetime.utcnow() + datetime.timedelta(hours=3, minutes=5)
		min_time = datetime.datetime.utcnow() - datetime.timedelta(hours=3, minutes=5)

		return [ l for l in location_list
			if l.next_rain_datetime < max_time
			and l.next_rain_datetime > min_time]


class DailyNotification(RainNotification):

	def _format_message(self, location):

		day = ['domingo', 'lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado'][location.next_rain_datetime.weekday()]

		return u"Está pronosticado lluvia para el día %s en tu ciudad, %s." % (day, location.name)

	def _get_locations(self):
		min_time = datetime.datetime.utcnow() + datetime.timedelta(hours=22)

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
