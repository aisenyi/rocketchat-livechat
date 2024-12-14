document.addEventListener('DOMContentLoaded', function() {
	frappe.call({
		method: 'rocketchat_livechat.api.get_rocketchat_settings',
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
							j.src = '${response.message.server_url}/livechat/rocketchat-livechat.min.js?_=201903270000';
							h.parentNode.insertBefore(j, h);
						})(window, document, 'script', '${response.message.server_url}/livechat');
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