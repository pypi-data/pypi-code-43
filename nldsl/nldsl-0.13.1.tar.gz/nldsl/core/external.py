# NLDSL (c) 2019 by Kevin Kiefer <abc.kiefer@gmail.com>, Heidelberg University
#
# NLDSL is licensed under a
# Creative Commons Attribution-NonCommercial 3.0 Unported License.
#
# You should have received a copy of the license along with this
# work.  If not, see <http://creativecommons.org/licenses/by-nc/3.0/>.

"""External Dynamic Grammar Rules are added via python functions.

It is advised to use the @grammar decorator for this, however it is not mandatory.
The following prototypes are valid:
* my_function(str: code, list: args, dict: env) -> str
* my_function(str: code, list: args) -> str
* my_function(str: code, dict: env) -> str
* my_function(str: code) -> str

In case my_function only takes two arguments the second argument must be named `args`or `env`.
Every class in this module contributes to the @grammar decorator.

Example:
    Implementation of a grammar rule for the pandas code generator::

        @grammar(PandasExpressionRule)
        def select_rows(code, args):
            \"\"\"Select the rows of a DataFrame based on some condition.

            The condition can be composed out of boolean, comparison and arithmetic
            expression. The operator precedence is equivalent to python and it is possible
            to use brackets to modify it.

            Examples:
                1. ## x = on df | select rows df.col1 > (14.2 + z) and df.col2 == 'A'
                2. ## x = on df | select rows df.col1 != 0 and not df.col2 in [3, 5, 7]
                3. ## x = on df | select rows df.col3 % df.col1 != 2 or df.col1 <= 12

            Grammar:
                select rows !condition

            Args:
                condition (expression): A boolean expression used as a row filter.

            Type:
                Transformer
            \"\"\"
            return code + "[{}]".format(args["condition"])
"""

from textwrap import dedent
from .types import Keyword, Variable, Expression, VarList
from .utils import decorator_factory, convert_function
from .rules import ExpressionRule, GrammarRule
from .exceptions import DSLArgumentError, DSLFunctionError




class GrammarParser:
    """A GrammarParser parses the argument list of a DSL sentence.
    The parsing procedure is define via specification of the associated grammar.
    A grammar rule should be specified as follows::

        <name> <variable List | <variable> | <keyword> | <expression>...
        variable name 1> := { value_1, ... , value_n}
        ...
        <variable name n> := { value_1, ... , value_m}

    1. <name> can be any sequence of words (e.g. rename columns),
       optionally surrounded with brackets "(<name>)"
    2. <keyword> can be any word
    3. <variable> a word prefixed by the `$` sign (e.g $my_variable)
    4. <variable list> has the form $var_list_name[$variable1 keyword1 ...],
       any number of variables and keywords may be contained within the brackets.
       Providing a <var_list_name> is optional and will default to the tuple
       ($variable1, ... , $variable2)
    5. The rows of the form `<variable name> := { value_1, ... , value_n}` are optional
       and specify a finite set of values { value_1, ... , value_n} available to the variable.

    Example:
        Definition of the grammar rule "group by"::

            group by $columns[$col] apply $agg
            agg := { min, max, avg, sum }

    Args:
        input_str (str): A string containing grammar rules.
        expr_rule (ExpressionRule): The type of expression rule to be used
    """

    def __init__(self, input_str, expr_rule=ExpressionRule):
        """Please see help(GrammarParser)."""
        grammar_lines, choice_lines, function_type = self._parse_grammar_desc(input_str)
        grammar_desc = self._prepare_grammar_desc(grammar_lines)
        name, grammar_desc = self._extract_rule_name(grammar_desc)
        instructions = self._extract_instructions(grammar_desc)
        choices = self._extract_choices(choice_lines)
        self.name = name
        self.function_type = function_type
        self.rule = GrammarRule(instructions, choices, expr_rule)


    @property
    def grammar_rules(self):
        """The GrammarRule, responsible for argument conversion."""
        return self.rule.rules

    @property
    def grammar_choices(self):
        """Mapping from variable names to choices."""
        return self.rule.choices

    @property
    def grammar_rule_name(self):
        """The GrammarRule's name."""
        return self.name

    @property
    def grammar_rule_type(self):
        """The GrammarRule's type."""
        return self.function_type

    @property
    def grammar_rule_desc(self):
        """A string containing a description of the associated grammar rule."""
        return self.rule.description


    def __call__(self, args):
        """Convert the list of arguments `args` into a dictinonary.

        All keywords are removed from `args`.
        All variable names become keys to their corresponding values.
        VarLists are converted into lists of tuples, where each tuples
        contains the values of the variables contained in the list in order.

        Args:
            args (list): A list of strings

        Returns:
            (dict) A dictionary, which maps from variable names to values
        """
        return self.rule(args)


    @classmethod
    def _parse_grammar_desc(cls, input_str):
        """Parse a string containg a grammar description.

        Args:
            input_str (str): A string containing grammar rules.

        Returns:
            (tuple) list of lines with grammar rules and list with choices
        """
        lines = [line.strip() for line in input_str.splitlines()]
        idx = lines.index("Grammar:")

        grammar_lines = []
        for line in lines[idx+1:]:
            idx += 1 # keep track of line number for "choices from a list"
            grammar_lines.append(line.strip("\\ \t\n"))
            # grammar rules may span multiple lines (via "\" at the end)
            if not line.endswith("\\"):
                break

        choice_lines = []
        for line in lines[idx+1:]:
            # skip empty lines
            if not line.strip():
                continue
            # A "choice from a list" line
            if ":=" in line and "{" in line and "}" in line:
                choice_lines.append(line)
            else:
                break

        try:
            function_type = lines[lines.index("Type:") + 1].strip()
        except ValueError:
            function_type = None

        return grammar_lines, choice_lines, function_type


    @classmethod
    def _extract_rule_name(cls, grammar_desc):
        """Extract the name of the rule from the grammar_desc.

        Args:
            grammar_desc (list): List of strings as return by _prepare_grammar_desc

        Returns:
            (tuple) The name of the grammar rule and the updated grammar_desc
        """
        if "(" in grammar_desc[0]:
            stop_idx = [")" in t for t in grammar_desc].index(True) + 1
        else:
            matches = [("$" in t or "!" in t) for t in grammar_desc]
            stop_idx = matches.index(True) if True in matches else len(grammar_desc)

        return " ".join(grammar_desc[0:stop_idx]).strip(" )("), grammar_desc[stop_idx:]


    @classmethod
    def _extract_instructions(cls, grammar_desc):
        """Extract the instruction on how to parse the grammar from a list of strings.

        Args:
            grammar_lines (list): A list of string with grammar rules

        Returns:
            (list) The parsing instructions.
        """
        instructions = []
        for token in grammar_desc:
            if token.startswith("!"):
                instructions.append(Expression(token[1:]))
            elif not token.startswith("$"):
                instructions.append(Keyword(token))
            elif "[" in token and token.endswith("]"):
                bracket_idx = token.index("[")
                name = token[1:bracket_idx]
                data = cls._extract_instructions(token[bracket_idx+1:-1].split())
                instructions.append(VarList(name, data))
            else:
                instructions.append(Variable(token[1:]))
        return instructions


    @classmethod
    def _extract_choices(cls, choice_lines):
        """Exract the choices from a list of strings.

        Args:
            grammar_lines (list): A list of string with choice rules.

        Returns:
            (dict) A list of choices for any variable if any.
        """
        choices = {}
        for line in choice_lines:
            var, vals = line.split(":=")
            choices[var.strip()] = [val.strip(" }{") for val in vals.split(",")]
        return choices


    @classmethod
    def _prepare_grammar_desc(cls, grammar_lines):
        """Prepares the a set of string containing grammar rules for futher processing.

        Args:
            grammar_lines (list): A list of strings containing grammar rules.

        Returns:
            (list) A processed list of strings containing grammar rules.

        Raises:
            ValueError: If the number of opening and closing square brackets do not match.
        """
        grammar_desc = " ".join(grammar_lines).split(" ")
        open_idx = [idx for idx, token in enumerate(grammar_desc) if "[" in token]
        close_idx = [idx+1 for idx, token in enumerate(grammar_desc) if "]" in token]
        if len(open_idx) != len(close_idx):
            raise ValueError("Number of '[' does not match the number of ']'")

        for o_idx, c_idx in zip(reversed(open_idx), reversed(close_idx)):
            grammar_desc[o_idx:c_idx] = [" ".join(grammar_desc[o_idx:c_idx])]
        return grammar_desc




class GrammarFunction:
    """A GrammarFunction is wrapper around a function describing grammar rule.

    It uses a GrammarRule internally to convert the `args` list of the function
    into the format returned by the Grammar Rule.
    If the `grammar_desc` parameter is ommitted, the docstring of `fun` will
    be used instead.

    Note:
        This docstring differs for every instance of GrammarFunction,
        that is the __init__ methods modifies the docstring.

    Args:
        fun (function): The function to be wrapped
        grammar_desc (str): A string describing the grammar.
        expr_rule (ExpressionRule): The type of expression rule to be used
    """

    def __init__(self, fun, grammar_desc=None, expr_rule=ExpressionRule):
        """Please see help(GrammarFunction)."""
        grammar_desc = dedent(grammar_desc) if not grammar_desc is None else fun.__doc__
        self._grammar_parser = GrammarParser(grammar_desc, expr_rule)
        self._fun = convert_function(fun)
        # override the docstring of this instance operator
        self.__name__ = fun.__name__
        self.__doc__ = grammar_desc


    @property
    def grammar_parser(self):
        """The Parser used for this grammar."""
        return self._grammar_parser

    @property
    def grammar_rule(self):
        """The GrammarRule, responsible for argument conversion."""
        return self._grammar_parser.rule

    @property
    def grammar_rule_name(self):
        """The GrammarRule's name."""
        return self._grammar_parser.name

    @property
    def grammar_rule_type(self):
        """The GrammarRule's type."""
        return self._grammar_parser.grammar_rule_type

    @property
    def grammar_rule_desc(self):
        """A string containing a description of the associated grammar rule."""
        return self._grammar_parser.grammar_rule_desc

    @property
    def function(self):
        """The function this GrammarRule wrappes around."""
        return self._fun


    def __call__(self, code, args, env=None):
        """Apply the internal `function` to code and args.

        The `args` argument is parsed by the internal `GrammarParser`
        before passing it to the `function`.

        Args:
            code (str): The already generated code
            args (list): A list of string representing DSL arguments
            env (dict): A dictionary with environment variables.
        Returns:
            (str) The modified code.

        Raises:
            DSLFunctionError: If a DSLArgumentError occurs while applying the grammar rules.
        """
        try:
            return self._fun(code, self._grammar_parser(args), env)
        except DSLArgumentError as err:
            raise DSLFunctionError("Missing argument", err.rule, self.__doc__) from err




@decorator_factory
def grammar(fun, doc=None, expr=ExpressionRule):
    """Decorator for external grammar rules.

    If no grammar is specified in the functions docstring
    or via the `doc` argument this will raise an error.
    Otherwise the argument list of the function will be converted into a dictonary,
    which maps grammar variables names to values.

    Args:
        fun (function): The function to be wrapped
        doc (str): A string containing the grammar description
        expr (ExpressionRule): The type of expression rule to be used

    Returns:
        (function) GrammarFunction - functor, which behaves similar to `fun`
    """
    return GrammarFunction(fun, doc, expr)
