# Copyright (C) 2003 Bruce Guenter <bruceg@em.ca>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

import re
import sys
import time
import types

from globals import *
import ezmlm
import config

ctxt = None
form = None

###############################################################################
# Context functions
def iif(cond, truestr, falsestr=''):
	global ctxt
	if cond:
		return truestr % ctxt
	return falsestr % ctxt

def escape(str, escapes):
    for (needle, replacement) in escapes:
        str = str.replace(needle, replacement)
    return str

_html_escapes = ( ('&', '&amp;'),
				  ('<', '&lt;'),
				  ('>', '&gt;'),
				  ('"', '&quot;') )

def escape_html(str): return escape(str, _html_escapes)

_url_escapes = ( ('%', '%25'),
				 (' ', '%20'),
				 ('&', '%26'),
				 ('?', '%3f'),
				 (':', '%3a'),
				 (';', '%3b'),
				 ('+', '%2b') )

def escape_url(str):  return escape(str, _url_escapes)

def nl2br(str): return str.replace('\n', '<br />')

rx_url = re.compile(r'([^\s\"]+://[^\s\"]+)')
def markup_urls(str): return rx_url.sub(r'<a href="\1">\1</a>', str)

#rx_addr = re.compile(r'<[^>@]+@[^>]+>')
rx_addr = re.compile(r'\S+@\S+\.\S+')
def mask_email(str):
	if config.mask_emails:
		return rx_addr.sub('####@####.####', str)
	return str

def wordwrap(str):
	try:
		width = int(ctxt.get(WRAPWIDTH, 0))
	except:
		return str
	if not width:
		return str
	out = []
	for line in str.split('\n'):
		while len(line) > width:
			# Try to break the line on the first space before the width.
			space = line.rfind(' ', 0, width)
			if space == -1:
				# None found, now fall back to the first space on the line.
				space = line.find(' ')
				if space == -1:
					# No spaces found, no word-wrapping can be done.
					break
			# If the remainder of the line is empty, don't do anything.
			nextline = line[space+1:].lstrip()
			if not nextline:
				break
			out.append(line[:space])
			line = nextline
		out.append(line)
	return '\n'.join(out)

def relurl(**kw):
	# Put certain keywords in a fixed order
	pre = []
	for key in (LIST, COMMAND):
		try:
			pre.append((key,kw[key]))
			del kw[key]
		except KeyError:
			pass
	kw = kw.items()
	kw.sort()
	kw = pre + kw
	kw = map(lambda val:"%s=%s"%(val[0],escape_url(str(val[1]))), kw)
	return '?%s' % ('&'.join(kw))

def absurl(**kw):
	global ctxt
	return ''.join(('http://',
					ctxt['SERVER_NAME'],
					ctxt['SCRIPT_NAME'],
					apply(relurl, (), kw)))

def relink(text, classname, **kw):
	return '<a class="%s" href="%s">%s</a>' % (
		classname, apply(relurl, (), kw), text)

def cmdlink(text, classname, command, **kw):
	global ctxt
	kw[COMMAND] = command
	kw[LIST] = ctxt[LIST]
	return apply(relink, (text, classname), kw)

def optlink(text, classname, dolink, command, **kw):
	if dolink:
		return apply(cmdlink, (text, classname, command), kw)
	else:
		return '<span class="%s">%s</span>' % (classname, text)

def pagelink(text, classname, index):
	global ctxt
	global form
	index = max(1, min(ctxt[PAGES], index))
	if index == ctxt[PAGE]:
		return '<span class="%s">%s</span>' % (classname, text)
	kw = form.copy()
	kw[PAGE] = index
	return apply(relink, (text, classname), kw)

def msgsubjlink(msg, **kw):
	global ctxt
	if type(msg) is types.IntType:
		kw[MSGNUM] = msg
		msg = ctxt[EZMLM].index[msg]
	else:
		kw[MSGNUM] = msg[MSGNUM]
	return apply(cmdlink, (msg[SUBJECT], 'subject', 'showmsg'), kw)

def msgauthlink(msg, **kw):
	global ctxt
	if type(msg) is types.IntType:
		msg = ctxt[EZMLM].index[msg]
	kw[AUTHORID] = msg[AUTHORID]
	return apply(cmdlink, (msg[AUTHOR], 'author', 'author'), kw)

def threadlink(text, classname, index):
	global ctxt
	index = max(1, min(ctxt['threadlen'], index))
	if index == ctxt[PAGE]:
		return '<span class="%s">%s</span>' % (classname, text)
	kw = form.copy()
	kw[MSGNUM] = ctxt[MESSAGES][index-1][MSGNUM]
	return apply(relink, (text, classname), kw)

def selectlist(name, list, value=None, options=''):
	s = ['<select name=%s %s>' % (name, options)]
	for option in list:
		selected = ''
		try:
			(ovalue,oname) = option
			if ovalue == value:
				selected = ' selected'
			s.append('<option value="%s"%s>%s' % (
				escape_html(ovalue), selected, escape_html(oname) ))
		except:
			if option == value:
				selected = ' selected'
			s.append('<option%s>%s' % ( selected, escape_html(option) ))
	s.append('</select>')
	return '\n'.join(s)

def monthname(number):
	if number >= 100000:
		number %= 100
	return ezmlm.month_names[number]

def isogmtime(ts):
	return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(float(ts)))

def rfc822gmtime(ts):
	return time.strftime('%a, %d %b %Y %H:%M:%S GMT',
						 time.gmtime(float(ts)))

###############################################################################
# Context management

global_context = {
    'math': __import__('math'),
    'random': __import__('random'),
    're': __import__('re'),
    'time': __import__('time'),
    'version': __import__('version'),

	'absurl': absurl,
	'cmdlink': cmdlink,
	'config': config,
	'format_timestamp': lambda msg:format_timestamp(ctxt, msg),
	'iif': iif,
	'isogmtime': isogmtime,
	'html': escape_html,
	'markup_urls': markup_urls,
	'mask_email': mask_email,
	'wordwrap': wordwrap,
	'msgauthlink': msgauthlink,
	'msgsubjlink': msgsubjlink,
	'monthname': monthname,
	'nl2br': nl2br,
	'optlink': optlink,
	'pagelink': pagelink,
	'relink': relink,
	'relurl': relurl,
	'rfc822gmtime': rfc822gmtime,
	'selectlist': selectlist,
	'threadlink': threadlink,
	'url': escape_url,
    }

class Context:
	def __init__(self):
		global global_context
		self.stack = [ {} ]
		self.globals = global_context.copy()
		self.pop()
	def pop(self):
		self.dict = self.stack.pop()
		self.get = self.dict.get
		self.has_key = self.dict.has_key
		self.items = self.dict.items
		self.iteritems = self.dict.iteritems
		self.iterkeys = self.dict.iterkeys
		self.itervalues = self.dict.itervalues
		self.keys = self.dict.keys
		self.setdefault = self.dict.setdefault
		self.values = self.dict.values
		self.update = self.dict.update
		self.__str__ = self.dict.__str__
		self.__repr__ = self.dict.__repr__
		# These need to be special cased :/
		self.globals['defined'] = self.dict.has_key
	def copy(self):
		return Context(self.dict.copy(), self.globals)
	def push(self):
		self.stack.append(self.dict.copy())
	def eval(self, body):
		return eval(body, self.globals, self.dict)
	def execute(self, body):
		exec(body, self.globals, self.dict)
	def __getitem__(self, key):
		try:
			return self.dict[key]
		except KeyError:
			return self.eval(key)
	def __setitem__(self, key, val):
		self.dict[key] = val
