# -*- coding: utf-8 -*-

# Copyright (C) 2010-2011 Ulteo SAS
# http://www.ulteo.com
# Author Laurent CLOUET <laurent@ulteo.com> 2010-2011
# Author Arnaud Legrand <arnaud@ulteo.com> 2010
# Author Samuel BOVEE <samuel@ulteo.com> 2010-2011
#
# This program is free software; you can redistribute it and/or 
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; version 2
# of the License
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

from OpenSSL import SSL

import asyncore
import re
import socket
import threading
import time
import uuid

from ovd.Logger import Logger
from receiver import receiver, receiverXMLRewriter
from sender import sender, senderHTTP


class ReverseProxy(asyncore.dispatcher):

	def __init__(self, ssl_ctx, gateway, sm, rdp_port):
		asyncore.dispatcher.__init__(self)

		self.sm = sm
		self.rdp_port = rdp_port
		self.ssl_ctx = ssl_ctx

		self.lock = threading.Lock()
		self.database = {}

		self.rdp_ptn = re.compile('\x03\x00.*Cookie: .*token=([\-\w]+);.*')
		self.http_ptn = re.compile('((?:HEAD)|(?:GET)|(?:POST)) (.*) HTTP/(.\..)')

		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.set_socket(SSL.Connection(self.ssl_ctx, sock))
		#self.set_reuse_addr()

		try:
			self.bind(gateway)
		except:
			Logger.error('Local Bind Error, Server at port %d is not ready' % gateway[1])
			exit()

		self.listen(5)
		Logger.info('Gateway:: listening started')


	def insertToken(self, fqdn):
		token = str(uuid.uuid4())
		try:
			self.lock.acquire()
			self.database[token] = fqdn
		finally:
			self.lock.release()
		Logger.debug('token %s inserted' % token)
		return token


	def handle_accept(self):
		conn, peer = self.accept()
		addr, port = peer

		r = None
		while r is None:
			try:
				r = conn.recv(4096)
			except (SSL.SysCallError, SSL.ZeroReturnError):
				conn.close()
				return
			except SSL.WantReadError:
				time.sleep(0.01)

		request = r.split('\n', 1)[0]
		utf8_request = request.rstrip('\n\r').decode("utf-8", "replace")

		# find protocol
		rdp  = self.rdp_ptn.match(request)
		http = self.http_ptn.match(request)

		try:
			# RDP case
			if rdp:
				token = rdp.group(1)

				# get FQDN
				try:
					self.lock.acquire()
					if self.database.has_key(token):
						fqdn = self.database[token]
						del self.database[token]
						Logger.debug("Access Granted token: %s for fqdn: %s" % (token, fqdn))
					else:
						raise Exception('token authorization failed for: ' + token)
				finally:
					self.lock.release()

				sender((fqdn, self.rdp_port), receiver(conn, r))

			# HTTP case
			elif http:
				Logger.debug("Gateway:: request: http %s (%s,%d)" % (utf8_request, addr, port))
				path = http.group(2)

				if not (path == '/ovd' or path.startswith("/ovd/")):
					raise Exception('wrong HTTP path: ' + path)

				if path == "/ovd/client/start.php":
					rec = receiverXMLRewriter(conn, r, self)
				else:
					rec = receiver(conn, r)
				senderHTTP(self.sm, rec, self.ssl_ctx)

			# protocol error
			else:
				raise Exception('bad first request line: ' + request)

		except Exception, err:
			Logger.debug("ReverseProxy::handle_accept error %s %s"%(type(err), err))
			conn.close()
