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

import sys as _sys

import connset as _cs
import _elementary
import _misc

# Connection-Set constructor
#
def cset (mask, *valueSets):
    if valueSets:
        c = _cs.ExplicitCSet (mask, *valueSets)
        return _cs.ConnectionSet (c)
    else:
        return mask

# Selectors
#
def mask (obj):
    cset = _cs.coerceCSet (obj)
    return cset.mask ()

def value (obj, k):
    assert isinstance (obj, _cs.ConnectionSet), 'expected connection-set'
    return obj.c.value (k)

# Cartesian product
#
def cross (set0, set1):
    return _cs.IntervalSetMask (set0, set1)

def partition (c, masks, selected):
    if isinstance (c, _cs.Mask):
        return _elementary.MaskPartition (c, masks, selected)
    elif isinstance (c, _cs.ConnectionSet):
        return _cs.ConnectionSet (_elementary.CSetPartition (c.c, masks, selected))

# Elementary masks
#
empty = _cs.ExplicitMask ([])

full = cross (xrange (_sys.maxint), xrange (_sys.maxint))

oneToOne = _elementary.OneToOne ()

random = _misc.Random ()

# Utilities
#
def tabulate (c):
    for x in c:
        print x[0],
        for e in x[1:]:
            print '\t', e,
        print

#del _elementary, cs, sys                # not for export
