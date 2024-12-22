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
		
		latest_message = data['messages'][-1]

		# Check if the last message is from the agent
		if 'agentId' in latest_message:
			user_phone = data['visitor'].get('phone')
			
			if user_phone:
				whatsapp = WhatsAppAPI()
				result = whatsapp.send_message(
					to_phone_number=user_phone,
					message=latest_message['msg']
				)
				frappe.local.response['http_status_code'] = 200
				frappe.local.response['message'] = {"status": "OK"}
				return frappe.local.response["message"]
			else:
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