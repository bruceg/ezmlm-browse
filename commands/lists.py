from globals import *
from globalfns import *
import config

###############################################################################
# Command: Lists menu
###############################################################################
def do(ctxt):
	for name in config.archives.keys():
		config.archives[name][LIST] = name
	lists = config.archives.values()
	lists.sort(lambda a,b:cmp(a[LIST],b[LIST]))
	header(ctxt, 'Lists Menu', 'lists')
	do_list(ctxt, 'lists', ctxt[PERPAGE], lists)
	footer(ctxt)
