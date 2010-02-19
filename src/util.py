import sys
import logging

sys.path.insert(0, 'tweepy.zip')
import tweepy

from entities import Location, User
from weather.utils import *
import credentials

STOP_KEYWORD = 'basta'
RESTART_KEYWORD = 'volve'
WHERE_KEYWORD = 'donde'
HELP_KEYWORD = 'help'
ABOUT_KEYWORD = 'about'
FORECAST_KEYWORD = 'pronostico'

def login_twitter_bot():
	return tweepy.API(auth_handler=tweepy.BasicAuthHandler(credentials.USERNAME, credentials.PASSWORD))

def send_location_dm(twitter, handle):
	twitter.send_direct_message(screen_name=handle, text="Cheee, no podemos darnos cuenta de donde estas. Mandanos un DM con tu ubicacion! Gracias.")
	logging.debug("Sent %s a DM" % (handle, ))

def send_success_dm(twitter, handle):
	location = None
	try:
		location = User.all().filter('screen_name =', handle).get().location
	except:
		logging.error("Error getting %s's data."%(handle, ))
		return
	text = "Te avisaremos cuando llueva por tus pagos, en %s! Cancela el servicio mandando '%s'." %(location.name, STOP_KEYWORD)
	twitter.send_direct_message(screen_name=handle, text=text)
	logging.debug("Successfully found %s" % (handle, ))

def send_stop_dm(twitter, handle):
	twitter.send_direct_message(screen_name=handle, text="Ya no te van a llegar mas updates. Chau ortiva.")
	logging.debug("Stopped sending updates to %s" % (handle, ))

def send_help_dm(twitter, handle):
	commands = ', '.join([
		STOP_KEYWORD,
		RESTART_KEYWORD,
		WHERE_KEYWORD,
		HELP_KEYWORD,
		ABOUT_KEYWORD,
		FORECAST_KEEYWORD])

	text = "Los comandos son: %s" % (commands, )
	twitter.send_direct_message(screen_name=handle, text=text)
	logging.debug("Sending help to %s" % (handle, ))

def send_about_dm(twitter, handle):
	twitter.send_direct_message(screen_name=handle, text='Te aviso cuando va a llover donde estes. Mis creadores son @eordano y @elchampo.')
	logging.debug("Sending about to %s" % (handle, ))

def send_where_dm(twitter, user):
	if user.location is None:
		text = 'Disculpa, todavia no sabemos donde estas. Mandanos un DM que diga donde estas!'
	else:
		text = 'Estas en %s' % (user.location.name, )

	twitter.send_direct_message(screen_name=user.screen_name, text=text)
	logging.debug("Sending %s a location DM" % (user.screen_name, ))

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
		text = "Che @%s seguime o no te puedo mandar updates! Una vez que estes siguiendome, mandame un DM con '%s'" % (handle, RESTART_KEYWORD)
		try:
			last_status = twitter.user_timeline(screen_name=handle)[0].id
		except:
			last_status = None

		twitter.update_status(status=text, in_reply_to_status_id=last_status)
		logging.debug('User %s tried to restart but it\'s not following me' % (handle, ))
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

	response = get_station_and_gmt(location)
	if response is None:
		return None

	station = response['station']
	timezone = response['gmt']
	name = response['name']
	location_entity = Location.all().filter('station =', station).get()

	if location_entity is None:
		location_entity = Location(name=name, station=station, timezone=timezone)
		location_entity.put()

	return location_entity

def send_forecast_dm(twitter, handle):
	location = None
	try:
		location = User.all().filter('screen_name =', handle).get().location
	except:
		logging.error('User or location not found!')
		return
	date = location.next_rain_datetime + datetime.timedelta(hours=location.timezone)
	twitter.send_direct_message(screen_name=handle, text='Pronosticado lluvia para el '+str(date.day)+' a las '+str(date.hour))
	logging.debug('User %s asked for forecast. Sent.'%(handle, ))
