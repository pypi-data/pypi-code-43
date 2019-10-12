'''Fundamental physical objects
'''

from numbers import Number
from math import log
from sympy import Matrix

class PhysicalSystem:
    """A PhysicalSystem is the abstract data of a number of a number of quantities and a list of physical constants which define what 1 unit is in this system
    """
    def __init__(self,quantities_and_units):
        """quantities_and_units: list of (str,str)"""
        QU_strings = []
        for qu in quantities_and_units:
            QU_strings.append((str(qu[0]),str(qu[1])))

        self.quantity_definitions = QU_strings

    def __call__(self,value,dimension,name=None):
        """Generate a quantity in this system with a given value and dimension"""
        return self.PhysicalQuantity(value,dimension,self,name=name)

    def base_quantities(self):
        """Generate the list of PhysicalQuantities that correspond to 1 of each of the base unit_systems"""
        base_quantities = []
        for i in range(len(self.quantity_definitions)):
            dimension = [0]*len(self.quantity_definitions)
            dimension[i] = 1
            base_quantities.append(PhysicalQuantity(1., dimension, self))
        return base_quantities


class Dimension(Matrix):
    """List of exponents that express the dimension of a quantity in a given system. Can be added and subtracted together, and multiplied or divided by numbers"""
    def __init__(self,*args,**kwargs):
        """Check that it has only one line"""
        assert self.shape[1] == 1,"Dimensions must be a one-dimensional vector"

class PhysicalQuantity:
    """A PhysicalQuantity is a quantity expressed in a PhysicalSystem. It is the data of a physical dimension(a product of powers of elementary quantities expressed as a list of floats) and of a value (float)"""
    def __init__(self,value,dimension,system,name=None):
        assert isinstance(value,Number)
        self.value = value

        assert isinstance(system,PhysicalSystem)
        self.system = system

        assert len(dimension) == len(system.quantity_definitions)
        self.dimension = Dimension(dimension)

        # With the use of the vector notation, the value and dimension entries are probably useless
        self.vector = Matrix([log(self.value)]+list(dimension))

        self.name=name



    def __mul__(self, other):
        if isinstance(other,Number):
            return self.__class__(self.value*other,self.dimension,self.system)
        else:
            assert other.system == self.system
            return self.__class__(self.value*other.value,self.dimension+other.dimension,self.system)

    def __rmul__(self, other):
        assert isinstance(other,Number)
        return self*other

    def __truediv__(self, other):
        if isinstance(other,Number):
            return self.__class__(self.value/other,self.dimension,self.system)
        else:
            assert other.system == self.system
            return self.__class__(self.value/other.value,self.dimension-other.dimension,self.system)

    def __rtruediv__(self, other):
        assert isinstance(other,Number)
        return self.__class__(other/self.value,-self.dimension,self.system)

    def __pow__(self, power):
        assert isinstance(power,Number),"The exponent must be a number"
        return self.__class__(self.value**power, power*self.dimension, self.system)

    def __add__(self, other):
        assert other.system == self.system
        assert self.dimension == other.dimension
        return self.__class__(self.value + other.value, self.dimension, self.system)

    def __sub__(self, other):
        assert other.system == self.system
        assert self.dimension == other.dimension
        return self.__class__(self.value - other.value, self.dimension, self.system)

    def build_value_string(self):
        ustr = "{0:e}".format(self.value)
        for i, qu in enumerate(self.system.quantity_definitions):
            if self.dimension[i]:
                ustr += " {}^{}".format(qu[1],self.dimension[i])
        return ustr

    def build_quantity_string(self):
        qstr = ""
        for i, qu in enumerate(self.system.quantity_definitions):
            if self.dimension[i]:
                qstr += "[{}]^{}".format(qu[0], self.dimension[i])
        return qstr

    def __str__(self):
        ustr = self.build_value_string()
        if self.name is not None:
            ustr= self.name+" = "+ustr

        qstr = self.build_quantity_string()
        ustr += " ("+qstr+")"

        return ustr

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__,self.build_value_string())




