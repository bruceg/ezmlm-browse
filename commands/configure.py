import Cookie

from globals import *
from globalfns import *
import timezones

###############################################################################
# Command: Configure interface
###############################################################################
def do(ctxt):
	cookie = Cookie.SimpleCookie()
	if ctxt.has_key('_tz'):
		cookie[TZ] = ctxt[TZ] = ctxt['_tz']
	if ctxt.has_key('_format_time'):
		cookie[FORMATTIME] = ctxt[FORMATTIME] = ctxt['_format_time']
	if ctxt.has_key('_style'):
		cookie[STYLE] = ctxt[STYLE] = ctxt['_style']
	if ctxt.has_key('_perpage'):
		try:
			cookie[PERPAGE] = ctxt[PERPAGE] = int(ctxt['_perpage'])
		except ValueError: pass
	if ctxt.has_key('_msgsperpage'):
		try:
			cookie[MSGSPERPAGE] = ctxt[MSGSPERPAGE] = int(ctxt['_msgsperpage'])
		except ValueError: pass
	if ctxt.has_key('_wrapwidth'):
		try:
			cookie[WRAPWIDTH] = ctxt[WRAPWIDTH] = int(ctxt['_wrapwidth'])
		except ValueError:
			pass
	if ctxt.has_key('_alt_part'):
		cookie[ALTPART] = ctxt[ALTPART] = ctxt['_alt_part']
	if ctxt.has_key('_date_sort'):
		cookie[DATESORT] = ctxt[DATESORT] = ctxt['_date_sort']
	if cookie:
		for key in cookie.keys():
			cookie[key]['expires'] = 60*60*24*365*2
		write(cookie.output(sep='\r\n'))
		write('\r\n')
	timezones.zones.insert(0, ('None','None'))
	ctxt['timezones'] = timezones.zones
	header(ctxt, 'Configure', 'configure')
	write(html('configure-form') % ctxt)
	footer(ctxt)
