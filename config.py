from ConfigParser import SafeConfigParser
import os
import sys

_config = SafeConfigParser()
_config.read([ os.path.join(d,'ezmlm-browse.ini')
			   for d in sys.path[:2] ])

basedir = _config.get('global', 'basedir')
basehost = _config.get('global', 'basehost')
allowraw = _config.getboolean('global', 'allowraw')
mask_emails = _config.getboolean('global', 'mask_emails')

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

defaults = dict(_config.items('defaults'))

def _parse_archive(config, section, name):
	archive = dict(config.items(section))
	archive.setdefault('listdesc', name)
	archive.setdefault('listdir', os.path.join(basedir, name))
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
