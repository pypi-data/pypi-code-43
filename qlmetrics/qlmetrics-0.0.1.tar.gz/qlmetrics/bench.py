"""bench.py: utilities for time tracking and benchmarking"""

from functools import wraps
from time import time as tm
import resource

DEFAULT_TIMING_FMT = "@timecall: {0} took {1} seconds"
DEFAULT_MEMORY_FMT = "@trackmem: {0} start: {1} end: {2} used: {3} {4}"


def timethis(fmt_func=None, verbose=True):
    """
    Parameterized decorator for tracking time of a function call
    :fmt_func is a string formatting function that should take func_name, duration
              paramters and return a string to print the timing info
    """
    def decorator(func):
        @wraps(func)
        def time_call(*args, **kwargs):
            t1 = tm()
            result = func(*args, **kwargs)
            t2 = tm()
            d = t2 - t1
            if verbose:
                if fmt_func is None:
                    print(DEFAULT_TIMING_FMT.format(func.__name__, d))
                else:
                    print(fmt_func(func.__name__, d))
            return result
        return time_call
    return decorator


def trackmem(fmt_func=None, verbose=True, unit="MB"):
    """
    Paramaterized decorator for tracking memory usage of a function calls via resource module
    Note that there has not been any specific review of how gargage collection affects this profiling
    """
    def decorator(func):
        @wraps(func)
        def memtrack_call(*args, **kwargs):
            m1 = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            result = func(*args, **kwargs)
            m2 = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            usage = m2 - m1
            cv = size([m1, m2, usage], unit)
            if verbose:
                if fmt_func is None:
                    print(DEFAULT_MEMORY_FMT.format(func.__name__, cv[0], cv[1], cv[2], unit.upper()))
                else:
                    print(fmt_func(func.__name__, cv[0], cv[1], cv[2], unit.upper()))
            return result
        return memtrack_call
    return decorator


def timethis_returnstats(func):
    """
    this decorator changes the function signature of `func` passed in
    returns a tuple where the first item is the normal result and the second is a dictionary of timing info
    """
    @wraps(func)
    def time_call(*args, **kwargs):
        t1 = tm()
        result = func(*args, **kwargs)
        t2 = tm()
        d = t2 - t1
        print("@timecall: %s took %s seconds" % (func.__name__, d))
        return result, {'func_name': func.__name__, 'duration': d}
    return time_call


def size(values, unit):
    converted = []
    u = unit.lower()
    UNITS = ('b', 'kb', 'mb', 'gb')
    if u not in UNITS:
        raise ValueError("Must provide unit as one of %s" % list(UNITS))
    for v in values:
        if u == 'b':
            cv = v
        elif u == 'kb':
            cv = v / 1024.0
        elif u == 'mb':
            cv = v / 1024 / 1024.0
        elif u == 'gb':
            cv = v / 1024 / 1024 / 1024.0
        else:
            raise ValueError("case not handled for unit")
        converted.append(cv)
    return converted
