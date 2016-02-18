from shell_transport import ShellTransportc
from array import array
import os
import threading
import tempfile
import time

class Client(ShellTransportc):
	def __init__(self, showc, id):
		self.showc = showc
		self.tube = tempfile.gettempdir() + os.path.sep + "tube"
		self.ctod = tempfile.gettempdir() + os.path.sep + "ctod-" + str(id)
		self.dtoc = tempfile.gettempdir() + os.path.sep + "dtoc-" + str(id)
		
		try:
			if os.path.exists(self.ctod) == False:
				os.mkfifo(self.ctod)
		except OSError:
			pass
		
		self.clock = threading.Thread(target=self._update_time, args=())
		self.clock.daemon = True
		self.clock.start()
		self.showc.log_info("local transport started")

	def _update_time(self):
		time.sleep(1)
		while True:
			self.showc.log_debug("wait for message")
			self.rdtoc = open(self.dtoc, 'r')
			input = self.rdtoc.read()
			#self.showc.log_debug("input:"+input)
			self.rdtoc.close()
			self.showc.update(input)
	
		
	def send(self, input):
		self.rctod = open(self.ctod, 'w+')
		self.rctod.write(input)
		self.rctod.close()
	
	def init_session(self, id, columns, rows):
		self.rtube = open(self.tube, 'w+')
		self.rtube.write(str(id)+","+str(rows)+","+str(columns))
		self.rtube.close()
		

	def close(self):
		self.showc.log_info("close")
		try:
			self.rctod.close()
			self.rdtoc.close()
		except OSError:
			pass