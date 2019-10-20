# NLDSL (c) 2019 by Kevin Kiefer <abc.kiefer@gmail.com>, Heidelberg University
#
# NLDSL is licensed under a
# Creative Commons Attribution-NonCommercial 3.0 Unported License.
#
# You should have received a copy of the license along with this
# work.  If not, see <http://creativecommons.org/licenses/by-nc/3.0/>.

"""The DSL provides a mechanism to add new grammar rules via DSL statements.

This mechanism is implemented by the PipeFunction class, which synthesizes
new grammar rules based on a DSL statement. The Converter classes translate
the arguments of the new grammar.
"""

from .types import is_variable, is_expression, is_var_list
from .rules import GrammarRule
from .exceptions import DSLArgumentError, DSLFunctionError




class IdentityConverter:
    """A converter for keyword and value arguments.
    It basically does nothing, it just exists for API consistency.

    Args:
        arg (dict): A dict containg a Keyword or Value (see nldsl.core.types).
        name_dict (dict): A mapping from variable names to instructions.
    """

    def __init__(self, arg, name_dict):
        """Please see help(IdentityConverter)."""
        self._value = arg.data


    @property
    def value(self):
        """The value (or keyword) which will be returned by the call method"""
        return self._value


    def __call__(self, input_dict):
        """Returns a list containing only the value of the `arg` element
        it received on constructions.

        Args:
            input_dict (dict): Not used, exist only for API consistency.

        Returns:
            (list) A list containing only a single string.
        """
        return [self._value]




class NameConverter:
    """Converts a variable or expression name to its values.

    Args:
        arg (dict): Either a Variable or Expression type (see nldsl.core.types).
        name_dict (dict): A mapping from variable names to instructions.

    Raises:
        ValueError: If the arg.data is not a key in `name_dict`.
    """

    def __init__(self, arg, name_dict):
        """Please see help(NameConverter)."""
        if not arg.data in name_dict:
            raise ValueError("Variable name not found.")
        self._name = arg.data


    @property
    def name(self):
        """The name of the variable or expression."""
        return self._name


    def __call__(self, input_dict):
        """Returns the value of the variable name stored in `input_dict`.

        Args:
           input_dict (dict): A map from variable names to values

        Returns:
            (list) A list containing only one string
        """
        return [input_dict[self._name]]




class ListConverter:
    """Converts a variable list to its values.

    Args:
        arg (dict): A dict containg a VarList (see nldsl.core.types).
        name_dict (dict): A mapping from variable names to instructions.

    Raises:
        ValueError: If the variable list name is not in `name_dict`.
    """

    def __init__(self, arg, name_dict):
        """Please see help(ListConverter)."""
        self._name = arg.name
        if not self._name:
            variables = {x.data for x in arg.data if is_variable(x)}
            self._name = next(name for name in name_dict if set(name) == variables)
        elif not self._name in name_dict:
            raise ValueError("Variable list name not found.")

        input_vars = [v.data for v in name_dict[self._name] if is_variable(v)]
        self._map = {x.data: input_vars.index(x.data) for x in arg.data if is_variable(x)}
        self._data = arg.data


    @property
    def name(self):
        """The name of the variable list."""
        return self._name

    @property
    def data(self):
        """The data of the target."""
        return self._data

    @property
    def map(self):
        """The mapping of variable positions."""
        return self._map


    def __call__(self, input_dict):
        """Returns the values for the variable list stored in `input_dict`.

        Args:
           input_dict (dict): A map from variable names to values

        Returns:
            (list) A list containg the values corresponding to variable list
        """
        return sum([self._map_input(data) for data in input_dict[self._name]], [])


    def _map_input(self, input_data):
        """Map a tuple of values to a list.

        This list contains all keywords and the values of variables
        found in the tuple in the correct order,
        as defined by the variable list.

        Args:
            input_data (tuple): A tuple of values

        Returns:
            (list) A list of strings.
        """
        res = []
        for arg in self._data:
            if is_variable(arg):
                res.append(input_data[self._map[arg.data]])
            else:
                res.append(arg.data)
        return res




class PipeFunction:
    """PipeFunction provides a mechanism to define functions within the DSL.

    Given a DSL statement such as::

        #$ prepare $x with labels $y = rename columns $x to data, $y to labels | sort by $y

    The left side of the equal sign defines the `instructions` and from the right
    side we derive the `fun_map`, which maps functions to partially specified argument lists.

    Note:
        This docstring differs for every instance of GrammarFunction,
        that is the __init__ methods modifies the docstring.

    Args:
        name (str): The name of this PipeFunction within the DSL.
        instructions (list): A list of argument parsing instructions.
        fun_list (list): An list of (function, argument list) pairs.
    """

    def __init__(self, name, instructions, fun_list):
        """Please see help(PipeFunction)."""
        self.name = name
        self.rule = GrammarRule(instructions, {})
        self.fun_conv = self._extract_args_converters(instructions, fun_list)

        self.function_type = self._compute_type(fun_list)
        self.__name__ = self.name.replace(" ", "_")
        self.__doc__ = self._build_docstring()


    @property
    def grammar_rule(self):
        """The GrammarRule, responsible for argument conversion."""
        return self.rule

    @property
    def grammar_rule_name(self):
        """The GrammarRule's name."""
        return self.name

    @property
    def grammar_rule_desc(self):
        """A string containing a description of the associated grammar rule."""
        return self.rule.description

    @property
    def grammar_rule_type(self):
        """The GrammarRule's type."""
        return self.function_type

    @property
    def functions(self):
        """A list of the internal functions."""
        return [fun for fun, conv in self.fun_conv]

    @property
    def argument_converters(self):
        """A list of (function, argument converters) pairs."""
        return self.fun_conv


    def __call__(self, code, args, env=None):
        """Map the arguments `args` into a DSL pipeline and convert it to code.

        Args:
            args (list): A list of strings.

        Returns:
            (str) A string containing executable python code.

        Raises:
            DSLFunctionError: If a DSLArgumentError occurs while applying the grammar rules.
        """
        try:
            args_dict = self.rule(args)
        except DSLArgumentError as err:
            raise DSLFunctionError("Missing argument", err.rule, self.__doc__) from err

        for fun, arg_converters in self.fun_conv:
            code = fun(code, sum([conv(args_dict) for conv in arg_converters], []), env)
        return code


    @classmethod
    def _extract_name_dict(cls, instructions):
        """Extract the names of variables and variable list from the `instructions`.

        Args:
            instructions (list): A list of parsing instructions.

        Returns:
            (dict) A mapping from variable names to (modified) instructions.
        """
        name_dict = {}
        for i in instructions:
            if is_variable(i) or is_expression(i):
                name_dict[i.data] = i.data
            elif is_var_list(i) and i.name:
                name_dict[i.name] = i.data
            elif is_var_list(i) and not i.name:
                vl_name = tuple([x.data for x in i.data if is_variable(x)])
                name_dict[vl_name] = i.data
        return name_dict


    def _extract_args_converters(self, instructions, fun_list):
        """Extract the necessary argument converters from `instructions`
        and `fun_list` and create them.

        Args:
            instructions (list): A list of parsing instructions
            fun_list (list): An list of (function, argument list) pairs.

        Returns:
            (list) A list of argument converters.
        """
        fun_conv, name_dict = [], self._extract_name_dict(instructions)
        for fun, args in fun_list:
            conv = []
            for arg in args:
                if is_var_list(arg):
                    conv.append(ListConverter(arg, name_dict))
                elif is_variable(arg):
                    conv.append(NameConverter(arg, name_dict))
                elif is_expression(arg):
                    conv.append(NameConverter(arg, name_dict))
                else:
                    conv.append(IdentityConverter(arg, name_dict))
            fun_conv.append((fun, conv))
        return fun_conv


    @classmethod
    def _compute_type(cls, fun_list):
        type_list = []
        for fun, _ in fun_list:
            if hasattr(fun, "grammar_rule_type"):
                type_list.append(fun.grammar_rule_type)
            else:
                type_list.append(None)

        if any(t is None for t in type_list):
            return None
        if any(t == "Function" for t in type_list):
            return "Function"
        if all(t == "Transformation" for t in type_list):
            return "Transformation"
        if type_list[0] == "Initialization":
            return "Initialization"
        if type_list[-1] == "Operation":
            return "Operation"
        return None


    def _build_docstring(self):
        # placeholder
        return ""
