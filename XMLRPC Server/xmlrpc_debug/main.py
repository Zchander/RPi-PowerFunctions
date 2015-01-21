#!/usr/bin/python -u
"""
  LEGO PowerFunctions I2C Server Tester

  File:		main.py
  Author:	Xander Maas <xander@xjmaas.nl>
  Version:	1.0.1
  Date:		21 January 2015

  Version history:
  1.0     30 dec 2014 -	Initial version, released on GitHub 31 dec 2014
  1.0.1	  21 jan 2015 -	Recreated version, with commandline options. Also
  						cleaned (some) code. Seems a good debug/test util
						to me ;)

  LICENSE INFO:
	This program is free software; you can redistribute it and/or modify it
	under the terms of the GNU General Public License as published by the
	Free Software Foundation; either version 2 of the License, or (at your
	option) any later version.
 
	This program is distributed in the hope that it will be useful, but
	WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	Copyright (c) Xander Maas, 2014-2015

	This program will connect to a XMLRPC server, which translates the
	commands sent from (another) device over TCP/IP to the I2C command(s)
	which will be sent over the I2C bus of the RPi
"""

import xmlrpclib
import sys
import getopt

channel = 1
command = None
server = "http://127.0.0.1:9000"
proxy = None
_debug = False

def main(argv):
	if (processCmdLine(argv) == False):
		# Actually we shouldn't get here (??)
		print "Something went terribly wrong, please find out what is was"
		sys.exit(2)

	# Show me the variables (DEBUG)
	if _debug == True:
		print "Channel: " + str(channel)
		print "Command: " + str(hex(command)) + " [type: " + str(type(command)) + "]"
		print "Server:  " + server

	# Setup the XMLRPC proxy
	proxy = xmlrpclib.ServerProxy(server, allow_none=True)

	# Before we continue, query our server to get the installed version
	serverVersion = proxy.returnVersion()

	# Next we request the installed boards
	boards = proxy.installedBoards()
	
	if _debug == True:
		print
		print "XMLRPC Server version: " + serverVersion
		print
		print "Installed boards:"
		for board in boards:
			print "  " + str(board)

	# Find out if we can send the command to the requested channel (e.g. is the board installed)
	if len(boards) < channel:
		print
		print "You cannot send a command to channel #" + str(channel) + ". The board is not installed"
		print "You have boards installed for channels:"
		print
		idx = 1
		for board in boards:
			# We reference the channels from 1, so we have to subtract 0x3f (63) from the address
			_channel = int(board["address"], 16) - 63
			_addr = board["address"]
			_version = board["version"]
			print str(idx) + ") Channel: " + str(_channel) + " (address: " + str(_addr) + " , Version: " + _version + ")"
			idx += 1
			# As we cannot continue, exit (err 2)
		print
		sys.exit(2)

	# Seems we can continue
	sendCommand(proxy, channel, command)
	
	# Just to be sure we quit ;)
	sys.exit(0)

def sendCommand(proxy, channel, command):
	result = proxy.pfCommand(command, channel)
	if result["status"] == False:
		print
		print
		print "****************"
		print "   E R R O R   *"
		print "****************"
		print
		print "Command failed: (" + result["description"] + ")"
	else:
		print
		print
		print "***************"
		print "*   D O N E   *"
		print "***************"
		print
		print

def processCmdLine(argv): 
	try:
		opts, args = getopt.getopt(argv, "c:dhk:s:", ["help", "command=", "channel=", "server="])
		if len(opts) == 0:
			usage()
			sys.exit(2)
	except getopt.GetoptError as e:
		# Output the error and show the proper usage
		print(e)
		usage()
		sys.exit(2)
	for opt, arg in opts:
		if opt in ("-h", "--help"):
			usage()
			sys.exit()
		elif opt in ("-c", "--channel"):
			global channel
			channel = int(arg)
			if (channel < 1 or channel > 4):
				print "Seems the channels are out of bound"
				usage()
				sys.exit(2)
		elif opt == "-d":
			global _debug
			_debug = True
		elif opt in ("-k", "--command"):
			global command
			command = int(arg, 16)
		elif opt in ("-s", "--server"):
			global server
			server = arg
	return True

	# Process the arguments we got
def usage():
	print "Usage: " + sys.argv[0] + " -c channel [-h] -k command -s server"
	print ""
	print " -c, --channel=(1...4)   The channel we send the command to"
	print " -h, --help              This information"
	print " -k, --command=<hex>     The command we want to send in hex, e.g. 0x8117"
	print " -s, --server=           The server we want to send the command to"
	print ""

if __name__ == "__main__":
	main(sys.argv[1:])
