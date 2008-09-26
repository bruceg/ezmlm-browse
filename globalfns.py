import email
import os
import re
import sys
import time

from globals import *
import config

write = sys.stdout.write

###############################################################################
# Template fetching
_template_cache = { }
_template_path = sys.path[:2]
_rx_percent = re.compile('%([^(])')
def template(filename):
	global _template_cache
	global _template_path
	try:
		f = _template_cache[filename]
	except KeyError:
		n = os.path.join('html', filename.replace('/', ':'))
		f = ''
		for dir in _template_path:
			try:
				f = open(os.path.join(dir, n)).read()
				break
			except IOError:
				pass
		_template_cache[filename] = f
	return f

def html(name):
	return template(name + '.html')

def xml(name):
	return template(name + '.xml')

###############################################################################
def _build_base():
	try:
		base = os.environ['SCRIPT_URI']
	except KeyError:
		port = int(os.environ['SERVER_PORT'])
		script = os.environ['SCRIPT_NAME']
		if port == 443:
			base = 'https://'
		else:
			base = 'http://'
		base += os.environ['SERVER_NAME']
		if port <> 443 and port <> 80:
			base += ':%d' % port
		base += script
	return base

def _make_menubar(ctxt):
	if not ctxt[LIST]:
		return ''
	if ctxt[COMMAND] == 'monthbydate':
		ctxt['idxcmd'] = 'monthbydate'
	else:
		ctxt['idxcmd'] = 'monthbythread'
	return html('menubar') % ctxt

###############################################################################
def header(ctxt, title, classbase):
	write('Content-Type: text/html; charset=utf-8\r\n\r\n')
	ctxt[BASE] = _build_base()
	ctxt[TITLE] = title
	ctxt[CLASS] = classbase
	if ctxt.has_key(LIST):
		ctxt[MENUBAR] = _make_menubar(ctxt)
	else:
		ctxt[MENUBAR] = ''
	write(html('header') % ctxt)

def footer(ctxt):
	write(html('footer') % ctxt)
	#print "<!--"
	#for item in os.environ.items():
	#	print "%s=%s" % item
	#print "-->"
	sys.exit(0)

###############################################################################
def die(ctxt, msg):
	ctxt['message'] = msg
	header(ctxt, 'Error', 'error')
	write(html('error') % ctxt)
	footer(ctxt)

def diesys(ctxt, a, b):
	ctxt['message'] = a
	ctxt['error'] = b
	header(ctxt, 'System Error', 'error')
	write(html('syserror') % ctxt)
	footer(ctxt)

###############################################################################
# Output commands
def do_list(ctxt, name, perpage, values, peritem=None):
	perpage = int(perpage)
	ctxt.push()
	ctxt[ROW] = 0
	write('<table class=%s>' % name)
	if perpage > 0:
		page = int(ctxt.get(PAGE, 1)) - 1
		pages = (len(values) + perpage - 1) / perpage
		page = max(0, min(pages, page))
		start = page * perpage
		ctxt[PAGE] = page + 1
		ctxt[PAGES] = pages
		write(html('pager') % ctxt)
		values = values[start:start+perpage]

	write(html(name+'-head') % ctxt)
	template = html(name+'-item')
	for value in values:
		ctxt.update(value)
		write(template % ctxt)
		if peritem:
			peritem()
		ctxt[ROW] += 1

	write(html(name+'-tail') % ctxt)
	if perpage > 0:
		write(html('pager') % ctxt)
	write('</table>')
	ctxt.pop()

###############################################################################
# Subcommands
###############################################################################
def rec_thread(ctxt):
	ctxt.push()
	write(html('rthread-head') % ctxt)
	item = html('rthread-item')
	format_timestamps(ctxt, ctxt[THREADS])
	for t in ctxt[THREADS]:
		ctxt.update(t)
		write(item % ctxt)
		rec_thread(ctxt)
	write(html('rthread-tail') % ctxt)
	ctxt.pop()

def sub_showpart(ctxt, part):
	body = part.get_payload(decode=1)
	charset = part.get_content_charset(config.charsets['default'])
	charset = config.charsets.get(charset, charset) or charset
	ctxt[CHARSET] = charset
	try:
		body = unicode(body, charset, 'replace').encode('utf-8')
	except LookupError:
		pass
	ctxt[BODY] = body
	type = ctxt[TYPE] = part.get_content_type()
	ctxt[FILENAME] = part.get_filename()
	template = html('msg-' + type.replace('/', '-'))
	if not template:
		template = html('msg-other')
	write(template % ctxt)

def rec_noshowpart(ctxt, part, partnum):
	ctxt[PART] = partnum
	ctxt[TYPE] = part.get_content_type()
	# FIXME: show something here
	if part.is_multipart():
		for p in part.get_payload():
			partnum = rec_noshowpart(ctxt, p, partnum+1)
	else:
		return partnum + 1
	return partnum

def rec_showpart(ctxt, part, partnum):
	ctxt[PART] = partnum
	ctxt[TYPE] = part.get_content_type()
	if part.is_multipart():
		# handle alternative parts differently
		if part.get_content_subtype() == 'alternative':
			m = { }
			for p in part.get_payload():
				m[p.get_content_type()] = p
			try:
				altpart = m[ctxt[ALTPART]]
			except KeyError:
				try:
					altpart = m['text/plain']
				except KeyError:
					altpart = part.get_payload()[0]
			for p in part.get_payload():
				if p is altpart:
					partnum = rec_showpart(ctxt, p, partnum+1)
				else:
					partnum = rec_noshowpart(ctxt, p, partnum+1)
		else:
			for p in part.get_payload():
				partnum = rec_showpart(ctxt, p, partnum+1)
	else:
		write(html('msg-sep') % ctxt)
		sub_showpart(ctxt, part)
		return partnum + 1
	return partnum

def sub_showmsg(ctxt, msgnum):
	ezmlm = ctxt[EZMLM]
	ctxt.push()
	ctxt.update(ezmlm.index[msgnum])
	msg = email.message_from_file(ezmlm.open(msgnum))
	ctxt[MESSAGE] = msg
	format_timestamp(ctxt, ctxt)
	write(html('msg-header') % ctxt)
	rec_showpart(ctxt, msg, 0)
	write(html('msg-footer') % ctxt)
	ctxt.pop()

def format_timestamp(ctxt, msg):
	if ctxt[TZ] and ctxt[TZ] <> 'None' and \
	   ctxt[FORMATTIME] and ctxt[FORMATTIME] <> 'None':
		msg[TIMESTR] = time.strftime(ctxt[FORMATTIME],
									 time.localtime(msg[TIMESTAMP]))
	else:
		msg[TIMESTR] = ctxt[DATE]
	return msg[TIMESTR]

def format_timestamps(ctxt, list):
	if ctxt[TZ] and ctxt[TZ] <> 'None' and \
	   ctxt[FORMATTIME] and ctxt[FORMATTIME] <> 'None':
		format = ctxt[FORMATTIME]
		for item in list:
			item[TIMESTR] = time.strftime(format,
										  time.localtime(item[TIMESTAMP]))
	else:
		for item in list:
			item[TIMESTR] = item[DATE]
	return list
