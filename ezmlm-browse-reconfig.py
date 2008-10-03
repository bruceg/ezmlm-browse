import os
import sys

ini = 'ezmlm-browse.ini'

argv0 = sys.argv[0]
if len(sys.argv) == 2:
	src = sys.argv[1]
	dst = os.path.join(os.path.dirname(src), ini)
elif len(sys.argv) == 3:
	src = sys.argv[1]
	dst = sys.argv[2]
else:
	print "usage: %s config.py [ezmlm-browse.ini]" % argv0
	sys.exit(1)

config = { }
execfile(src, config)

defaults = config.get('defaults', {})
styles = config.get('styles', [])
archives = config.get('archives', [])

if os.path.exists(dst):
	print 'Error: Destination file "%s" already exists.' % dst
	sys.exit(1)

out = file(dst, 'w')

out.write('[global]\n')
out.write('allowraw = %s\n' % (
	config.get('allowraw', 'false') and 'true' or 'false'))
out.write('allowraw_image = true\n')
out.write('mask_emails = %s\n' % (
	config.get('mask_emails', 'false') and 'true' or 'false'))
out.write('basedir = %s\n' % config['basedir'])
out.write('basehost = %s\n' % config['basehost'])
out.write('filesprefix = %s\n' % defaults['filesprefix'])
out.write('\n')

out.write('[defaults]\n')
for item in defaults.items():
	out.write('%s = %s\n' % item)
out.write('\n')

out.write('[styles]\n')
for style in styles:
	if type(style) is type(''):
		style = (style, 'None')
	out.write('%s = %s\n' % style)
out.write('\n')

for archive in archives:
	out.write('[archive:%s]\n' % archive)
	archive = archives[archive]
	for item in archive.items():
		out.write('%s = %s\n' % item)
	out.write('\n')
