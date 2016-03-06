from shell_transport import ShellTransportc
from shell_transport import TransportMessage
from array import array
import os
import threading
import tempfile
import logging
import time

class Client(ShellTransportc):
	def __init__(self, showc, clientId, sessionId):
		self.showc = showc
		self.clientId = clientId
		self.sessionId = sessionId
		self.tube = tempfile.gettempdir() + os.path.sep + "tube"
		self.ctod = tempfile.gettempdir() + os.path.sep + "ctod-" + str(clientId)
		self.dtoc = tempfile.gettempdir() + os.path.sep + "dtoc-" + str(clientId)
		self.rctod = None
		self.rdtoc = None
		
		try:
			if os.path.exists(self.ctod) == False:
				os.mkfifo(self.ctod)
			if os.path.exists(self.dtoc) == False:
			 	os.mkfifo(self.dtoc)
		except OSError:
			pass
		
	def _update_time(self):
		while True:
			logging.debug("wait for message clientId " + self.clientId)
			self.rdtoc = open(self.dtoc, 'r')
			input = self.rdtoc.read()
			logging.debug("input:"+input)
			self.rdtoc.close()
			self.showc.update(input)
	
		
	def send(self, input):
		self.rctod = open(self.ctod, 'w+')
		self.rctod.write(input)
		self.rctod.close()
	
	def init_session(self, columns, rows, cmd=TransportMessage.CMD_INIT_SESSION):
		if cmd is None:
			cmd = TransportMessage.CMD_INIT_SESSION
		msg = TransportMessage(self.clientId, self.sessionId, cmd)
		msg.setDimension(columns, rows)
		self.rtube = open(self.tube, 'w+')
		self.rtube.write(msg.to_JSON())
		self.rtube.close()
		
		self.clock = threading.Thread(target=self._update_time, args=())
		self.clock.daemon = True
		logging.info("local transport started clientId" + self.clientId)
		self.clock.start()
		

	def close(self):
		logging.info("close clientId " + self.clientId)
		try:
			if self.rctod is not None:
				self.rctod.close()
			if self.rdtoc is not None:
				self.rdtoc.close()
		except OSError:
			pass