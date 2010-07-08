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

import random as _random
import numpy as _numpy

import connset as _cs
import intervalset as _is

class MaskPartition (_cs.Finite, _cs.Mask):
    def __init__ (self, mask, partitions, selected):
        self.subMask = partitions[selected] * mask

        domain = _cs.IntervalSetMask ([], [])
        for m in partitions:
            assert _cs.isFinite (m), 'partitions must be finite'
            domain = domain.multisetSum (m)
        
        self.state = { 'domain' : domain,
                       'partitions' : partitions,
                       'selected' : selected }

    def bounds (self):
        return self.subMask.bounds ()

    def startIteration (self, state):
        for key in self.state:
            state[key] = self.state[key]
        self.subMask.startIteration (state)

    def iterator (self, low0, high0, low1, high1, state):
        return self.subMask.iterator (low0, high0, low1, high1, state)


class OneToOne (_cs.Mask):
    def __init__ (self):
        _cs.Mask.__init__ (self)
    
    def iterator (self, low0, high0, low1, high1, state):
        for i in xrange (max (low0, low1), min (high0, high1)):
            yield (i, i)


class ConstantRandomMask (_cs.Mask):
    def __init__ (self, p):
        _cs.Mask.__init__ (self)
        self.p = p
        self.state = _random.getstate ()

    def startIteration (self, state):
        _random.setstate (self.state)

    def iterator (self, low0, high0, low1, high1, state):
        for j in xrange (low1, high1):
            for i in xrange (low0, high0):
                if _random.random () < self.p:
                    yield (i, j)


class SampleNRandomMask (_cs.Mask):
    # The algorithm based on first sampling the number of connections
    # per partition has been arrived at through discussions with Hans
    # Ekkehard Plesser.
    #
    def __init__ (self, N):
        _cs.Mask.__init__ (self)
        self.N = N
        self.randomState = _random.getstate ()
        self.npRandomState = _numpy.random.get_state ()
        # The following yields the same result on all processes.
        # We should add a seed function to the CSA.
        _numpy.random.seed (hash ('SampleNRandomMask'))
        self.npCommonState = _numpy.random.get_state ()

    def startIteration (self, state):
        _random.setstate (self.randomState)
        if not 'partitions' in state:
            state['N'] = self.N
        else:
            _numpy.random.set_state (self.npCommonState)
            sizes = map (len, state['partitions'])
            total = sum (sizes)
            N = _numpy.random.multinomial (self.N, _numpy.array (sizes) \
                                           / float (total))
            state['N'] = N[state['selected']]
            _numpy.random.set_state (self.npRandomState)

    def iterator (self, low0, high0, low1, high1, state):
        N = state['N']
        if not 'partitions' in state:
            set0 = _is.IntervalSet ((low0, high0 - 1))
            set1 = _is.IntervalSet ((low1, high1 - 1))
        else:
            mask = state['partitions'][state['selected']]
            assert isinstance (mask, _cs.IntervalSetMask), \
                   'SampleNRandomMask iterator only handles IntervalSetMask partitions'
            set0 = mask.set0
            set1 = mask.set1

        N0 = set0.nIntegers
        N1 = set1.nIntegers
        perTarget = _numpy.random.multinomial (N, [1.0 / N1] * N1)
        sources = []
        for i in set0:
            sources.append (i)

        m = 0
        for j in set1:
            s = []
            for k in xrange (0, perTarget[m]):
                s.append (sources[_random.randint (0, N0 - 1)])
            s.sort ()
            for i in s:
                yield (i, j)
            m += 1
