'''
Python decorators for memoization

Usage:
@memoized
def fibonacci(n):
   "Return the nth fibonacci number."
   if n in (0, 1):
      return n
   return fibonacci(n-1) + fibonacci(n-2)

print fibonacci(12)

History:
09-13-2019 - 1.0.0 - Stephen Funkhouser
    - Created
'''
__version__ = '1.0.0'

import collections
import functools

def memoize(obj):
    cache = obj.cache = {}

    @functools.wraps(obj)
    def memoizer(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key not in cache:
            cache[key] = obj(*args, **kwargs)
        return cache[key]
    return memoizer
