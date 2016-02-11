
from shell_transport import ShellTransportd
from showd import Showd

class ShellHTTPTransportd(ShellTransportd):
	def update(self, id, input, columns, rows):
		print "update"