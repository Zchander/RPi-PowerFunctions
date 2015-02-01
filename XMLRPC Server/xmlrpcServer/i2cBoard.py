"""
  LEGO PowerFunctions I2C Server

  File:       main.py
  Author:     Xander Maas <xander@xjmaas.nl>
  Date:       10 oct 2014

  LICENSE INFO:
    AS FOR NOW THIS SOFTWARE IS NOT TO BE PUBLISHED WITHOUT MY EXPLICIT
    WRITTEN PERMISSION ONLY.

  Copyright (c) Xander Maas, 2014

  This programm will create a tcp based server, which translates the
  commands sent from (another) device over TCP/IP to the I2C command(s)
  which will be sent over the I2C bus of the RPi
"""
import smbus
import logging

class i2cBoard(object):
	# The address this board belongs to
	address = 0x00

	# Did we identify the board as 'real'
	identified = False

	# Is a board installed on the mentioned address
	installed = False

	# What is the firmware version of the board
	boardVersion = '0.0.0'

	logging.basicConfig(level=logging.DEBUG)

	def identifySlaveBoard(self):
		idByte1 = unichr(self.bus.read_byte_data(self.address, 10))
		idByte2 = unichr(self.bus.read_byte_data(self.address, 11))
		idByte3 = unichr(self.bus.read_byte_data(self.address, 12))
		idByte4 = unichr(self.bus.read_byte_data(self.address, 13))
		identification = str(idByte1) + str(idByte2) + str(idByte3) + str(idByte4)
		if identification != 'PFXM':
			print 'Unknown board at I2C address ' + str(hex(self.address))
			print 'Received identification string: ' + identification
			return False
		else:
			return True

	def boardVersion(self):
		major = self.bus.read_byte_data(self.address, 0)
		minor = self.bus.read_byte_data(self.address, 1)
		rev = self.bus.read_byte_data(self.address, 2)
		self.version = str(major) + '.' + str(minor) + '.' + str(rev)
		return self.version

	def sendPowerFunctionCommand(self, register, command):
		logging.debug('==== i2cBoard.sendPowerFunctionCommand() ====')
		logging.debug('Received command %s for register %s', str(hex(command)), str(hex(register)))
		logging.debug('For address %s', str(hex(self.address)))
		self.bus.write_byte_data(self.address, register, command)

	def __init__(self, address = 0x40, i2cBus = 0):
		self.bus = i2cBus
		self.address = address

		try:
			if self.identifySlaveBoard():
				self.identified = True
				self.boardVersion()
			else:
				self.identified = False
			self.installed = True
		except:
      # Something went wrong, e.g. no board with this address installed
			self.installed = False

if __name__ == "__main__":
	print 'i2cBoard.py'
