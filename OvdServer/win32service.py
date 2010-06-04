#!/usr/bin/python
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

import os
import sys
import servicemanager

from ovd.Communication.HttpServer import HttpServer as Communication
from ovd.Config import Config
from ovd.Logger import Logger
from ovd.SlaveServer import SlaveServer
from ovd.Platform import Platform

class OVD(win32serviceutil.ServiceFramework, SlaveServer):
	_svc_name_ = "OVD"
	_svc_display_name_ = "Ulteo OVD Slave Server"
	_svc_description_ = "Ulteo OVD Slave Server"
	
	def __init__(self,args):
		win32serviceutil.ServiceFramework.__init__(self, args)
		
		# Init the logger instance
		Win32Logger.initialize("OVD", Logger.INFO | Logger.WARN | Logger.ERROR, None)
		
		config_file = os.path.join(Platform.System.get_default_config_dir(), "ovd-slaveserver.conf")
		if not Config.read(config_file):
			Logger.error("invalid configuration file '%s'"%(config_file))
			sys.exit(1)
	
		if not Config.is_valid():
			Logger.error("invalid config")
			sys.exit(1)
		
		
		self.log_flags = 0
		for item in Config.log_level:
			if item == "info":
				self.log_flags|= Logger.INFO
			elif item == "warn":
				self.log_flags|= Logger.WARN
			elif item == "error":
				self.log_flags|= Logger.ERROR
			elif item == "debug":
				self.log_flags|= Logger.DEBUG
		Win32Logger.initialize("OVD", self.log_flags, Config.log_file)
		
		
		SlaveServer.__init__(self, Communication)
		self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
	
	
	def SvcDoRun(self):
		self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
		
		if not SlaveServer.init(self):
			Logger.error("Unable to initialize SlaveServer")
			self.ReportServiceStatus(win32service.SERVICE_STOPPED)
			return
		
		self.ReportServiceStatus(win32service.SERVICE_RUNNING)
		Logger.info("SlaveServer started")
		
		rc = win32event.WAIT_TIMEOUT
		while rc == win32event.WAIT_TIMEOUT:
			SlaveServer.loop_procedure(self)
			
			rc = win32event.WaitForSingleObject(self.hWaitStop, 30 * 1000)
		
		if not self.stopped:
			SlaveServer.stop(self)
		
		Logger.info("SlaveServer stopped")
		self.ReportServiceStatus(win32service.SERVICE_STOPPED)
	
	def SvcStop(self):
		Logger.info("Stopping SlaveServer")
		self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
		
		win32event.SetEvent(self.hWaitStop)
	
	def SvcShutdown(self):
		# Reinit Logger because the Windows service manager logging system is already down
		Logger.initialize("OVD", self.log_flags, Config.log_file, False)
		Logger.info("Stopping SlaveServer (shutdown)")

		win32event.SetEvent(self.hWaitStop)



class Win32Logger(Logger):
	def __init__(self, name, loglevel, file = None):
		Logger.__init__(self, name, loglevel, file, False)
	
	
	def log_info(self, message):
		if Logger.log_info(self, message) is False:
			return False

		servicemanager.LogInfoMsg(message)

	
	def log_warn(self, message):
		if Logger.log_warn(self, message) is False:
			return False

		servicemanager.LogWarningMsg(message)
	
	def log_error(self, message):
		if Logger.log_error(self, message) is False:
			return False
		
		servicemanager.LogErrorMsg(message)

	# Static methods
	@staticmethod 
	def initialize(name, loglevel, file=None, stdout=False, win32LogService=False):
		instance = Logger(name, loglevel, file, stdout, win32LogService)
		Logger._instance = instance



if __name__=='__main__':
	win32serviceutil.HandleCommandLine(OVD)
