from globals import *
from globalfns import *
import config

###############################################################################
# Command: Month Index
###############################################################################
def do(ctxt):
	ezmlm = ctxt[EZMLM]
	header(ctxt, 'Month Index', 'months')
	do_list(ctxt, 'months', ctxt[PERPAGE],
			[ {MONTH: month,
			   MSGCOUNT: reduce(lambda a,b:a+b,
								[ t[MSGCOUNT]
								  for t in ezmlm.threads(month) ])}
			  for month in map(int, ezmlm.months) ])
	footer(ctxt)
