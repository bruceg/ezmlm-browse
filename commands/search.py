from globals import *
from globalfns import *

###############################################################################
# Command: Search form / results
###############################################################################
def do(ctxt):
	terms = ctxt[TERMS]
	if terms:
		header(ctxt, 'Search for: ' + ctxt['html(terms)'], 'search')
		do_list(ctxt, 'threadlist', ctxt[PERPAGE], ctxt[EZMLM].search(terms))
		write(html('search-sep') % ctxt)
	else:
		header(ctxt, 'Search', 'search')
	write(html('search-form') % ctxt)
	footer(ctxt)
