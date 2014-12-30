"""
  LEGO PowerFunctions I2C Server

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

from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
import xmlrpclib
import logging

# Enable logging
logging.basicConfig(level=logging.DEBUG)

# We want to restrict the server to a particular path
class RequestHandler(SimpleXMLRPCRequestHandler):
	rpc_paths = ('/RPC2',)

class xmlServer(object):

	def startServer(self):
		logging.debug('Starting XMLRPC Server')
		self.server = SimpleXMLRPCServer((self.address, self.port), requestHandler=RequestHandler, logRequests=True, allow_none=True)
		self.server.register_introspection_functions()

	def __init__(self, address='0.0.0.0', port=9000):

		# Store our address and port info
		self.address = address
		self.port = port

		self.startServer()	

if __name__ == "__main__":
	print 'xmlServer.py'
