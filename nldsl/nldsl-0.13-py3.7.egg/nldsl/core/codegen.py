# NLDSL (c) 2019 by Kevin Kiefer <abc.kiefer@gmail.com>, Heidelberg University
#
# NLDSL is licensed under a
# Creative Commons Attribution-NonCommercial 3.0 Unported License.
#
# You should have received a copy of the license along with this
# work.  If not, see <http://creativecommons.org/licenses/by-nc/3.0/>.

"""This module contains the CodeMap, CodeGenerator and Recommendation classes.

The CodeMap is essentially a dispatcher dict, which contains all dynamically added
grammar rules. It stores them in his __dict__ attribute. It implements the interface
of a python dictonary.

The CodeGenerator generates executable code from DSL statements.
In generall one want to derive from this class to crate a CodeGenerator with a specific
target, such a Pandas, Spark, R, etc.

A Recommendation is returned by the CodeGenerator instead of executable code in case no code
could be generated due to an incomplete or incorrect DSL argument list.

Example:
    First import::

        from nldsl import CodeGenerator, grammar

    Create custom code generator::

        class MyCodeGenerator(CodeGenerator):
            def __init__(my_env_var_1, ..., my_env_var_n=default_val):
                # all arguments passed to super.__int__() will be added to the environment,
                # which in turn will be passed to any dynamic grammar rule if requested.
                super().__init__(my_env_var_1=my_env_var_1, ..., my_env_var_n=my_env_var_n)

    Create a grammar rule, specifing the `env` parameter request the environment dict::

        @grammar
        def my_grammar_rule(code, args, env):
            \"\"\"My grammar rule doc...
            Grammar:
                parse my expression !expr
            \"\"\"
            return code + args["expr"] + env["my_var_1"]

    Add to the code generators class itself::

        MyCodeGenerator.register_function(my_grammar_rule)

    Or only add it to specific instance instead::

        code_gen = MyCodeGenerator(my_env_var_1)
        code_gen[\"parse my expression\"] = my_grammar_rule

    One may also tell the code generator to infer the name::

        code_gen[\"__infer__\"] = my_grammar_rule
"""

import itertools as it
from collections.abc import MutableMapping
from os.path import join, abspath, dirname
from textx import metamodel_from_file
from .utils import cast_down, convert_function
from .internal import PipeFunction
from .rules import KeywordRule, VariableRule
from .types import Value, Keyword, Variable, Expression, VarList, is_value, is_keyword
from .exceptions import DSLFunctionError




class Recommendation:
    """Provides recommendation on how to continue with a DSL statement.

    A Recommendation is returned by the CodeGenerator instead of executable code in case no code
    could be generated due to an incomplete or incorrect DSL argument list.

    Args:
        rule (grammar rule): A Keyword-/Variable-/Expression-/VarListRule.
    """

    def __init__(self, rule, doc=""):
        """Please see help(Recommendation)."""
        self.rule = rule
        self.doc = doc


    @property
    def documentation(self):
        """The docstring of the grammar rule which raised this error."""
        return self.doc


    @property
    def description(self):
        """A string describing the arguments of the grammar rule which raised this error."""
        return self.rule.description


    def recommend(self):
        """Provide a list of recommendations on how to continue with a DSL statement.

        Returns:
            (list) Contains either a keyword, all choices for a variable or nothing.
        """
        if isinstance(self.rule, KeywordRule):
            return [self.rule.keyword]
        if isinstance(self.rule, VariableRule):
            return self.rule.choices
        return []




class CodeMap(MutableMapping):
    """A CodeMap maps the names of DSL functions to python functions.

    The names of DSL function are expected to be a sequence of lower case letters seperated
    by whitespaces. A CodeMap implements the dictonary interface.

    A new function may either be added to a specific instance of CodeMap::

        my_CodeMap["my dsl function name"] = my_function

    Or to the class itself::

        CodeMap.register_function(my_function, "my dsl function name")
    """

    CODEMAP_VERIFY_TAG = True # The CodeMap and all its child classes must have this tag!

    static_longest_name = 0
    infer_name_constant = "__infer__"
    dynamic_prefix = "_CODE_MAP_DYNAMIC_FUNCTION"
    dynamic_length = 4


    def __init__(self):
        """Please see help(CodeMap)."""
        self.own_longest_name = self.compute_own_longest_name()


    @property
    def longest_name(self):
        """The length of the longest sequence of tokens, which correspond to a function name."""
        return max(self.static_longest_name, self.own_longest_name)


    def __getitem__(self, name):
        """Access the function that is associated with `name` and attached to this instance.

        Args:
            name (str): A name corresponding to the desired function.

        Returns:
            (function) A python function, which takes a list as argument and returns a string.

        Raises:
            KeyError: If no function corresponding to `name` exists.
        """
        fun_name, _ = self.convert_name(name)
        if not hasattr(self, fun_name):
            raise KeyError("A function corresponding to the name `" + name + "` does not exists")
        return getattr(self, fun_name)


    def __setitem__(self, name, fun):
        """Define a function that will be associated with `name` only for this instance.

        Args:
            name (str): The name to be assoicated with the function.
            fun (function): The function this name should map to.

        Returns:
            (class CodeMap) this instance of the class
        """
        if name == self.infer_name_constant:
            name = fun.grammar_rule_name

        fun_name, length = self.convert_name(name)

        if length > self.own_longest_name:
            self.own_longest_name = length
        # calling setattr(<x>, name, <function>) will automatically
        # add the argument `self` to the prototype of <function> if <x> is an instance
        setattr(self, fun_name, convert_function(fun))
        return self


    def __delitem__(self, name):
        """Delete the function that is associated with `name` and attached to this instance.

        Args:
            name (str): A name corresponding to the desired function.

        Returns:
            (class CodeMap) this instance of the class.

        Raises:
            KeyError: If no function corresponding to `name` exists.
        """
        fun_name, length = self.convert_name(name)
        if not hasattr(self, fun_name):
            raise KeyError("A function corresponding to the name `" + name + "` does not exists")
        delattr(self, fun_name)
        if self.own_longest_name == length:
            self.own_longest_name = self.compute_own_longest_name()
        return self


    def __iter__(self):
        """Create an iterator over all dynmically added methods.

        Returns:
            (iterator) Said iterator.
        """
        # NOTE: When calling getattr(b, "__iter__")(b) b is a class not an instance!
        # This yields the correct results however because type(b) == abc.ABCMeta, hence ops == []
        # and b.__dict__ equals type(self).__dict if self would be an instance.
        # Meaning self_ops contains the result that would normal belong into ops and ops is empty
        bases = set(it.chain(*[getattr(b, "__iter__")(b) for b in self.determine_inheritance()]))
        offset = len(self.dynamic_prefix) + 1
        ops = [" ".join(k[offset:].split("_")) for k in type(self).__dict__ if self.is_dynamic(k)]
        self_ops = [" ".join(k[offset:].split("_")) for k in self.__dict__ if self.is_dynamic(k)]
        return it.chain(iter(self_ops + ops), bases)


    def __len__(self):
        """The number of all dynamically added methods.

        Returns:
            (int) The number of of dynamically added methods.
        """
        # See __iter__ impl for an explanation why this works.
        bases = set(it.chain(*[getattr(b, "__iter__")(b) for b in self.determine_inheritance()]))
        cls_len = len([k for k in type(self).__dict__ if self.is_dynamic(k)])
        self_len = len([k for k in self.__dict__ if self.is_dynamic(k)])
        return self_len + cls_len + len(bases)


    def update(self, other):
        """Updated the CodeMap with `other`.

        Args:
            other (CodeMap): Another instance of CodeMap.

        Returns:
            (CodeMap) This instance.
        """
        for name, fun in other.items():
            fun_name, _ = self.convert_name(name)
            # Do not overwrite dynamic class methods
            if not hasattr(type(self), fun_name):
                self[name] = fun
        return self


    def __eq__(self, other):
        """Compares two CodeMaps for equality.

        Args:
            other (CodeMap): Another instance of CodeMap

        Returns:
            (bool) True if the are equal, false otherwise.
        """
        if type(self) != type(other):
            return False
        if self.__dict__ != other.__dict__:
            return False
        return True


    @classmethod
    def request_function(cls, name):
        """Access the function that is associated with `name` for all instances of this class.

        Args:
            name (str): A name corresponding to the desired function.

        Returns:
            (function) A python function, or None.
        """
        fun_name, _ = cls.convert_name(name)
        if not hasattr(cls, fun_name):
            return None

        fun = getattr(cls, fun_name)

        def __anonymous_function_wrapper(code, args, env):
            return fun(cls, code, args, env)

        desc = fun.grammar_rule_desc if hasattr(fun, "grammar_rule_desc") else None
        gtype = fun.grammar_rule_type if hasattr(fun, "grammar_rule_type") else None
        __anonymous_function_wrapper.grammar_rule_desc = desc
        __anonymous_function_wrapper.grammar_rule_type = gtype
        __anonymous_function_wrapper.__name__ = fun.__name__
        __anonymous_function_wrapper.__doc__ = fun.__doc__

        return __anonymous_function_wrapper


    @classmethod
    def register_function(cls, fun, name=None):
        """Define a function that will be associated with `name` for all instances of this class.

        Args:
            fun (function): The function this name should map to.
            name (str): The name to be assoicated with the function.
        """
        if name is None:
            name = fun.grammar_rule_name

        fun_name, length = cls.convert_name(name)
        if length > cls.static_longest_name:
            cls.static_longest_name = length

        # calling setattr(<x>, name, <somefunction>) will NOT(!)
        # add the argument `self` to the prototype of <function> if <x> is a class
        tmp = convert_function(fun)

        def __anonymous_function_wrapper(self, code, args, env):
            return tmp(code, args, env)

        desc = fun.grammar_rule_desc if hasattr(fun, "grammar_rule_desc") else None
        gtype = fun.grammar_rule_type if hasattr(fun, "grammar_rule_type") else None
        __anonymous_function_wrapper.grammar_rule_desc = desc
        __anonymous_function_wrapper.grammar_rule_type = gtype
        __anonymous_function_wrapper.__name__ = fun.__name__
        __anonymous_function_wrapper.__doc__ = fun.__doc__

        setattr(cls, fun_name, __anonymous_function_wrapper)
        return cls


    @classmethod
    def remove_function(cls, name):
        """Delete the function that is associated with `name` from all instances of this class

        Args:
            name (str): A name corresponding to the desired function.

        Raises:
            KeyError: If no function corresponding to `name` exists.
        """
        fun_name, length = cls.convert_name(name)
        if not hasattr(cls, fun_name):
            raise KeyError("A function corresponding to the name `" + name + "` does not exists")
        delattr(cls, fun_name)
        if cls.static_longest_name == length:
            cls.static_longest_name = cls.compute_static_longest_name()
        return cls


    @classmethod
    def convert_name(cls, name):
        """Convert the `name` to a proper function name.

        Args:
            name (str): The name to be converted

        Returns:
            (tuple) The converted name and the number of tokens
        """
        if name == "":
            return cls.dynamic_prefix + "_", 0

        tokens = name.split()
        prefix = "" if tokens[0].startswith("_") else "_"
        return cls.dynamic_prefix + prefix + "_".join(tokens), len(tokens)


    @classmethod
    def is_dynamic(cls, name):
        """Check if method has been added dynamically.

        Args:
            name (str): The name of the method.

        Returns:
            (bool) True if the method has been added dynamically, false otherwise.
        """
        return name.startswith(cls.dynamic_prefix)


    def compute_longest_name(self):
        """Compute the length of the longest sequence of tokens.

        Returns:
            (int): The computed length
        """
        return self.compute_own_longest_name() + self.compute_static_longest_name()


    def compute_own_longest_name(self):
        """Compute the length of the longest sequence of tokens from this instance.

        Returns:
            (int): The computed length
        """
        # remove all methods, which are not dynamic grammar rules
        ops = [k[1:] for k in self.__dict__ if self.is_dynamic(k)]
        length = [len(s.split("_")) - self.dynamic_length for s in ops]
        return max(length) if length else 0


    @classmethod
    def compute_static_longest_name(cls):
        """Compute the length of the longest sequence of tokens from this class.

        Returns:
            (int): The computed length
        """
        bases_sln = [getattr(b, "compute_static_longest_name")()
                     for b in cls.determine_inheritance()]

        # remove all methods, which are not dynamic grammar rules
        ops = [k[1:] for k in cls.__dict__ if cls.is_dynamic(k)]
        length = [len(s.split("_")) - cls.dynamic_length for s in ops if s != ""] + bases_sln
        return max(length) if length else 0


    @classmethod
    def determine_inheritance(cls):
        """Traverse the inheritance hierachy upwards and extract a set of all CodeMap-parents.

        Note:
            If one wants to access the member functions of the returned classes,
            it is necessary to use getitem(cls, "name of member function").

        Returns:
            (set): A set of classes derived from CodeMap and the CodeMap class itself.
        """
        bases = list(base for base in cls.__bases__ if hasattr(base, "CODEMAP_VERIFY_TAG"))
        bases += list(it.chain(*[base.determine_inheritance() for base in bases]))
        return set(bases)




class CodeGenerator(CodeMap):
    """A CodeGenerator translates DSL statements into executable code or changes the Grammer.

    There are two kind of DSL statements, the ones which can be evaluate to executable code
    and the ones, which extend the DSL Grammer.
    As a result parsing a set of DSL statements usually has two impacts.
    Executable code is generate and the CodeGenerator modifies itself in such a way
    that he is capable of parsing statements according to the new Grammer rules.

    Furthermore the CodeGenerator derives from the CodeMap class and his grammer can also
    be extended by rules, which can not be expressed within the DSL.
    This is done with the __setitem__ and register_function methods.

    Args:
        recommend (bool): Whether to return a Recommendation if possible or always raise an error.
        kwargs (dict): Specify the environment, which will be passed to all grammar rules.
    """
    meta_model = metamodel_from_file(join(abspath(dirname(__file__)), "grammar", "grammar.tx"))


    def __init__(self, recommend=True, **kwargs):
        """Please see help(CodeGenerator)."""
        super().__init__()
        self.recommend = recommend
        self.env = kwargs if kwargs is not None else {}


    def __call__(self, model, is_file=False):
        """Convert the given model into code.

        Args:
            model (str): A filename or string containg DSL statements
            is_file (bool): True if model is filename, False otherwise.

        Returns:
            (list) A list of strings containing executable code or recommendations.
        """
        if is_file:
            model = self.meta_model.model_from_file(model)
        else:
            model = self.meta_model.model_from_str(model)
        return self.postprocessing(self._parse_input(model))


    @classmethod
    def register_dsl(cls, model, is_file=False):
        """Add all define statements in model to this class.

        Args:
            model (str): A filename or string containg DSL statements
            is_file (bool): True if model is filename, False otherwise.

        Returns:
            (CodeGenerator) This class.
        """
        if is_file:
            model = cls.meta_model.model_from_file(model)
        else:
            model = cls.meta_model.model_from_str(model)

        for stmt in model.stmts:
            if stmt.define:
                cls._static_parse_define_pipe_stmt(stmt.define)
        return cls


    @classmethod
    def _static_parse_define_pipe_stmt(cls, node):
        """Parse a node corresponding to a definition statement.

        Instead of creating code, this statement will dynamically add a new grammer rule.
        This is done by construing a PipeFunction and adding it as an attribute to this class.

        Args:
            node (class DefinePipeStmt): The node describing the statement.

        Returns:
            (CodeGenerator) This instance.
        """
        name, instructions = cls._process_assignment(node.assign)

        # compute mapping from new pipeline to DSL statements
        fun_list = [cls._static_parse_def_op_expr(op) for op in node.operations]
        pipe_fun = PipeFunction(name, instructions, fun_list)
        cls.register_function(fun=pipe_fun, name=name)
        return cls


    @classmethod
    def _static_parse_def_op_expr(cls, node):
        """Parse a node corresponding to a definition operation expression.

        Args:
            node (class DefOpExpr): The node describing the expression

        Returns:
            (tuple) A tuple of a function and a list of its arguments

        Raises:
            ValueError: If the name of the function could not be resolved.
        """
        args = [cls._parse_def_arg_expr(arg) for arg in node.args]

        for num_tokens in range(cls.static_longest_name, -1, -1):
            tokens = [arg.data for arg in args[:num_tokens] if is_keyword(arg) or is_value(arg)]
            fun_name, name_length = " ".join(tokens), len(tokens)
            fun = cls.request_function(fun_name)
            if fun is not None:
                return (fun, args[name_length:])

        raise ValueError("Unable to resolve name of operation")


    def _parse_input(self, node):
        """Parse the AST rooted at `node`.

        Args:
            node (class Input): The root of the AST

        Returns:
            (list) A list of strings containing executable code or recommendations
        """
        for stmt in node.stmts:
            if stmt.define:
                self._parse_define_pipe_stmt(stmt.define)

        return [self._parse_eval_pipe_stmt(stmt.eval) for stmt in node.stmts if stmt.eval]


    def _parse_eval_pipe_stmt(self, node):
        """Parse a node corresponding to an evaluation statement.

        Args:
            node (class EvalPipeStmt): The node describing the statement.

        Returns:
            (str) A string containing executable code or a recommendation.
        """
        assign, code = node.result + " = " if node.result else "", ""
        for operation in node.operations:
            try:
                code = self._parse_op_expr(operation, code)
            except DSLFunctionError as err:
                if self.recommend:
                    return Recommendation(err.rule, err.doc)
                raise err from None
        return assign + code


    def _parse_define_pipe_stmt(self, node):
        """Parse a node corresponding to a definition statement.

        Instead of creating code, this statement will dynamically add a new grammer rule.
        This is done by construing a pipe_operator and adding as attribute to this instance
        of the class.

        Args:
            node (class DefinePipeStmt): The node describing the statement.

        Returns:
            (CodeGenerator) This instance.
        """
        name, instructions = self._process_assignment(node.assign)

        # compute mapping from new pipeline to DSL statements
        fun_list = [self._parse_def_op_expr(op) for op in node.operations]
        pipe_fun = PipeFunction(name, instructions, fun_list)
        self[name] = pipe_fun
        return self


    def _parse_op_expr(self, node, code):
        """Parse a node corresponding to an operation expression.

        Args:
            node (class OpExpr): The node describing the expression

        Returns:
            (str) A string containing a fragment of code.
        """
        args = [self._parse_arg_expr(arg) for arg in node.args]

        for num_tokens in range(self.longest_name, -1, -1):
            fun_name = " ".join([arg for arg in args[:num_tokens]])
            if fun_name in self:
                return self[fun_name](code, args[num_tokens:], self.env)

        raise ValueError("Unable to resolve name of operation")


    @classmethod
    def _parse_arg_expr(cls, node):
        """Parse a node corresponding to an argument expression.

        Args:
            node (class ArgExpr): The node describing the expression

        Returns:
            (str) A string containing a fragment of code.
        """
        return cls._parse_expr(node.expr)


    def _parse_def_op_expr(self, node):
        """Parse a node corresponding to a definition operation expression.

        Args:
            node (class DefOpExpr): The node describing the expression

        Returns:
            (tuple) A tuple of a function and a list of its arguments
        """
        args = [self._parse_def_arg_expr(arg) for arg in node.args]

        for num_tokens in range(self.longest_name, 0, -1):
            tokens = [arg.data for arg in args[:num_tokens] if is_keyword(arg) or is_value(arg)]
            fun_name, name_length = " ".join(tokens), len(tokens)
            if fun_name in self:
                return (self[fun_name], args[name_length:])

        raise ValueError("Unable to resolve name of operation")


    @classmethod
    def _parse_def_assign_expr(cls, node):
        """Parse a node corresponding to a definition assignment expression.

        Args:
            node (class DefAssignExpr): The node describing the expression

        Returns:
            (dict) A dict with a `data` and `type` field
        """
        if node.variable:
            return Variable(node.variable)
        if node.value:
            return Keyword(node.value)
        if node.def_expr:
            return Expression(node.def_expr)
        if node.var_list:
            var_list = [cls._parse_def_arg_list_expr(expr) for expr in node.var_list]
            return VarList(None, var_list)

        raise ValueError("Invalid assignment expression")


    @classmethod
    def _parse_def_arg_expr(cls, node):
        """Parse a node corresponding to a definition argument expression.

        Args:
            node (class DefArgExpr): The node describing the expression

        Returns:
            (dict) A dict with a `data` and `type` field
        """
        if node.variable:
            return Variable(node.variable)
        if node.expr:
            return Value(cls._parse_expr(node.expr))
        if node.def_expr:
            return Expression(node.def_expr)
        if node.var_list:
            var_list = [cls._parse_def_arg_list_expr(expr) for expr in node.var_list]
            return VarList(None, var_list)

        raise ValueError("Invalid argument expression")


    @classmethod
    def _parse_def_arg_list_expr(cls, node):
        """Parse a node corresponding to a definition argument list expression.

        Args:
            node (class DefArgExpr): The node describing the expression

        Returns:
            (dict) A dict with a `data` and `type` field
        """
        if node.variable:
            return Variable(node.variable)
        if node.value:
            return Keyword(node.value)
        if node.def_expr:
            raise ValueError("Argument list must not contain expression arguments.")
        raise ValueError("Invalid argument expression")


    @classmethod
    def _parse_expr(cls, node):
        """Parse a node corresponding to an expression.

        Args:
            node (class Expr): The node describing the expression

        Returns:
            (str) A string containing a fragment of code.
        """
        return cls._parse_value(node.value)


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


    @classmethod
    def _process_assignment(cls, assignment):
        """Extract the name and instructions from an assignment definition

        Args:
            assignment (list): A list of DefAssignExpr objects

        Returns:
            (tuple) The name and instruction list.
        """
        # prepare assignment expressions
        assign = [cls._parse_def_assign_expr(ass) for ass in assignment]
        split_idx = [is_keyword(ass) for ass in assign].index(False)

        # process assignment expressions
        name = " ".join([ass.data for ass in assign[:split_idx]])
        instructions = assign[split_idx:]

        return name, instructions


    def postprocessing(self, code_list):
        """A hook for subclasses to modifiy the generate code list before it is returned.

        Args:
            code_list (list): A list of string containing executable code.

        Returns:
            (list) The modified code list
        """
        return code_list


    def extract_environment(self, source_lines):
        """A hook for sublcasses, which is used by the compiler and completion generator.

        Extract environment variables from the `source_lines` and update self.env accordingly.

        Args:
            source_lines (list): A list of strings containing source code.
        """
