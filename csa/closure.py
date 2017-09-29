#
#  This file is part of the Connection-Set Algebra (CSA).
#  Copyright (C) 2010,2011,2012 Mikael Djurfeldt
#
#  CSA is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  CSA is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from .csaobject import *

import inspect

try:
    from lxml import etree
    from lxml.builder import E
except ImportError:
    pass

class Closure (CSAObject):
    tag = 'closure'
    name = tag
    
    def __init__ (self, formals, e):
        self.formals = formals
        self.etree = e

    @staticmethod
    def formalToXML (formal):
        return E ('bvar', E ('ci', formal))
    
    def _to_xml (self):
        formals = list (map (Closure.formalToXML, self.formals))
        return E ('bind', E ('closure'), *formals + [ self.etree ])

    def __call__ (self, *args):
        assert len (args) == len (self.formals), "arguments %s don't match formals %s" % (args, self.formals)
        bindings = {}
        for (formal, arg) in map (self.formals, args):
            bindings[formal] = arg
        return CSAObject.from_xml (self.etree, bindings)

registerTag (Closure.tag, Closure, BINDOPERATOR)
