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

import math as _math
import random as _random
import numpy as _numpy

import intervalset as _iset

def grid2d (width, xScale = 1.0, yScale = 1.0, x0 = 0.0, y0 = 0.0):
    xScale /= width
    yScale /= width
    g = lambda i: \
        (x0 + xScale * (i % width), y0 + yScale * (i / width))
    g.type = 'grid'
    g.width = width
    g.xScale = xScale
    g.yScale = yScale
    g.x0 = x0
    g.y0 = y0
    g.inverse = lambda x, y: \
                    int (round (x / xScale - x0)) \
                    + width * int (round (y / yScale - y0))
    return g

def random2d (N, xScale = 1.0, yScale = 1.0):
    coords = [(xScale * _random.random (), yScale * _random.random ())
              for i in xrange (0, N)]
    g = lambda i: coords[i]
    g.type = 'ramdom'
    g.N = N
    g.xScale = xScale
    g.yScale = yScale
    # We should use a KD-tree here
    g.inverse = lambda x, y, domain=_iset.IntervalSet ((0, N - 1)): \
                    _numpy.array ([euclidDistance2d ((x, y), g(i)) \
                                   for i in domain]).argmin () \
                                   + domain.min ()
    return g

def euclidDistance2d (p1, p2):
    dx = p1[0] - p2[0]
    dy = p1[1] - p2[1]
    return _math.sqrt (dx * dx + dy * dy)

class ProjectionOperator (object):
    def __init__ (self, projection):
        self.projection = projection

    def __mul__ (self, g):
        projection = self.projection
        return lambda i: projection (g (i))

def euclidMetric2d (g1, g2 = None):
    g2 = g1 if g2 == None else g2
    return lambda i, j: euclidDistance2d (g1 (i), g2 (j))

#del random
