Connection-Set Algebra (CSA)
============================

This is a demonstration implementation in Python of the Connection-Set
Algebra (Djurfeldt, Mikael (2012), Neuroinformatics)

Code status
===========
[![Build Status](https://travis-ci.org/INCF/csa.svg?branch=master)](https://travis-ci.org/INCF/csa)
[![Coverage Status](https://coveralls.io/repos/github/INCF/csa/badge.svg?branch=master)](https://coveralls.io/github/INCF/csa?branch=master)

Purpose
=======

The CSA library provides elementary connection-sets and operators for
combining them. It also provides an iteration interface to such
connection-sets enabling efficient iteration over existing connections
with a small memory footprint also for very large networks. The CSA
can be used as a component of neuronal network simulators or other
tools.

See the following reference for more information:

Mikael Djurfeldt (2012) "The Connection-set Algebra---A Novel
Formalism for the Representation of Connectivity Structure in Neuronal
Network Models" Neuroinformatics 10(3), 1539-2791,
http://dx.doi.org/10.1007/s12021-012-9146-1

License
=======

CSA is released under the GNU General Public License

Requirements
============

CSA is dependent on Numpy and Matplotlib

Introduction
============

A connection set is a set of existing connections between a set of
source nodes and a set of target nodes.  Typically, source and target
nodes are neurons in a neuronal network, but targets could also be
particular structures of a neuron, such synaptic sites.  Sources and
targets are enumerated by integers and a connection is represented by
a pair of integers, one denoting the source node and one the target
node.  Source and target can be (and is often) the same set.

CSA connection sets are usually infinite.  This is a simplification
compared to the common situation of finite source and target sets in
that the sizes of these sets do not need to be considered.  Connection
sets can have arbitrary values associated with connections.  Pure
connection sets without any values associated are called masks.

Getting started
===============

Basics
------

To get access to the CSA in Python, type:
::

    from csa import *

The mask representing all possible connections between an infinite
source and target set is:
::
    
    full

To display a finite portion of the corresponding connectivity matrix,
type:
::

    show (full)

One-to-one connectivity (where source node 0 is connected to target
node 0, source 1 to target 1 etc) is represented by the mask oneToOne:
::

    show (oneToOne)

The default portion displayed by "show" is (0, 29) x (0, 29).
(0, 99) x (0, 99) can be displayed using:
::

    show (oneToOne, 100, 100)

If source and target set is the same, oneToOne describes
self-connections.  We can use CSA to compute the set of connections
consisting of all possible connections except for self-connections
using the set difference operator "-":
::
  
    show (full - oneToOne)

Finite connection sets can be represented using either lists of
connections, with connections represented as tuples:
::
  
    show ([(22, 7), (8, 23)])

or using the Cartesian product of intervals:
::

    show (cross (range (10), range (20)))

We can form a finite version of the infinite oneToOne by taking the
intersection "*" with a finite connection set:
::

      c = cross (range (10), range (10)) * oneToOne
      show (c)

Finite connection sets can be tabulated:
::

    tabulate (c)

In Python, finite connection sets provide an iterator interface:
::

    for x in cross (range (10), range (10)) * oneToOne:
        print x

Random connectivity and the block operator
------------------------------------------

Connectivity where the existence of each possible connection is
determined by a Bernoulli trial with probability p is expressed with
the random mask random (p), e.g.:
::

    show (random (0.5))

The block operator expands each connection in the operand into a
rectangular block in the resulting connection matrix, e.g.:
::

    show (block (5,3) * random (0.5))

Note that "*" here means operator application.  There is also a
quadratic version of the operator:
::
  
    show (block (10) * random (0.7))

Using intersection and set difference, we can now formulate a more
complex mask:
::

    show (block (10) * random (0.7) * random (0.5) - oneToOne)

Geometry
--------

In CSA, the basic tool to handle distance dependent connectivity is
metrics.  Metrics are value sets d (i, j).  Metrics can be defined
through geometry functions.  A geometry function maps an index to a
position.  We can, for example, assign a random position in the unit
square to each index:
::

    g = random2d (900)

The positions of the grid described by g have indices from 0 to 899
and can be displayed like this:
::

    gplot2d (g, 900)

Alternatively, we can arrange indices in a 30 x 30 grid within the
unit square:
::
  
    g = grid2d (30)

We can now define the euclidean metric on this grid:
::

    d = euclidMetric2d (g)

An example of a distance dependent connection set is the disc mask
Disc (r) * d which connects each index i to all indices j within a
distance d (i, j) < r:
::

    c = disc (r) * d

To examine the result we can employ the function gplotsel2d (g, c, i)
which displays the targets g (j) of i in the connection set c:
::

    gplotsel2d (g, c, 434)

In the case where the connection set represents a projection between
two different coordinate systems, we define one geometry function for
each.  In the following example g1 is direction in visual space in arc
minutes while g2 is position in the cortical representation of the
Macaque fovea in mm:
::

    g1 = grid2d (30)
    g2 = grid2d (30, x0 = -7.0, xScale = 8.0, yScale = 8.0)

We now define a projection operator which takes visual coordinates
into cortical (Dow et al. 1985):
::

    import cmath

    @ProjectionOperator
    def GvspaceToCx (p):
        w = 7.7 * cmath.log (complex (p[0] + 0.33, p[1]))
        return (w.real, w.imag)

To see how the grid g1 is transformed into cortical space, we type:
::

    gplot2d (GvspaceToCx * g1, 900)

The inverse projection is defined:
::

    @ProjectionOperator
    def GcxToVspace (p):
        c = cmath.exp (complex (p[0], p[1]) / 7.7) - 0.33
        return (c.real, c.imag)

Real receptive field sizes vary with eccentricity.  Assume, for now,
that we want to connect each target index to sources within a disc of
constant radius.  We then need to project back into visual space and
use the disc operator:
::

    c = disc (0.1) * euclidMetric2d (g1, GcxToVspace * g2)

Again, we use gplotsel2d to check the result:
::

    gplotsel2d (g2, c, 282)

