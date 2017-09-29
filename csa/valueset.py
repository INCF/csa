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

from .csaobject import *

class ValueSet (CSAObject):
    def __init__ (self):
        CSAObject.__init__ (self, "valueset")
        
    def __neg__ (self):
        return GenericValueSet (lambda i, j: - self (i, j))
    
    def __add__ (self, other):
        if not callable (other):
            return maybeAffine (other, 1.0, self)
        elif isinstance (other, (QuotedValueSet, AffineValueSet)):
            return other.__add__ (self)
        elif isinstance (other, GenericValueSet):
            return GenericValueSet (lambda i, j: self (i, j) + other.function (i, j))
        else:
            return GenericValueSet (lambda i, j: self (i, j) + other (i, j))

    def __radd__ (self, other):
        return self.__add__ (other)

    def __sub__ (self, other):
        return self.__add__ (- other)

    def __rsub__ (self, other):
        return self.__neg__ ().__add__ (other)

    def __mul__ (self, other):
        if not callable (other):
            return maybeAffine (0.0, other, self)
        elif isinstance (other, (QuotedValueSet, AffineValueSet)):
            return other.__mul__ (self)
        elif isinstance (other, GenericValueSet):
            return GenericValueSet (lambda i, j: self (i, j) * other.function (i, j))
        else:
            return GenericValueSet (lambda i, j: self (i, j) * other (i, j))

    def __rmul__ (self, other):
        return self.__mul__ (other)


class QuotedValueSet (ValueSet):
    def __init__ (self, expression):
        ValueSet.__init__ (self)
        self.expression = expression

    def __call__ (self, i, j):
        return self.expression

    def __neg__ (self):
        return QuotedValueSet (- self.expression)
    
    def __add__ (self, other):
        if not callable (other):
            return QuotedValueSet (self.expression + other)
        elif isinstance (other, QuotedValueSet):
            return QuotedValueSet (self.expression + other.expression)
        elif isinstance (other, AffineValueSet):
            return other.__add__ (self)
        else:
            return maybeAffine (self.expression, 1.0, other)

    def __mul__ (self, other):
        if not callable (other):
            return QuotedValueSet (self.expression * other)
        elif isinstance (other, QuotedValueSet):
            return QuotedValueSet (self.expression * other.expression)
        elif isinstance (other, AffineValueSet):
            return other.__mul__ (self)
        else:
            return maybeAffine (0.0, self.expression, other)        


class GenericValueSet (ValueSet):
    def __init__ (self, function):
        ValueSet.__init__ (self)
        self.function = function

    def __call__ (self, i, j):
        return self.function (i, j)

    def __neg__ (self):
        return GenericValueSet (lambda i, j: - self.function (i, j))

    def __add__ (self, other):
        if not callable (other):
            return maybeAffine (other, 1.0, self.function)
        elif isinstance (other, (QuotedValueSet, AffineValueSet)):
            return other.__add__ (self)
        elif isinstance (other, GenericValueSet):
            return GenericValueSet (lambda i, j: self.function (i, j) + other.function (i, j))
        else:
            return GenericValueSet (lambda i, j: self.function (i, j) + other (i, j))

    def __mul__ (self, other):
        if not callable (other):
            return maybeAffine (0.0, other, self.function)
        elif isinstance (other, (QuotedValueSet, AffineValueSet)):
            return other.__mul__ (self)
        elif isinstance (other, GenericValueSet):
            return GenericValueSet (lambda i, j: self.function (i, j) * other.function (i, j))
        else:
            return GenericValueSet (lambda i, j: self.function (i, j) * other (i, j))


class AffineValueSet (ValueSet):
    def __init__ (self, constant, coefficient, function):
        ValueSet.__init__ (self)
        self.const = constant
        self.coeff = coefficient
        self.func = function

    def __call__ (self, i, j):
        return self.const + self.coeff * self.func (i, j)

    def __neg__ (self):
        return maybeAffine (- self.const, - self.coeff, self.func)
    
    def __add__ (self, other):
        if not callable (other):
            return maybeAffine (self.const + other, self.coeff, self.func)
        elif isinstance (other, QuotedValueSet):
            return maybeAffine (self.const + other.expression,
                                self.coeff, self.func)
        elif isinstance (other, AffineValueSet):
            f = lambda i, j: \
                    self.const * self.func (i, j) \
                    + other.const * other.func (i, j)
            return maybeAffine (self.const + other.const,
                                1.0,
                                f)

    def __mul__ (self, other):
        if not callable (other):
            return maybeAffine (self.const * other,
                                self.coeff * other,
                                self.func)
        elif isinstance (other, QuotedValueSet):
            return maybeAffine (self.const * other.expression,
                                self.coeff * other.expression,
                                self.func)
        elif isinstance (other, AffineValueSet):
            f = lambda i, j: \
                    other.const * self.coeff * self.func (i, j) \
                    + self.const * other.coeff * other.func (i, j) \
                    + self.coeff * other.coeff \
                      * self.func (i, j) * other.func (i, j)
            return maybeAffine (self.const * other.const,
                                1.0,
                                f)

def maybeAffine (const, coeff, func):
    if coeff == 0.0:
        return QuotedValueSet (const)
    elif const == 0.0 and coeff == 1.0:
        return GenericValueSet (func)
    else:
        return AffineValueSet (const, coeff, func)
