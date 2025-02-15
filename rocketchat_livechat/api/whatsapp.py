import requests
import json
from rocketchat_livechat.api.rocketchat import get_rocketchat_settings
from frappe import request
import frappe
from werkzeug.wrappers import Response
from io import BytesIO

class WhatsAppAPI:
	def __init__(self, phone_number_id):
		settings = get_rocketchat_settings()
		self.access_token = settings.get_password('whatsapp_access_token')
		self.phone_number_id = phone_number_id
		self.enabled = settings.enable_whatsapp_support

		if not self.enabled:
			frappe.throw("Whatsapp integration not enabled")
		
		if not self.access_token or not self.phone_number_id:
			raise ValueError("WhatsApp credentials not found in RocketChat settings")
			
		self.api_url = f"https://graph.facebook.com/v21.0/{self.phone_number_id}/messages"
		self.headers = {
			'Authorization': f'Bearer {self.access_token}',
			'Content-Type': 'application/json'
		}

	def send_message(self, to_phone_number, message="", type="text", media=None):
		payload = {
			'messaging_product': 'whatsapp',
			'recipient_type': 'individual',
			'to': to_phone_number,
			'type': type
		}

		if type != "text":
			media_id = self.upload_media(media.get("file_path"), media.get("type"))
			payload[type] = {
				"id": media_id.get("id"),
				"caption": media.get("caption")
			}
		else:
			payload["text"] = {
				'body': message
			}
		
		try:
			response = requests.post(
				self.api_url,
				headers=self.headers,
				data=json.dumps(payload)
			)
			response.raise_for_status()
			return response.json()
		except requests.exceptions.RequestException as e:
			return {'error': str(e)}
		
	def download_media(self, media_url):
		try:
			url = requests.get(media_url, headers=self.headers)
			url.raise_for_status()
			#return url.json())
			headers = {
				'Authorization': f'Bearer {self.access_token}',
				'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
			}
			response = requests.get(url.json().get("url"), headers=headers)
			response.raise_for_status()
			return response.content
		except requests.exceptions.RequestException as e:
			frappe.log_error(message=str(e), title="WhatsApp Media Download Error")
			return None
		
	
	def upload_media(self, file_path, mime_type):
		url = f"https://graph.facebook.com/v21.0/{self.phone_number_id}/media"

		try:
			token = file_path.split('token=')[1]
			file_path = file_path.split('?token=')[0]
			params = {
				'token': token
			}
			response = requests.get(file_path, params=params)
			response.raise_for_status()
			media_content = BytesIO(response.content)

			files = {
				'file': (file_path, media_content, mime_type)
			}
			payload = {
				'messaging_product': 'whatsapp'
			}

			uresponse = requests.post(
				url,
				headers={'Authorization': f'Bearer {self.access_token}'},
				data=payload,
				files=files
			)
			uresponse.raise_for_status()
			return uresponse.json()
		except requests.exceptions.RequestException as e:
			frappe.log_error(message=str(frappe.get_traceback()), title="WhatsApp Media Upload Error")
			return {'error': str(e)}
		
	def get_file_type(self, mime_type):
		mime_types = {
			'image/jpeg': 'image',
			'image/png': 'image',
			'image/gif': 'image',
			'video/mp4': 'video',
			'audio/mpeg': 'audio',
			'application/pdf': 'document',
			'application/msword': 'document',
			'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'document',
			'application/vnd.ms-excel': 'document',
			'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'document',
			'text/plain': 'document',
			'text/csv': 'document',
			'application/zip': 'document',
			'application/x-rar-compressed': 'document',
			'application/vnd.ms-powerpoint': 'document',
			'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'document',
			'image/heic': 'image',
			'image/heif': 'image'
		}
		return mime_types.get(mime_type, 'unknown')

@frappe.whitelist(allow_guest=True)
def whatsapp_webhook():
	from rocketchat_livechat.api.rocketchat import RocketChat
	if request.method == 'POST':
		try:
				# data = {
				# 	'object': 'whatsapp_business_account',
				# 	'entry': [{
				# 		'id': '486606171206665',
				# 		'changes': [{
				# 			'value': {
				# 				'messaging_product': 'whatsapp',
				# 				'metadata': {
				# 					'display_phone_number': '15551725501',
				# 					'phone_number_id': '469448259592538'
				# 				},
				# 				'contacts': [{
				# 					'profile': {
				# 						'name': 'Aisenyi'
				# 					},
				# 					'wa_id': '255769925950'
				# 				}],
				# 				'messages': [{
				# 					'from': '255769925950',
				# 					'id': 'wamid.HBgMMjU1NzY5OTI1OTUwFQIAEhgUM0FEQzU5Q0JBOURCRDc5QUI3MjEA',
				# 					'timestamp': '1737305342',
				# 					'type': 'video',
				# 					'video': {
				# 						'mime_type': 'video/mp4',
				# 						'sha256': 'qz/RPAOQI+tFyyrCdCQLCnQrmIOahbidU4XH48WSgTA=',
				# 						'id': '1135601261249656'
				# 					}
				# 				}]
				# 			},
				# 			'field': 'messages'
				# 		}]
				# 	}]
				# }

				data = json.loads(request.data)

				log = frappe.new_doc("Whatsapp Webhook Log")
				log.update({"request_data": str(data)})
				log.insert(ignore_permissions=True)
				frappe.db.commit()

				changes = data.get("entry")[0].get("changes")
				for change in changes:
					if change.get("field") == "messages":
						phone_number_id = change.get("metadata", {}).get("phone_number_id")
						message = change.get("value").get("messages", [])[0]
						sender = message.get('from')
						message_type = message.get('type')
						media_url = f"https://graph.facebook.com/v21.0/"

						if message_type == 'image':
							media_id = message.get('image', {}).get('id')
							caption = message.get('image', {}).get('caption')
							mime_type = message.get('image', {}).get('mime_type')
							media_url = f"{media_url}{media_id}"
							whatsapp_api = WhatsAppAPI(phone_number_id)
							media_content = whatsapp_api.download_media(media_url)

							if media_content:
								message = {
									"type": "media",
									"media": media_content,
									"text": caption,
									"media_type": mime_type
								}
						elif message_type == "audio":
							media_id = message.get('audio', {}).get('id')
							mime_type = message.get('audio', {}).get('mime_type')
							media_url = f"{media_url}{media_id}"
							whatsapp_api = WhatsAppAPI(phone_number_id)
							media_content = whatsapp_api.download_media(media_url)

							if media_content:
								message = {
									"type": "media",
									"media": media_content,
									"text": "",
									"media_type": mime_type
								}
						elif message_type == "document":
							media_id = message.get('document', {}).get('id')
							mime_type = message.get('document', {}).get('mime_type')
							media_url = f"{media_url}{media_id}"
							whatsapp_api = WhatsAppAPI(phone_number_id)
							media_content = whatsapp_api.download_media(media_url)

							if media_content:
								message = {
									"type": "media",
									"media": media_content,
									"text": "",
									"media_type": mime_type
								}
						elif message_type == "video":
							media_id = message.get('video', {}).get('id')
							mime_type = message.get('video', {}).get('mime_type')
							media_url = f"{media_url}{media_id}"
							whatsapp_api = WhatsAppAPI(phone_number_id)
							media_content = whatsapp_api.download_media(media_url)

							if media_content:
								message = {
									"type": "media",
									"media": media_content,
									"text": "",
									"media_type": mime_type
								}
						elif message_type == 'text':
							message = {
								"type": "text",
								"text": message.get('text', {}).get('body')
							}
						
						rc = RocketChat()
						rc.send_message("Whatsapp", message_type, message, "Phone", 
							sender, {"visitor_phone": sender, "phone_number_id": phone_number_id})
				frappe.local.response['http_status_code'] = 200
				frappe.local.response['message'] = {"status": "OK"}
				return frappe.local.response["message"]
		except Exception as e:
			frappe.log_error(message=frappe.get_traceback(), title="Whatsapp Webhook error")
			frappe.local.response['http_status_code'] = 500
			frappe.local.response['message'] = {"error": e}
			return frappe.local.response["message"]
	elif request.method == 'GET':
		hub_mode = frappe.form_dict.get('hub.mode')
		hub_challenge = frappe.form_dict.get('hub.challenge')
		hub_verify_token = frappe.form_dict.get('hub.verify_token')

		if hub_mode and hub_challenge and hub_verify_token:
			settings = get_rocketchat_settings()
			verify_token = settings.get('whatsapp_verification_token')

			if hub_verify_token == verify_token:
				return Response(hub_challenge, status=200, content_type="text/plain")
			else:
				frappe.local.response['http_status_code'] = 405
				frappe.local.response['message'] = {"error": "Invalid Verify Token"}
				return frappe.local.response['message']
	else:
		# Respond with a 405 Method Not Allowed status for non-POST requests
		frappe.local.response['http_status_code'] = 405
		frappe.local.response['message'] = {"error": "Method Not Allowed"}
		return frappe.local.response['message']