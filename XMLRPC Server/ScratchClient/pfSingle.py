class pfSingle(object):

	def __init(self):
		print "pfSingle  Initialized"

	def createCommand(self, channel, output, command):
		_nib1 = 0x0
		_nib2 = 0x0
		_nib3 = 0x0

		# Create _nib1, channel will be 1-4 when received, should be rewritten
		# as 0-3 for the software
		_nib1 = 0x0 + (int(channel) - 1)

		# Create _nib2
		# As we are not going to use the extended address space, the base 
		# will always be 0x4
		_nib2  = 0x4
		if output[0].upper() == 'R':
			_nib2 = _nib2
		elif output[0].upper() == 'B':
			_nib2 = _nib2 | 0x1 << 1
		else:
			return False

		# Create _nib3
		if command == 'FLT':
			_byte = 0x0
		elif command == 'FWD1':
			_byte = 0x1
		elif command == 'FWD2':
			_byte = 0x2
		elif command == 'FWD3':
			_byte = 0x3
		elif command == 'FWD4':
			_byte = 0x4
		elif command == 'FWD5':
			_byte = 0x5
		elif command == 'FWD6':
			_byte = 0x6
		elif command == 'FWD7':
			_byte = 0x7
		elif command == 'BRK':
			_byte = 0x8
		elif command == 'REV7':
			_byte = 0x9
		elif command == 'REV6':
			_byte = 0xa
		elif command == 'REV5':
			_byte = 0xb
		elif command == 'REV4':
			_byte = 0xc
		elif command == 'REV3':
			_byte = 0xd
		elif command == 'REV2':
			_byte = 0xe
		elif command == 'REV1':
			_byte = 0xf
		else:
			return False

		_nib3 = _byte
		chkSum = self.calculateChecksum(_nib1, _nib2, _nib3)

		# compose the command
		return _nib1 << 12 | _nib2 << 8 | _nib3 <<4 | chkSum

	def calculateChecksum(self, nib1, nib2, nib3):
		return 0xf ^ nib1 ^ nib2 ^ nib3

if __name__ == "__main__":
	print "pfSingle.py"
