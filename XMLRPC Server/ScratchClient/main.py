#!/usr/bin/env python
"""
	Scratch Client for Lego PowerFunctions I2C

	File:           main.py
	Author:         Xander Maas
	Version:        1.0.1
	Date:           01 feb 2015

	Version history:
	1.0     31 jan 2015 -   Initial release
	1.0.1   01 feb 2015 -   Just added version information switch
                                Also updated the source files with additional
                                comments

	LICENSE INFO:
	AS FOR NOW THIS SOFTWARE IS NOT TO BE PUBLISHED WITHOUT MY EXPLICIT
	WRITTEN PERMISSION ONLY.

	Copyright (c)  Xander Maas, 2015

	This program creates a client which can be used with the broadcast messages
	in Scratch (version 1.4).
"""

import scratch
from subprocess import call
import sys
import getopt
from pfExtended import *
from pfDirect import *
from pfSingle import *
from pfCombo import *
from xmlClient import *

_server = 'localhost'
_xmlserver = 'http://localhost:9000'
_debug = False

def main(argv):
	if (processCmdLine(argv) == False):
		# Actually we shouldn't get here (??)
		print " Something went terribly wrong, please find out why"
		sys.exit(2)
	if (_debug == True):
		print " DEBUG >>"
		print ""
		print " Scratch Server: " + _server
		print ""
		print " << DEBUG"

	# Setup the scratch object
	scratch = setupScratch(_server)

	# Process the received broadcast messages
	for msg in listen(scratch):
		# Listen for a broadcast from Scratch, ignore everything else
		if msg[0] != 'broadcast':
			continue

		data = msg[1].split()

		"""
		We have defined our Scratch message as 
		 		PF_IC <channel> <mode> <options/commands>
		
		<channel>  is the Lego PowerFunctions channel from 1 to 4
		<mode>     is the powerfunctions. The following modes are available
		               - Direct
		               - Extended
		               - Single
		               - Combo
		<options>  is mode dependent
		"""
		# We expect a broadcast message of 5 objects
		if data[0].upper() != 'PF_I2C':
			continue

		# First we have to test what type of command we want to send
		# as this determines the number of arguments
		if data[2].upper() == 'EXTENDED':
			"""
			For an extended command we expect the following arguments:
			 - channel <1...4>
			 - command (BRK | INCA | DECA | TOGB)

			 BRK  =  Break, then float on A
			 INCA =  Increase on A
			 DECA =  Decrease on A
			 TOGB =  Toggle forward/float on B
			"""
			numArgs = 4
			if testArgs(data, numArgs) == False:
				continue
			channel = data[1]
			if testChannel(channel) == False:
				continue

			cmd = pfExtended().createCommand(channel, data[3])
			if cmd == False:
				print 'Error'
				continue

			# Send the command
			if (_debug == True):
				print 'Command to be send: (int) ' + str(hex(cmd))
				print 'For channel: ' + channel
				print ' *+*+*+*+*+*+*+*+*+*+*+*'
			sendCommand(channel, cmd)
			
			if _debug == True:
				print 'Extended command: ' + str(hex(cmd))
		elif data[2].upper() == 'DIRECT':
			"""
			For a direct command, we expect the following arguments:
			 	data[1] = Channel (1...4)
				data[2] = Command Type
				data[3] = Command Output A (FLTA | FWDA | REVA | BRKA)
				data[4] = Command Output B (FLTB | FWDB | REVB | BRKB)
			"""
			numArgs = 5
			if testArgs(data, numArgs) == False:
				continue

			channel = data[1]
			if testChannel(channel) == False:
				continue

			commandA = data[3].upper()
			commandB = data[4].upper()

			cmd = pfDirect().createCommand(channel, commandA, commandB)
			if cmd == False:
				print 'Error'
				continue

			# Send the command to the XML-RPC Server
			sendCommand(channel, cmd)
			if (_debug == True):
				print 'Command to be send: (int) ' + str(hex(cmd))

			if _debug == True:
				print 'Direct command: ' + str(hex(cmd))
		elif data[2].upper() == "SINGLE":
			"""
			To send a command to a single output
				data[1] = channel
				data[2] = Command type
				data[3] = Output (Red or Blue)
				data[4] = Data (FLT | FWD1...7 | BRK | REV1...7)
			"""
			# Mode should be PWM, so mode = 0 for bit 0x2
			mode = 0x0
			
			numArgs = 5
			if testArgs(data, numArgs) == False:
				continue
			
			channel = data[1]
			if testChannel(channel) == False:
				continue
			
			output = data[3]
			print 'Output: ' + output[0]
			if output[0].upper() not in ('R', 'B'):
				print 'Wrong output selected: ' + output.upper()
				print 'Expected RED or BLUE'
				continue

			cmd = pfSingle().createCommand(channel, output, data[4].upper())
			if cmd == False:
				print 'Error'
				continue

			# Send the command to the XML-RPC Server
			sendCommand(channel, cmd)


			if (_debug == True):
				print 'Single PWM Command: ' + str(hex(cmd))
		elif data[2].upper() == "COMBO":
			"""
			To send a command to both outputs simultanous
				data[1] = Channel
				data[2] = Command Type
				data[3] = Command Output A (Red)
				data[4] = Command Output B (Blue)

				Command is (FLT | FWD1...7 | BRK | REV1...7)
			"""
			numArgs = 5
			if testArgs(data, numArgs) == False:
				continue

			commandA = data[3].upper()
			commandB = data[4].upper()

			channel = data[1]
			if testChannel(channel) == False:
				continue

			cmd = pfCombo().createCommand(channel, commandA, commandB)
			if cmd == False:
				print 'Error'
				continue

			# Send the command to the XML-RPC Server
			sendCommand(channel, cmd)

			if (_debug == True):
				print 'Combo PWM command ' + str(hex(cmd))
		elif data[2].upper() == 'CSTID':
			print 'Command not implemented, yet'
			continue
		else:
			print 'Wrong command received: ' + data[2].upper()
			continue

def sendCommand(channel, command):
	client = xmlClient(_xmlserver)
	
	client.sendCommand(int(channel), command)

def testChannel(channel):
	# Test if the channel is in the range 1 - 4
	if channel not in [str(c) for c in range(1, 5)]:
		print ' Wrong channel, not in range 1...4: ' + channel
		return False
	else:
		return True

		"""

		Must be used for PWM mode!
		# Extract the color we want to address
		if data[2][0].upper() not in ('R', 'B'):
			print "Incorrect color received, not red nor blue: "+ data[2]
			continue
		color = data[2][0].upper()
		"""

def testArgs(args, numArgs):
	if len(args) > numArgs:
		print 'Number of arguments is incorrect, ' + str(numArgs) + ' required, ' + str(len(args)) + ' given'
		return False
	return True

def setupScratch(host):
	s = scratch.Scratch(host=host)
	return s

# Send and receive Scratch messages
def listen(server):
	while True:
		try:
			yield server.receive()
		except scratch.ScratchError:
			raise stopIteration

def processCmdLine(argv):
	try:
		opts, args = getopt.getopt(argv, "dhs:vx:", ["debug", "help", "server=", "xmlserver=", "version"])
		if len(opts) == 0:
			usage()
			sys.exit(2)
	except getopt.GetoptError as e:
		print(e)
		usage()
		sys.exit(2)
	
	for opt, arg in opts:
		if opt in ("-h", "--help"):
			usage()
			sys.exit()
		elif opt in ("-d", "--debug"):
			print " Showing Debug info"
			global _debug
			_debug = True
		elif opt in ("-s", "--server"):
			if (arg == "" or arg == None):
				usage()
				sys.exit(2)
			global _server
			_server = arg
		elif opt in ("-v", "--version"):
			print "Scratch Client for Lego PowerFunctions I2C"
			print "Version 1.0"
			print ""
			sys.exit(0)
		elif opt in ("-x", "--xmlserver"):
			if (arg == "" or arg == None):
				usage()
				sys.exit(2)
			global _xmlserver
			_xmlserver = arg
	return True

def usage():
	print "Usage: " + sys.argv[0] + " -s server -x XML-RPC-server [-dh]"
	print ""
	print " -s, --server=      The computer on which Scratch is sending/receiving"
	print "                    broadcast messages"
	print " -x, -xmlserver     IP address of XML-RPC server, e.g. http://127.0.0.1:9000"
	print " -d, --debug        Enable debug logging"
	print " -h, --help         Show this information"
	print " -v, --version      Show version information"
	print ""

if __name__ == "__main__":
	main(sys.argv[1:])
