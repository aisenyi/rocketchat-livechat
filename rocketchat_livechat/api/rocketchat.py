import frappe
import requests
import uuid
import json
from frappe import request

class RocketChat():
	def __init__(self):
		self.settings = frappe.get_single("Rocketchat Settings")

	def send_message(self, source, msg, id_type, id, visitor_info):
		room_id = None
		visitor_token = None
		room_exists = frappe.db.exists("Rocketchat Livechat User", 
									{"id_type": id_type, "source": source, "id": id, "closed": 0})

		if room_exists:
			room_doc = frappe.get_doc("Rocketchat Livechat User", room_exists)
			visitor_token = room_doc.visitor_token

			if room_doc.room_id is None or room_doc.room_id != "":
				room = self.create_room(room_doc.visitor_token, room_doc.id_type, room_doc.id, room_doc.source, False, room_exists)
				if room.get("success"):
					room_id = room.get("room_id")
					room_doc = room.get("room_doc")
			else:
				room_id = room_doc.get("room_id")
		else:
			visitor, visitor_token = self.create_visitor(visitor_name=visitor_info.get("visitor_name"), 
												visitor_phone=visitor_info.get("visitor_phone"), 
												visitor_email=visitor_info.get("visitor_email"))
			if visitor.get("success"):
				message_sent = False
				room = self.create_room(visitor_token, id_type, id, source)

				room_doc = room.get("room_doc")
				if room.get("success"):
					room_id = room.get("room_id")

		if room_id is not None:
			message = self.send_message_to_room(room_id, visitor_token, msg)
			if message.get("success"):
				message_sent = True
		else:
			message_sent = False


		room_doc.append("messages", {
			"message": msg,
			"message_date": frappe.utils.now(),
			"status": "Queued" if not message_sent else "Sent"
		})
		room_doc.save()

				

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

	def create_room(self, visitor_token, id_type, id, source, new_user=True, user=None):
		rocketchat_url = self.settings.server_url
		create_room_endpoint = f"{rocketchat_url}/api/v1/livechat/room"

		headers = {
			"Content-Type": "application/json"
		}

		payload = {
			"token": visitor_token
		}

		try:
			room_id = None
			success = False
			response = requests.get(f'{create_room_endpoint}', headers=headers, params=payload)

			if response.status_code == 200:
				response_data = response.json()
				room_id = response_data.get("room", {}).get("_id")
				success = True
			elif response.status_code == 400 and response.json().get("errorType") == "no-agent-online":
				success = False
			else:
				raise Exception(f"""Failed to create live chat room. 
						Status Code: {response.status_code}, Response: {response.json()}""")
			
			if new_user:
				room_doc = frappe.new_doc("Rocketchat Livechat User")
				room_doc.update({
					"id_type": id_type,
					"id": id,
					"source": source,
					"visitor_token": visitor_token
				})

				if room_id is not None:
					room_doc.update({"room_id": room_id})
				room_doc.insert(ignore_permissions=True)
			else:
				room_doc = frappe.get_doc("Rocketchat Livechat User", user)
				if room_id is not None:
					room_doc.update({"room_id": room_id})
				room_doc.save()
			return {"success": success, "room_id": room_id, "room_doc": room_doc}
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

	def check_online(self):
		rocketchat_url = self.settings.server_url
		check_online_endpoint = f"{rocketchat_url}/api/v1/omnichannel/agents/available"

		user_info = self.login()

		headers = {
			"Content-Type": "application/json",
			"X-Auth-Token": user_info.get("auth_token"),
			"X-User-Id": user_info.get("user_id")
		}

		try:
			response = requests.get(check_online_endpoint, headers=headers)

			if response.status_code == 200:
				response_data = response.json()
				print(response_data)
				return response_data.get("success", False)
			else:
				raise Exception(f"""Failed to check online agents. 
						Status Code: {response.status_code}, Response: {response.json()}""")
		except Exception as e:
			frappe.log_error(message=str(e), title="Rocketchat API error")
			return False
		
	def login(self):
		rocketchat_url = self.settings.server_url
		login_endpoint = f"{rocketchat_url}/api/v1/login"

		headers = {
			"Content-Type": "application/json"
		}

		payload = {
			"user": self.settings.rocketchat_email,
			"password": self.settings.get_password("rocketchat_password")
		}

		try:
			response = requests.post(login_endpoint, headers=headers, json=payload)

			if response.status_code == 200:
				response_data = response.json()
				user_id = response_data.get("data", {}).get("userId")
				auth_token = response_data.get("data", {}).get("authToken")
				return {"user_id": user_id, "auth_token": auth_token}
			else:
				raise Exception(f"""Failed to login. 
						Status Code: {response.status_code}, Response: {response.json()}""")
		except Exception as e:
			frappe.log_error(message=str(e), title="Rocketchat API error")
			return None

@frappe.whitelist()
def get_rocketchat_settings():
	settings = frappe.get_single("Rocketchat Settings")
	return settings

@frappe.whitelist(allow_guest=True)
def rocketchat_webhook():
	from rocketchat_livechat.api.whatsapp import WhatsAppAPI
	if request.method == 'POST':
		data = json.loads(request.data)

		# Save the webhook log first
		new_log = frappe.new_doc('Rocketchat Webhook Log')
		new_log.update({
			'request_data': str(data)
		})
		new_log.insert(ignore_permissions=True)
		frappe.db.commit()
		
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

def test():
	source = "Whatsapp" 
	msg = "Just testing 2" 
	id_type = "Phone"
	id = "+255769925950" 
	visitor_info = {}
	chat = RocketChat()
	res = chat.send_message(source, msg, id_type, id, visitor_info)
	#res = chat.check_online()
	print(res)