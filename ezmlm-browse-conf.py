import getopt
import os
import sys

argv0 = sys.argv[0]

try:
	opts,args = getopt.getopt(sys.argv[1:], '',
							  [ 'apache', 'setuid' ])
	opts = dict(opts)
except getopt.GetoptError, x:
	print '%s: Invalid option: %s' % (argv0, x)
	sys.exit(1)

if len(args) == 2:
	destbase,target = args
	listpath = None
	hostname = None
elif len(args) == 4:
	destbase,target,listpath,hostname = args
	if listpath[0] != '/':
		print '%s: LISTPATH should start with a "/".' % argv0
		sys.exit(1)
else:
	print 'usage: %s [options] DESTPATH TARGET.cgi [ LISTPATH HOSTNAME ]' % argv0
	print '  Options:'
	print '  --apache -- Create a .htaccess file for Apache'
	print '  --setuid -- Copy in a setuid wrapper program'
	sys.exit(1)

srcbase = os.getcwd()

def destpath(name):
	return os.path.join(destbase, name)

def srcpath(name):
	return os.path.join(srcbase, name)

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
	wrapper = open(srcpath('wrapper')).read()
	f = open(destpath(target), 'w')
	f.write(wrapper)
	f.close()
	os.chmod(destpath(target), 06755)
else:
	os.symlink(srcpath('browse.cgi'), destpath(target))

try:
	os.unlink(destpath('files'))
except:
	pass
os.symlink(srcpath('files'), destpath('files'))

if listpath:
	f = open(destpath('ezmlm-browse.ini'), 'w')
	f.write('''# Automatically generated configuration file
# All of the settings below
[globals]
allowraw = 0
mask_emails = 1
basedir = %(listpath)s
basehost = %(hostname)s
filesprefix = files/

[defaults]
style = browse.css
perpage = 20
msgsperpage = 10
wrapwidth = 0
feedtype = atom
feedmsgs = 10
datesort = ascending

[styles]
browse.css = Default
purple.css = Purple
greenterm.css = Terminal

[charsets]

# Replace this with suitable entries for your list.  listdir, listemail,
# and listsub are all automatically generated from the archive name and
# basedir and basehost above.

[archive:sample]
listdesc = Sample mailing list description
listdir = %(listpath)s/sample
listemail = sample@%(hostname)s
listsub = sample-subscribe@%(hostname)s
''' % locals())
	f.close()

if '--apache' in opts:
	f = open(destpath('.htaccess'), 'w')
	f.write('DirectoryIndex %s\n'
			'AddHandler cgi-script .cgi\n'
			'Options +ExecCGI\n' % target)
	f.close()
