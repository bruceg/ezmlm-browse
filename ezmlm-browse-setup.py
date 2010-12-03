import getopt
import os
import sys

argv0 = sys.argv[0]

def die_usage():
	print 'usage: %s [options] DESTPATH TARGET.cgi' % argv0
	print '  Options:'
	print '  --apache -- Create a .htaccess file for Apache'
	print '  --setuid -- Copy in a setuid wrapper program'
	sys.exit(1)

try:
	opts,args = getopt.getopt(sys.argv[1:], '',
							  [ 'apache', 'setuid' ])
	opts = dict(opts)
except getopt.GetoptError, x:
	print '%s: Invalid option: %s' % (argv0, x)
	die_usage()

if len(args) == 2:
	destbase,target = args
else:
	die_usage()

srcbase = os.getcwd()

def destpath(name):
	return os.path.join(destbase, name)

def srcpath(name):
	return os.path.join(srcbase, name)

def copyfile(srcname, destname=None, mode=None):
	data = file(srcpath(srcname)).read()
	dest = destpath(destname or srcname)
	file(dest, 'w').write(data)
	if mode:
		os.chmod(dest, mode)

if not os.path.isdir(destbase):
	os.mkdir(destbase, 0777)

try:
	os.unlink(destpath(target))
except:
	pass

if '--setuid' in opts:
	if os.getuid() == 0 or os.getgid() == 0:
		print '"%s: NEVER use the --setuid option as root' % argv0
		sys.exit(1)
	copyfile('wrapper', target, 06711)
else:
	copyfile('ezmlm-browse', target, 0755)

if not os.path.exists(destpath('ezmlm-browse.ini')):
	copyfile('ezmlm-browse.ini')

if '--apache' in opts:
	f = open(destpath('.htaccess'), 'w')
	f.write('DirectoryIndex %s\n'
			'AddHandler cgi-script .cgi\n'
			'Options +ExecCGI\n' % target)
	f.close()

print 'ezmlm-browse has been set up in "%s"' % destbase
print 'Make sure to edit "%s" for your lists' % destpath('ezmlm-browse.ini')
