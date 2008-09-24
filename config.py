from ConfigParser import SafeConfigParser
import os
import sys

_config = SafeConfigParser()
_config.read([ os.path.join(d,'config.ini')
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
