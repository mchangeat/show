import os
from shell_transport import ShellTransportd
from shell_transport import TransportMessage
import threading
import time
import tempfile
import logging

class Server(ShellTransportd):
	def __init__(self, showd):
		self.showd = showd
		logging.info("Starting server local transport")
		
		self.tube = tempfile.gettempdir() + os.path.sep +"tube"
		
		try:
			if os.path.exists(self.tube) == False:
				os.mkfifo(self.tube)
				os.chmod(self.tube, 0666)
		except OSError:
			pass
			
		clock_inputs = threading.Thread(target=self._read_new_connections, args=())
		clock_inputs.daemon = True
		clock_inputs.start()
		logging.info("server local transport started")
		
	
	def _read_new_connections(self):
		while True:
			#that line contains the shell sessionId, the number of rows and columns of the client terminal
			self.rtube = open(self.tube, 'r')
			r = self.rtube.read()
			self.rtube.close()
			
			msg = TransportMessage.from_JSON(r)
			
			logging.debug("msg received:"+r)
			
			if msg.cmd == TransportMessage.CMD_INIT_SESSION:
				self.showd.init_session(msg.clientId, msg.sessionId, msg.columns, msg.rows)
			elif msg.cmd == TransportMessage.CMD_LIST_SESSIONS:
				self.showd.list_sessions(msg.clientId)
			else:
				logging.info("Bad command received:"+str(msg.cmd))

class ServerInstance:
	def __init__(self, showd, clientId, sessionId):
		self.showd = showd
		self.clientId = clientId
		self.sessionId = sessionId
		self.lock = threading.Lock()
		self.key_input = ""
		self.stopped = False
		self.last_dump = ""
		
		self.ctod = tempfile.gettempdir() + os.path.sep + "ctod-" + str(self.clientId)
		self.dtoc = tempfile.gettempdir() + os.path.sep + "dtoc-" + str(self.clientId)
		try:
			if os.path.exists(self.dtoc) == False:
				os.mkfifo(self.dtoc)
				os.chmod(self.dtoc, 0666)
		except OSError:
			pass
		
	def start(self):
		clock = threading.Thread(target=self._update_time, args=())
		clock.daemon = True
		clock.start()
		
		clock_inputs = threading.Thread(target=self._read_inputs, args=())
		clock_inputs.daemon = True
		clock_inputs.start()
		
		logging.info("local transport %s started" % self.clientId)
	
	def stop(self):
		logging.info("local transport stopping")
		self.stopped = True
		
	def _read_inputs(self):
		
		while not self.stopped:
			self.rctod = open(self.ctod, 'r')
			r = self.rctod.read()
			logging.debug("read :"+r)
			self.rctod.close()
			
			if not self.stopped:
				self.lock.acquire()
				self.key_input = self.key_input + r
				self.lock.release()
		
		logging.debug("local transport %s thread _read_inputs stopped" % self.clientId)

	def _update_time(self):
		input = ""
		while not self.stopped:
			screen = self.showd.update(self.sessionId, self.clientId, input)
			if len(screen) > 0 and self.last_dump != screen:
				logging.debug("screen for %s: %s" % (self.clientId, screen))
				self.rdtoc = open(self.dtoc, 'w+')
				self.rdtoc.write(screen)
				self.rdtoc.close()
				self.last_dump = screen
			
			if not self.stopped:
				self.lock.acquire()
				input = self.key_input
				self.key_input = ""
				self.lock.release()
			
			time.sleep(0.1)
		
		logging.debug("local transport %s thread _update_time stopped" % self.clientId)
	
	def __del__(self):
		logging.info("local transport %s stopped" % self.clientId)