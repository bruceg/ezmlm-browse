from globals import *
from globalfns import *

###############################################################################
# Command: Thread index
###############################################################################
def do(ctxt):
	ezmlm = ctxt[EZMLM]
	ctxt.update(ezmlm.thread(ctxt[THREADID]))
	header(ctxt, 'Thread: ' + ctxt[SUBJECT], 'threadidx')
	ctxt[THREADS] = ezmlm.thread_messages(ctxt[MESSAGES])
	rec_thread(ctxt)
	footer(ctxt)
