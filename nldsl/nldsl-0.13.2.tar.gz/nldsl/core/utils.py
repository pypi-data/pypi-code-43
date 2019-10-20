# NLDSL (c) 2019 by Kevin Kiefer <abc.kiefer@gmail.com>, Heidelberg University
#
# NLDSL is licensed under a
# Creative Commons Attribution-NonCommercial 3.0 Unported License.
#
# You should have received a copy of the license along with this
# work.  If not, see <http://creativecommons.org/licenses/by-nc/3.0/>.

"""The `utils` module provides utility functions for the `core` package."""

from inspect import signature
from functools import wraps




def decorator_factory(decorator):
    """A decorator which improves the parsing of optional arguments of other decorators.

    Let a decorator of the following form be given::

        decorator(arg1=value1, ... , kwargsN=valueN)'

    One would need to write the following in case all arguments should be left as default::

        @decorator()
        def myFunction ...

    If we declare our decorator as follow::

        @decorator_factory
        def decorator(fun, arg1=value1, ... , kwargsN=valueN)

    We could write instead::

        @decorator
        def myFunction ...

    Furthermore, we do not have to write the boilderplate code necessary to implement
    a decorator with arguments in the first place.
    """
    @wraps(decorator)
    def decorator_wrapper(*args, **kwargs):
        if len(args) == 1 and callable(args[0]):
            return decorator(args[0])
        return lambda fun: decorator(fun, *args, **kwargs)
    return decorator_wrapper




def cast_down(value):
    """Convert an object to an integer if no rounding is required.

    If the object is a float, which can be converted to an integer
    without rounding int(`value`) is returned. Otherwise `value` is returned.

    Args:
        value (object): An object to possibly converted

    Returns:
       (object or int) Either `value` or its integer representation.
    """
    return int(value) if isinstance(value, float) and int(value) == value else value




def convert_function(fun):
    """Convert the function signature if necessary

    The target signature is:
    my_function(str: code, list: args, dict: env) -> str

    The changes are strictly additive, in that no argument will be removed.

    Args:
        fun (function): The function to be converterd.

    Returns:
        (function) A function with proper signature.

    Raises:
        ValueError: If `fun` has four or more parameters.
    """
    sig = signature(fun)
    num_params = len(sig.parameters)

    if num_params == 3:
        if not hasattr(fun, "grammar_rule_desc"):
            fun.grammar_rule_desc = None
        if not hasattr(fun, "grammar_rule_type"):
            fun.grammar_rule_type = None
        return fun

    if num_params == 2 and "args" in sig.parameters:
        def __anonymous_function_wrapper(code, args, env):
            return fun(code, args)
    elif num_params == 2 and "env" in sig.parameters:
        def __anonymous_function_wrapper(code, args, env):
            return fun(code, env)
    elif num_params == 1:
        def __anonymous_function_wrapper(code, args, env):
            return fun(code)
    else:
        raise ValueError("Invalid function signatur - got {}, expected {}"
                         .format(str(sig), "(code, args, env)"))

    desc = fun.grammar_rule_desc if hasattr(fun, "grammar_rule_desc") else None
    gtype = fun.grammar_rule_type if hasattr(fun, "grammar_rule_type") else None
    __anonymous_function_wrapper.grammar_rule_desc = desc
    __anonymous_function_wrapper.grammar_rule_type = gtype
    __anonymous_function_wrapper.__name__ = fun.__name__
    __anonymous_function_wrapper.__doc__ = fun.__doc__
    return __anonymous_function_wrapper




def split_code(code, split_on=" = "):
    """Split the code in half on the string specified by `split_on`.

    Args:
        code (str): A string containg code
        split_on (str): The string on which to split the code

    Returns:
        (tuple) Code before and after the string `split_on`
    """
    splitted_code = code.split(split_on)

    if len(splitted_code) > 2:
        raise ValueError("Code has been splitted into more than two fragements")

    return splitted_code if len(splitted_code) == 2 else ("", splitted_code[0])




def list_to_string(string_list):
    """Converts a list of strings into a single string.

    Unlike {}.format(some_list) this treats elements of the form "'...'" properly.

    Args:
        string_list (list): A list of strings

    Returns:
        (str) A string containing the list.
    """
    return "[" + ", ".join(string_list) + "]"
