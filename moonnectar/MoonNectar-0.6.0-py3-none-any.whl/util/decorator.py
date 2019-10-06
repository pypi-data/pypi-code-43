# Useful decorators

import functools
import inspect
import platform
from copy import copy


class Decorator:
    """
    Decorator base class capable of decorating a function or class method, with or
    without additional default arguments.

    The default implementation does nothing and is designed to be used as part of a base
    class for a new decorator.

    Example:

        >>> class mul(Decorator):
        ...     def __init__(self, func=None, default=2):
        ...         super().__init__(func)
        ...         self.default = default
        ...     def _call_wrapped(self, *args, **kwargs):
        ...         args = tuple(_*2 if type(_) == int else _ for _ in args)
        ...         kwargs = {key:val*self.default for key,val in kwargs.items()}
        ...         super()._call_wrapped(*args, **kwargs)
        ... class Foo:
        ...     @mul
        ...     def mul2(self, val1, val2=None):
        ...         print(f"Foo.mul2: {val1} ... {val2}")
        ...     @mul(default=3)
        ...     def mul3(self, val1, val2=None):
        ...         print(f"Foo.mul3: {val1} ... {val2}")
        ... obj=Foo()
        ... obj.mul2(123)
        ... obj.mul2(123, 456)
        ... obj.mul3(3, 9)
        Foo.mul2: 246 ... None
        Foo.mul2: 246 ... 912
        Foo.mul3: 6 ... 18

    """

    def __init__(self, func=None):
        """
        Override as necessary to add additional keyword arguments
        """
        self.__self__ = None

        if func is None:
            self.__with_args = True
            self.__wrapped__ = None
        else:
            self.__with_args = False
            self.__wrapped__ = func
            self._wrap_func(self, func)

    def _call_wrapped(self, *args, **kwargs):
        """
        Calls the wrapped function/method.  Override this method to customize how the
        wrapped function is called.
        """
        return self.__wrapped__(*args, **kwargs)

    def _wrap_func(self, obj, func):
        """
        Wrap the function or class method to update __doc__ and other similar
        attributes.  Override this method to customize how the function is wrapped.
        """
        # update __doc__ and similar attributes
        functools.update_wrapper(obj, func)

        return self

    def __call__(self, *args, **kwargs):
        if self.__with_args:
            if self.__wrapped__ is None:
                assert len(args) == 1
                assert len(kwargs) == 0
                return self._wrap_func(self, args[0])
            else:
                return self.__call_wrapped_function(*args, **kwargs)
        else:
            return self.__call_wrapped_function(*args, **kwargs)

    def __get_wrapped_args(self, *args):
        # if bound to an object, pass it as the first argument
        if self.__self__ is not None:
            args = (self.__self__,) + args
        return args

    def __call_wrapped_function(self, *args, **kwargs):
        args = self.__get_wrapped_args(*args)
        return self._call_wrapped(*args, **kwargs)

    def __set_name__(self, owner, name):
        self._name = name

    def _bind(self, instance, owner):
        """
        Override this method to customize the property binding process
        """

        # create a bound copy of this object
        bound = copy(self)
        bound.__self__ = instance

        if self.__with_args:
            bound._wrap_func(self, self.__wrapped__)
        else:
            bound._wrap_func(bound, self.__wrapped__)

        return bound

    def __get__(self, instance, owner):
        if instance is None:
            return self
        else:
            bound = self._bind(instance, owner)

            # add the bound decorator to the object's dict so that
            # __get__ won't be called a 2nd time
            setattr(instance, self.__wrapped__.__name__, bound)

            return bound


class oscheck(Decorator):
    def __init__(self, function=None, target=None, return_value=None, return_factory=None):
        """
        Decorator which executes the specified class method only if matching the specified
        operating system.

        :param function: The function or method being decorated.
        :param return_value: The return value to use if the check fails.
        :param return_factory: The return value factory to use if the check fails (called with NO arguments)
        """

        super().__init__(function)

        if return_value and return_factory:
            raise ValueError("Canot specify both 'return_value' and 'return_factory'!")
        elif target is None:
            raise ValueError("Missing required keyword 'target'")
        else:
            self.target = target
            self.return_value = return_value
            self.return_factory = return_factory

    def _call_wrapped(self, *arg, **kw):
        if platform.system() == self.target:
            return super()._call_wrapped(*arg, **kw)
        elif self.return_factory is not None:
            return self.return_factory()
        else:
            return self.return_value

class classproperty:
    """
    Simple class property decorator
    """
    def __init__(self, getter):
        self.getter = getter

    def __get__(self, instance, owner):
        return self.getter(owner)
