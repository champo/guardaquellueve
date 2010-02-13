import logging
import email
import re

from google.appengine.ext import webapp
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
from google.appengine.ext.webapp.util import run_wsgi_app

import util
from entities import User, Location
from weather.utils import *
import tweepy

def send_location_dm(twitter, handle):
	twitter.send_direct_message(screen_name=handle, text="Cheee, no podemos darnos cuenta de donde estas. Mandanos un DM con tu ubicacion! Gracias.")
	logging.debug("Sent %s a DM" % (handle, ))

def send_success_dm(twitter, handle):
	twitter.send_direct_message(screen_name=handle, text="Ya te van a llegar los updates cuando llueva por tus pagos!")

def find_location(location):
	if location is None:
		return None

	location = location.strip()
	location_entity = Location.all().filter('name =', location).get()
	if location_entity is None:
		response = get_station_and_days(location)
		if response is None:
			return None

		station = response['station']
		location_entity = Location.all().filter('station =', station).get()

		if location_entity is None:
			location_entity = Location(name=location, station=station)
			location_entity.put()

	return location_entity


class TwitterMailHandler(InboundMailHandler):

	def receive(self, mail_message):
		sender = mail_message.sender
		body = mail_message.bodies()

		if sender.find('twitter-dm-bot') != -1:
			self.dm(body)
		elif sender.find('twitter-follow-bot') != -1:
			self.follow(body)
		else:
			logging.warning('Unknown email recieived.')
			logging.warning(list(body)[1][1].decode())

	def dm(self, bodies):
		text_body = [body.decode() for type, body in bodies if type == 'text/plain'][0]
		dm_body, sender = [val.strip() for val in text_body.split('\n')[0:2]]
		sender = sender.split(' ')[-1]

		twitter = tweepy.API(auth_handler=tweepy.BasicAuthHandler('guardaquellueve', 'panchito123'))
		location = find_location(dm_body)
		if location is None:
			send_location_dm(twitter, sender)
			return

		user = User.all().filter('screen_name =', sender).get()
		if user is None:
			logging.warning('WTF User %s sent a DM but the db dont know about him' % (sender, ))
			return

		user.location = location
		user.put()

		send_success_dm(twitter, sender)

	def follow(self, bodies):
		text_body = [body.decode() for type, body in bodies if type == 'text/plain'][0]
		name = re.search('twitter.com/([^ \n\r\t]+)', text_body).groups()[0]
		logging.debug(name)

		twitter = tweepy.API(auth_handler=tweepy.BasicAuthHandler('guardaquellueve', 'panchito123'))
		if twitter.exists_friendship(user_a='guardaquellueve', user_b=name):
			method = twitter.get_user
		else:
			method = twitter.create_friendship

		try:
			user_data = method(twitter, screen_name=name)
		except tweepy.TweepError, e:
			logging.critical(e)
			return
			# We're screwed :D

		logging.debug(user_data.location)
		location = find_location(user_data.location)
		if location is None:
			send_location_dm(twitter, name)
			return

		user = User.all().filter('screen_name =', name).get()
		if user is None:
			user = User(screen_name=name, location=location)
		else:
			user.location = location
		user.put()

		send_success_dm(twitter, name)

def main():
	logging.getLogger().setLevel(logging.DEBUG)
	application = webapp.WSGIApplication([('/_ah/mail/.+', TwitterMailHandler)], debug=True)
	run_wsgi_app(application)

if __name__ == "__main__":
	main()
