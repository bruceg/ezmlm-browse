from globals import *
from globalfns import *
import feedgen

def rec_gettext(part):
	if part.is_multipart():
		return '\n'.join([ rec_gettext(p)
						   for p in part.get_payload() ])
	if part.get_content_type() == 'text/plain':
		return part.get_payload(decode=1)
	return ''

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
	for msg in msgs:
		e = ctxt[EZMLM].open(int(msg[MSGNUM]))
		msg[BODY] = rec_gettext(e).strip()
	feedtype.generate(ctxt, msgs)
