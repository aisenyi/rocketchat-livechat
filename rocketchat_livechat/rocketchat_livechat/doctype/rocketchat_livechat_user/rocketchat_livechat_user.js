// Copyright (c) 2024, Impex and contributors
// For license information, please see license.txt

frappe.ui.form.on('Rocketchat Livechat User', {
	refresh: function(frm) {
		frm.events.show_hide_phone(frm);
	},

	source: function(frm) {
		frm.events.show_hide_phone(frm);
	},

	show_hide_phone: function(frm){
		if (frm.doc.source === 'Whatsapp') {
			frm.set_df_property('whatsapp_phone_number_id', 'hidden', 0);
		} else {
			frm.set_df_property('whatsapp_phone_number_id', 'hidden', 1);
		}
	}
});
