# NLDSL (c) 2019 by Kevin Kiefer <abc.kiefer@gmail.com>, Heidelberg University
#
# NLDSL is licensed under a
# Creative Commons Attribution-NonCommercial 3.0 Unported License.
#
# You should have received a copy of the license along with this
# work.  If not, see <http://creativecommons.org/licenses/by-nc/3.0/>.

"""Each argument provided to a DSL statement is of a certain type.
The DSL argument types are Value, Keyword, Variable, Expression and VarList.
Additionally some types dedicated to the operators used by expression exists.
"""

from enum import IntEnum




class OperatorType(IntEnum):
    """Type of operators as used by the ExpressionRule."""
    OPERATOR = 0
    UNARY_FUNCTION = 1
    BINARY_FUNCTION = 2




class Type:
    """Base class for DSL argument types.

    Args:
        data (object): The data associated with this object
    """

    def __init__(self, data):
        """Please see help(Type)."""
        self._data = data

    @property
    def data(self):
        """Get the data member."""
        return self._data

    @data.setter
    def data(self, new_data):
        """Set the data member."""
        self._data = new_data
        return self




class Value(Type):
    """A Type for arguments which are plain values."""

    @property
    def value(self):
        """Set the value."""
        return self.data

    @value.setter
    def value(self, new_value):
        """Get the value."""
        self.data = new_value
        return self




class Keyword(Type):
    """A Type for arguments which are keywords."""

    @property
    def keyword(self):
        """Get the keyword."""
        return self.data

    @keyword.setter
    def keyword(self, new_keyword):
        """Set the keyword."""
        self.data = new_keyword
        return self


class Variable(Type):
    """A Type for arguments which are variables."""

    @property
    def name(self):

        """Get the name."""
        return self.data

    @name.setter
    def name(self, new_name):
        """Set the name."""
        self.data = new_name
        return self


class Expression(Type):
    """A Type for arguments which are expressions.

    Args:
        name (str): The name of this variable
    """

    def __init__(self, name):
        """Please see help(Expression)."""
        super().__init__(name)
        self.name = name

    @property
    def name(self):
        """Get the name."""
        return self.data

    @name.setter
    def name(self, new_name):
        """Set the name."""
        self.data = new_name
        return self


class VarList(Type):
    """A Type for arguments which are Variable Lists.

    Args:
        name (str): The name of this variable list
        variables (list): A list of Variable or Keyword objects
    """

    def __init__(self, name, variables):
        """Please see help(VarList)."""
        super().__init__(variables)
        self._name = name

    @property
    def name(self):
        """Get the name."""
        return self._name

    @name.setter
    def name(self, new_name):
        """Set the name."""
        self._name = new_name
        return self

    @property
    def variables(self):
        """Get the variables and keywords."""
        return self.data

    @variables.setter
    def variables(self, new_variables):
        """Set the variables and keywords."""
        self.data = new_variables
        return self




def is_type(arg):
    """Check if `arg` is an instance of Type.

    Args:
        arg (object): The object to investigate.

    Returns:
        (bool) True if the argument is a Type, false otherwise.
    """
    return isinstance(arg, Type)




def is_value(arg):
    """Check if `arg` is an instance of Value.

    Args:
        arg (object): The object to investigate.

    Returns:
        (bool) True if the argument is a Value, false otherwise.
    """
    return isinstance(arg, Value)




def is_keyword(arg):
    """Check if `arg` is an instance of Keyword.

    Args:
        arg (object): The object to investigate.

    Returns:
        (bool) True if the argument is a Keyoword, false otherwise.
    """
    return isinstance(arg, Keyword)




def is_variable(arg):
    """Check if `arg` is an instance of Variable.

    Args:
        arg (object): The object to investigate.

    Returns:
        (bool) True if the argument is a Variable, false otherwise.
    """
    return isinstance(arg, Variable)




def is_expression(arg):
    """Check if `arg` is an instance of Expression.

    Args:
        arg (object): The object to investigate.

    Returns:
        (bool) True if the argument is a Expression, false otherwise.
    """
    return isinstance(arg, Expression)




def is_var_list(arg):
    """Check if `arg` is an instance of VarList.

    Args:
        arg (object): The object to investigate.

    Returns:
        (bool) True if the argument is a VarList, false otherwise.
    """
    return isinstance(arg, VarList)
