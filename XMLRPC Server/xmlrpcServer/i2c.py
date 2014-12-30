"""
  LEGO PowerFunctions I2C Server

  File:		i2c.py
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
		if rpiModel.model == "B" and rpiModel.ram_mb > 256:
			self.i2cChannel = 1
		else:
			self.i2cChannel = 0
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

