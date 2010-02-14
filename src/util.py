import sys
import logging

sys.path.insert(0, 'tweepy.zip')
import tweepy

from entities import Location, User
from weather.utils import *

STOP_KEYWORD = 'basta'
RESTART_KEYWORD = 'volve'

def login_twitter_bot():
	return tweepy.API(auth_handler=tweepy.BasicAuthHandler('guardaquellueve', 'panchito123'))

def send_location_dm(twitter, handle):
	twitter.send_direct_message(screen_name=handle, text="Cheee, no podemos darnos cuenta de donde estas. Mandanos un DM con tu ubicacion! Gracias.")
	logging.debug("Sent %s a DM" % (handle, ))

def send_success_dm(twitter, handle):
	text = "Ya te van a llegar los updates cuando llueva por tus pagos! Si no queres que te lleguen mas, manda un DM que diga '%s'." %(STOP_KEYWORD, )
	twitter.send_direct_message(screen_name=handle, text=text)
	logging.debug("Successfully found %s" % (handle, ))

def send_stop_dm(twitter, handle):
	twitter.send_direct_message(screen_name=handle, text="Ya no te van a llegar mas updates. Chau ortiva.")
	logging.debug("Stopped sending updates to %s" % (handle, ))

def follow_user_and_get(twitter, handle):
	if twitter.exists_friendship(user_a='guardaquellueve', user_b=handle):
		method = twitter.get_user
	else:
		method = twitter.create_friendship

	try:
		user_data = method(twitter, screen_name=handle)
	except tweepy.TweepError, e:
		logging.critical(e)
		user_data = None
		# We're screwed :D

	return user_data

def unfollow(twitter, handle):
	user = User.all().filter('screen_name =', handle).get()
	if user is None:
		logging.warning('User %s sent a stop DM but is not on the datastore' % (handle, ))
		return
	user.active = False
	user.put()

	send_stop_dm(twitter, handle)

def follow(twitter, handle):
	user_data = follow_user_and_get(twitter, handle)
	if user_data is None:
		return

	user = User.all().filter('screen_name =', handle).get()
	if user is None:
		user = User(screen_name=handle)
	else:
		user.active = True
		if user.location is not None:
			user.put()
			send_success_dm(twitter, handle)
			return

	relocate(twitter, user_data.location, user)
	user.put()

def refollow(twitter, handle):
	he_follows = twitter.exists_friendship(user_a=handle, user_b='guardaquellueve')
	if not he_follows:
		text = "Che @%s haceme follow o no te puedo mandar updates! Hace follow y manda un DM con '%s'" % (handle, RESTART_KEYWORD)
		twitter.update_status(status=text)
		logging.debug('User %s tried to restart but its not following me' % (handle, ))
		return

	follow(twitter, handle)


def relocate(twitter, location, user):
	location = find_location(location)
	if location is None:
		send_location_dm(twitter, user.screen_name)
		return

	user.location = location
	send_success_dm(twitter, user.screen_name)

def find_location(location):

	if location is None:
		return None

	location = location.strip()
	location_entity = Location.all().filter('name =', location).get()
	if location_entity is None:
		response = get_station_and_gmt(location)
		if response is None:
			return None

		station = response['station']
		timezone = response['gmt']
		location_entity = Location.all().filter('station =', station).get()

		if location_entity is None:
			location_entity = Location(name=location, station=station, timezone=timezone)
			location_entity.put()

	return location_entity

