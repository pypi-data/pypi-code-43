'''
Python decorator for deprecation warnings

History:
04-05-2018 - 1.0.0 - Stephen Funkhouser
    Created
'''
__version__ = '1.0.0'

import warnings
import functools


def deprecated(func):
    '''This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used.'''
    @functools.wraps(func)
    def new_func(*args, **kwargs):
        warnings.simplefilter('always', DeprecationWarning)  # turn off filter
        warnings.warn(
            'Call to deprecated function {fn}.'.format(
                fn=func.__name__,
            ), category=DeprecationWarning, stacklevel=2
        )
        warnings.simplefilter('default', DeprecationWarning)  # reset filter
        return func(*args, **kwargs)
    return new_func


if __name__ == '__main__':

    @deprecated
    def square(a):
        return a ^ 2

    with warnings.catch_warnings(record=True) as w:
        # Cause all warnings to always be triggered.
        warnings.simplefilter("always")
        # Trigger a warning.
        square(2)

        print '-' * 40
        print w
        for d in w:
            print d
        print '-' * 40

        warnings.simplefilter('default')

        # Verify some things
        assert len(w) == 1
        assert issubclass(w[-1].category, DeprecationWarning)
        assert "deprecated" in str(w[-1].message)
        assert "deprecated function %s" % (
            square.__name__) in str(w[-1].message)

        # -1 is the last element in the list
        print '4', w[-1]
