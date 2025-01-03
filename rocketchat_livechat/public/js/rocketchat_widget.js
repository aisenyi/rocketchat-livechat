document.addEventListener('DOMContentLoaded', function() {
	frappe.call({
		method: 'rocketchat_livechat.api.rocketchat.get_rocketchat_settings',
		callback: function(response) {
			if (response.message.enabled) {
				(function(w, d) {
					w.RocketChat = function(c) { w.RocketChat._.push(c) };
					w.RocketChat._ = [];
					w.RocketChat.url = response.message.server_url;
					var scriptContent = `
						(function(w, d, s, u) {
							w.RocketChat = function(c) { w.RocketChat._.push(c) };
							w.RocketChat._ = [];
							w.RocketChat.url = u;
							var h = d.getElementsByTagName(s)[0],
								j = d.createElement(s);
							j.async = true;
							j.src = '${response.message.server_url}/livechat/rocketchat-livechat.min.js';
							h.parentNode.insertBefore(j, h);
						})(window, document, 'script', '${response.message.server_url}/livechat');

						RocketChat(function() {
							this.registerGuest({
								name: '${frappe.session.user_fullname}',
								email: '${frappe.session.user_email}'
							});
						});
					`;
					var script = d.createElement('script');
					script.type = 'text/javascript';
					script.text = scriptContent;
					d.body.appendChild(script);
				})(window, document);
			}
		}
	});
});