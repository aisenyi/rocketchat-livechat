import json
from requests import Request, Session
from frappe.tests.utils import FrappeTestCase

class TestRocketchatWebhook(FrappeTestCase):
	def test_rocketchat_whatsapp_webhook_trigger(self):
		#Sample payload from Whatsapp Cloud API
		payload = {
			"_id": "Tc5SyBZHovD4k8BXv",
			"label": "James",
			"createdAt": "2023-02-02T10:16:07.230Z",
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
				}
			],
			"servedBy": {
				"_id": "aXjjcPwq4Pcp7xftH",
				"username": "user1",
				"ts": "2023-02-02T10:16:07.375Z"
			}
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

	def test_rocketchat_messenger_webhook_trigger(self):
		# Sample payload from Whatsapp Cloud API
		payload = {
			"_id": "Aoi6cRtANnngPgKPg",
			"label": "James",
			"createdAt": "2023-02-02T10:16:07.230Z",
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
				"msg": "Just another test?",
				"ts": "2023-02-02T10:21:05.391Z",
				"agentId": "aXjjcPwq4Pcp7xftH"
				}
			],
			"servedBy": {
				"_id": "aXjjcPwq4Pcp7xftH",
				"username": "user1",
				"ts": "2023-02-02T10:16:07.375Z"
			}
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

	def test_rocketchat_room_close(self):
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

	def test_rocketchat_whatsapp_media_webhook(self):
		payload = {
			"_id": "6KSaaKJyAHeo5ePKw",
			"label": "255769925950",
			"createdAt": "2025-01-18T17:49:42.119Z",
			"lastMessageAt": "2025-01-22T21:36:13.889Z",
			"visitor": {
				"_id": "6773aa32af674dc1104a3430",
				"token": "eb31eaf3-61df-444d-a7a0-046356beb893",
				"name": "255769925950",
				"username": "guest-2",
				"phone": [
					{
						"phoneNumber": "255769925950"
					}
				]
			},
			"agent": {
				"_id": "3cn732F4x9eHygJ32",
				"username": "aisenyi",
				"name": "Aisenyi Malisa",
				"email": "malisa.aisenyi@gmail.com"
			},
			"type": "Message",
			"messages": [
				{
					"u": {
						"_id": "3cn732F4x9eHygJ32",
						"username": "aisenyi",
						"name": "Aisenyi Malisa"
					},
					"_id": "H9fRao2XYvxufiFdM",
					"username": "aisenyi",
					"ts": "2025-01-22T22:21:03.721Z",
					"rid": "6KSaaKJyAHeo5ePKw",
					"agentId": "3cn732F4x9eHygJ32",
					"file": {
						"_id": "67916f4faf674dc1104a36bd",
						"name": "Screenshot 2025-01-08 at 17.22.38.png",
						"type": "image/png",
						"size": 2679793,
						"format": "png"
					},
					"attachments": [
						{
							"ts": "1970-01-01T00:00:00.000Z",
							"title": "Screenshot 2025-01-08 at 17.22.38.png",
							"title_link": "/file-upload/67916f4faf674dc1104a36bd/Screenshot%202025-01-08%20at%2017.22.38.png",
							"title_link_download": True,
							"image_dimensions": {
								"width": 480,
								"height": 285
							},
							"image_preview": "/9j/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAATACADASIAAhEBAxEB/8QAGAAAAwEBAAAAAAAAAAAAAAAAAAUGBwL/xAAjEAACAQQCAgIDAAAAAAAAAAABAgMABAURBhIhURMxIjJB/8QAFwEAAwEAAAAAAAAAAAAAAAAAAQIDAP/EABkRAQEBAQEBAAAAAAAAAAAAAAEAEQMCQf/aAAwDAQACEQMRAD8A03i/NsxeXiwX1oVDNosB4Aq4fJ9JCp7Ej1UlzvjWcvrixXAutrCjAy9V/bzVdZY2dLOBJx2lVAGPs1Tkmvl+S9Vwy6iyveQJtwT7FZ3zfm/IMVlbuGwtmeGEBkPXYatJawkKtpPJGqn8FhL5cleNfRbhbwofyNUemJgyeFHU2d5a4ljzECJIVU/YFPmP4E/3VFFTqSxbiX5AO51umq/VFFC1/9k=",
							"image_url": "/file-upload/67916f50af674dc1104a36c9/Screenshot%202025-01-08%20at%2017.22.38.png",
							"image_type": "image/png",
							"image_size": 2679793,
							"type": "file",
							"description": "Just another test",
							"descriptionMd": [
								{
									"type": "PARAGRAPH",
									"value": [
										{
											"type": "PLAIN_TEXT",
											"value": "Just another test"
										}
									]
								}
							]
						}
					],
					"fileUpload": {
						"publicFilePath": "http://172.104.134.226:3000/file-upload/67916f4faf674dc1104a36bd/Screenshot%202025-01-08%20at%2017.22.38.png?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE3Mzc1ODQ0NjQsIm5iZiI6MTczNzU4NDQ2NCwiZXhwIjoxNzM3NTg4MDY0LCJhdWQiOiJSb2NrZXRDaGF0IiwiY29udGV4dCI6eyJyaWQiOiI2S1NhYUtKeUFIZW81ZVBLdyIsInVzZXJJZCI6IjNjbjczMkY0eDllSHlnSjMyIiwiZmlsZUlkIjoiNjc5MTZmNGZhZjY3NGRjMTEwNGEzNmJkIn19.jpcUOyAk9SMooh5Kyk2U_esSQNqwlExBHQhS-M0NAFQ",
						"type": "image/png",
						"size": 2679793
					},
					"_updatedAt": "2025-01-22T22:21:04.281Z"
				}
			]
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
		print(response.json())
		self.assertEqual(response.status_code, 200)