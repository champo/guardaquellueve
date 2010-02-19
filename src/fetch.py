import logging
import datetime

from google.appengine.ext import webapp, db
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api.labs import taskqueue

from queue import QueueHandler
from entities import Location, User
from weather.utils import get_next_rainy_day

class FetchForecast(webapp.RequestHandler):
	def get(self):
		places = list(Location.all(keys_only=True))
		for i in xrange(len(places)):
			QueueHandler.queue_fetch(places[i], 5*i)

def main():
	application = webapp.WSGIApplication([
		('/cron/fetch', FetchForecast)
		], debug=True)
	run_wsgi_app(application)

if __name__ == "__main__":
	main()
