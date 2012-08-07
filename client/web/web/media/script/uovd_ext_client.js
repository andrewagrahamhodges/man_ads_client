/**
 * Copyright (C) 2012 Ulteo SAS
 * http://www.ulteo.com
 * Author Julien LANGLOIS <julien@ulteo.com> 2012
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; version 2
 * of the License.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
 **/

Event.observe(window, 'load', function() {
	var test = new JavaTester();
	test.perform();
});

function startExternalSession(mode_) {
	new Ajax.Request(
		'login.php',
		{
			method: 'post',
			parameters: {
				mode: mode_,
				language: client_language,
				keymap: user_keymap,
				timezone: getTimezoneName(),
				debug: 0
			},
			onSuccess: function(transport) {
				onStartExternalSessionSuccess(transport.responseXML);
			},
			onFailure: function() {
				onStartExternalSessionFailure();
			}
		}
	);

	return false;
}

function onStartExternalSessionSuccess(xml_) {
	var xml = xml_;

	var buffer = xml.getElementsByTagName('response');
	if (buffer.length == 1) {
		try {
			showError(i18n.get(buffer[0].getAttribute('code')));
		} catch(e) {}
		return false;
	}

	var buffer = xml.getElementsByTagName('error');
	if (buffer.length == 1) {
		try {
			if (typeof i18n.get(buffer[0].getAttribute('error_id')) != 'undefined')
				showError(i18n.get(buffer[0].getAttribute('error_id')));
			else
				showError(i18n.get('internal_error'));
		} catch(e) {}
		return false;
	}

	var buffer = xml.getElementsByTagName('session');
	if (buffer.length != 1)
		return false;
	session_node = buffer[0];

	var sessionmanager_host = session_node.getAttribute('sessionmanager');
	if (sessionmanager_host == '127.0.0.1' || sessionmanager_host == '127.0.1.1' || sessionmanager_host == 'localhost' || sessionmanager_host == 'localhost.localdomain')
		sessionmanager_host = window.location.hostname;
	if (sessionmanager_host.indexOf(':') == -1)
		sessionmanager_host += ':443';
	
	var session_mode = false;
	try {
		session_mode = session_node.getAttribute('mode');
		session_mode = session_mode.substr(0, 1).toUpperCase()+session_mode.substr(1, session_mode.length-1);
	} catch(e) {}

	setTimeout(function() {
		if (session_mode == 'Desktop')
			daemon = new Desktop(debug_mode);
		else
			daemon = new External(debug_mode);

		daemon.sessionmanager = sessionmanager_host;
		daemon.keymap = user_keymap;
		try {
			daemon.duration = parseInt(session_node.getAttribute('duration'));
		} catch(e) {}
		daemon.duration = parseInt(session_node.getAttribute('duration'));
		daemon.multimedia = ((session_node.getAttribute('multimedia') == 1)?true:false);
		daemon.redirect_client_printers = ((session_node.getAttribute('redirect_client_printers') == 1)?true:false);
		daemon.redirect_smartcards_readers = ((session_node.getAttribute('redirect_smartcards_readers') == 1)?true:false);
		try {
			daemon.redirect_client_drives = session_node.getAttribute('redirect_client_drives');
		} catch(e) {}

		var settings_node = session_node.getElementsByTagName('settings');
		if (settings_node.length > 0) {
			var setting_nodes = settings_node[0].getElementsByTagName('setting');
			daemon.parseSessionSettings(setting_nodes);
		}

		daemon.i18n['session_close_unexpected'] = i18n.get('session_close_unexpected');
		daemon.i18n['session_end_ok'] = i18n.get('session_end_ok');
		daemon.i18n['session_end_unexpected'] = i18n.get('session_end_unexpected');
		daemon.i18n['error_details'] = i18n.get('error_details');
		daemon.i18n['close_this_window'] = i18n.get('close_this_window');
		daemon.i18n['start_another_session'] = i18n.get('start_another_session');

		daemon.i18n['suspend'] = i18n.get('suspend');
		daemon.i18n['resume'] = i18n.get('resume');

		daemon.prepare();
		if (! daemon.parse_list_servers(xml)) {
			try {
				showError(i18n.get('internal_error'));
			} catch(e) {}
			
			enableLogin();
			return false;
		}
		
		daemon.loop();
	}, 2500);

	return true;
}

function onStartExternalSessionFailure() {
	showError(i18n.get('internal_error'));

	return false;
}
