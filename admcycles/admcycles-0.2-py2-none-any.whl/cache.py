r"""
This should be removed

Instead the program should use cached_function/cached_method that
implements much better caching.
"""
cache_dict = {}

def capply(f, *args):
  global cache_dict
  key = (f.__name__, args)
  if key not in cache_dict:
    cache_dict[key] = f(*args) #apply(f, args)
  return cache_dict[key]

def clear_cache():
  global cache_dict
  cache_dict = {}
