from globals import *
from globalfns import *

###############################################################################
# Command: Static file retrieval
###############################################################################
def do(ctxt):
	name = ctxt[FILE]
	if '/' in name:
		die('"/" is not allowed in file names: %s' % name)
	f = open(os.path.join('files', name)).read()
	write(f)
