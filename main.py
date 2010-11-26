import cgitb
cgitb.enable()
import cgi
import email
import os
import re
import sys
import time
import types
import Cookie

import ezmlm
from globals import *
from globalfns import *
import context

import config

ctxt = None
form = None

###############################################################################
# Fixup configuration values
def fixup_config():
	for name in config.archives.keys():
		l = config.archives[name]
		if l.has_key(LISTDIR):
			l[LISTDIR] = os.path.join(config.basedir, l[LISTDIR])
		else:
			l[LISTDIR] = os.path.join(config.basedir, name)
		if not l.has_key(LISTEMAIL):
			l[LISTEMAIL] = '%s@%s' % (name, config.basehost)
		if not l.has_key(LISTSUB):
			l[LISTSUB] = '%s-subscribe@%s' % (name, config.basehost)

###############################################################################
# Context functions
def iif(cond, truestr, falsestr=''):
	global ctxt
	if cond:
		return truestr % ctxt
	return falsestr % ctxt

def defined(name):
	global ctxt
	return ctxt.has_key(name)

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

def update_global_context():
	context.global_context.update({
		'absurl': absurl,
		'cmdlink': cmdlink,
		'config': config,
		'defined': defined,
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
		})

###############################################################################
# Main routine
###############################################################################
def load_form():
	#if not os.environ['QUERY_STRING']:
	#	return { }
	cgi.maxlen = 64*1024
	cgiform = cgi.FieldStorage()
	form = { }
	for key in cgiform.keys():
		item = cgiform[key]
		if type(item) is not type([]) and \
		   not item.file:
			form[key] = item.value
	return form

def setup_list():
	global ctxt
	list = ctxt[LIST]
	if list:
		try:
			base = config.archives[list]
		except KeyError:
			die(ctxt, 'Unknown list: ' + list)
		ctxt.update(base)
		eza = ctxt[EZMLM] = ezmlm.EzmlmArchive(ctxt[LISTDIR])
		if ctxt.has_key(MSGNUM):
			ctxt.update(eza.index[ctxt[MSGNUM]])
		if ctxt.has_key(THREADID):
			ctxt.update(eza.thread(ctxt[THREADID]))
		eza.set_months(ctxt)
	if ctxt[TZ] and ctxt[TZ] <> 'None':
		os.environ['TZ'] = ctxt[TZ]

def die_no_download():
	global ctxt
	die(ctxt, "Downloading raw messages is administratively prohibited.")

def dump_part(part):
	global ctxt
	if not config.allowraw \
		   and not ( part.get_content_maintype() == 'image'
					 and config.allowraw_image ):
		die_no_download()
	write('Content-Type: %s; charset=%s\r\n\r\n' % (
		part.get_content_type(),
		part.get_content_charset('us-ascii').lower()))
	write(part.get_payload(decode=1))

def main_path(pathstr):
	# FIXME: handle ?part=#.#.#&filename=string
	# and then convert sub_showmsg et al to use the same notation
	global ctxt
	if not config.allowraw and not config.allowraw_image:
		die_no_download()
	while pathstr[0] == '/':
		pathstr = pathstr[1:]
	path = pathstr.split('/')
	ctxt[LIST] = path[0]
	try:
		msgnum = int(path[1])
	except:
		die(ctxt, "Invalid path: " + pathstr)
	setup_list()
	msg = ctxt[EZMLM].open(msgnum)
	if ctxt.has_key(PART):
		parts = map(int, ctxt[PART].split('.'))
		part = msg
		# FIXME: What the heck am I supposed to be doing with these numbers?!?
		if parts[0] != 1:
			raise ValueError
		parts = parts[1:]
		while parts:
			part = part.get_payload()[parts[0]]
			parts = parts[1:]
		dump_part(part)
	else:
		try:
			partnum = int(path[2])
			for part in msg.walk():
				if partnum <= 0:
					break
				partnum -= 1
			dump_part(part)
		except:
			if not config.allowraw:
				die_no_download()
				
			write('Content-Type: message/rfc822\r\n\r\n')
			buf = msg.read(8192)
			while buf:
				write(buf)
				buf = msg.read(8192)
	sys.exit(0)

def import_command(command):
	commands = __import__('commands', fromlist=[command])
	try:
		return getattr(commands, command)
	except AttributeError:
		raise ImportError, "Could not locate command: " + command

def main_form():
	global ctxt
	setup_list()
	if ctxt.has_key('command'): ctxt[COMMAND] = ctxt['command']
	if '/' in ctxt[COMMAND]:
		die(ctxt, "Invalid command")
	if not ctxt[LIST]:
		ctxt[COMMAND] = 'lists'
	try:
		module = import_command(ctxt[COMMAND])
	except ImportError:
		die(ctxt, "Invalid command")
	module.do(ctxt)

def main():
	update_global_context()
	global ctxt
	ctxt = context.Context()
	# Insert the environment (CGI) variables
	ctxt.update(os.environ)
	# Set up hard-coded defaults
	ctxt[ALTPART] = 'text/plain'
	ctxt[COMMAND] = 'months'
	ctxt[DATESORT] = 'ascending'
	ctxt[FEEDMSGS] = 10
	ctxt[FEEDTYPE] = 'atom'
	ctxt[FORMATTIME] = ''
	ctxt[LIST] = ''
	ctxt[MSGSPERPAGE] = 10
	ctxt[PERPAGE] = 20
	ctxt[STYLE] = ''
	ctxt[WRAPWIDTH] = 0
	ctxt[TERMS] = ''
	ctxt[TZ] = ''
	# Update with defaults from the config
	ctxt.update(config.defaults)
	# Update with all cookies
	for c in Cookie.SimpleCookie(os.environ.get('HTTP_COOKIE', '')).values():
		ctxt[c.key] = c.value
	fixup_config()

	global form
	form = load_form()
	ctxt.update(form)

	# Override certain context values based on configured settings
	ctxt[ALLOWRAW] = config.allowraw
	ctxt[FILESPREFIX] = config.filesprefix

	try:
		path = os.environ['PATH_INFO']
		main_path(path)
	except KeyError:
		pass
	main_form()
