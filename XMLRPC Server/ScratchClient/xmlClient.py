"""
	Scratch Client for Lego PowerFunctions I2C

	File:           xmlClient.py
	Author:         Xander Maas
	Version:        1.0
	Date:           31 jan 2015

	Version history:
	1.0     31 jan 2015 -   Initial release

	LICENSE INFO:
	AS FOR NOW THIS SOFTWARE IS NOT TO BE PUBLISHED WITHOUT MY EXPLICIT
	WRITTEN PERMISSION ONLY.

	Copyright (c)  Xander Maas, 2015

	Class to create a connection and send commands to the RaspberryPi
	server software
"""

import xmlrpclib

class xmlClient(object):

	def __init__(self):
		print 'xmlClient.py'

	def __init__(self, server):
		self._proxy = xmlrpclib.ServerProxy(server, allow_none=True)

	def sendCommand(self, channel, command):
		result = self._proxy.pfCommand(command, channel)
		if result == False:
			print 'Seems something went wrong'
			
		else:
			print 'Success!'

if __name__ == '__main__':
	print 'xmlClient.py'
