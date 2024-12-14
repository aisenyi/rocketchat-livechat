import frappe

@frappe.whitelist()
def get_rocketchat_settings():
	settings = frappe.get_single("Rocketchat Settings")
	return {
		"server_url": settings.server_url,
		"enabled": settings.enabled
	}