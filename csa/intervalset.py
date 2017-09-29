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

import sys

from .csaobject import *

infinity = sys.maxsize - 1

# Interval sets are represented as ordered lists of closed intervals
#
class IntervalSet (CSAObject):
    tag = 'intervalset'
    
    @staticmethod
    # return true if tuple i represents a well-formed interval
    def goodInterval (i):
        return len (i) == 2 \
               and isinstance (i[0], int) \
               and isinstance (i[1], int) \
               and i[0] <= i[1]

    @staticmethod
    def rangeToIntervals (x):
        if not x:
            return []
        elif len (x) == 1:
            return [(x[0], x[0])]
        elif x[1] - x[0] == 1:
            return [(x[0], x[-1])]
        else:
            return ((e, e) for e in x)

    @staticmethod
    def coerce (s):
        if not isinstance (s, list):
            s = [ s ]
            
        res = []
        for x in s:
            if isinstance (x, tuple):
                assert IntervalSet.goodInterval (x), 'malformed interval'
                res.append (x)
            elif isinstance (x, int):
                res.append ((x, x))
            elif isinstance (x, range):
                res += IntervalSet.rangeToIntervals (x)
            else:
                raise TypeError ("can't interpret element as interval")
        s = res

        s.sort ()

        # merge intervals
        # by construction we know that i[0] <= i[1] for i in s
        res = []
        N = 0
        if s:
            lastLower = s[0][0]
            lastUpper = s[0][1]

            assert lastLower >= 0, 'only positive values allowed'

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

        return (res, N)
    
    def __init__ (self, s = [], intervals = None, nIntegers = None):
        if intervals:
            self.intervals = intervals
            self.nIntegers = nIntegers
        else:
            (self.intervals, self.nIntegers) = self.coerce (s)

    def repr (self):
        return 'IntervalSet(%r)' % self.intervals

    def __len__ (self):
        return self.nIntegers

    def __contains__ (self, n):
        for i in self.intervals:
            if n > i[1]:
                continue
            elif n >= i[0]:
                return True
            else:
                return False
        return False

    def __iter__ (self):
        for i in self.intervals:
            for e in range (i[0], i[1] + 1):
                yield e

    def __invert__ (self):
        return ComplementaryIntervalSet (intervals = self.intervals, \
                                         nIntegers = self.nIntegers)

    def __add__ (self, other):
        if not isinstance (other, IntervalSet):
            other = IntervalSet (other)
        return self.union (other)

    def __radd__ (self, other):
        return IntervalSet (other).union (self)

    def __sub__ (self, other):
        if not isinstance (other, IntervalSet):
            other = IntervalSet (other)
        return self.intersection (~other)

    def __rsub__ (self, other):
        return IntervalSet (other).intersection (~self)

    def __mul__ (self, other):
        if not isinstance (other, IntervalSet):
            other = IntervalSet (other)
        return self.intersection (other)

    def __rmul__ (self, other):
        return IntervalSet (other).intersection (self)

    def finite (self):
        return True

    def shift (self, N):
        if not self or N == 0:
            return self

        intervals = []
        nIntegers = self.nIntegers
        for (i, j) in self.intervals:
            i += N
            j += N
            if i >= 0:
                intervals.append ((i, j))
            elif j >= 0:
                intervals.append ((0, j))
                nIntegers += i
                
        return IntervalSet (intervals = intervals, nIntegers = nIntegers)

    def intervalIterator (self):
        return iter (self.intervals)

    def boundedIterator (self, low, high):
        iterator = iter (self.intervals)
        i = next (iterator)
        while i[1] < low:
            i = next (iterator)
        while i[0] < high:
            for e in range (max (low, i[0]), min (i[1] + 1, high)):
                yield e
            i = next (iterator)

    def count (self, low, high):
        iterator = iter (self.intervals)
        c = 0
        try:
            i = next (iterator)
            while i[1] < low:
                i = next (iterator)
            while i[0] < high:
                c += min (i[1] + 1, high) - max (low, i[0])
                i = next (iterator)
        except StopIteration:
            pass
        return c

    def min (self):
        return self.intervals[0][0]

    def max (self):
        return self.intervals[-1][1]

    def skipIntervals (self):
        if len (self.intervals) <= 1 or self.intervals[0][0] != self.intervals[0][1]:
            return 1, self.intervals
        skip = self.intervals[1][0] - self.intervals[0][0]
        res = []
        start = last = self.intervals[0][0]
        for i in self.intervals[1:]:
            if i[0] != i[1]:
                return 1, self.intervals
            if i[0] != last + skip:
                if i[0] % skip != 0:
                    return 1, self.intervals
                res.append ((start, last))
                start = i[0]
            last = i[0]
        res.append ((start, last))
        return skip, res

    def intersection (self, other):
        res = []
        N = 0
        iter0 = self.intervalIterator ()
        iter1 = other.intervalIterator ()
        try:
            i0 = next (iter0)
            i1 = next (iter1)
            while True:
                if i0[1] <= i1[1]:
                    if i0[1] >= i1[0]:
                        lower = max (i0[0], i1[0])
                        res.append ((lower, i0[1]))
                        N += 1 + i0[1] - lower
                    i0 = next (iter0)
                else:
                    if i1[1] >= i0[0]:
                        lower = max (i0[0], i1[0])
                        res.append ((lower, i1[1]))
                        N += 1 + i1[1] - lower
                    i1 = next (iter1)
        except StopIteration:
            pass
        iset = IntervalSet ()
        iset.intervals = res
        iset.nIntegers = N
        return iset

    def union (self, other):
        if isinstance (other, ComplementaryIntervalSet):
            return ~(~self).intersection (~other)
        
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
        i0 = next (iter0)
        i1 = next (iter1)
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
                        i0 = next (iter0)
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
                            i1 = next (iter1)
                else:
                    if i1[0] <= upper + 1:
                        if i1[1] > upper:
                            upper = i1[1]
                    else:
                        res.append ((lower, upper))
                        N += 1 + upper - lower
                        (lower, upper) = i1
                    try:
                        i1 = next (iter1)
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
                            i0 = next (iter0)
        except StopIteration:
            pass
        iset.intervals = res
        iset.nIntegers = N
        return iset

    def _to_xml (self):
        intervals = [ E ('interval', E ('cn', str (i)), E ('cn', str (j)))
                      for (i, j) in self.intervals ]
        return E (IntervalSet.tag, *intervals)

    @classmethod
    def from_xml (cls, element, env = {}):
        intervals = []
        for ivalElement in element.getchildren ():
            ival = ivalElement.getchildren ()
            intervals.append ((int (ival[0].text), int (ival[1].text)))
        return IntervalSet (intervals)

CSAObject.tag_map[CSA + IntervalSet.tag] = (IntervalSet, CUSTOM)


class ComplementaryIntervalSet (IntervalSet):
    def __init__ (self, s = [], intervals = None, nIntegers = None):
        IntervalSet.__init__ (self, s, intervals, nIntegers)

    def repr (self):
        if not self.intervals:
            return 'N'
        else:
            return '~IntervalSet(%r)' % self.intervals

    def __bool__ (self):
        return True

    # def __len__ (self):
    #     raise RuntimeError ('ComplementaryIntervalSet has infinite length')
 
    def __contains__ (self, n):
        for i in self.intervals:
            if n < i[0]:
                continue
            elif n <= i[1]:
                return False
            else:
                return True
        return True

    def __iter__ (self):
        raise RuntimeError ("can't interate over ComplementaryIntervalSet")

    def __invert__ (self):
        return IntervalSet (intervals = self.intervals, \
                            nIntegers = self.nIntegers)

    def finite (self):
        return False

    def shift (self, N):
        iset = IntervalSet (intervals = self.intervals, \
                            nIntegers = self.nIntegers).shift (N)
        return ComplementaryIntervalSet (intervals = iset.intervals, \
                                         nIntegers = iset.nIntegers)

    def intervalIterator (self):
        start = 0
        for i in self.intervals:
            if i[0] > 0:
                yield (start, i[0] - 1)
            start = i[1] + 1
        yield (start, infinity)

    def boundedIterator (self, low, high):
        raise RuntimeError ("can't interate over ComplementaryIntervalSet")

    def count (self, low, high):
        iterator = iter (self.intervals)
        c = 0
        prev = low
        try:
            i = next (iterator)
            while i[1] < low:
                i = next (iterator)
            while i[0] < high:
                c += i[0] - prev
                prev = i[1] + 1
                i = next (iterator)
        except StopIteration:
            pass
        if prev < high:
            c += high - prev
        return c

    def min (self):
        if not self.intervals or self.intervals[0][0] > 0:
            return 0
        else:
            return self.intervals[0][1] + 1

    def max (self):
        raise RuntimeError ('the maximum of a ComplementaryIntervalSet is infinity')

    def intersection (self, other):
        if isinstance (other, ComplementaryIntervalSet):
            return ~(~self).union (~other)
        else:
            return IntervalSet.intersection (self, other)

    def union (self, other):
        return ~(~self).intersection (~other)

    def _to_xml (self):
        if not self.intervals:
            return E ('N')
        else:
            return E ('apply', E ('complement'), IntervalSet._to_xml (self))


N = ComplementaryIntervalSet ([])

CSAObject.tag_map[CSA + 'N'] = (N, SINGLETON)
