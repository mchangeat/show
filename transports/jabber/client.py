
from shell_transport import ShellTransportc
from showd import Showd
import xmpp
import threading


username = 'showc'
passwd = '12078122'
to='showd@crypt.am'

class Client(ShellTransportc):
	def __init__(self, showc):
		self.showc = showc
		self.client = xmpp.Client('crypt.am') #,debug=[])
		self.client._DEBUG._fh=open("jabber_remote_shellc.log",'w')
		
		self.client.connect(server=('crypt.am',5222))
		self.client.auth(username, passwd, 'showc')
		self.client.sendInitPresence()
		#self.lock = threading.Lock()
		self.client.RegisterHandler('message',self.xmpp_message)
		
		self.clock = threading.Thread(target=self.update_time, args=())
		self.clock.daemon = True
		self.clock.start()
		
	def update_time(self):
		while True:
			self.client.Process(1)

	def xmpp_message(self, con, event):
		self.showc.update(event.getBody())
		
	def send(self, input):
		message = xmpp.Message(to, input)
		message.setAttr('type', 'chat')
		self.client.send(message)
