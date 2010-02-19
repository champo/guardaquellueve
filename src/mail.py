import logging
import email
import re

from google.appengine.ext import webapp
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
from google.appengine.ext.webapp.util import run_wsgi_app

from util import *
from entities import User

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
		sender = re.search('twitter.com/([^ \n\r\t]+)', text_body).groups()[0]

		text_lines = text_body.split('\n')
		dm_lines = []
		for line in text_lines:
			if line.find(sender) == -1:
				dm_lines.append(line)
			else:
				break

		dm_body = ''.join(dm_lines).strip() \
				.replace('\n', ' ') \
				.replace('\t', ' ') \
				.replace('\r', ' ')

		twitter = login_twitter_bot()
		logging.debug(dm_body)

		if dm_body == STOP_KEYWORD:
			unfollow(twitter, sender)
		elif dm_body == RESTART_KEYWORD:
			refollow(twitter, sender)
		elif dm_body == HELP_KEYWORD:
			send_help_dm(twitter, sender)
		elif dm_body == WHERE_KEYWORD:
			user = User.all().filter('screen_name =', sender).get()
			if user is None:
				logging.warning('An unknown user sent a DM (%s)' % (sender, ))
			else:
				send_where_dm(twitter, user)
		elif dm_body == ABOUT_KEYWORD:
			send_about_dm(twitter, sender)
		elif dm_body == FORECAST_KEYWORD:
			send_forecast_dm(twitter, sender)
		else:
			user = User.all().filter('screen_name =', sender).get()
			if user is None:
				logging.warning('An unknown user sent a DM (%s)' % (sender, ))
			else:
				relocate(twitter, dm_body, user)
				user.put()

	def follow(self, bodies):
		text_body = [body.decode() for type, body in bodies if type == 'text/plain'][0]
		name = re.search('twitter.com/([^ \n\r\t]+)', text_body).groups()[0]

		follow(login_twitter_bot(), name)

def main():
	logging.getLogger().setLevel(logging.DEBUG)
	application = webapp.WSGIApplication([('/_ah/mail/.+', TwitterMailHandler)], debug=True)
	run_wsgi_app(application)

if __name__ == "__main__":
	main()
