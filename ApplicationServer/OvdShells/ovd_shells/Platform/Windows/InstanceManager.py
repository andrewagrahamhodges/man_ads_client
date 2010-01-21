# -*- coding: utf-8 -*-

# Copyright (C) 2009,2010 Ulteo SAS
# http://www.ulteo.com
# Author Julien LANGLOIS <julien@ulteo.com> 2009, 2010
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

import win32event
import win32file


from ovd_shell.InstanceManager import InstanceManager as AbstractInstanceManager

class InstanceManager(AbstractInstanceManager):
	def launch(self, cmd):
		(hProcess, hThread, dwProcessId, dwThreadId) = win32process.CreateProcess(None, cmd, None , None, False, 0 , None, None, win32process.STARTUPINFO())
		win32file.CloseHandle(hThread)

	
	def wait(self):
		#win32event.WaitForSingleObject(hProcess, win32event.INFINITE)
		
		handleList = [instance[0] for instance in self.instances] 
		
	
		res = WaitForMultipleObjects(handleList, False , 200)
		
		if res in [win32event.WAIT_TIMEOUT, win32event.WAIT_FAILED]:
			return
		
		if res > win32event.WAIT_ABANDONED_0:
			# todo: understand what it means!
			return
		
		index = res - win32event.WAIT_OBJECT_0
		
		win32file.CloseHandle(handleList[index])
		
		self.onInstanceExited(self.instances[index])
	
	def kill(self, handle):
		TerminateProcess(handle, 0)
		
		win32file.CloseHandle(handle)
