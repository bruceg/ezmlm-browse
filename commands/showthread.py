from globals import *
from globalfns import *

###############################################################################
# Command: Show thread
###############################################################################
def do(ctxt):
	ezmlm = ctxt[EZMLM]
	ctxt.update(ezmlm.thread(ctxt[THREADID]))
	header(ctxt, 'Thread: ' + ctxt[SUBJECT], 'showthread')
	do_list(ctxt, 'msgs', ctxt[MSGSPERPAGE], ctxt[MESSAGES],
			lambda:sub_showmsg(ctxt, ctxt[MSGNUM]))
	footer(ctxt)
