from globals import *
from globalfns import *
import time

class Feed:
	def __init__(self, header, entry, footer):
		self.header = header
		self.entry = entry
		self.footer = footer

feedtypes = {
	'atom': Feed(
'''Content-Type: application/atom+xml\r
\r
<?xml version="1.0" encoding="iso-8859-1"?>
<feed version="0.3"
      xmlns="http://purl.org/atom/ns#draft-ietf-atompub-format-03">
 <head>
  <title>%(listdesc)s</title>
  <link href="%(html(absurl(list=list)))s"/>
  <updated>%(now)s</updated>
  <author>
   <name>%(listemail)s</name>
  </author>
  <generator url="http://untroubled.org/ezmlm-browse/"
             version="%(version.version)s">
   %(version.full)s
  </generator>
 </head>
''',
''' <entry>
  <title>%(subject)s</title>
  <link rel="alternate"
        type="text/html"
        href="%(html(absurl(list=list,cmd='showmsg',msgnum=msgnum)))s"/>
  <id>%(html(absurl(list=list,cmd='showmsg',msgnum=msgnum)))s</id>
  <author>
   <name>%(author)s</name>
  </author>
  <updated>%(isotime)s</updated>
 </entry>
''',
'''</feed>
'''),
	}

def fmttime(t=None):
	if not t:
		t = time.time()
	return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(t))

###############################################################################
# Command: Generate news feed
###############################################################################
def do(ctxt):
	feedtype = feedtypes[ctxt[FEEDTYPE]]
	# Set a hard maximum on the number of messages to reduce DoS attacks
	count = min(int(ctxt[FEEDMSGS]), 100)
	ctxt['now'] = fmttime()
	write(feedtype.header % ctxt)
	num = ctxt[EZMLM].num
	ctxt.push()
	while count > 0 and num > 0:
		try:
			ctxt.update(ctxt[EZMLM].index[num])
			ctxt['isotime'] = fmttime(ctxt[TIMESTAMP])
			write(feedtype.entry % ctxt)
			count -= 1
		except KeyError:
			pass
		num -= 1
	ctxt.pop()
	write(feedtype.footer % ctxt)
