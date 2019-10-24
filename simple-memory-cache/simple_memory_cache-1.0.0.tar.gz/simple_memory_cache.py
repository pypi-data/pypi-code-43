# Special object used as reference check to detect no value vs None
NO_VALUE_STORED = object()

class NoStoredValue(Exception):
    pass

class CachedVar(object):
    """ Abstract class, requires two methods to be declared:
    def _get_stored_value(self):
        Should return the value found in the cache if found, 
        or return NO_VALUE_STORED if no value was found in the cache. 
        The second case triggers the value-fetching.
        
    def _set_stored_value(self, value):
        Should simply set the value as is in the cache.
    """
    def __init__(self, name):
        self.name = name
        self._first_access_fn = lambda: None
        self._each_access_fn = lambda x: x 
        
    def on_first_access(self, fn):
        self._first_access_fn = fn
        return fn
    
    def on_each_access(self, fn):
        self._each_access_fn = fn
        return fn
        
    def invalidate(self):
        self._set_stored_value(NO_VALUE_STORED)
    
    def get_stored_value(self):
        stored_value = self._get_stored_value()
        if stored_value is NO_VALUE_STORED:
            raise NoStoredValue()
        return stored_value
        
    def get(self):
        stored_value = self._get_stored_value()
        if stored_value is NO_VALUE_STORED:
            stored_value = self._first_access_fn()
            self._set_stored_value(stored_value)
            
        return self._each_access_fn(stored_value)

class MemoryCache(object):
    class _MemoryCachedVar(CachedVar):
        def __init__(self, name, _cache):
            self._cache = _cache
            super(MemoryCache._MemoryCachedVar, self).__init__(name)
        
        def _get_stored_value(self):
            return self._cache.get(self.name, NO_VALUE_STORED)
        
        def _set_stored_value(self, value):
            self._cache[self.name] = value
    
    def __init__(self):
        self._cache = dict()
    
    def MemoryCachedVar(self, name):
        return self._MemoryCachedVar(name, _cache=self._cache)  
    
GLOBAL_CACHE = MemoryCache()
    