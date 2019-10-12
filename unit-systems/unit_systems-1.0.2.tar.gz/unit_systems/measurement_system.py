"""Defines measurement systems and related objects
A measurement system is a specific unit system in a given physical system.
It has a complete set of defining quantities, which are not necessarily aligned with the defining quantities
of the underlying physical system

For example, one can choose the SI system to describe all of physics and the defining physical quantities.
An example of derived system is the HEP system, in which one has action (with defining unit hbar) and velocity
(with defining unit c) as defining quantities.
"""
# External imports
from sympy import Matrix,det
from math import log,exp

# Internal imports
from .physical_system import PhysicalQuantity,PhysicalSystem


class MeasurementSystem(PhysicalSystem):
    """
    TODO Comments about the matrix of the form
    1      | 0 0 0 0
    _________________
    log(u1)|
       .   |
       .   |   Y
       .   |
    log(uN)|
    where Y is the transfer matrix of the exponents and ui are the value of the defining quantities
    cf log(Ui) = log(ui) + Yij log(U'j) = M.(1,log(U'j)


    """
    def __init__(self,defining_quantities):
        """

        :param defining_quantities: tuples of length 3: (quantity_name unit_name,PhysicalQuantity)
        All quantities must share the same system
        TODO option to build the quantity name from the underlying system quantity_string
        """
        #TODO The naming must be better handled ! A system similar to the physicalsystem must be taken to have names
        #TODO for the quantities that are expressed within the system
        #TODO Best would be to align the structure of defining_quantities better with the parent class

        # TODO Check input structure
        # system = None
        # for Quq in defining_quantities:
        #     if system is None:
        #         system = Quq[2].system
        #     else:
        #         assert Quq[2].system == system
        #         Quq[2].name = Quq[1]



        # No zero value can be used
        assert all([Quq[2].value != 0 for Quq in defining_quantities])

        # Load data
        self.quantity_definitions = []
        self.quantities = []
        for Q, u, q in defining_quantities:
            self.quantity_definitions.append((Q,u))
            if isinstance(q,MeasurementQuantity):
                self.quantities.append(q.underlying_quantity())
            elif isinstance(q,PhysicalQuantity):
                self.quantities.append(q)
            else:
                raise TypeError("Need quantities")
        self.physical_system = self.quantities[0].system
        for q in self.quantities:
            assert self.physical_system == q.system, "All quantities must have the same underlying system"

        # Build the transfer matrix, check that it is invertible
        first_row = Matrix([1]+[0]*len(defining_quantities))
        log_qs = Matrix([log(q.value) for Q,u,q in defining_quantities])
        Y = Matrix([list(q.dimension) for Q, u, q in defining_quantities])
        self.matrix = Y.col_insert(0,log_qs).row_insert(0,first_row.transpose())
        Yinv = Y.inv()
        assert det(self.matrix) != 0
        # Build the inverse transfer matrix
        # We exploit the block structure to avoid mixing floats of the logs with potential int/rationals
        # that are in the exponent matrix Y/Yinv
        self.inverse_matrix = Yinv.col_insert(0,-Yinv*log_qs).row_insert(0,first_row.transpose())

    def one_unit(self,quantity):
        """Take a quantity and return a MeasurementQuantity in this system with the same dimension
        and with value 1 unit"""
        # Check if the quantity is a Measurement of a Physical quantity
        # TODO LATER WE ASSUME IT IS A MEASUREMENT
        assert isinstance(quantity,MeasurementQuantity)

        # If this is already the right system just set the value to 1
        if quantity.system == self:
            return MeasurementQuantity(1,quantity.dimension,self)
        # Otherwise first convert to the current system and then set the value to 1
        else:
            converted_quantity = quantity.to_system(self)
            return MeasurementQuantity(1,converted_quantity.dimension,self)

    def base_quantities(self):
        """Generate the list of MeasurementQuantities that correspond to 1 of each of the base unit_systems"""
        base_quantities = []
        for i,qu in enumerate(self.quantity_definitions):
            dimension = [0]*len(self.quantity_definitions)
            dimension[i] = 1
            base_quantities.append(MeasurementQuantity(1., dimension, self,name=self.quantity_definitions[i][1]))
        return base_quantities

    def __call__(self,*args,**kwargs):
        """Calling a MeasurementSystem instance on:
        - a MeasurementQuantity converts it to the system
        No other option for now
        """
        if len(args)==1 and isinstance(args[0],MeasurementQuantity):
            if self == args[0].system:
                return args[0]
            else:
                return(args[0].to_system(self))
        else:
            raise TypeError("Cannot process this type of input")

    #TODO add derived_units attribute that uses the derived unit name as a shorthand for
    #TODO some combinations of base unit_systems (eg: Newton = kg*m/s**2)
    #TODO build_value_string would then first look for the unit in a dict whose keys are tuple(dimension)
    #TODO and if found use the name


class MeasurementQuantity(PhysicalQuantity):
    """A MeasurementQuantity is a quantity expressed in a MeasurementSystem. It is the data of a physical dimension(a product of powers of elementary quantities expressed as a list of floats) and of a value (float)"""
    def __init__(self,value,dimension,system,name=None):
        assert isinstance(system,MeasurementSystem)
        PhysicalQuantity.__init__(self,value,dimension,system,name=name)

    def underlying_quantity(self):
        """Generate a PhysicalQuantity expressed in the underlying PhysicalSystem

        quantity = value * defining_quantity_1**n_1 * ... * defining_quantity_N**n_N
        where N = len(self.dimension)
        defining_quantity has a similar expression in terms of a value and the defining quantities of the underlying
        system
        """

        underlying_vector = self.vector.transpose() * self.system.matrix

        return PhysicalQuantity(exp(underlying_vector[0]),underlying_vector[1:],self.system.physical_system,name=self.name)

    def to_system(self,new_system):
        assert self.system.physical_system == new_system.physical_system
        new_vector = self.vector.transpose()* self.system.matrix * new_system.inverse_matrix
        return MeasurementQuantity(exp(new_vector[0]), new_vector[1:], new_system,
                                name=self.name)

# Allow system conversion when using the mother class algebraic operations
def system_match_left(func):
    def matched_func(left, right):
        if not (isinstance(left, MeasurementQuantity) and isinstance(right, MeasurementQuantity)):
            return func(left,right)
        if left.system != right.system:
            return func(left, right.to_system(left.system))
        else:
            return func(left, right)
    return matched_func
# Loop over algebraic functions and apply system convertor
for f in ["__mul__", "__rmul__", "__truediv__", "__rtruediv__", "__add__", "__sub__"]:
    setattr(MeasurementQuantity,
            f,
            system_match_left(getattr(PhysicalQuantity,f))
            )

def physical_measurement_system(physical_system):
    """Build a measurement system from the defining quantities of a physical system"""
    N = len(physical_system.quantity_definitions)
    defining_quantities = []
    for i,q in enumerate(physical_system.quantity_definitions):
        d = [0 if j != i else 1 for j in range(N) ]
        quantity_definition = (
            physical_system.quantity_definitions[i][0],
            physical_system.quantity_definitions[i][1],
            PhysicalQuantity(1, d, physical_system)
        )
        defining_quantities.append(quantity_definition)

    return MeasurementSystem(defining_quantities)

