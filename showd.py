#!/usr/bin/env python

from ajaxterm import Multiplex
import time
import optparse
import glob
import sys
import imp
import logging

class Showd:
	def __init__(self,cmd=None, module=None): #module must contain a Server class
		logging.basicConfig(filename='showd.log',level=logging.DEBUG)
		self.multi = Multiplex(cmd)
		self.sessions = {}
		self.last_dump = ""
		self.module = module
		if module is not None:
			try:
				self.shell_transport = module.Server(self)
			except:
				print "Problem with transport module, dying..."
				self.multi.die()
				sys.exit(1)
	
	def _create_session(self, id, columns, rows):
		if not (columns > 2 and columns < 256 and rows > 2 and rows < 100):
				columns, rows= 80, 25
		term = self.multi.create(columns, rows)
		self.sessions[id] = term
		
		return term
	
	def init_session(self, id, columns, rows):
		if id in self.sessions:
			#term = self.sessions[id]
			#TODO : update dimensions
			self.log_info("existing session")
		else:
			term = self._create_session(id, columns, rows)
			self.log_info("new connection id:"+id+" rows:"+str(rows)+" cols:"+str(columns))
			server_instance = self.module.ServerInstance(self, id)
			server_instance.start()
		
	def log_debug(self, msg):
		logging.debug("showd - " + msg)	

	def log_info(self, msg):
		logging.info("showd - " + msg)
	
	def update(self, id, input):
		ret = result = ""
		if id in self.sessions:
			term = self.sessions[id]
		
			if input:
				self.multi.proc_write(term, input)
			time.sleep(0.002)
			dump=self.multi.dump(term, 1, False)
			
			if isinstance(dump,str):
				result = dump
			else:
				result="wrong"
				del self.sessions[id]
			
			#check if something new has appeared on the screen
			#if not return nothing
			ret = result
			if result == self.last_dump:
				ret = ""
			self.last_dump = result
		
		return ret


if __name__ == '__main__':
	parser = optparse.OptionParser()
	parser.add_option("-l", "--list", dest="list",action="store_true", help="List available transports")
	parser.add_option("-t", "--transport", dest="transport",default=None, help="Transport to use")
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
			module = imp.load_source('server', "transports/" + o.transport + "/server.py")
		
		showd = Showd(None, module)
	