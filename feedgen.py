from globals import *
from globalfns import *
import time

class Feed:
	def __init__(self, prefix, ctype):
		self.ctype = ctype
		self.prefix = prefix

	def generate(self, ctxt, msgs):
		header = xml(self.prefix + '-head')
		entry = xml(self.prefix + '-item')
		footer = xml(self.prefix + '-tail')
		ctxt['timestamp'] = msgs[0][TIMESTAMP]
		write("Content-Type: %s; charset=utf-8\r\n\r\n" % self.ctype)
		write(header % ctxt)
		ctxt.push()
		for msg in msgs:
			ctxt.update(msg)
			write(entry % ctxt)
		ctxt.pop()
		write(footer % ctxt)

atom = Feed('atom', 'application/atom+xml')
rss2 = Feed('rss2', 'application/rss+xml')

types = {
	'atom': atom,
	'rss': rss2,
	'rss2': rss2,
	}
