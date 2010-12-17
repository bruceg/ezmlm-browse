import cgitb
cgitb.enable()
import cgi
import email
import os
import sys
import time
import zipfile
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
	pathstr = pathstr.lstrip('/')
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

file_content_types = {
	'css': 'text/css',
	'png': 'image/png',
	'gif': 'image/gif',
	'jpg': 'image/jpeg',
	'jpeg': 'image/jpeg',
	}

def main_file(filename):
	path = os.path.join('files', filename)
	try:
		st = os.stat(path)
		timestamp = st.st_mtime
		data = open(path).read()
	except OSError:
		zf = zipfile.ZipFile(sys.argv[0])
		data = zf.open(path).read()
		timestamp = time.mktime(zf.getinfo(path).date_time + (0, 0, 0))
	timestamp = time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime(timestamp))
	ext = filename[filename.rindex('.')+1:].lower()
	ct = file_content_types[ext]
	sys.stdout.write('Content-Type: %s\r\n'
					 'Content-Length: %i\r\n'
					 'Last-Modified: %s\r\n'
					 '\r\n' % ( ct, len(data), timestamp ))
	sys.stdout.write(data)
	sys.stdout.flush()
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
	try:
		path = os.environ['PATH_INFO']
	except KeyError:
		path = None
	else:
		if path.startswith('/files/'):
			main_file(path[7:])

	global ctxt
	ctxt = context.ctxt = context.Context()
	# Insert the environment (CGI) variables
	ctxt.update(os.environ)
	# Update with defaults from the config
	ctxt.update(config.defaults)
	# Update with all cookies
	for c in Cookie.SimpleCookie(os.environ.get('HTTP_COOKIE', '')).values():
		ctxt[c.key] = c.value
	fixup_config()

	global form
	form = context.form = load_form()
	ctxt.update(form)

	# Override certain context values based on configured settings
	ctxt[ALLOWRAW] = config.allowraw
	ctxt[FILESPREFIX] = config.filesprefix or os.environ['SCRIPT_NAME'] + '/files/'

	if path is not None:
		main_path(path)
	else:
		main_form()
