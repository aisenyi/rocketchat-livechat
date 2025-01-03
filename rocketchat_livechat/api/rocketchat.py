import frappe
import requests
import uuid
import json
from frappe import request

class RocketChat():
	def __init__(self):
		self.settings = frappe.get_single("Rocketchat Settings")

	def create_visitor(self, visitor_name=None, visitor_email=None, visitor_phone=None):
		# Rocket.Chat server URL
		rocketchat_url = self.settings.server_url
		register_visitor_endpoint = f"{rocketchat_url}/api/v1/livechat/visitor"

		visitor_token = str(uuid.uuid4())

		headers = {
			"Content-Type": "application/json"
		}

		payload = {
			"visitor": {
				"token": visitor_token
			}
		}

		if visitor_name:
			payload["visitor"]["name"] = visitor_name

		if visitor_email:
			payload["visitor"]["email"] = visitor_email
		
		if visitor_phone:
			payload["visitor"]["phone"] = visitor_phone

		try:
			response = requests.post(register_visitor_endpoint, headers=headers, json=payload)

			if response.status_code == 200:
				response_data = response.json()
				visitor_token = response_data.get("visitor", {}).get("token")
				return response_data, visitor_token
			else:
				raise Exception(f"""Failed to register live chat visitor. 
					Status Code: {response.status_code}, Response: {response.json()}""")
		except Exception as e:
			frappe.log_error(message=str(e), title="Rocketchat API error")

	def create_room(self, visitor_token):
		rocketchat_url = self.settings.server_url
		create_room_endpoint = f"{rocketchat_url}/api/v1/livechat/room"

		headers = {
			"Content-Type": "application/json"
		}

		payload = {
			"token": visitor_token
		}

		try:
			response = requests.get(f'{create_room_endpoint}', headers=headers, params=payload)

			if response.status_code == 200:
				response_data = response.json()
				return response_data
			else:
				raise Exception(f"""Failed to create live chat room. 
						Status Code: {response.status_code}, Response: {response.json()}""")
		except Exception as e:
			frappe.log_error(message=str(e), title="Rocketchat API error")

	def send_message_to_room(self, room_id, visitor_token, message):
		rocketchat_url = self.settings.server_url
		send_message_endpoint = f"{rocketchat_url}/api/v1/livechat/message"

		headers = {
			"Content-Type": "application/json"
		}

		payload = {
			"rid": room_id,
			"msg": message,
			"token": visitor_token
		}

		try:
			response = requests.post(send_message_endpoint, headers=headers, json=payload)

			if response.status_code == 200:
				response_data = response.json()
				return response_data
			else:
				raise Exception(f"""Failed to send message to room. 
						Status Code: {response.status_code}, Response: {response.json()}""")
		except Exception as e:
			frappe.log_error(message=str(e), title="Rocketchat API error")

@frappe.whitelist()
def get_rocketchat_settings():
	settings = frappe.get_single("Rocketchat Settings")
	return settings

@frappe.whitelist(allow_guest=True)
def rocketchat_webhook():
	from rocketchat_livechat.api.whatsapp import WhatsAppAPI
	if request.method == 'POST':
		data = json.loads(request.data)

		data = {
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
		
		latest_message = data['messages'][-1]
		room = frappe.db.exists("Rocketchat Livechat User", {"room_id": data.get("_id")})

		if room:
			source = frappe.db.get_value("Rocketchat Livechat User", room, "source")

			if source == "Whatsapp":
				# Check if the last message is from the agent
				if 'agentId' in latest_message:
					user_phone = data['visitor'].get('phone')
					
					if user_phone:
						whatsapp = WhatsAppAPI()
						result = whatsapp.send_message(
							to_phone_number=user_phone,
							message=latest_message['msg']
						)
					else:
						frappe.local.response['http_status_code'] = 200
						frappe.local.response['message'] = {"status": "OK"}
						return frappe.local.response["message"]
			
		# Check if the room was closed
		if data.get('closedAt') and data.get('closedAt') != "":
			if room:
				frappe.db.set_value("Rocketchat Livechat User", room, "closed", 1)

				frappe.local.response['http_status_code'] = 200
				frappe.local.response['message'] = {"status": "OK"}
				return frappe.local.response["message"]
		else:
			frappe.local.response['http_status_code'] = 200
			frappe.local.response['message'] = {"status": "OK"}
			return frappe.local.response["message"]
	else:
		# Respond with a 405 Method Not Allowed status for non-POST requests
		frappe.local.response['http_status_code'] = 405
		frappe.local.response['message'] = {"error": "Method Not Allowed"}
		return frappe.local.response['message']