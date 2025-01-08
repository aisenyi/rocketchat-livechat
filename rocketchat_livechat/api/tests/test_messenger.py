from frappe.tests.utils import FrappeTestCase
import requests
from requests import Request, Session
import json

class TestFacebookWebhook(FrappeTestCase):
	def test_messenger_webhook_verification(self):
		url = 'http://frappe-ludovic/api/method/rocketchat_livechat.api.messenger.messenger_webhook'
		params = {
			'hub.challenge': 'CHALLENGE_TOKEN',
			'hub.mode': 'subscribe',
			'hub.verify_token': 'VERIFY_TOKEN'
		}

		# Send GET request with parameters
		response = requests.get(url, params=params)

		# Assert that the response text is the challenge token
		self.assertEqual(response.text, 'CHALLENGE_TOKEN')

	def test_messenger_webhook(self):
		url = 'http://frappe-ludovic/api/method/rocketchat_livechat.api.messenger.messenger_webhook'
		payload = {
			'object': 'page', 
			'entry': [{
				'time': 1735507605534, 
	 			'id': '1701202886814226', 
				'messaging': [{
					'sender': {'id': '9092096187479591'}, 
					'recipient': {'id': '1701202886814226'}, 
					'timestamp': 1735507604307, 
					'message': {
						'mid': 'm_WqcpYUB_-JwEAv3wNgRyfQVKSY3mgT5RNHvPH8ogyBsu8-s9vWron73cgni4wt0lS7PU76gMN7ezjtYf9xuWpA', 
						'text': 'Just a test'
					}
				}]
			}]
		}
		headers = {'Content-Type': 'application/json'}
		request = Request('POST', url, headers=headers, data=json.dumps(payload))
		prepared_request = request.prepare()

		# Use a requests.Session to send the request
		session = Session()
		response = session.send(prepared_request)

		# Assert that the response status code is 200
		self.assertEqual(response.status_code, 200)