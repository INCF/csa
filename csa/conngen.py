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

try:
    from nineml.connection_generator import ConnectionGenerator
    HAVE_CG=True
except ImportError:
    HAVE_CG=False

if HAVE_CG:
    from .csaobject import from_xml
    from .elementary import arity, cross, partition
    from .closure import Closure
    
    class CSAConnectionGenerator (ConnectionGenerator):
        def __init__ (self, cset):
            self.cset = cset
            self.generator = False

        @property
        def arity (self):
            return arity (self.cset)

        def setMask (self, mask):
            self.setMasks ([mask], 0)

        def setMasks (self, masks, local):
            csaMasks = list (map (CSAConnectionGenerator.makeMask, masks))
            self.generator = partition (self.cset, csaMasks, local)

        @staticmethod
        def makeMask (mask):
            return cross (CSAConnectionGenerator.makeIList (mask.sources),
                          CSAConnectionGenerator.makeIList (mask.targets))

        @staticmethod
        def makeIList (iset):
            if iset.skip == 1:
                return iset.intervals
            else:
                ls = []
                for ivl in iset.intervals:
                    for i in range (ivl[0], ivl[1] + 1, iset.skip):
                        ls.append ((i, i))
                return ls

        def __len__ (self):
            return self.generator.__len__ ()

        def __iter__ (self):
            return self.generator.__iter__ ()

def connectionGeneratorClosureFromXML (element):
    cset = from_xml (element)
    if isinstance (cset, Closure):
        return lambda *args: CSAConnectionGenerator (cset (*args))
    else:
        return lambda: CSAConnectionGenerator (cset)
