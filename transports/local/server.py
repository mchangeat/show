import os
from shell_transport import ShellTransportd
import threading
import time
import tempfile

class Server(ShellTransportd):
	def __init__(self, showd):
		self.showd = showd
		
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
		
	
	def _read_new_connections(self):
		while True:
			#that line contains the shell id, the number of rows and columns of the client terminal
			self.rtube = open(self.tube, 'r')
			r = self.rtube.read()
			self.rtube.close()
			id = r.split(",")[0].strip()
			rows = int(r.split(",")[1])
			columns = int(r.split(",")[2])
			
			self.showd.init_session(id, columns, rows)

class ServerInstance:
	def __init__(self, showd, id):
		self.showd = showd
		self.id = id
		self.lock = threading.Lock()
		self.key_input = ""
		
	def start(self):
		self.ctod = tempfile.gettempdir() + os.path.sep + "ctod-" + str(self.id)
		self.dtoc = tempfile.gettempdir() + os.path.sep + "dtoc-" + str(self.id)
		try:
			if os.path.exists(self.dtoc) == False:
				os.mkfifo(self.dtoc)
				os.chmod(self.dtoc, 0666)
			#if os.path.exists(self.ctod) == False:
			#	os.mkfifo(self.ctod)
			#	os.chmod(self.ctod, 0666)
		except OSError:
			pass
			
		clock = threading.Thread(target=self._update_time, args=())
		clock.daemon = True
		clock.start()
		
		clock_inputs = threading.Thread(target=self._read_inputs, args=())
		clock_inputs.daemon = True
		clock_inputs.start()
		
		self.showd.log_info("local transport started")
		
	def _read_inputs(self):
		
		while True:
			self.rctod = open(self.ctod, 'r')
			r = self.rctod.read()
			self.showd.log_debug("read :"+r)
			self.rctod.close()
			
			self.lock.acquire()
			self.key_input = self.key_input + r
			self.lock.release()

	def _update_time(self):
		
		while True:
			self.lock.acquire()
			input = self.key_input
			self.key_input = ""
			self.lock.release()
			screen = self.showd.update(self.id, input)
			if screen != "":
				self.rdtoc = open(self.dtoc, 'w+')
				self.rdtoc.write(screen)
				self.rdtoc.close()
			
			time.sleep(0.1)