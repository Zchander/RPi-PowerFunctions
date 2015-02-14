"""
  LEGO PowerFunctions I2C Server

  File:       main.py
  Author:     Xander Maas <xander@xjmaas.nl>
  Date:       12 feb 2015

  Version history:
     1.0     10 oct 2014 -   Initial version
     1.1     12 feb 2015 -   Added supoport for newer models

  LICENSE INFO:
    AS FOR NOW THIS SOFTWARE IS NOT TO BE PUBLISHED WITHOUT MY EXPLICIT
    WRITTEN PERMISSION ONLY.

  Copyright (c) Xander Maas, 2014-2015

  This programm will create a tcp based server, which translates the
  commands sent from (another) device over TCP/IP to the I2C command(s)
  which will be sent over the I2C bus of the RPi
"""
import smbus
from rpi_detect_model import *

class i2c(object):
	# Just initialize the I2C Channel
	i2cChannel = 0

	# The I2C bus object
	bus = 0x00

	def setSMBus(self):
		self.bus = smbus.SMBus(self.i2cChannel)

	def determineRpiModel(self):
		rpiModel = ModelInfo()
		"""
		if rpiModel.model == "B" and rpiModel.ram_mb > 256:
			self.i2cChannel = 1
		else:
			self.i2cChannel = 0
		"""
		if rpiModel.ram_mb < 512:
			# Seems all 256MB  models have I2C on channel 0
			self.i2cChannel = 0
		else:
			self.i2cChannel = 1
		print 'We are running on a ' + str(rpiModel)

	def sendPowerFunctionCommand(register, cmd = 0x00):
		self.bus.write_byte_address(self.address, register, cmd)

	def __init__(self):

		# Determine the I2C channel we have to use, based on the
		# RPi model
		self.determineRpiModel()
		
		# Set the I2C bus we want to use, based on the RPi model
		self.setSMBus()

if __name__ == "__main__":
	print 'i2c.py'

