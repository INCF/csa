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

import intervalset as _iset
import connset as _cs
import valueset as _vs
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

def arity (obj):
    if isinstance (obj, _cs.ConnectionSet):
        return obj.c.arity
    else:
        return 0

# Value-set constructor
#
def vset (obj):
    if not callable (obj):
        return _vs.QuotedValueSet (obj)
    else:
        return _vs.GenericValueSet (obj)

# Intervals
#
def ival (beg, end):
    return _iset.IntervalSet ((beg, end))

N = _iset.N

# Cartesian product
#
def cross (set0, set1):
    return _cs.intervalSetMask (set0, set1)

# Elementary masks
#
empty = cross ([], [])

full = _elementary.FullMask ()

oneToOne = _elementary.OneToOne ()

random = _misc.Random ()

# Support for parallel simulator
#
def partition (c, masks, selected, seed = None):
    if isinstance (c, _cs.Mask):
        return _cs.MaskPartition (c, masks, selected, seed)
    elif isinstance (c, _cs.ConnectionSet):
        return _cs.ConnectionSet (_cs.CSetPartition (c, masks, selected, seed))

# Utilities
#
def tabulate (c):
    for x in c:
        print x[0],
        for e in x[1:]:
            print '\t', e,
        print

#del _elementary, cs, sys                # not for export
