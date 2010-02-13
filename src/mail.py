import logging
import email
import re

from google.appengine.ext import webapp
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
from google.appengine.ext.webapp.util import run_wsgi_app

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

	def dm(self, bodies):
		pass

	def follow(self, bodies):
		text_body = [body.decode() for type, body in bodies if type == 'text/plain'][0]
		match = re.match(text_body, 'twitter.com/([^ ]+)').groups()[0]

		# TODO: Record this user is following us & follow him back



def main():
	logging.getLogger().setLevel(logging.DEBUG)
	application = webapp.WSGIApplication([('/_ah/mail/.+', TwitterMailHandler)], debug=True)
	run_wsgi_app(application)

if __name__ == "__main__":
	main()
