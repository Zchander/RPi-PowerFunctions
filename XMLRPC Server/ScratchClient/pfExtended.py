class pfExtended(object):

	def __init(self):
		print "pfExtended Initialized"

	def createCommand(self, channel, command):
		_nib1 = 0x0
		_nib2 = 0x0
		_nib3 = 0x0

		# Create _nib1, channel will be 1-4 when received, should be rewritten
		# as 0-3 for the software
		_nib1 = 0x0 + (int(channel) - 1)

		# Create _nib2
		# As we are not going to use the extended address space, this is 
		# always 0x0 (!!)
		_nib2  = 0x0

		# Create _nib3
		if command.upper() == 'BRK':
			_nib3 = 0x0
		elif command.upper() == 'INCA':
			_nib3 = 0x1
		elif command.upper() == 'DECA':
			_nib3 = 0x2
		elif command.upper() == 'TOGB':
			_nib3 = 0x4

		chkSum = self.calculateChecksum(_nib1, _nib2, _nib3)

		# compose the command
		return _nib1 << 12 | _nib2 << 8 | _nib3 <<4 | chkSum

	def calculateChecksum(self, nib1, nib2, nib3):
		return 0xf ^ nib1 ^ nib2 ^ nib3

if __name__ == "__main__":
	print "pfExtended.py"
