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
      xmlns="http://purl.org/atom/ns#">
 <title>%(listdesc)s</title>
 <link rel="alternate"
       type="text/html"
       href="%(html(absurl(list=list)))s"/>
 <modified>%(time.strftime("%Y-%m-%dT%H:%M:%S",time.gmtime(timestamp)))s</modified>
 <author>
  <name>%(listemail)s</name>
 </author>
 <generator url="http://untroubled.org/ezmlm-browse/"
            version="%(version.version)s">
  %(version.full)s
 </generator>
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
  <issued>%(time.strftime("%Y-%m-%dT%H:%M:%S",time.gmtime(timestamp)))s</issued>
  <modified>%(time.strftime("%Y-%m-%dT%H:%M:%S",time.gmtime(timestamp)))s</modified>
 </entry>
''',
'''</feed>
'''),
	}

###############################################################################
# Command: Generate news feed
###############################################################################
def do(ctxt):
	feedtype = feedtypes[ctxt[FEEDTYPE]]
	# Set a hard maximum on the number of messages to reduce DoS attacks
	count = min(int(ctxt[FEEDMSGS]), 100)
	num = ctxt[EZMLM].num
	msgs = []
	while len(msgs) < count and num > 0:
		try:
			msgs.append(ctxt[EZMLM].index[num])
		except KeyError:
			pass
		num -= 1
	ctxt['timestamp'] = msgs[0][TIMESTAMP]
	write(feedtype.header % ctxt)
	num = ctxt[EZMLM].num
	ctxt.push()
	for msg in msgs:
		ctxt.update(msg)
		write(feedtype.entry % ctxt)
	ctxt.pop()
	write(feedtype.footer % ctxt)