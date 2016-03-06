#!/usr/bin/env python

from ajaxterm import Multiplex
import time
import optparse
import glob
import sys
import imp
import logging
import logging.config
import uuid

class Showd:
	def __init__(self,cmd=None, module=None): #module must contain a Server class
		logging.config.fileConfig('showd_logging.ini')
		logging.info("Starting showd")
		self.multi = Multiplex(cmd)
		self.sessions = {}
		self.threads = {}
		#self.last_dump = ""
		self.module = module
		if module is not None:
			try:
				self.shell_transport = module.Server(self)
			except:
				print "Problem with transport module, dying..."
				self.multi.die()
				sys.exit(1)
		
		logging.info("Showd started")
	
	def _create_session(self, columns, rows):
		if not (columns > 2 and columns < 256 and rows > 2 and rows < 100):
				columns, rows= 80, 25
		term = self.multi.create(columns, rows)
		
		sessionId = str(uuid.uuid4())
		self.sessions[sessionId] = term
		
		return term, sessionId
	
	def init_session(self, clientId, sessionId, columns, rows):
		if sessionId is not None and sessionId in self.sessions:
			#TODO : update dimensions
			logging.info("existing session : "+str(sessionId))
			term = self.sessions[sessionId]
		else:
			term, sessionId = self._create_session(columns, rows)
			logging.info("new connection sessionId:"+str(sessionId)+" cols:"+str(columns)+" rows:"+str(rows))
			
		server_instance = self.module.ServerInstance(self, clientId, sessionId)
		self.add_thread(clientId, server_instance)
		server_instance.start()
	
	def add_thread(self, clientId, server_instance):
		if clientId in self.threads:
			self.threads[clientId].stop()
		
		self.threads[clientId] = server_instance
	
	def stop_thread(self, clientId):
		self.threads[clientId].stop()
		del self.threads[clientId]
		
	def list_sessions(self, clientId):
		#todo handle rights
		sessionId = str(uuid.uuid4())
		logging.info("new sessionId for list_sessions :"+str(sessionId))
		self.sessions[sessionId] = 'Current opened sessions:\n- ' + '\n- '.join(map(str,sorted(self.sessions)))
		server_instance = self.module.ServerInstance(self, clientId, sessionId)
		self.add_thread(clientId, server_instance)
		server_instance.start()
	
	def log_debug(self, msg):
		logging.debug("showd - " + msg)	

	def log_info(self, msg):
		logging.info("showd - " + msg)
	
	def update(self, sessionId, clientId, input):
		ret = result = ""
		stop = False
		if sessionId in self.sessions:
			o = self.sessions[sessionId]
			if isinstance(o,str):
				#this is a command
				ret = o
				del self.sessions[sessionId]
				self.stop_thread(clientId)
			else: #this is a terminal
				term = o
				if input:
					self.multi.proc_write(term, input)
				time.sleep(0.002)
				dump=self.multi.dump(term, 1, False)
				
				if isinstance(dump,str):
					ret = dump
				else:
					ret="wrong"
					del self.sessions[sessionId]
				
				#check if something new has appeared on the screen
				#if not return nothing
				#ret = result
				#if result == self.last_dump:
				#	ret = ""
				#self.last_dump = result
		
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
	