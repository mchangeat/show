
from shell_transport import ShellTransportd
import threading
import time
import xmpp

username = 'showd'
passwd = '12078122'
to='showc@crypt.am'

class Server(ShellTransportd):
	def __init__(self, showd):
		self.lock = threading.Lock()
		self.key_input = ""
		self.columns = 80
		self.rows = 25
		self.id = 0
		self.showd = showd
		
		self.client = xmpp.Client('crypt.am') #,debug=[])
		self.client._DEBUG._fh=open("jabber_remote_shelld.log",'w')
		
		self.client.connect(server=('crypt.am',5222))
		self.client.auth(username, passwd, 'showc')
		self.client.sendInitPresence()
		#self.lock = threading.Lock()
		self.client.RegisterHandler('message',self.xmpp_message)
		while True:
			self.client.Process(1)
		
	def xmpp_message(self, con, event):
		msg = event.getBody()
		
		if self.id == 0:
			self.id = msg.split(",")[0]
			self.rows = int(msg.split(",")[1])
			self.columns = int(msg.split(",")[2])
			
			print "new connection id:"+self.id+" rows:"+str(self.rows)+" cols:"+str(self.columns)
			
			clock = threading.Thread(target=self.update_time, args=())
			clock.daemon = True
			clock.start()
		else:
			self.lock.acquire()
			self.key_input = self.key_input + msg
			self.lock.release()
		
		#type = event.getType()
		#fromjid = event.getFrom().getStripped()
		#if type in ['message', 'chat', None] and fromjid == self.remotejid:
			#self.received_msg = event.getBody()
		#print event.getBody()
		
		#self.lock.release()

	def update_time(self):
		
		while True:
			self.lock.acquire()
			input = self.key_input
			self.key_input = ""
			self.lock.release()
			screen = self.showd.update(self.id, input, 1, self.columns, self.rows)
			if screen != "":
				message = xmpp.Message(to, screen)
				message.setAttr('type', 'chat')
				self.client.send(message)
			
			time.sleep(0.1)