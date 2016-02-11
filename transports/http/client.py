
from shell_transport import ShellTransportc
from showd import Showd

class ShellHTTPTransportc(ShellTransportc):
	def update(self, id, input, columns, rows):
		print "update"