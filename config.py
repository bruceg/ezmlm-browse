from globals import *

# Values are looked up in the following order:
# 1. CGI environment variables
# 2. Hard-coded defaults
# 3. Configured defaults (below)
# 4. Cookies
# 5. Form/URL items
# 6. List configuration (below)
# Values set later in the list override earlier values.

styles = (
	'None',
	('browse.css', 'Default'),
	('purple.css', 'Purple'),
	('greenterm.css', 'Terminal'),
	)

# The following list itemizes default values.  Most of these can be
# omitted if desired.
defaults = {
	# The default style sheet.
	STYLE: 'browse.css',
	# The number of items per page.
	PERPAGE: 20,
	# The number of messages per page.
	MSGSPERPAGE: 10,
}

# The base directory under which all of the mailing lists can be found.
basedir = '/home/bruce/lists'

# The base hostname for mailing list and subscribe addresses.
basehost = 'lists.untroubled.org'

# For each mailing list you want to have visible to the web, add an
# entry to this table.  Each entry consists of a dictionary
# containing:
#
# LISTDESC: The description to show for this list when producing the index
# LISTDIR: The directory in which the "archive" directory can be found.
# LISTEMAIL: The email address to use to send messages to the list.
# LISTSUB: The email address to use to subscribe to the list.
#
# If they are not present, the LISTDIR, LISTEMAIL, and LISTSUB values
# are automatically generated from the list name and the base directory
# or host above.
#
# This is the place to override any of the defaults above.
# Note that any setting you put here will override any cookie or URL/form
# value as well.
archives = {
	'bgware': { LISTDESC: 'Software by Bruce Guenter' },
	'vmailmgr': { LISTDESC: 'VMailMgr announcements, development, and users' },
	'nullmailer': { LISTDESC: 'The NullMailer MTA' },
	'rpms': { LISTDESC: 'RPMs Built by Bruce Guenter' },
	'test-idx': { LISTDESC: 'Test list' },
	}
