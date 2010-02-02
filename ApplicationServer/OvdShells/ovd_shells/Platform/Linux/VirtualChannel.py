# -*- coding: utf-8 -*-

# Copyright (C) 2010 Ulteo SAS
# http://www.ulteo.com
# Author Julien LANGLOIS <julien@ulteo.com> 2010
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

import xrdp

from ovd_shells.VirtualChannel import VirtualChannel as AbstractVirtualChannel

class VirtualChannel(AbstractVirtualChannel):
	def __init__(self, name_):
		AbstractVirtualChannel.__init__(self, name_)
		self._handle = None
	
	
	def Open(self):
		self._handle = xrdp.VchannelOpen(self.name)
		return self._handle != False
	
	
	def Close(self):
		if self._handle is not None:
			xrdp.VchannelClose(self._handle)
	
	
	def Read(self, size):
		return xrdp.VchannelRead(self._handle)
	
	
	def Write(self, message):
		return xrdp.VchannelWrite(self._handle, message)
