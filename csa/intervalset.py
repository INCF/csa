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

# Interval sets are represented as ordered lists of closed intervals
#
class IntervalSet:
    def __init__ (self, s = []):
        if not isinstance (s, list):
            s = [ s ]
            
        res = []
        for x in s:
            if isinstance (x, tuple):
                assert goodInterval (x), 'malformed interval'
                res.append (x)
            elif isinstance (x, int):
                res.append ((x, x))
            elif isinstance (x, xrange):
                res += xrangeToIntervals (x)
            else:
                raise TypeError, "can't interpret element as interval"
        s = res

        s.sort ()

        # merge intervals
        # by construction we know that i[0] <= i[1] for i in s
        res = []
        N = 0
        if s:
            lastLower = s[0][0]
            lastUpper = s[0][1]
            for i in s[1:]:
                assert lastLower < i[0] and lastUpper < i[0], 'intervals overlap'
                if i[0] - lastUpper == 1:
                    lastUpper = i[1]
                else:
                    res.append ((lastLower, lastUpper))
                    N += 1 + lastUpper - lastLower
                    lastLower = i[0]
                    lastUpper = i[1]
            res.append ((lastLower, lastUpper))
            N += 1 + lastUpper - lastLower

        self.intervals = res
        self.nIntegers = N

        assert not self or self.min () >= 0, 'only positive values allowed'

    def __len__ (self):
        return self.nIntegers

    def __iter__ (self):
        for i in self.intervals:
            for e in xrange (i[0], i[1] + 1):
                yield e

    def intervalIterator (self):
        return iter (self.intervals)

    def min (self):
        return self.intervals[0][0]

    def max (self):
        return self.intervals[-1][1]

    def intersection (self, other):
        res = []
        N = 0
        iter0 = self.intervalIterator ()
        iter1 = other.intervalIterator ()
        try:
            i0 = iter0.next ()
            i1 = iter1.next ()
            while True:
                if i0[1] <= i1[1]:
                    if i0[1] >= i1[0]:
                        lower = max (i0[0], i1[0])
                        res.append ((lower, i0[1]))
                        N += 1 + i0[1] - lower
                    i0 = iter0.next ()
                else:
                    if i1[1] >= i0[0]:
                        lower = max (i0[0], i1[0])
                        res.append ((lower, i1[1]))
                        N += 1 + i1[1] - lower
                    i1 = iter1.next ()
        except StopIteration:
            pass
        iset = IntervalSet ()
        iset.intervals = res
        iset.nIntegers = N
        return iset

    def union (self, other):
        iset = IntervalSet ()
        if not other.nIntegers:
            iset.intervals = list (self.intervals)
            iset.nIntegers = self.nIntegers
            return iset
        if not self.nIntegers:
            iset.intervals = list (other.intervals)
            iset.nIntegers = other.nIntegers
            return iset
        res = []
        N = 0
        iter0 = self.intervalIterator ()
        iter1 = other.intervalIterator ()
        i0 = iter0.next ()
        i1 = iter1.next ()
        if i0[0] <= i1[0]:
            (lower, upper) = i0
        else:
            (lower, upper) = i1
        try:
            while True:
                if i0[0] <= i1[0]:
                    if i0[0] <= upper + 1:
                        if i0[1] > upper:
                            upper = i0[1]
                    else:
                        res.append ((lower, upper))
                        N += 1 + upper - lower
                        (lower, upper) = i0
                    try:
                        i0 = iter0.next ()
                    except StopIteration:
                        if i1[0] <= upper + 1:
                            if i1[1] > upper:
                                upper = i1[1]
                            i1 = (lower, upper)
                        else:
                            res.append ((lower, upper))
                            N += 1 + upper - lower
                        while True:
                            res.append (i1)
                            N += 1 + i1[1] - i1[0]
                            i1 = iter1.next ()
                else:
                    if i1[0] <= upper + 1:
                        if i1[1] > upper:
                            upper = i1[1]
                    else:
                        res.append ((lower, upper))
                        N += 1 + upper - lower
                        (lower, upper) = i1
                    try:
                        i1 = iter1.next ()
                    except StopIteration:
                        if i0[0] <= upper + 1:
                            if i0[1] > upper:
                                upper = i0[1]
                            i0 = (lower, upper)
                        else:
                            res.append ((lower, upper))
                            N += 1 + upper - lower
                        while True:
                            res.append (i0)
                            N += 1 + i0[1] - i0[0]
                            i0 = iter0.next ()
        except StopIteration:
            pass
        iset.intervals = res
        iset.nIntegers = N
        return iset


# return true if tuple i represents a well-formed interval
def goodInterval (i):
    return len (i) == 2 \
           and isinstance (i[0], int) \
           and isinstance (i[1], int) \
           and i[0] <= i[1]


def xrangeToIntervals (x):
    if not x:
        return []
    elif len (x) == 1:
        return [(x[0], x[0])]
    elif x[1] - x[0] == 1:
        return [(x[0], x[-1])]
    else:
        return ((e, e) for e in x)
