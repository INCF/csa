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

from __future__ import with_statement

import sys

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

class TestOperators (TestCSA):
    def test_difference (self):
        # Test difference
        self.assertEqual4x4 (full - oneToOne,
                            [(i, j) for j in xrange (0,4) for i in xrange (0,4) if i != j],
                            'difference operator')


def test_main():
    test_support.run_unittest(TestElementary,
                              TestOperators
                             )

if __name__ == '__main__':
    test_main()

