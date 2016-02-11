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
		#	if os.path.exists(self.tube) == False:
		#		os.mkfifo(self.tube)
			#if os.path.exists(self.dtoc) == False:
		#		os.mkfifo(self.dtoc)
			if os.path.exists(self.ctod) == False:
				os.mkfifo(self.ctod)
		except OSError:
			pass
		
		self.clock = threading.Thread(target=self._update_time, args=())
		self.clock.daemon = True
		self.clock.start()
		

	def _update_time(self):
		time.sleep(1)
		while True:
			self.rdtoc = open(self.dtoc, 'r')
			input = self.rdtoc.read()
			self.rdtoc.close()
			self.showc.update(input)
	
		
	def send(self, input):
		self.rctod = open(self.ctod, 'w+')
		self.rctod.write(input)
		self.rctod.close()
	
	def init_session(self, id, columns, rows):
		self.rtube = open(self.tube, 'w+')
		self.rtube.write(str(id)+","+str(columns)+","+str(rows))
		self.rtube.close()
		

#if __name__ == '__main__':
#	showc = ShellLocalTransportc(None)
#	showc.clock.join()