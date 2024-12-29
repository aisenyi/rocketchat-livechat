from frappe.tests.utils import FrappeTestCase
import requests

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