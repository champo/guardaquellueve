from google.appengine.api.labs import taskqueue

class QueueHandler(object):

	@staticmethod
	def queue_fetch(location_key, countdown=15):

		taskqueue.add(url='/cron/fetch', params={'location': location_key}, countdown=countdown)

	@staticmethod
	def queue_notify(message, user_key_list, countdown=15):

		if not isinstance(user_key_list, list):
			user_key_list = [user_key_list]

		params = {
			  'message': message,
			  'users': user_key_list
			  }
		taskqueue.add(url='/cron/dm', params=params, countdown=countdown)
