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

from __future__ import with_statement

import sys
import numpy

from csa import *

import unittest
from test import test_support


class TestCSA(unittest.TestCase):
    def assertEqualCS (self, cs, ls, msg):
        self.assertEqual([x for x in cs], ls, msg)

    def assertEqual4x4 (self, cs, ls, msg):
        self.assertEqualCS (cross ((0, 3), (0, 3)) * cs, ls, msg)

    def assertEqual30x30 (self, cs, ls, msg):
        self.assertEqualCS (cross ((0, 29), (0, 29)) * cs, ls, msg)

    def sampleN (self, func, dims, N):
        data = numpy.zeros ((N,) + dims)
        for k in xrange (N):
            data[k] = func ()
        return numpy.mean (data, 0)


class TestElementary (TestCSA):

    # Only use setUp() and tearDown() if necessary

    #def setUp(self):
    #    ... code to execute in preparation for tests ...

    #def tearDown(self):
    #    ... code to execute to clean up after tests ...
    def test_list (self):
        # Test list cs
        self.assertEqual30x30 ([(22,7),(8,23)],
                               [(22,7),(8,23)],
                               'list cs')

    def test_xrange (self):
        # Test xrange
        self.assertEqual30x30 (cross (xrange (10), xrange (10, 20, 3)),
                               [(i, j) for j in xrange (10, 20, 3) for i in xrange (10)],
                               'xrange specified interval set mask')

    def test_full (self):
        # Test full cs
        self.assertEqualCS (cross ((0, 7), (8, 15)) * full, 
                            [(i, j) for j in xrange (8, 16) for i in xrange (0, 8)],
                            'finite piece of full connection-set bogus')

    def test_oneToOne (self):
        # Test oneToOne cs
        self.assertEqualCS (cross ((0, 7), (1, 8)) * oneToOne, 
                            [(i, i) for i in xrange (1, 8)],
                            'finite piece of oneToOne connection-set bogus')

    def test_tabulate (self):
        # Test tabulate
        if sys.version < '2.6':         #*fixme*
            return
        with test_support.captured_stdout () as s:
            tabulate (cross ((0, 3), (0, 3)) * oneToOne)
        self.assertEqual (s.getvalue (),
                          '0 \t0\n1 \t1\n2 \t2\n3 \t3\n',
                          'tabulate malfunctioning')

    def test_gaussnet (self):
        e = ival (0, 19)
        i = ival (20, 29)
        a = e + i

        g = random2d (900)
        d = euclidMetric2d (g)

        g_e = gaussian (0.1, 0.3) * d
        g_i = gaussian (0.2, 0.3) * d

        c_e = cset (random * g_e, g_e)
        c_i = cset (random * g_i, -g_i)

        c = cross (e, a) * c_e + cross (i, a) * c_i

        self.assertTrue (cross (N, 0) * c)
        self.assertFalse (cross (N, 100) * c)
        
        for (i, j, g) in cross (i, a) * c:
            self.assertTrue (g < 0.0)


    def partitionRandomN (self):
        K = self.K
        N = 3 * K
        R = (0, N - 1)
        R0 = (0, K - 1)
        R2 = (2 * K, 3 * K - 1)
        c = random (N = N) * cross (R, R)
        c0 = partition (c, [cross (R, R0), cross (R, R2)], 0)
        c1 = partition (c, [cross (R, R0), cross (R, R2)], 1)
        c2 = transpose * partition (c, [cross (R0, R), cross (R2, R)], 0)
        c3 = transpose * partition (c, [cross (R0, R), cross (R2, R)], 1)
        res = numpy.zeros ((4 * N, K))
        row = 0
        for (c, offset) in [(c0, 0), (c1, 2 * K), (c2, 0), (c3, 2 * K)]:
            a = numpy.zeros ((N, K))
            for (i, j) in c:
                j -= offset
                if 0 <= i < N and 0 <= j < K:
                    a[i, j] = 1
                else:
                    self.fail ('connection outside mask')
            res[row:row + N, :] = a
            row += N
        return 2.0 * K * res           # normalization

    def test_partitionRandomN (self):
        self.K = 5
        res = self.sampleN (self.partitionRandomN, (12 * self.K, self.K), 1000)
        for x in res.flatten ():
            self.assertAlmostEqual (x, 1.0, 0, 'maybe wrong statistics %g != 1.' % x)
    def intersectionRandomN (self):
        K = self.K
        N = 3 * K
        R = (0, N - 1)
        R0 = (0, K - 1)
        R2 = (2 * K, 3 * K - 1)
        c = random (N = N) * cross (R, R)
        c0 = cross (R, [R0, R2]) * c
        c1 = transpose * (cross ([R0, R2], R) * c)
        res = numpy.zeros ((2 * N, 2 * K))
        row = 0
        for c in [c0, c1]:
            a = numpy.zeros ((N, 2 * K))
            for (i, j) in c:
                if 0 <= i < N and 0 <= j < K:
                    a[i, j] = 1
                elif 0 <= i < N and 2 * K <= j < 3 * K:
                    a[i, j - K] = 1
                else:
                    self.fail ('connection outside mask')
            res[row:row + N, :] = a
            row += N
        return N * res           # normalization

    def test_intersectionRandomN (self):
        self.K = 5
        res = self.sampleN (self.intersectionRandomN, (6 * self.K, 2 * self.K), 1000)
        for x in res.flatten ():
            self.assertAlmostEqual (x, 1.0, 0, 'maybe wrong statistics %g != 1.' % x)

class TestOperators (TestCSA):
    def test_difference (self):
        # Test difference
        self.assertEqual4x4 (full - oneToOne,
                            [(i, j) for j in xrange (0,4) for i in xrange (0,4) if i != j],
                            'difference operator')


def main():
    test_support.run_unittest(TestElementary,
                              TestOperators
                             )

if __name__ == '__main__':
    main()

