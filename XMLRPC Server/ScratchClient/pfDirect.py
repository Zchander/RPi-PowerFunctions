class pfDirect(object):

	def __init(self):
		print "pfDirect Initialized"

	def createCommand(self, channel, commandA, commandB):
		_nib1 = 0x0
		_nib2 = 0x0
		_nib3 = 0x0
		_byteH = 0x0
		_byteL = 0x0
		
		print ' CommandA: ' + str(commandA)
		print ' CommandB: ' + str(commandB)
		# Create _nib1, channel will be 1-4 when received, should be rewritten
		# as 0-3 for the software
		_nib1 = 0x0 + (int(channel) - 1)

		# Create _nib2
		# As we are not going to use the extended address space, this is 
		# always 0x1 (!!)
		_nib2  = 0x1

		# Create _nib3
		if commandB.upper() == 'FLTB':
			_byteH = 0x0
		elif commandB.upper() == 'FWDB':
			_byteH = 0x1
		elif commandB.upper() == 'REVB':
			_byteH = 0x2
		elif commandB.upper() == 'BRKB':
			_byteH = 0x3
		else:
			return False
		
		if commandA.upper() == 'FLTA':
			_byteL = 0x0
		elif commandA.upper() == 'FWDA':
			_byteL = 0x1
		elif commandA.upper() == 'REVA':
			_byteL = 0x2
		elif commandA.upper() == 'BRKA':
			_byteL = 0x3
		else:
			return False

		_nib3 = _byteH << 2 | _byteL
		chkSum = self.calculateChecksum(_nib1, _nib2, _nib3)

		# compose the command
		return _nib1 << 12 | _nib2 << 8 | _nib3 <<4 | chkSum

	def calculateChecksum(self, nib1, nib2, nib3):
		return 0xf ^ nib1 ^ nib2 ^ nib3

if __name__ == "__main__":
	print "pfDirect.py"
