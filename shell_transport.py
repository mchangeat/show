import json

class ShellTransportd:
	def update(self, sessionId, clientId, input):
		pass
	


class ShellTransportc:
	def update(self, id, input, columns, rows):
		pass

'''
Object used between client and server
'''
class TransportMessage:
	CMD_INIT_SESSION = "init_session"
	CMD_LIST_SESSIONS  = "list_sessions"
	CMD_CLOSE_CLIENT = "close_client"
	CMD_CLOSE_SESSION = "close_session"
	
	def __init__(self, clientId, sessionId, cmd):
		self.clientId = clientId
		self.sessionId = sessionId
		self.cmd = cmd
	
	def setSessionId(self, sessionId):
		self.sessionId = sessionId
		
	def setDimension(self, columns, rows):
		self.columns = columns
		self.rows = rows
	
	@staticmethod
	def from_JSON(string):
		ts = TransportMessage(None, None, None)
		ts.__dict__ = json.loads(string)
		return ts
	
	def to_JSON(self):
		return json.dumps(self, default=lambda o: o.__dict__,  sort_keys=True)	
