from globals import *
from globalfns import *

###############################################################################
# Command: Month by thread
###############################################################################
def do(ctxt):
	ctxt[MONTH] = int(ctxt[MONTH])
	header(ctxt, 'Threads for %(monthname(month))s %(month/100)s' % ctxt,
		   'threads')
	do_list(ctxt, 'threadlist', ctxt[PERPAGE],
			ctxt[EZMLM].threads(ctxt[MONTH]))
	footer(ctxt)
