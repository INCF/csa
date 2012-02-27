#
#  This file is part of the Connection-Set Algebra (CSA).
#  Copyright (C) 2010 Mikael Djurfeldt
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

try:
    from nineml.connection_generator import ConnectionGenerator
    HAVE_CG=True
except ImportError:
    HAVE_CG=False

if HAVE_CG:
    from csaobject import from_xml
    from elementary import partition
    
    class CSAConnectionGenerator (ConnectionGenerator):
        def __init__ (self, cset):
            self.cset = cset
            self.masks = False
            self.generator = False

        @property
        def arity (self):
            return self.cset.arity ()

        def setMask (self, mask):
            self.setMasks (self, [mask], 0)

        def setMasks (self, masks, local):
            if len (masks) = 1:
                

        def __len__ (self):
            return self.generator.__len__ ()

def connectionGeneratorClosureFromXML (element):
    cset = from_xml (element)
    return CSAConnectionGenerator (cset)
