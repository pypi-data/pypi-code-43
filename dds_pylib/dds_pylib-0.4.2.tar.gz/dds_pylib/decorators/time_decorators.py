'''
Python decorators for time

History:
11-12-2013 - 1.0.0 - Stephen Funkhouser
    Created
'''
__version__ = '1.0.0'


import time

from functools import wraps, partial


def timeit(method):
    ''' decorator that prints the amount of
    time a function/method takes to execute
    '''
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        print '%2.2f sec -- %s (%s, %s)' % (
            (te - ts), method.__name__, args, kw,
        )
        return result
    return timed
