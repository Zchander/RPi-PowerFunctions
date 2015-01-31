class pfCombo(object):

	def __init(self):
		print "pfCombo  Initialized"

	def createCommand(self, channel, commandA, commandB):
		_nib1 = 0x0
		_nib2 = 0x0
		_nib3 = 0x0

		print 'Arguments: channel ' + str(channel) + ' Command A: ' + str(commandA) + ' Command B: ' + str(commandB)
		# Create _nib1, channel will be 1-4 when received, should be rewritten
		# as 0-3 for the software
		_nib1 = 0x4 + (int(channel) - 1)
		print 'Nibble #1: ' + str(_nib1)

		# Create nib2
		_nib2 = self.createNib(commandB)
		if _nib2 == 0xff:
			return False
		print 'Nibble #2: ' + str(_nib2)

		# Create nib3
		_nib3 = self.createNib(commandA)
		if _nib3 == 0xff:
			return False
		print 'Nibble #3: ' + str(_nib3)

		# Create nib4 (Checksum)
		checksum = self.calculateChecksum(_nib1, _nib2, _nib3)
		print 'Nibble #4: ' + str(hex(checksum))

		# Compose the command
		return _nib1 << 12 | _nib2 << 8 | _nib3 << 4 | checksum

	def createNib(self, command):
		# Create a nib
		if command == 'FLT':
			return 0x0
		elif command == 'FWD1':
			return 0x1
		elif command == 'FWD2':
			return 0x2
		elif command == 'FWD3':
			return 0x3
		elif command == 'FWD4':
			return 0x4
		elif command == 'FWD5':
			return 0x5
		elif command == 'FWD6':
			return 0x6
		elif command == 'FWD7':
			return 0x7
		elif command == 'BRK':
			return 0x8
		elif command == 'REV7':
			return 0x9
		elif command == 'REV6':
			return 0xa
		elif command == 'REV5':
			return 0xb
		elif command == 'REV4':
			return 0xc
		elif command == 'REV3':
			return 0xd
		elif command == 'REV2':
			return 0xe
		elif command == 'REV1':
			return 0xf
		else:
			return 0xff
	
	def calculateChecksum(self, nib1, nib2, nib3):
		return 0xf ^ nib1 ^ nib2 ^ nib3

if __name__ == "__main__":
	print "pfCombo.py"
