from google.appengine.api.labs import taskqueue

class QueueHandler(object):

	@staticmethod
	def queue_fetch(location_key, countdown=15):

		taskqueue.add(url='/task/fetchlocation', params={'location_key': location_key}, countdown=countdown)

	@staticmethod
	def queue_notify(message, user_key_list, countdown=15):

		if not isinstance(user_key_list, list):
			user_key_list = [user_key_list]

		params = {
			  'message': message,
			  'users': user_key_list
			  }
		taskqueue.add(url='/cron/notify/dm', params=params, countdown=countdown)

	@staticmethod
	def queue_hourly_notify(location_key, countdown=15):

		taskqueue.add(url='/cron/notify/hourly', params={'location': location_key}, countdown=countdown)
