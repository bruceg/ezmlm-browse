from globals import *
from globalfns import *
import feedgen

###############################################################################
# Command: Generate news feed
###############################################################################
def do(ctxt):
	feedtype = feedgen.types[ctxt[FEEDTYPE]]
	# Set a hard maximum on the number of messages to reduce DoS attacks
	count = min(int(ctxt[FEEDMSGS]), 100)
	num = ctxt[EZMLM].num
	msgs = []
	while len(msgs) < count and num > 0:
		try:
			msgs.append(ctxt[EZMLM].index[num])
		except KeyError:
			pass
		num -= 1
	feedtype.generate(ctxt, msgs)
