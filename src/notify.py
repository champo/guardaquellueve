import logging

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

import tweepy

from entities import Location, User

class RainNotification(webapp.RequestHandler):

	def get(self):
		#TODO: Magic method that tells where it's gonna rain in the next hour or two

		rainy_places = Location.all()
		twitter = tweepy.API(auth_handler=tweepy.BasicAuthHandler('guardaquellueve', 'panchito123'))

		for rainy_place in rainy_places:
			users = User.all().filter('location =', rainy_place)
			for user in users:
				twitter.send_direct_message(screen_name=user.screen_name, \
						text="Guarda que llueve en una horita o dos")

def main():
	logging.getLogger().setLevel(logging.DEBUG)
	application = webapp.WSGIApplication([
		('/cron/notify', RainNotification)
		], debug=True)
	run_wsgi_app(application)

if __name__=="__main__":
	main()
