import frappe
import requests
import uuid
import json
from frappe import request
from frappe.utils import get_files_path

class RocketChat():
	def __init__(self):
		self.settings = frappe.get_single("Rocketchat Settings")

	def send_message(self, source, msg_type, msg, id_type, id, visitor_info):
		room_id = None
		visitor_token = None
		file_path = None
		message_sent = False
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
			if msg_type == "image":
				file_path = self.save_media(msg.get("media"), msg.get("media_type"), room_doc.name)
				message = self.upload_file_to_livechat(room_id, visitor_token, room_doc.name, msg.get("caption"), msg.get("media"))
				if message.get("success"):
					message_sent = True
			elif msg_type == "text":
				message = self.send_message_to_room(room_id, visitor_token, msg.get("text"))
				if message.get("success"):
					message_sent = True
		else:
			message_sent = False


		room_doc.append("messages", {
			"message": msg.get("text"),
			"attachment": file_path,
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
				room_doc.save(ignore_permissions=True)
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
		
	def save_media(self, media_content, media_type, docname):
		try:
			extension = {
				'image/jpeg': 'jpg',
				'image/png': 'png',
				'image/gif': 'gif',
				'video/mp4': 'mp4',
				'audio/mpeg': 'mp3',
				'application/pdf': 'pdf',
				'application/msword': 'doc',
				'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
				'application/vnd.ms-excel': 'xls',
				'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'xlsx',
				'text/plain': 'txt',
				'text/csv': 'csv',
				'application/zip': 'zip',
				'application/x-rar-compressed': 'rar',
				'application/vnd.ms-powerpoint': 'ppt',
				'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'pptx',
				'image/heic': 'heic',
				'image/heif': 'heif'
			}.get(media_type, 'bin')

			file_name = f"{str(uuid.uuid4())}.{extension}"
			file_path = get_files_path(f"{file_name}", is_private=True)

			with open(file_path, 'wb') as f:
				f.write(media_content)

			file_path = file_path.replace('./', "http://")
			file_path = file_path.replace('/public/', '/')
			
			file_doc = frappe.new_doc('File')
			file_doc.update({
				'file_name': f"{file_name}",
				'file_url': file_path,
				'is_private': 1,
				'folder': 'Home/Attachments',
				'attached_to_doctype': 'Rocketchat Livechat User',
				'attached_to_name': docname,
				'attached_to_field': "attachment",
				'file_size': len(media_content),
			})
			file_doc.insert(ignore_permissions=True)
			return file_path
		except IOError as e:
			frappe.log_error(message=str(e), title="WhatsApp Media Save Error")
			return False
		
	def upload_file_to_livechat(self, room_id, visitor_token, file_name, description, file_content):
		upload_endpoint = f"{self.settings.server_url}api/v1/livechat/upload/{room_id}"

		files = {
			"file": (file_name, file_content, "image/jpeg")
		}

		headers = {
			"X-Visitor-Token": visitor_token
		}

		try:
			response = requests.post(upload_endpoint, headers=headers, files=files)
			response.raise_for_status()
			return response.json()
		except requests.exceptions.RequestException as e:
			frappe.log_error(
				message=f"File upload failed for room {room_id}. Error: {e}",
				title="RocketChat File Upload Error"
			)
			return {"success": False, "error": str(e)}

@frappe.whitelist()
def get_rocketchat_settings():
	settings = frappe.get_single("Rocketchat Settings")
	return settings

@frappe.whitelist(allow_guest=True)
def rocketchat_webhook():
	from rocketchat_livechat.api.whatsapp import WhatsAppAPI
	from rocketchat_livechat.api.messenger import FacebookMessenger

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
			elif source == "Facebook Messenger":
				if 'agentId' in latest_message:
					user_id = frappe.db.get_value("Rocketchat Livechat User", room, "id")
					messenger = FacebookMessenger()
					messenger.send_to_messenger(user_id, latest_message['msg'])

			
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
	
def send_queued_messages():
	messages = frappe.db.sql("""
				SELECT
					messages.message, user.id_type, user.id, user.source,
					user.room_id, user.visitor_token, messages.parent AS user_docname,
					messages.name AS message_docname
				FROM 
					`tabRocketchat Message` AS messages
				LEFT JOIN
					`tabRocketchat Livechat User` user ON user.name = messages.parent
				WHERE
					messages.status = 'Queued' AND user.closed <> 1
				ORDER BY messages.message_date ASC
				""", as_dict=1)
	
	rc = RocketChat()
	for message in messages:
		if message.room_id is not None and message.room_id != "":
			res = rc.send_message_to_room(message.room_id, message.visitor_token, message.message)
			if res.get("success"):
				frappe.db.set_value("Rocketchat Message", message.message_docname, "status", "Sent")
		else:
			room = rc.create_room(message.visitor_token, message.id_type, message.id, 
				  message.source, False, message.user_docname)
			if room.get("success"):
				frappe.db.set_value("Rocketchat Livechat User", message.user_docname, "room_id", room.get("room_id"))
				res = rc.send_message_to_room(room.get("room_id"), message.visitor_token, message.message)
				if res.get("success"):
					frappe.db.set_value("Rocketchat Message", message.message_docname, "status", "Sent")
