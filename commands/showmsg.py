from globals import *
from globalfns import *

###############################################################################
# Command: Show message
###############################################################################
def do(ctxt):
	format_timestamp(ctxt, ctxt)
	header(ctxt, ctxt[SUBJECT], 'msg')
	ctxt['threadnum'] = 0
	ctxt['threadidx'] = 0
	for i in range(len(ctxt[MESSAGES])):
		if int(ctxt[MESSAGES][i][MSGNUM]) == ctxt[MSGNUM]:
			ctxt['threadidx'] = i
			break
	ctxt['threadlen'] = len(ctxt[MESSAGES])
	write('<div class=msg>')
	write(html('msg-pager') % ctxt)
	write('<hr>')
	sub_showmsg(ctxt, ctxt[MSGNUM])
	write('<hr>')
	write(html('msg-pager') % ctxt)
	write('</div>')
	footer(ctxt)
