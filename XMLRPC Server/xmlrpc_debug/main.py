#!/usr/bin/python -u
"""
  LEGO PowerFunctions I2C Server Tester

  File:		main.py
  Author:	Xander Maas <xander@xjmaas.nl>
  Date:		30 dec 2014

  LICENSE INFO:
	This program is free software; you can redistribute it and/or modify it
	under the terms of the GNU General Public License as published by the
	Free Software Foundation; either version 2 of the License, or (at your
	option) any later version.
 
	This program is distributed in the hope that it will be useful, but
	WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	Copyright (c) Xander Maas, 2014

	This program will create a XMLRPC server, which translates the
	commands sent from (another) device over TCP/IP to the I2C command(s)
	which will be sent over the I2C bus of the RPi
"""

import xmlrpclib

proxy = xmlrpclib.ServerProxy('http://192.168.32.10:9000', allow_none=True)
print proxy.installedBoards()

print proxy.returnVersion()

command = 0x8117
channel = 1

result = proxy.pfCommand(command,channel)

if result["status"] == False:
	print 'Command failed (' + result['description'] +')'
else:
	print 'Command succeeded'
