# Created: 10/12/2019
# Author:  Emiliano Jordan
# Project: settings

from functools import wraps
from inspect import getfullargspec

from .core import Sejings


def extract_sejings(*ignore_args):
    if (len(ignore_args) == 1
            and callable(ignore_args[0])
            and not isinstance(ignore_args[0], str)):
        # The user function was passed in as args.
        user_function, ignore_args = ignore_args[0], []

        return _extract_settings_wrapper(user_function, ignore_args)

    def decorator(func):
        return _extract_settings_wrapper(func, *ignore_args)

    return decorator


def _extract_settings_wrapper(func, *ignore_args):

    @wraps(func)
    def wrapper(*args, **kwargs):
        # ##### Parse Function Signature for kwarg Sejings ########## #
        # Get the argument specification for the function. This
        # comes with one caveat, if a function has a decorator with
        # a different signature (think functools.lru_cache) then
        # getfullargspec() returns the signature of the decorator
        # not the function. But! in this case func is a partial and
        # has a __wrapped__ attribute that we can use to extract
        # the desired function.

        func_for_argspec = func

        while hasattr(func_for_argspec, '__wrapped__'):
            func_for_argspec = func.__wrapped__

        argspec = getfullargspec(func_for_argspec)

        # Iterate through args to evaluate any Sejings instances
        list_args = list(args)
        for i, (name, val) in enumerate(zip(argspec.args, args)):
            if isinstance(val, Sejings) and name not in ignore_args:
                list_args[i] = val()
        args = tuple(list_args)

        # Iterate through kwargs to evaluate any Sejings instance
        for name, val in kwargs.items():
            if isinstance(val, Sejings) and name not in ignore_args:
                kwargs[name] = val()

        # ####### Get names and default values for all kwargs ######## #
        if argspec.varargs is None and argspec.defaults is not None:
            # The signature has args and kwargs. This is a very typical
            # signature, yet the proper extraction should not be
            # trivialized as a function call could be passing kwargs
            # as positional args.
            defaults_offset = len(args) \
                              + len(argspec.defaults) \
                              - len(argspec.args)

            args_offset = defaults_offset - len(argspec.defaults)

            kwarg_names = argspec.args[args_offset:]
            defaults = argspec.defaults[defaults_offset:]

        elif argspec.defaults is None and argspec.kwonlydefaults is not None:
            # The signature has an Arbitrary Argument List
            # (think *args) and kwargs that follow. This means that the
            # kwargs names are now most easily accessible in kwonlyargs.
            # And the corresponding values are stored in
            # kwonlydefaults dict and not defaults.
            kwarg_names = argspec.kwonlyargs
            defaults = [v for k, v in argspec.kwonlydefaults.items()]

        else:
            # The signature has only args or no args at all.
            # AKA there's no edge cases here! :)
            return func(*args, **kwargs)

        for name, val in zip(kwarg_names, defaults):
            # Evaluate any Sejings instance that is in a kwarg and
            # hasn't been already defined by the function call.
            if name not in kwargs and isinstance(val, Sejings) and name not in ignore_args:
                kwargs[name] = val()

        return func(*args, **kwargs)

    return wrapper
