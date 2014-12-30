#!/usr/bin/python -u
"""
  LEGO PowerFunctions I2C Server

  File:		main.py
  Author:	Xander Maas <xander@xjmaas.nl>
  Date:		10 oct 2014

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

# Our import(s)
#from tcpServer import *
from i2c import *
from i2cBoard import *
from xmlServer import *
import logging
import smbus

i2cBoards = []
i2cBus = i2c().bus

if __name__ == '__main__':
	print 'Running'
	print 'Identifying/detecting boards'
	addressRange = range(0x40, 0x43)
	for i in addressRange:
		board = i2cBoard(i, i2cBus)
		if board.installed == True:
			i2cBoards.append(board)

	for board in i2cBoards:
		if board.identified == True:
			print 'Seems we have a legit board at the address ' + hex(board.address)
			print 'Board version: ' + board.version

	# Set up our logging
	logging.basicConfig(level=logging.DEBUG)

	# Next we initialize our XMLRPC Server
	server = xmlServer('0.0.0.0', 9000)
	logging.debug('Just asked the server to start')

	# Define our function(s)
	def installedBoards():
		logging.debug('==== main.installedBoards() ====')
		return boardsDict()

	def returnVersion():
		logging.debug('==== main.returnVersion() ====')
		return '1.0'

	def pfCommand(command, channel = 1):
		logging.debug('==== main.pfCommand() ====')
		logging.debug('Received a PowerFunctions Command => %s', str(hex(command)))
		logging.debug('for channel => %d', channel)
		
		# Test if the channel within bounds (1 ... 4)
		if (channel < 0 or channel > 4):
			logging.debug('Seems the requested channel is out of bounds')
			return dict(status = False, description = 'Channel out of bounds')

		# Test if the requested channel is available (board installed/connected)
		boardAvailable = channelAvailable(channel)
		address = boardAvailable['address']
		if boardAvailable['status'] == False:
			logging.debug('Seems the requested channel is unavailable (board %s not installed)', str(hex(address)))
			return dict(status = False, description = 'Channel (board ' + str(hex(address)) + ') not installed')

		# Seems we got an available channel/board, next we have to send the
		# command to the board
		logging.debug('Going to send the command %s to the requested board %s', str(hex(command)), str(hex(address)))
		logging.debug('We got %d boards', len(i2cBoards))
		sendCommand(command, boardAvailable['board'])

		# Give our client a status to act on
		return dict(status = True, description = 'Success')

	# Register the functions
	server.server.register_function(installedBoards)
	server.server.register_function(returnVersion)
	server.server.register_function(pfCommand)

	# Send the command to the board
	def sendCommand(command, board):
		logging.debug('==== main.sendCommand() ====')
		# First we have to break up our command into two (2) bytes
		lowByte = command & 0xff # should give 0x17
		highByte = command >> 8 # should give 0x81
		logging.debug('Sending command to board => %s', str(hex(board.address)))
		logging.debug('Command => %s %s',  str(hex(highByte)), str(hex(lowByte)))

		# Now we've got our seperated bytes, we can send them.
		# lowByte goes into register 0x30
		# highByte goes into register 0x31
		board.sendPowerFunctionCommand(30, lowByte)
		board.sendPowerFunctionCommand(31, highByte)

	# Test if the channel is available
	def channelAvailable(channel = 1):
		logging.debug('==== main.channelAvailable() ====')
		i2cAddress = 0x40 + (channel - 1)
		logging.debug('We want to send a command to I2C device at address %s', str(hex(i2cAddress)))
		for board in i2cBoards:
			if board.address == i2cAddress:
				logging.debug('We found the requested board')
				return dict(status = True, board = board, address =  i2cAddress)
				break
		return dict(status = False, board = board, address = i2cAddress)

	# We have to convert our i2cBoards array to something we can return
	def boardsDict():
		logging.debug('==== main.boardsDict() ====')
		boards = []
		for board in i2cBoards:
			boards.append(dict(address = hex(board.address), version = board.version))
		return boards

	try:
		print 'Use Control-C to exit)'
		server.server.serve_forever()
	except KeyboardInterrupt:
		print 'Exiting'
