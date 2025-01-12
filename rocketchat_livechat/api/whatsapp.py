import requests
import json
from rocketchat_livechat.api.rocketchat import get_rocketchat_settings
from frappe import request
import frappe
from werkzeug.wrappers import Response

class WhatsAppAPI:
	def __init__(self):
		settings = get_rocketchat_settings()
		self.access_token = settings.get_password('whatsapp_access_token')
		self.phone_number_id = settings.get('whatsapp_phone_number_id')
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

	def send_message(self, to_phone_number, message):
		payload = {
			'messaging_product': 'whatsapp',
			'recipient_type': 'individual',
			'to': to_phone_number,
			'type': 'text',
			'text': {'body': message}
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

@frappe.whitelist(allow_guest=True)
def whatsapp_webhook():
	from rocketchat_livechat.api.rocketchat import RocketChat
	if request.method == 'POST':
		try:
			# data = {
			# 	"object": "whatsapp_business_account",
			# 	"entry": [{
			# 		"id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
			# 		"changes": [{
			# 			"value": {
			# 				"messages": [{
			# 					"from": "+255769925954",
			# 					"id": "wamid.ID",
			# 					"timestamp": "TIMESTAMP",
			# 					"text": {
			# 						"body": "Second test message, woohoo!"
			# 					},
			# 					"type": "text"
			# 				}]
			# 			},
			# 			"field": "messages"
			# 		}]
			# 	}]
			# }
			data = json.loads(request.data)

			changes = data.get("entry")[0].get("changes")
			for change in changes:
				if change.get("field") == "messages":
					message = change.get("value").get("messages", [])[0]
					sender = message.get('from')
					message = message.get('text', {}).get('body')
					frappe.set_user("Administrator")
					rc = RocketChat()
					rc.send_message("Whatsapp", message, "Phone", sender, {"visitor_phone": sender})
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