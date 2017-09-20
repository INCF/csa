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

try:
    from lxml import etree
    from lxml.builder import E
except ImportError:
    pass

csa_tag = 'CSA'
csa_namespace = 'http://software.incf.org/software/csa/1.0'
CSA = '{%s}' % csa_namespace

CUSTOM = -4
OPERATOR = -3
BINDOPERATOR = -2
SINGLETON = -1

def to_xml (obj):
    if isinstance (obj, str):
        return E (obj)
    elif isinstance (obj, (int, float)):
        return E ('cn', str (obj))
    elif isinstance (obj, CSAObject):
        return obj._to_xml ()
    else:
        raise RuntimeError ("don't know how to turn %s into xml" % obj)

# precedence levels:
#
# 0 + -
# 1 *
# 2 ~

class CSAObject (object):
    tag_map = {}

    def __init__ (self, name, precedence = 3):
        self.name = name
        self.precedence = precedence

    def __repr__ (self):
        return 'CSA(%s)' % self.repr ()

    def repr (self):
        if hasattr (self, 'name'):
            return self.name
        else:
            return self.__class__.__name__

    def _repr_as_op2 (self, parentPrecedence):
        if self.precedence <= parentPrecedence:
            return '(%s)' % self.repr ()
        else:
            return self.repr ()

    def _repr_applyop (self, op_repr, obj):
        return '%s*%s' % (op_repr, obj._repr_as_op2 (1))

    def to_xml (self):
        return E (csa_tag, self._to_xml (), xmlns=csa_namespace)

    def _to_xml (self):
        return E (self.name)

    @classmethod
    def apply (cls, operator, *operands):
        return E ('apply', to_xml (operator), *list (map (to_xml, operands)))

    @classmethod
    def formalFromXML (cls, element):
        assert element.tag == CSA + 'bvar'
        nodes = element.getchildren ()
        assert nodes[0].tag == CSA + 'ci'
        return nodes[0].text

    @classmethod
    def from_xml (cls, element, env = {}):
        if element.tag == CSA + 'cn':
            return eval (element.text)
        elif element.tag == CSA + 'ci':
            #*fixme* Implement env as lists of dictionaries
            return env[element.text]
        elif element.tag == CSA + 'apply':
            nodes = element.getchildren ()
            operator = nodes[0].tag
            operands = [ cls.from_xml (e, env) for e in nodes[1:] ]
            if operator == CSA + 'plus':
                return operands[0].__add__ (operands[1])
            elif operator == CSA + 'minus':
                return operands[0].__sub__ (operands[1])
            elif operator == CSA + 'times':
                return operands[0].__mul__ (operands[1])
            elif operator == CSA + 'complement':
                return operands[0].__invert__ ()
            else:
                # Function or operator application
                entry = CSAObject.tag_map[operator]
                obj = entry[0]
                if entry[1] == OPERATOR:
                    return obj * operands[1]
                else:
                    return obj (*operands)
        elif element.tag == CSA + 'bind':
            nodes = element.getchildren ()
            tag = nodes[0].tag
            entry = CSAObject.tag_map[tag]
            if entry[1] != BINDOPERATOR:
                raise RuntimeError ("unknown binding operator tag %s" % tag)
            bindingOperator = entry[0]
            bvars = [ CSAObject.formalFromXML (e) for e in nodes[1:-1] ]
            return bindingOperator (bvars, nodes[-1])
        elif element.tag in CSAObject.tag_map:
            entry = CSAObject.tag_map[element.tag]
            obj = entry[0]
            if entry[1] == SINGLETON:
                return obj
            elif entry[1] == CUSTOM:
                return obj.from_xml (element, env)
            else:
                return obj ()
        else:
            raise RuntimeError ("don't know how parse tag %s" % element.tag)

    def xml (e):
        print(etree.tostring (e))

    def write(self, file):
        doc = self.to_xml ()
        etree.ElementTree(doc).write (file, encoding="UTF-8",
                                      pretty_print=True, xml_declaration=True)

class BinaryCSAObject (CSAObject):
    operator_table = {'+': 'plus', '-': 'minus', '*': 'times'}
    
    def __init__ (self, name, op1, op2, precedence = 0):
        CSAObject.__init__ (self, name, precedence)
        self.op1 = op1
        self.op2 = op2

    def repr (self):
        if isinstance (self.op1, CSAObject):
            op1 = self.op1.repr ()
            if self.op1.precedence < self.precedence:
                op1 = "(%s)" % op1
        else:
            op1 = self.op1

        if isinstance (self.op2, CSAObject):
            op2 = self.op2._repr_as_op2 (self.precedence)
        else:
            op2 = self.op2
            
        return "%s%s%s" % (op1, self.name, op2)

    def _to_xml (self):
        if isinstance (self.op1, CSAObject):
            op1 = self.op1._to_xml ()
        else:
            op1 = self.op1

        if isinstance (self.op2, CSAObject):
            op2 = self.op2._to_xml ()
        else:
            op2 = self.op2

        if self.name in BinaryCSAObject.operator_table:
            op = BinaryCSAObject.operator_table[self.name]
        else:
            op = self.name
        return E ('apply', E (op), op1, op2)


class OpExprValue (BinaryCSAObject):
    def __init__ (self, operator, operand):
        BinaryCSAObject.__init__ (self, '*', operator, operand, 1)


class Operator (CSAObject):
    def __init__ (self, name='ioperator'):
        CSAObject.__init__ (self, name)


def from_xml (root):
    assert root.nsmap[None] == csa_namespace
    return CSAObject.from_xml (root.getchildren ()[0])


def parse (filename):
    doc = etree.parse (filename)
    return from_xml (doc.getroot())


def parseString (string):
    el = etree.fromstring (string)
    return from_xml (el)


def registerTag (tag, obj, mode):
    CSAObject.tag_map[CSA + tag] = (obj, mode)
 
