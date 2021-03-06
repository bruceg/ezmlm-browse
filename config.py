from ConfigParser import SafeConfigParser
import os
import sys

_config = SafeConfigParser()
_config.read([ os.path.join(d,'ezmlm-browse.ini')
			   for d in ['']+sys.path[:2] ])

basedir = _config.get('global', 'basedir')
basehost = _config.get('global', 'basehost')
if _config.has_option('global', 'filesprefix'):
	filesprefix = _config.get('global', 'filesprefix')
else:
	filesprefix = ''
try:
	allowraw = _config.getboolean('global', 'allowraw')
except:
	allowraw = False
try:
	allowraw_image = _config.getboolean('global', 'allowraw_image')
except:
	allowraw_image = True
try:
	mask_emails = _config.getboolean('global', 'mask_emails')
except:
	mask_emails = True

if 'styles' in _config.sections():
	styles = [ ]
	for css in _config.options('styles'):
		styles.append((css, _config.get('styles', css)))
else:
	styles = [ None ]

charsets = {
	# the charset used if none is declared
	# standards define this to be us-ascii, change at your own peril
	'default': 'us-ascii',
	# first, the superset maps:
	'us-ascii': 'windows-1252',
	'iso-8859-1': 'windows-1252',
	'iso-8859-8-i': 'iso-8859-8',
	'ks_c_5601-1987': 'euc-kr',
	# second, the educated guesses:
	'x-unknown': 'windows-1252',
	'x-user-defined': 'windows-1252',
	'unknown-8bit': 'windows-1252',
	}

if 'charsets' in _config.sections():
	charsets.update(dict(_config.items('charsets')))

# Hard-coded defaults
defaults = {
	'alt_part': 'text/plain',
	'cmd': 'months',
	'date_sort': 'ascending',
	'feedmsgs': 10,
	'feedtype': 'atom',
	'format_time': '',
	'list': '',
	'msgsperpage': 10,
	'perpage': 20,
	'style': '',
	'wrapwidth': 0,
	'terms': '',
	'tz': '',
	}

defaults.update(dict(_config.items('defaults')))

def _parse_archive(config, section, name):
	global basedir, basehost
	archive = dict(config.items(section))
	archive.setdefault('listdesc', name)
	if archive.has_key('listdir'):
		archive['listdir'] = os.path.join(basedir, archive['listdir'])
	else:
		archive['listdir'] = os.path.join(basedir, name)
	archive.setdefault('listemail', '%s@%s' % (name,basehost))
	archive.setdefault('listsub', '%s-subscribe@%s' % (name,basehost))
	return archive

def _parse_archives(config):
	archives = { }
	for section in config.sections():
		if section[:8] == 'archive:':
			name = section[8:]
			archives[name] = _parse_archive(config, section, name)
	return archives

archives = _parse_archives(_config)
