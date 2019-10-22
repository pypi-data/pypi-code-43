""" syncurity_utils.typecheck

IR-Flow Integrations utility that checks if the correct value types are being passed into a given function

Examples:
    In some function ``func(a, b, c)``, ensure that ``a`` is of type ``str``, ``b`` is of type ``int``, and ``c``
    is of type ``dict``::

        @typecheck(str, int, dict, isclassmethod=False)
        def func(a, b, c):
            print('{0}\\n{1}\\n{2}'.format(a, b, c))

    Notice the use of the ``isclassmethod`` optional parameter. In the case that ``func()`` was a member of a class
    such that its first parameter was ``self``, this parameter could be left to safely default to ``True``. This
    will simply ignore the first parameter found in the signature of the function.

    If multiple possible types are permitted for a parameter (generally in the case that an optional parameter will
    default to ``None`` should no value be provided), a tuple of types can be passed in as such::

        @typecheck(str, int, (dict, None), isclassmethod=False)
        def func(a, b, c=None):
            print('{0}\\n{1}\\n{2}'.format(a, b, c if c is not None else 'None'))

    If there is a parameter that could accept any possible type, perhaps in the use case of a formatting function,
    such that passing an n-tuple to the decorator is impractical the ``object`` type works as a catch all::

        @typecheck(str, object, (dict, None), isclassmethod=False)
        def func(a, b, c=None):
            if isinstance(b, int):
                print('{0}: {1}'.format(a, b))
            elif isinstance(b, str):
                try:
                    int_b = int(b)
                except ValueError:
                    int_b = NaN
                print('{0}: {1}'.format(a, int_b))
            elif isinstance(b, float):
                print('{0}: {1}'.format(a, math.floor(b))
            else:
                print('{0}: Strange Value'.format(a))

            print(c if c is not None else 'None')

    This example, while not necessarily ever useful, is a fairly reasonable case where a value of any type should be
    accepted for parameter b, with different cases for handling the value within the function. What may seem to be
    an equivalent implementation if the tuple ``(int, str, float)`` were used does not account for the final
    ``else:`` block, where values of any type not included in that tuple will be handled uniquely.

    The ``object`` catch all should never be used in a tuple of values - since any subclass of object will return
    true during the ``isinstance(var, object)`` comparison - the usage is redundant. If any value should be
    acceptable for a parameter the ``object`` catch should be used as a single parameter, not as a tuple.

    The Typecheck decorator also works when used on functions that have optional parameters set in the function
    signature, regardless of how many are used when the function is called, or in what order optional parameters are
    provided during the function call::

        @typecheck(int, int, (str, None), (str, None), bool)
        def func(a, b, c=None, d=None, e=False):
            print('{} + {} = {}'.format(a, b, a+b)
            print('{} {}!'.format('Hello' if c is None else c, 'World' if d is None else d)
            print('I'm feeling {} today'.format(e))

        # Valid
        func(10, 12, e=True)

        # Will cause TypeError
        func(10, 12, e='47')

        # Valid
        func(10, 12, e=True, d='Everyone')

        # Will cause TypeError for parameter c
        func(10, 12, d='Mom', c=17, e=True)

:copyright: (c) 2019 Syncurity
:license: Apache 2.0, see LICENSE.txt for more details
"""
import functools
import inspect

from .exceptions import TypecheckError

__all__ = ['typecheck']


def typecheck(*args1, isclassmethod=True):
    """Typechecking decorator

    Args:
        args1 (list): List of args passed to this function, args should be of type class, however this is not checked.
            Passing a value that is not a type or tuple of types will result in a TypeError regardless, thrown by the
            isinstance() function.
        isclassmethod (bool): True by default, should be set False when this decorator is used on a static function, or
            a function that is not a member of a class. Used for skipping the ``self`` parameter of all class functions

    Raises:
        TypeError: If a zip of 3-tuples of the form (value, type, name), where ``value`` is the value of a parameter in
            the function being wrapped by the decorator; ``type`` is the expected type of value; and ``name`` is the
            name of the parameter as it appears in the Signature object associated with the function does not contain a
            ``value`` of type ``type``, a TypeError will be thrown
        TypecheckError: If the type ``object`` is passed as a value in a tuple of types, a TypecheckError wil be thrown
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args2, **keywords):

            # Get key, value pairs of provided arguments (i.e. optional arguments for which non-default values were
            # not provided will not be provided in this object)
            all_args = inspect.signature(func).bind(*args2, **keywords).arguments
            if isclassmethod:
                if 'self' in all_args:
                    del all_args['self']

            # Split up the arguments and their names for use later
            args = tuple(all_args.values())
            names = tuple(all_args.keys())

            # Get the names of all parameters in the signature of the function so we can determine the difference
            # between the parameters provided and the parameters declared
            all_params = [k for k, v in inspect.signature(func).parameters.items()]
            all_params = all_params[1:] if isclassmethod else all_params

            # Get a mutable list of type arguments
            list_args1 = list(args1)
            # If there are more type arguments than arguments provided, we need to trim away the arguments that
            # we're not dealing with
            if len(list_args1) > len(all_args):
                # Get the set difference between the provided and declared parameters
                provided_diff_all = list(set(all_params) - set(names))
                # Get the indices at which the differing parameters are in the declared parameters
                indices = [all_params.index(i) for i in provided_diff_all]
                # Sort ascending
                indices.sort()
                # subtract the value of the index at which each item in the list of indices appears - we know
                # there will not be duplicates in this list because parameters have unique names, and therefore a
                # search through a list of parameters for two unique parameter names could not return the same
                # index.
                #
                # We do this because as each type is removed from the list of types provided to the decorator,
                # the total length of that list decreases, we start by removing the type at the lowest index,
                # then the next lowest, etc. Each time we remove one, the next one we need to remove will slide
                # down one index as the list gets smaller.
                #
                # For example - if we have a list of types [int, int, str, str, dict] that correspond to the
                # signature func(a, b, c='c', d='d', e={'value': 'e'}), and the function is called as func(10,
                # 11, e={'value': 'newval'}), the indices at which we are missing parameters are 2 and 3. If we
                # were to remove the type at index 2 (str) the list of types would be [int, int, str, dict] - if
                # we then tried to remove the type at index 3 (now dict), we'd be removing the wrong type,
                # thus we subtract the value of the index at which the item in the indices list appears,
                # we will remove the value knowing that the size of the list of types has decreased by one for
                # each item removed
                indices = [x - indices.index(x) for x in indices]
                for i in indices:
                    del list_args1[i]

            for (arg2, arg1, name) in zip(args, list_args1, names):
                if isinstance(arg1, tuple):
                    if object in arg1:
                        raise TypecheckError('Type \'object\' found in tuple of {0}'.format(arg1))
                    if arg2 is None:
                        if None not in arg1:
                            raise TypeError('Type of {0} is {1}, and not any of {2}'.format(name, type(arg2), arg1))
                    elif not isinstance(arg2, arg1):
                        raise TypeError('Type of {0} is {1}, and not any of {2}'.format(name, type(arg2), arg1))
                elif not isinstance(arg2, arg1):
                    raise TypeError('Type of {0} is {1} and not {2}'.format(name, type(arg2), arg1))
            return func(*args2, **keywords)
        return wrapper
    return decorator
