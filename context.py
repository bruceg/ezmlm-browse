# Copyright (C) 2003 Bruce Guenter <bruceg@em.ca>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

import sys

###############################################################################
# Context management

global_context = {
    'math': __import__('math'),
    'random': __import__('random'),
    're': __import__('re'),
    'time': __import__('time'),
    }

class Context:
	def __init__(self):
		global global_context
		self.stack = [ {} ]
		self.globals = global_context.copy()
		self.pop()
	def pop(self):
		self.dict = self.stack.pop()
		self.get = self.dict.get
		self.has_key = self.dict.has_key
		self.items = self.dict.items
		self.iteritems = self.dict.iteritems
		self.iterkeys = self.dict.iterkeys
		self.itervalues = self.dict.itervalues
		self.keys = self.dict.keys
		self.setdefault = self.dict.setdefault
		self.values = self.dict.values
		self.update = self.dict.update
		self.__str__ = self.dict.__str__
		self.__repr__ = self.dict.__repr__
		# These need to be special cased :/
		self.globals['defined'] = self.dict.has_key
	def copy(self):
		return Context(self.dict.copy(), self.globals)
	def push(self):
		self.stack.append(self.dict.copy())
	def eval(self, body):
		return eval(body, self.globals, self.dict)
	def execute(self, body):
		exec(body, self.globals, self.dict)
	def __getitem__(self, key):
		try:
			return self.dict[key]
		except KeyError:
			return self.eval(key)
	def __setitem__(self, key, val):
		self.dict[key] = val
