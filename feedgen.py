from globals import *
from globalfns import *
import time

class Feed:
	def __init__(self, ctype, header, entry, footer):
		self.ctype = ctype
		self.header = header
		self.entry = entry
		self.footer = footer

	def generate(self, ctxt, msgs):
		ctxt['timestamp'] = msgs[0][TIMESTAMP]
		write("Content-Type: %s\r\n\r\n" % self.ctype)
		write(self.header % ctxt)
		ctxt.push()
		for msg in msgs:
			ctxt.update(msg)
			write(self.entry % ctxt)
		ctxt.pop()
		write(self.footer % ctxt)

atom = Feed('application/atom+xml',
'''<?xml version="1.0" encoding="iso-8859-1"?>
<feed version="0.3"
      xmlns="http://purl.org/atom/ns#">
 <title>%(html(listdesc))s</title>
 <link rel="alternate"
       type="text/html"
       href="%(html(absurl(list=list)))s"/>
 <modified>%(isogmtime(timestamp))s</modified>
 <author>
  <name>%(html(listemail))s</name>
 </author>
 <generator url="http://untroubled.org/ezmlm-browse/"
            version="%(version.version)s">
  %(version.full)s
 </generator>
''',
''' <entry>
  <title>%(html(subject))s</title>
  <link rel="alternate"
        type="text/html"
        href="%(html(absurl(list=list,cmd='showmsg',msgnum=msgnum)))s"/>
  <id>%(html(absurl(list=list,cmd='showmsg',msgnum=msgnum)))s</id>
  <author>
   <name>%(html(author))s</name>
  </author>
  <issued>%(isogmtime(timestamp))s</issued>
  <modified>%(isogmtime(timestamp))s</modified>
  <content><pre>From: %(html(author))s

%(html(mask_email(body)))s</pre></content>
 </entry>
''',
'''</feed>
''')

rss2 = Feed('application/rss+xml',
'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
 <channel>
  <title>%(html(listdesc))s</title>
  <link>%(html(absurl(list=list)))s</link>
  <description>%(html(listdesc))s</description>
  <lastBuildDate>%(rfc822gmtime(timestamp))s</lastBuildDate>
  <generator>%(version.full)s</generator>
''',
'''  <item>
   <title>%(html(subject))s</title>
   <link>%(html(absurl(list=list,cmd='showmsg',msgnum=msgnum)))s</link>
   <pubDate>%(rfc822gmtime(timestamp))s</pubDate>
   <description>&lt;pre&gt;From: %(html(author))s

%(html(mask_email(body)))s&lt;/pre&gt;</description>
   <guid>%(html(absurl(list=list,cmd='showmsg',msgnum=msgnum)))s</guid>
  </item>
''',
''' </channel>
</rss>
''')

types = {
	'atom': atom,
	'rss': rss2,
	'rss2': rss2,
	}
