"""
	Based on example code from 
	https://docs.python.org/2/library/simplexmlrpcserver.html#simplexmlrpcserver-example

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

	def _listMethods(self):
		return list_public_methods_self()

	def __init__(self, address='0.0.0.0', port=9000):

		# Store our address and port info
		self.address = address
		self.port = port

		self.startServer()	

if __name__ == "__main__":
	print 'xmlServer.py'
