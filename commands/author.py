from globals import *
from globalfns import *

###############################################################################
# Command: Author post listing
###############################################################################
def do(ctxt):
	ctxt.update(ctxt[EZMLM].author(ctxt[AUTHORID]))
	format_timestamps(ctxt, ctxt[MESSAGES])
	header(ctxt, 'Author: ' + ctxt[AUTHOR], 'author')
	do_list(ctxt, 'msglist', ctxt[PERPAGE], ctxt[MESSAGES])
	footer(ctxt)
