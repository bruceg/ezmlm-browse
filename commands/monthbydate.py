from globals import *
from globalfns import *

###############################################################################
# Command: Month by date
###############################################################################
def do(ctxt):
	ctxt[MONTH] = int(ctxt[MONTH])
	header(ctxt, 'Messages for %(monthname(month))s %(month/100)s' % ctxt,
		   'bydate')
	month = ctxt[EZMLM].month(ctxt[MONTH])
	if ctxt[DATESORT][0] == 'd':
		month.reverse()
	do_list(ctxt, 'msglist', ctxt[PERPAGE],
			format_timestamps(ctxt, month))
	footer(ctxt)
