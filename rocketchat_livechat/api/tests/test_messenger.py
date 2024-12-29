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
			"sender":{
				"id":"<PSID>"
			},
			"recipient":{
				"id":"<PAGE_ID>"
			},
			"timestamp":1458692752478,
			"message":{
				"mid":"mid.1457764197618:41d102a3e1ae206a38",
				"text":"hello, world!",
				"quick_reply": {
				"payload": "<DEVELOPER_DEFINED_PAYLOAD>"
				}
			}
		}
		headers = {'Content-Type': 'application/json'}
		request = Request('POST', url, headers=headers, data=json.dumps(payload))
		prepared_request = request.prepare()

		# Use a requests.Session to send the request
		session = Session()
		response = session.send(prepared_request)

		# Assert that the response status code is 200
		self.assertEqual(response.status_code, 200)