import frappe
import unittest
import json
from requests import Request, Session
from frappe.tests.utils import FrappeTestCase
from unittest.mock import patch
from rocketchat_livechat.api.whatsapp import whatsapp_webhook

class TestWhatsappWebhook(FrappeTestCase):
	def test_whatsapp_webhook_trigger(self):
		# Sample payload from Whatsapp Cloud API
		payload = {
			"object": "whatsapp_business_account",
			"entry": [{
				"id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
				"changes": [{
					"value": {
						"messages": [{
							"from": "+255769925950",
							"id": "wamid.ID",
							"timestamp": "TIMESTAMP",
							"text": {
								"body": "Hello, I need help with my order."
							},
							"type": "text"
						}]
					},
					"field": "messages"
				}]
			}]
		}

		# Create a requests.Request object
		url = 'http://frappe-ludovic/api/method/rocketchat_livechat.api.whatsapp.whatsapp_webhook'
		headers = {'Content-Type': 'application/json'}
		request = Request('POST', url, headers=headers, data=json.dumps(payload))
		prepared_request = request.prepare()

		# Use a requests.Session to send the request
		session = Session()
		response = session.send(prepared_request)

		# Assert that the response status code is 200
		self.assertEqual(response.status_code, 200)