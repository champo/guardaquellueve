import logging
import datetime

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

from util import *
import tweepy

from entities import Location, User


class RainNotification(webapp.RequestHandler):

	def _format_message(location):
		raise NotImplementedError()

	def _get_locations(locations):
		raise NotImplementedError()

	def get(self):
		all_places = list(Location.all())
		rainy_places = self._get_locations(all_places)
		twitter = login_twitter_bot()

		logging.debug("The rainy places are: "+str([location.name for location in rainy_places]))
		for place in all_places:
			if place in rainy_places:
				users = User.all().filter('location =', place).filter('active =', True)
				logging.debug("Sending messages to these users: "+str([u.screen_name for u in users]))
				message = self._format_message(place)
				logging.debug("The message being sent is: "+message)
				for user in users:
					twitter.send_direct_message(screen_name=user.screen_name, text=message)
			else:
				place.last_broadcast_rain = False

		db.put(all_places)


class HourlyNotification(RainNotification):
	def _format_message(self, location):
		if location.last_broadcast_rain:
			return "Sigue lloviendo en %s!" % (location.name, )
		else:
			hours = (location.next_rain_datetime - datetime.datetime.utcnow()).seconds/3600
			location.last_broadcast_rain = True
			return "Va a llover en menos de %d horas en %s" % (hours, location.name, )

	def _get_locations(self, locations):
		max_time = datetime.datetime.utcnow() + datetime.timedelta(hours=6, minutes=-5)
		min_time = datetime.datetime.utcnow() - datetime.timedelta(hours=6, minutes=-5)

		return [ l for l in locations if l.next_rain_datetime
			and l.next_rain_datetime < max_time
			and l.next_rain_datetime > min_time]


class DailyNotification(RainNotification):

	def _format_message(self, location):
		day = ['domingo', 'lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado'][location.next_rain_datetime.weekday()]

		place.last_broadcast_rain = False
		return u"Pronosticado lluvia para el %s en tu ciudad, %s." % (day, location.name)

	def _get_locations(self, locations):
		min_time = datetime.datetime.utcnow() + datetime.timedelta(hours=22)
		return [l for l in locations if l.next_rain_datetime
			and l.next_rain_datetime > min_time]

def main():
	logging.getLogger().setLevel(logging.DEBUG)
	application = webapp.WSGIApplication([
		('/cron/notify/daily', DailyNotification),
		('/cron/notify/hourly', HourlyNotification)
		], debug=True)
	run_wsgi_app(application)

if __name__=="__main__":
	main()
