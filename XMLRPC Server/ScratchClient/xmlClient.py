"""
	XML-RPC Client for RPi Lego Powerfunctions I2C


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
