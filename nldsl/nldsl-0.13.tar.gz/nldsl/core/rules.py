# NLDSL (c) 2019 by Kevin Kiefer <abc.kiefer@gmail.com>, Heidelberg University
#
# NLDSL is licensed under a
# Creative Commons Attribution-NonCommercial 3.0 Unported License.
#
# You should have received a copy of the license along with this
# work.  If not, see <http://creativecommons.org/licenses/by-nc/3.0/>.

"""For each DSL argument type exist a dedicated rule responsible for parsing it.

The class GrammarRule contains a list of such rules, which it uses to parse
a list of different DSL arguments. Amongst all rules the ExpressionRule is the
most sophistaced one and it is also intended that the a user may derive from it
to adjust the parsing of expressions to his/her needs.
"""

from collections import OrderedDict
from os.path import join, abspath, dirname
from textx import metamodel_from_file
from .utils import cast_down
from .types import is_keyword, is_variable, is_expression, is_var_list, OperatorType
from .exceptions import DSLArgumentError




class KeywordRule:
    """A KeywordRule is responsible for parsing keywords.

     Args:
        keyword (str): A string describing a keyword
    """

    def __init__(self, keyword):
        """Please see help(KeywordRule)."""
        self.keyword = keyword


    @property
    def name(self):
        """The name of the keyword."""
        return self.keyword


    @property
    def description(self):
        """A string containing a description of the grammar rule."""
        return self.name


    def __call__(self, res_dict, args):
        """Apply the KeywordRule.

        If the first element from `args` is a euqal to the keyword stored
        in this rule, it will be removed. Otherwise an error is raised.

        Args:
            res_dict (dict): redundant - exists only for api consistency
            args (list): A list of strings

        Returns:
            (tuple) The first element is `res_dict` and the second args

        Raises:
            ValueError: This error is raised if the keyword is not the next argument.
            DSLArgumentError: If the keyword is incomplete e.g ("keyw" instead of "keyword").
        """
        if args[0] != self.keyword:
            if self.keyword.startswith(args[0]):
                raise DSLArgumentError("Incomplete Keyword", self)
            err_str = "Invalid keyword - expected {} but got {} instead"
            raise ValueError(err_str.format(self.keyword, args))
        return res_dict, args[1:]




class VariableRule:
    """A VariableRule is responsible for parsing variables.

    Args:
        variable_name (str): A string containing the name of a variable
        choice_rules (dict): A dict mapping variable names to a list of possible values
    """

    def __init__(self, variable_name, choice_rules=None):
        """Please see help(VariableRule)."""
        choice_rules = {} if choice_rules is None else choice_rules
        self.variable_name = variable_name
        self.choices = choice_rules[variable_name] if variable_name in choice_rules else []


    @property
    def name(self):
        """The name of the variable."""
        return self.variable_name


    @property
    def description(self):
        """A string containing a description of the grammar rule."""
        return "$" + self.name


    def __call__(self, res_dict, args):
        """Apply the VariableRule.

        Adds the first value of `args` to the dictionary where the internally stored
        `variable_name` is used as a key. Raises an error if a list of choices for the variable
        is given (via `choice_rules`) and the value is not contained in that list.

        Args:
            res_dict (dict): A dictionary mapping variable names to values
            args (list): A list of strings

        Returns:
            (tuple) The first element is `res_dict` and the second args

        Raises:
            ValueError: Raised if the value is not contained in the list of choices.
        """
        if self.choices and not args[0] in self.choices:
            remaining_choices = [c for c in self.choices if c.startswith(args[0])]
            if remaining_choices:
                rule = VariableRule(self.name, {self.name: remaining_choices})
                raise DSLArgumentError("Incomplete choice", rule)
            raise ValueError("Invalid value for variable")
        res_dict[self.variable_name] = args[0]
        return res_dict, args[1:]




class VarListRule:
    """A VariableRule is responsible for parsing variable lists.

    Args:
        var_list_name (str): A string containing the name of a variable
        internal (list): List key_word_rules or VariableRules
        next_keyword (str): The keyword that comes after this varlist or None
    """

    def __init__(self, var_list_name, internal_rules, next_keyword=None):
        """Please see help(VarListRule)."""
        if var_list_name:
            self.var_list_name = var_list_name
            self._artificial_name = False
        else:
            name_list = [x.variable_name for x in internal_rules if isinstance(x, VariableRule)]
            self.var_list_name = tuple(name_list) if len(name_list) > 1 else name_list[0]
            self._artificial_name = True

        self.next_keyword = next_keyword
        self.internal_rules = internal_rules


    @property
    def name(self):
        """The name of the variable list."""
        return self.var_list_name


    @property
    def description(self):
        """A string containing a description of the grammar rule."""
        internal_desc = [r.description for r in self.internal_rules]
        name = "" if self._artificial_name else self.name
        return "$" + name + "[{}]".format(" ".join(internal_desc))


    def __call__(self, res_dict, args):
        """Apply the VariableRule.

        Adds a list to the dictionary with tuples containing
        the values of the variables in the list.

        Args:
            res_dict (dict): A dictionary mapping variable names to values
            args (list): A list of strings

        Returns:
            (tuple) The first element is `res_dict` and the second the remaining args

        Raises:
            DSLArgumentError: If a DSL argument is missing.
        """
        try:
            stop_idx = len(args) if self.next_keyword is None or self.next_keyword not in args\
                                 else args.index(self.next_keyword)
        except ValueError as err:
            next_rule = KeywordRule(self.next_keyword)
            raise DSLArgumentError("DSL keyword delimiter is missing", next_rule) from err

        res_dict[self.var_list_name] = []

        for _ in range(0, stop_idx, len(self.internal_rules)):
            values = []
            for rule in self.internal_rules:
                if not args:
                    raise DSLArgumentError("DSL argument is missing", rule)

                tmp_res, args = rule({}, args)
                if rule.name in tmp_res:
                    values.append(tmp_res[rule.name])

            values = tuple(values) if len(values) > 1 else values[0]
            res_dict[self.var_list_name].append(values)

        return res_dict, args


    def _apply_internal_rule(self, rule_idx, arg):
        """Apply the `rule_idx`'th internal rule to arg

        Args:
            rule_idx (int): The index of the rule
            arg (str): The argument to the rule

        Returns:
            (str): Either arg itself or None (depending on the rule)
        """
        rule = self.internal_rules[rule_idx]
        if isinstance(rule, KeywordRule):
            return None
        res, _ = rule({}, [arg])
        return res[rule.variable_name]




class ExpressionRule:
    """An ExpressionRule is responsible for parsing expression.

    Args:
        expr_name (str): The name of the expression.
        next_keyword (str): The keyword after this expression or None
    """

    meta_model = metamodel_from_file(join(abspath(dirname(__file__)),
                                          "grammar", "expr_grammar.tx"))

    def __init__(self, expr_name, next_keyword=None):
        """Please see help(ExpressionRule)."""
        self.expr_name = expr_name
        self.next_keyword = next_keyword
        self.operator_map = {
            "or": " or ", "and": " and ", "not": "not ",
            "+": " + ", "-": " - ", "*": " * ", "/": " / ", "%": " % ", "**": "**",
            "<": " < ", ">": " > ", "==": " == ", "!=": " != ",
            "<=": " <= ", ">=": " >= ", "<>": " <> ",
            "in": " in ", "not in": " not in ", "is": " is ", "is not": " is not ",
            "[": "[", "]": "]", "(": "(", ")": ")"
        }
        self.operator_type = {op: OperatorType.OPERATOR for op in self.operator_map}
        self.brackets = "()"


    @property
    def name(self):
        """The name of the expression."""
        return self.expr_name


    @property
    def description(self):
        """A string containing a description of the grammar rule."""
        return "!" + self.name


    def __call__(self, res_dict, args):
        """Apply the ExpressionRule.

        Adds a string containing the parsed expression to 'res_dict'

        Args:
            res_dict (dict): A dictionary mapping variable names to values
            args (list): A list of strings

        Returns:
            (tuple) The first element is `res_dict` and the second the remaining args
        """
        try:
            stop_idx = len(args) if self.next_keyword is None else args.index(self.next_keyword)
        except ValueError as err:
            next_rule = KeywordRule(self.next_keyword)
            raise DSLArgumentError("DSL keyword delimiter is missing", next_rule) from err

        try:
            model = self.meta_model.model_from_str(" ".join(args[:stop_idx]))
        except:
            raise DSLArgumentError("Incomplete expression", self)
        res_dict[self.expr_name] = self._parse_or_expr(model)
        return res_dict, args[stop_idx:]


    def _parse_or_expr(self, node):
        """Pare a node corresponding to an boolean or-expression

        Args:
            node (OrExpr): The node describing the expression

        Returns:
            (str) A string containing the parsed expression
        """
        exprs = [("or", self._parse_and_expr(expr)) for expr in node.exprs]
        return self.apply_operator_seq(exprs[0][1], exprs[1:])


    def _parse_and_expr(self, node):
        """Pare a node corresponding to an boolean and-expression

        Args:
            node (OrExpr): The node describing the expression

        Returns:
            (str) A string containing the parsed expression
        """
        exprs = [("and", self._parse_not_expr(expr)) for expr in node.exprs]
        return self.apply_operator_seq(exprs[0][1], exprs[1:])


    def _parse_not_expr(self, node):
        """Pare a node corresponding to an boolean not-expression

        Args:
            node (OrExpr): The node describing the expression

        Returns:
            (str) A string containing the parsed expression
        """
        if node.comp:
            return self._parse_comparison_expr(node.comp)
        exprs = [("not", self._parse_not_expr(expr)) for expr in node.exprs]
        return self.apply_operator_seq("", exprs)


    def _parse_comparison_expr(self, node):
        """Pare a node corresponding to a comparsion expression

        Args:
            node (OrExpr): The node describing the expression

        Returns:
            (str) A string containing the parsed expression
        """
        rhs_list = [self._parse_comparison_expr_rhs(expr) for expr in node.rhs]
        return self.apply_operator_seq(self._parse_arith_expr(node.lhs), rhs_list)


    def _parse_comparison_expr_rhs(self, node):
        """Pare a node corresponding to the right hand side of comparisoin-expression

        Args:
            node (OrExpr): The node describing the expression

        Returns:
            (tuple) The operator and the expression.
        """
        if node.operator == "notin":
            node.operator = "not in"
        if node.operator == "isnot":
            node.operator = "is not"
        return (node.operator, self._parse_arith_expr(node.expr))


    def _parse_arith_expr(self, node):
        """Pare a node corresponding to an arithmetic-expression

        Args:
            node (OrExpr): The node describing the expression

        Returns:
            (str) A string containing the parsed expression
        """
        rhs_list = [self._parse_arith_expr_rhs(expr) for expr in node.rhs]
        return self.apply_operator_seq(self._parse_term_expr(node.lhs), rhs_list)


    def _parse_arith_expr_rhs(self, node):
        """Pare a node corresponding to the right hand side of a arithmetic-expression

        Args:
            node (OrExpr): The node describing the expression

        Returns:
            (tuple) The operator and the expression.
        """
        return (node.operator, self._parse_term_expr(node.expr))


    def _parse_term_expr(self, node):
        """Pare a node corresponding to a term-expression

        Args:
            node (OrExpr): The node describing the expression

        Returns:
            (str) A string containing the parsed expression
        """
        rhs_list = [self._parse_term_expr_rhs(expr) for expr in node.rhs]
        return self.apply_operator_seq(self._parse_factor_expr(node.lhs), rhs_list)


    def _parse_term_expr_rhs(self, node):
        """Pare a node corresponding to the right hand side of term-expression

        Args:
            node (OrExpr): The node describing the expression

        Returns:
            (tuple) The operator and the expression.
        """
        return (node.operator, self._parse_factor_expr(node.expr))


    def _parse_factor_expr(self, node):
        """Pare a node corresponding to an arithmetic factor-expression

        Args:
            node (OrExpr): The node describing the expression

        Returns:
            (str) A string containing the parsed expression
        """
        if node.expr:
            return self._parse_power_expr(node.expr)

        operator = self.operator_map[node.operator]
        operator = self.factor_sign(operator)

        if self.operator_type[node.operator] == OperatorType.UNARY_FUNCTION:
            return self.apply_operator(operator, rhs=self._parse_factor_expr(node.factor))

        return operator + self._parse_factor_expr(node.factor)


    def _parse_power_expr(self, node):
        """Pare a node corresponding to an arithmetic power-expression

        Args:
            node (OrExpr): The node describing the expression

        Returns:
            (str) A string containing the parsed expression
        """
        if node.factor:
            lhs, rhs = self._parse_atom_expr(node.atom), self._parse_factor_expr(node.factor)
            return self.apply_operator("**", lhs, rhs)
        return self._parse_atom_expr(node.atom)


    def _parse_atom_expr(self, node):
        """Pare a node corresponding to an atomic expression

        Args:
            node (OrExpr): The node describing the expression

        Returns:
            (str) A string containing the parsed expression
        """
        if node.expr:
            return self._parse_or_expr(node.expr)
        if node.dyck_expr:
            left, right = self.operator_map["("], self.operator_map[")"]
            return left + self._parse_or_expr(node.dyck_expr) + right
        if node.value_list:
            left, right = self.operator_map["["], self.operator_map["]"]
            vals = [self._parse_value(val) for val in node.value_list]
            return left + ", ".join(vals) + right
        return self._parse_value(node.value)


    @classmethod
    def _parse_value(cls, node):
        """Pare a node corresponding to a value.

        Args:
            node (TYPE): The node describing the value

        Returns:
            (str) A string containing the parsed value
        """
        if node.string:
            return "'" + node.string + "'"
        if node.float:
            return str(cast_down(node.float))
        return str(node.value)


    def apply_operator_seq(self, lhs, rhs_list):
        """Concatenates `lhs` and all expressions in `rhs_list`.

        Args:
            lhs (str): The left most expression
            rhs_list (list): A list of (operator, expression) tuples

        Returns:
            (str) A string containing the parsed expressions
        """
        result = lhs
        for operation, rhs in rhs_list:
            result = self.apply_operator(operation, result, rhs)
        return result


    def apply_operator(self, operator, lhs="", rhs=""):
        """Applies the `operator` to the left- and right-hand-side expression

        If the operator is a function the expressions will become its arguments.
        Otherwise they will simply be concatenated.

        Args:
            operator (str): A string containg an operator
            lhs (str): A string containg an expression
            rhs (str): A string containg an expression

        Returns:
            (str) The resulting expression
        """
        sym = self.operator_map[operator]
        if self.operator_type[operator] == OperatorType.UNARY_FUNCTION:
            return lhs + sym + self.brackets[0] + rhs + self.brackets[1]
        if self.operator_type[operator] == OperatorType.BINARY_FUNCTION:
            return sym + self.brackets[0] + lhs + ", " + rhs + self.brackets[1]
        return lhs + sym + rhs


    def factor_sign(self, operator):
        """Modify an operator, which describes the sign of a base.

        The default implementation simply strips all whitespaces.

        Args:
            operator (str): A string representation of the operator.

        Returns:
            (str) The operator string stripped from preceeding and trailing whitespaces.
        """
        return operator.strip()




class GrammarRule:
    """A GrammarRule consists out of a list of rules.

    Args:
        instructions (list): Descibes how to synthesize the rule.
        choices (dict): A dict, which maps variable names to values.
        expr_rule (ExpressionRule): The type of expression rule to be used.
    """

    def __init__(self, instructions, choices=None, expr_rule=ExpressionRule):
        """Please see help(GrammarRule)."""
        choices = {} if choices is None else choices
        self._expr_rule = expr_rule
        self._rules = self._parse_rules(instructions, choices)
        self._choices = self._parse_choices(self._rules, choices)


    @property
    def rules(self):
        """A list of the internal rules."""
        return self._rules

    @property
    def choices(self):
        """A dictionary wich maps variable names to lists of choices."""
        return self._choices

    @property
    def expression_rule(self):
        """The type of expression rule that is used."""
        return self._expr_rule

    @property
    def description(self):
        """A string containing a description of the grammar rule."""
        return " ".join(r.description for r in self.rules)


    def __call__(self, args):
        """Convert the list of arguments `args` into a dictinonary.

        All keywords are removed from `args`.
        All variable names become keys to their corresponding values.
        VarLists are converted into lists of tuples, where each tuples
        contains the values of the variables contained in the list in order.

        Args:
            args (list): A list of strings.

        Returns:
            (dict) A dictionary, which maps from variable names to values.

        Raises:
            ValueError: Raised if too many arguments are provided.
            DSLArgumentError: If a DSL argument is missing
        """
        res_dict = OrderedDict()
        for rule in self.rules:
            if not args:
                raise DSLArgumentError("DSL argument is missing", rule)
            res_dict, args = rule(res_dict, args)

        if args:
            raise ValueError("Too many arguments")
        return res_dict


    def _parse_rules(self, instructions, choices):
        """Parse the grammar rules as specified by the instructions.

        Args:
            instructions (list): Descibes how to synthesize the rule.
            choices (dict): A dict, which maps variable names to values.

        Returns:
            (list) A list of functors, which implement the rules.
        """
        rules = []
        for idx, arg in enumerate(instructions):
            next_arg = instructions[idx+1] if idx < len(instructions) - 1 else None
            # variable list parsing rule
            if is_var_list(arg):
                rules.append(self._create_var_list_rule(arg, next_arg, choices))
            # expression parsing rule
            elif is_expression(arg):
                rules.append(self._create_expression_rule(arg, next_arg))
            # variable parsing rule
            elif is_variable(arg):
                rules.append(VariableRule(arg.data, choices))
            # keyword parsing rule
            elif is_keyword(arg):
                rules.append(KeywordRule(arg.data))
            else:
                raise ValueError("Unkown rule type")

        return rules


    def _parse_choices(self, rules, choices):
        """Parse the lists of choices for all rules.

        Args:
            rule (list): A list of rules.
            choices (dict): The dictionary of already extracted choices.

        Returns:
            (dict): A mapping from variables names to lists of choices if any.
        """
        for rule in rules:
            if isinstance(rule, VariableRule) and rule.choices:
                choices[rule.name] = rule.choices
            if isinstance(rule, VarListRule):
                choices = self._parse_choices(rule.internal_rules, choices)
        return choices


    def _create_var_list_rule(self, arg, next_arg, choices):
        """ Create an instance of VarListRule.

        Args:
            arg (dict): The argument describing the variable list rule.
            next_arg (dict): The next argument in the instructions or None.
            choices (dict): A map from variable names to values.

        Returns:
            (VarListRule) A new variable list rule.

        Raises:
            ValueError: If the VarList is neither the last argument nor followed by a keyword.
        """
        # internals of a variable list are parsed recursively
        internal_rules = self._parse_rules(arg.data, choices)

        # ensure the next_arg does not exist or is a keyword
        if not next_arg is None and not is_keyword(next_arg):
            raise ValueError("A variable list must be followed by a keyword or be the last rule.")

        next_arg = next_arg.data if not next_arg is None else next_arg
        return VarListRule(arg.name, internal_rules, next_arg)


    def _create_expression_rule(self, arg, next_arg):
        """Create an instance of ExpressionRule.

        Args:
            arg (dict): The argument describing the expression rule.
            next_arg (dict): The next argument in the instructions or None.

        Returns:
            (ExpressionRule) A new variable list rule.

        Raises:
            ValueError: If the Expression is neither the last argument nor followed by a keyword.
        """
        # ensure the next_arg does not exist or is a keyword
        if not next_arg is None and not is_keyword(next_arg):
            raise ValueError("An expression must be followed by a keyword or be the last rule.")

        next_arg = next_arg.data if not next_arg is None else next_arg
        return self.expression_rule(arg.data, next_arg)
