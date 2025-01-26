import requests
import json
from rocketchat_livechat.api.rocketchat import get_rocketchat_settings
from frappe import request
import frappe
from werkzeug.wrappers import Response

class FacebookMessenger():
	def __init__(self):
		settings = get_rocketchat_settings()
		self.enabled = settings.enable_messenger_support
		self.access_token = settings.get_password("facebook_access_token")
		self.page_id = settings.facebook_page_id

	def get_user_name(self, psid):
		"""
		Fetches the name of a Facebook user given their PSID (Page-Scoped ID).
		"""
		url = f"https://graph.facebook.com/v12.0/{psid}"
		params = {
			"fields": "first_name,last_name",
			"access_token": self.access_token
		}

		response = requests.get(url, params=params)
		
		if response.status_code == 200:
			data = response.json()
			first_name = data.get("first_name", "Unknown")
			last_name = data.get("last_name", "Unknown")
			return f"{first_name} {last_name}"
		else:
			print(f"Failed to fetch user details: {response.json()}")
			return None

	def send_to_messenger(self, user_id, message):
		url = f"https://graph.facebook.com/v21.0/{self.page_id}/messages?access_token={self.access_token}"
		headers = {
			"Content-Type": "application/json"
		}
		payload = {
			"recipient": {
				"id": user_id
			},
			"messaging_type": "RESPONSE",
			"message": {
				"text": message
			}
		}

		response = requests.post(url, headers=headers, json=payload)

		if response.status_code == 200:
			return response.json()
		else:
			frappe.log_error(message=response.json(), title="Facebook Messenger API Error")



@frappe.whitelist(allow_guest=True)
def messenger_webhook():
	if request.method == 'GET':
		hub_mode = frappe.form_dict.get('hub.mode')
		hub_challenge = frappe.form_dict.get('hub.challenge')
		hub_verify_token = frappe.form_dict.get('hub.verify_token')

		if hub_mode and hub_challenge and hub_verify_token:
			settings = get_rocketchat_settings()
			verify_token = settings.get('messenger_verification_token')

			if settings.get('enable_messenger_support') and hub_verify_token == verify_token:
				return Response(hub_challenge, status=200, content_type="text/plain")
			else:
				frappe.local.response['http_status_code'] = 405
				frappe.local.response['message'] = {"error": "Invalid Verify Token"}
				return frappe.local.response['message']
	elif request.method == 'POST':
		data = json.loads(request.data)
		return handle_incoming_message(data)
	else:
		# Respond with a 405 Method Not Allowed status for non-POST requests
		frappe.local.response['http_status_code'] = 405
		frappe.local.response['message'] = {"error": "Method Not Allowed"}
		return frappe.local.response['message']
	
def handle_incoming_message(data=None):
	from rocketchat_livechat.api.rocketchat import RocketChat

	data = {
		'object': 'page',
		'entry': [
			{
				'time': 1737711202317,
				'id': '1701202886814226',
				'messaging': [
					{
						'sender': {'id': '9092096187479591'},
						'recipient': {'id': '1701202886814226'},
						'timestamp': 1737709873042,
						'message': {
							'mid': 'm_8q1Csg4di6ZuprSetYuiLgVKSY3mgT5RNHvPH8ogyBun4xxaGqUK3efIohSGJaXHdhGcabPEMzVHOU2IzP8LrQ',
							'text': 'Is this still working?'
						}
					}
				]
			}
		]
	}

	# Save the webhook log first
	new_log = frappe.new_doc('Facebook Webhook Log')
	new_log.update({
		'request_data': str(data)
	})
	new_log.insert(ignore_permissions=True)
	frappe.db.commit()

	fb = FacebookMessenger()
	rc = RocketChat()
	if not fb.enabled or not rc.enabled:
		return
	
	for entry in data.get("entry", []):
		for messaging_event in entry.get("messaging", []):
			if "message" in messaging_event:
				sender_id = messaging_event["sender"]["id"]
				message = messaging_event["message"].get("text", "")

				message_doc = {
					"type": "text",
					"media": "",
					"text": message,
					"media_type": ""
				}

				rc.send_message("Facebook Messenger", "Text", message_doc, 
					"ID", sender_id, {})

				# If the user has sent a message before, get the room and send message,
				# otherwise create a visitor and room
				# message_doc = {"type": "text", "media": "", "text": message, "media_type": ""}
				# room_exists = frappe.db.exists("Rocketchat Livechat User", 
				# 					{"id_type": "ID", "source": "Facebook Messenger", "id": sender_id, "closed": 0})
				# if room_exists:
				# 	room_id, visitor_token = frappe.db.get_value("Rocketchat Livechat User", 
				# 								room_exists, ["room_id", "visitor_token"])
				# 	rc.send_message_to_room(room_id, visitor_token, message, message_doc)
				# else:
				# 	sender_name = fb.get_user_name(sender_id)
				# 	visitor, visitor_token = rc.create_visitor(visitor_name=sender_name)
				# 	if visitor.get("success"):
				# 		room = rc.create_room(visitor_token, 'ID', sender_id, 'Facebook Messenger')

				# 		if room.get("success"):
				# 			room_id = room.get("room", {}).get("_id")
				# 			if room_id:
				# 				new_user = frappe.new_doc("Rocketchat Livechat User")
				# 				new_user.update({
				# 					"id_type": "ID",
				# 					"id": sender_id,
				# 					"source": "Facebook Messenger",
				# 					"room_id": room_id,
				# 					"visitor_token": visitor_token
				# 				})
				# 				new_user.insert(ignore_permissions=True)
				# 			message_doc = {"type": "text", "media": "", "msg": message, "media_type": ""}
				# 			rc.send_message_to_room(room_id, visitor_token, message, message_doc)

	frappe.local.response['http_status_code'] = 200
	frappe.local.response['message'] = "OK"
	return frappe.local.response['message']