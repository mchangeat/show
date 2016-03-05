#!/usr/bin/env python
import time
import os
import curses 
import base64
import signal
import sys
import random
import optparse
import glob
import imp
import traceback
import logging
from shell_transport import TransportMessage

class Showc:
	def __init__(self, module, sessionId, cmd): #module must contain a Client class
		logging.basicConfig(filename='showc.log',level=logging.DEBUG)
		self.sessionId = sessionId
		self.cmd = cmd
		self.clientId = random.randint(1, 100000)
		if module is not None:
			try:
				self.shell_transport = module.Client(self, self.clientId, self.sessionId)
			except:
				print "Wrong transport module, dying..."
				traceback.print_exc(file=sys.stdout)
				sys.exit(1)
		
		self.key_input = ""
		self.quitting = False
		self.last_screen = ""
		
		#read the number of rows and columns of the screen
		r, c = os.popen('stty size', 'r').read().split()
		self.rows = int(r) -1
		self.columns = int(c)
		
		signal.signal(signal.SIGINT, self.signal_handler)
	
	def log_debug(self, msg):
		logging.debug("showc - " + msg)	

	def log_info(self, msg):
		logging.info("showc - " + msg)
	
	#update screen if not empty
	def update(self, screen):
		if self.quitting:
			for i in range(0, self.rows):
				if i == self.rows / 2:
					str = "Are you sure you want to leave client session (y/n)?"
					self.screen.addstr(i, 0, "".ljust((self.columns - len(str))/2, " ") + str.ljust((self.columns - len(str))/2, " "))
				else:
					self.screen.addstr(i, 0, "".ljust(self.columns, " "))
		elif screen != "":
			self.last_screen = screen
			lines = screen.split("\n")
			for i in range(0, self.rows):
				if i < len(lines):
					self.screen.addstr(i, 0, lines[i].replace("\n","").ljust(self.columns, " "))
			self.screen.refresh()
	
	def start(self):
		#first send the id, and the number of rows and columns of the current terminal
		self.shell_transport.init_session(self.columns, self.rows, self.cmd)
		
		os.environ.setdefault('ESCDELAY', '25')
		self.screen = curses.initscr() 
		curses.noecho() 
		curses.curs_set(0) 
		self.screen.keypad(1) 
		
		#get user key inputs
		self.key_input= ""
		echap_nb_press = 0
		try:
			while True: 
				event = self.screen.getch() 
				
				if self.quitting:
					if event == 121: #y key
						break
					else:
						self.quitting = False
						self.update(self.last_screen)
				
				if event == 27: # ECHAP
					echap_nb_press = echap_nb_press + 1
				else:
					echap_nb_press = 0
				
				if echap_nb_press == 2:
					self.quitting = True
					self.update("")
				
				#some keys must send a special code
				if event == curses.KEY_ENTER:
					self.add_input("%20")
				elif event == curses.KEY_BACKSPACE:
					self.add_input(base64.b64decode("fw=="))
				elif event == curses.KEY_DC:
					self.add_input(base64.b64decode("G1szfg=="))
				elif event == curses.KEY_HOME:
					self.add_input(base64.b64decode("G1sxfg=="))
				elif event == curses.KEY_F1:
					self.add_input(base64.b64decode("G1tbQQ=="))
				elif event == curses.KEY_F2:
					self.add_input(base64.b64decode("G1tbQg=="))
				elif event == curses.KEY_F3:
					self.add_input(base64.b64decode("G1tbQw=="))
				elif event == curses.KEY_F4:
					self.add_input(base64.b64decode("G1tbRA=="))
				elif event == curses.KEY_F5:
					self.add_input(base64.b64decode("G1tbRQ=="))
				elif event == curses.KEY_F6:
					self.add_input(base64.b64decode("G1sxN34="))
				elif event == curses.KEY_F7:
					self.add_input(base64.b64decode("G1sxOH4="))
				elif event == curses.KEY_F8:
					self.add_input(base64.b64decode("G1sxOX4="))
				elif event == curses.KEY_F9:
					self.add_input(base64.b64decode("G1syMH4="))
				elif event == curses.KEY_F10:
					self.add_input(base64.b64decode("G1syMX4="))
				elif event == curses.KEY_F11:
					self.add_input(base64.b64decode("G1syM34="))
				elif event == curses.KEY_F12:
					self.add_input(base64.b64decode("G1syNH4="))
				elif event == curses.KEY_END:
					self.add_input(base64.b64decode("G1s0fg=="))
				elif event == curses.KEY_UP:
					self.add_input(base64.b64decode("G1tB"))
				elif event == curses.KEY_DOWN:
					self.add_input(base64.b64decode("G1tC"))
				elif event == curses.KEY_LEFT:
					self.add_input(base64.b64decode("G1tE"))
				elif event == curses.KEY_RIGHT:
					self.add_input(base64.b64decode("G1tD"))
				elif event > 0:
						self.add_input(chr(event))
			
				self.shell_transport.send(self.get_input())
		finally:
			self.close_shell()
		
		print "Leaving session"
	
	def close_shell(self):
		curses.nocbreak();
		self.screen.keypad(0);
		curses.echo()
		curses.endwin()
		self.shell_transport.close()
	
	#return input and empty the current input buffer
	def get_input(self):
		ret = self.key_input
		self.key_input = ""
		
		return ret
	
	
	def add_input(self, input):
		self.key_input = self.key_input + input
		
	def signal_handler(self, signal, frame):
		#add ctrl+c input
		self.add_input(base64.b64decode("Aw=="))
		
	
if __name__ == '__main__':
	parser = optparse.OptionParser()
	parser.add_option("-l", "--list", dest="list",action="store_true", help="List available transports")
	parser.add_option("-t", "--transport", dest="transport",default=None, help="Transport to use")
	parser.add_option("-r", "--resume", dest="sessionId",default=None, help="Resume session id")
	parser.add_option("-s", "--sessions", dest="sessions",action="store_true", help="List session ids")
	(o, a) = parser.parse_args()
	
	#list transports
	if o.list:
		for path in glob.glob("transports/*"):
			print path.split("/")[1]
	else:
		module = None
		if not o.transport:
			parser.error("Transport must be set, use -l to list all available transports")
		else:
			module = imp.load_source('client', "transports/" + o.transport + "/client.py")
		
		cmd = None
		if o.sessions:
			cmd = TransportMessage.CMD_LIST_SESSIONS
		
		showc = Showc(module, o.sessionId, cmd)
		showc.start()

