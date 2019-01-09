#
#  This file is part of the Connection-Set Algebra (CSA).
#  Copyright (C) 2010,2011,2012,2019 Mikael Djurfeldt
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

from . import intervalset as _iset

def grid2d (width, xScale = 1.0, yScale = 1.0, x0 = 0.0, y0 = 0.0):
    xScale /= width
    yScale /= width
    g = lambda i: \
        (x0 + xScale * (i % width), y0 + yScale * (i // width))
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
              for i in range (0, N)]
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

class ProjectionOperator (object):
    def __init__ (self, projection):
        self.projection = projection

    def __mul__ (self, g):
        projection = self.projection
        return lambda i: projection (g (i))

def euclidDistance2d (p1, p2):
    dx = p1[0] - p2[0]
    dy = p1[1] - p2[1]
    return _math.sqrt (dx * dx + dy * dy)

def euclidMetric2d (g1, g2 = None):
    g2 = g1 if g2 == None else g2
    return lambda i, j: euclidDistance2d (g1 (i), g2 (j))

# These functions were contributed by Dr. Birgit Kriener

def euclidToroidDistance2d (p1, p2, xScale=1.0, yScale=1.0):
    ddx, ddy = abs (p1[0] - p2[0]), abs (p1[1] - p2[1])
    dx = ddx if ddx < xScale/2. else  xScale - ddx
    dy = ddy if ddy < yScale/2. else  yScale - ddy
    return _math.sqrt (dx * dx + dy * dy)

def euclidToroidMetric2d (g1, g2 = None, xScale=1.0, yScale=1.0):
    g2 = g1 if g2 == None else g2
    return lambda i, j: euclidToroidDistance2d (g1 (i), g2 (j), xScale, yScale)

# 3D functions

def grid3d(width, xScale = 1.0, yScale = 1.0, zScale = 1.0, x0 = 0.0, y0 = 0.0, z0 = 0.0):
    """Returns a 3D grid between (0, 0, 0) and (1, 1, 1)
    :param width: The number of rows/columns the grid has
    :type width: int
    :param xScale: Scales the grid along the x axis
    :type xScale: float
    :param yScale: Scales the grid along the y axis
    :type yScale: float
    :param zScale: Scales the grid along the z axis
    :type zScale: float
    :param x0: Translates the grid along the x axis
    :type xScale: float
    :param y0: Translates the grid along the y axis
    :type yScale: float
    :param z0: Translates the grid along the z axis
    :type zScale: float
    :return: A callable grid that returns 3d positions when given an index"""
    xScale /= width
    yScale /= width
    zScale /= width
    g = lambda i: \
        (x0 + xScale * (i % width), y0 + yScale * ((i % (width*width)) / width), z0 + zScale * (i / (width*width)))
    g.type = 'grid3d'
    g.width = width
    g.xScale = xScale
    g.yScale = yScale
    g.zScale = zScale
    g.x0 = x0
    g.y0 = y0
    g.z0 = z0
    g.inverse = lambda x, y, z: \
                    int (round (x / xScale - x0)) \
                    + width * (int (round (y / yScale - y0)
                    + width * int (round (z / zScale - z0))))
    return g
    
def random3d(N, xScale = 1.0, yScale = 1.0, zScale = 1.0):
    """Creates a set of points scattered uniformly inside a 3D box
    :param N: Number of 3D points
    :type N: int
    :param xScale: The scale of the box on the x axis
    :type xScale: float
    :param yScale: The scale of the box on the y axis
    :type yScale: float
    :param zScale: The scale of the box on the z axis
    :type zScale: float
    """
    coords = _numpy.random.random((N, 3))
    coords[...,0] *= xScale
    coords[...,1] *= yScale
    coords[...,2] *= zScale
    g = lambda i: coords[i]
    g.type = 'random'
    g.N = N
    g.xScale = xScale
    g.yScale = yScale
    g.zScale = zScale
    g.inverse = lambda x, y, z, domain=_iset.IntervalSet ((0, N - 1)): \
                    _numpy.array ([euclidDistance3d (_numpy.array((x, y, z)), g(i)) \
                                   for i in domain]).argmin () \
                                   + domain.min ()
    return g

def euclidDistance3d(p1, p2):
    """Returns the euclidean distance in 3D between two points
    :param p1: The first point
    :type p1: numpy.array((3))
    :param p2: The second point
    :type p2: numpy.array((3))
    :return: The euclidean distance
    :rtype: float
    """
    return _numpy.linalg.norm(p2 - p1)

def euclidMetric3d (g1, g2 = None):
    """Returns an euclidean metric for 3D points
    :param g1: The first group of points
    :type g1: callable
    :param g2: The second group of points. If None, the first group of points is used
    :type g2: callable
    :return: A 3D euclidean metric function
    :rtype: function
    """
    g2 = g1 if g2 == None else g2
    return lambda i, j: euclidDistance3d (g1 (i), g2 (j))
