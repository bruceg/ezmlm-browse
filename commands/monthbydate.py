from globals import *
from globalfns import *

###############################################################################
# Command: Month by date
###############################################################################
def do(ctxt):
	ctxt[MONTH] = int(ctxt[MONTH])
	header(ctxt, 'Messages for %(monthname(month))s %(month/100)s' % ctxt,
		   'bydate')
	do_list(ctxt, 'msglist', ctxt[PERPAGE],
			format_timestamps(ctxt, ctxt[EZMLM].month(ctxt[MONTH])))
	footer(ctxt)
