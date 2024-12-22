import json
from requests import Request, Session
from frappe.tests.utils import FrappeTestCase

class TestRocketchatWebhook(FrappeTestCase):
	def test_rocketchat_webhook_trigger(self):
		# Sample payload from Whatsapp Cloud API
		payload = {
			"_id": "Tc5SyBZHovD4k8BXv",
			"label": "James",
			"createdAt": "2023-02-02T10:16:07.230Z",
			"lastMessageAt": "2023-02-02T10:22:14.087Z",
			"tags": [
				"self"
			],
			"visitor": {
				"_id": "63db8d4990fe6eda42ad429a",
				"token": "e36e352c742eee48860d576fcefb372afc44ebc95750fa1e3b646195f702341a",
				"name": "James",
				"username": "guest-3",
				"email": [
				{
					"address": "abc.xyz+local-on@rocket.chat"
				}
				],
				"phone": "+255769925950"
			},
			"agent": {
				"_id": "aXjjcPwq4Pcp7xftH",
				"username": "user1",
				"name": "User One",
				"email": "uaser1@mail.com"
			},
			"type": "LivechatSession",
			"messages": [
				{
				"u": {
					"_id": "63db8d4990fe6eda42ad429a",
					"username": "guest-3",
					"name": "James"
				},
				"_id": "2untSdndqBP7opGWw",
				"username": "guest-3",
				"msg": "Hi",
				"ts": "2023-02-02T10:16:09.615Z"
				},
				{
				"u": {
					"_id": "aXjjcPwq4Pcp7xftH",
					"username": "user1",
					"name": "User One"
				},
				"_id": "7xjkw8ZFitMSNGmeJ",
				"username": "user1",
				"msg": "How can I help you today?",
				"ts": "2023-02-02T10:21:05.391Z",
				"agentId": "aXjjcPwq4Pcp7xftH"
				},
				{
				"u": {
					"_id": "63db8d4990fe6eda42ad429a",
					"username": "guest-3",
					"name": "James"
				},
				"_id": "y7p77YFfkHJeg5gD9",
				"username": "guest-3",
				"msg": "don't worry,thank you",
				"ts": "2023-02-02T10:22:14.087Z"
				},
				{
				"u": {
					"_id": "aXjjcPwq4Pcp7xftH",
					"username": "user1",
					"name": "User One"
				},
				"_id": "ciAggDuN8ioqDrTby",
				"username": "user1",
				"msg": "Thank you for visiting. We did it again",
				"ts": "2023-02-02T10:23:11.437Z",
				"agentId": "aXjjcPwq4Pcp7xftH",
				"closingMessage": "true"
				}
			],
			"servedBy": {
				"_id": "aXjjcPwq4Pcp7xftH",
				"username": "user1",
				"ts": "2023-02-02T10:16:07.375Z"
			},
			"closedAt": "2023-02-02T10:23:11.344Z",
			"closedBy": {
				"_id": "aXjjcPwq4Pcp7xftH",
				"username": "user1"
			},
			"closer": "user"
		}

		# Create a requests.Request object
		url = 'http://frappe-ludovic/api/method/rocketchat_livechat.api.rocketchat.rocketchat_webhook'
		headers = {'Content-Type': 'application/json'}
		request = Request('POST', url, headers=headers, data=json.dumps(payload))
		prepared_request = request.prepare()

		# Use a requests.Session to send the request
		session = Session()
		response = session.send(prepared_request)

		# Assert that the response status code is 200
		self.assertEqual(response.status_code, 200)