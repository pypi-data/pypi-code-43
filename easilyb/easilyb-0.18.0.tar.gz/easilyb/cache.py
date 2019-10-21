import time
import logging
import json
from threading import Lock
logger = logging.getLogger(__name__)
DEFAULT_TTL = 3600
DEFAULT_NAMESPACE = "DEFAULT_NAMESPACE"
DEFAULT_CLEAN_INTERVAL = 60


class SimpleCache:
    def __init__(self, clean_interval=DEFAULT_CLEAN_INTERVAL, expires=True, ttl=DEFAULT_TTL):
        self._db = dict()
        self.clean_interval = clean_interval
        self._last_clean = time.time()
        self._lock = Lock()
        self.expires = expires
        self.ttl = ttl

    def get(self, key, action=None, action_kwargs=None, namespace=DEFAULT_NAMESPACE,
            expires=None, ttl=None):
        if expires is None: expires = self.expires
        if ttl is None: ttl = self.ttl
        with self._lock:
            self._auto_clean()
            if namespace not in self._db:
                self._db[namespace] = dict()
            if key in self._db[namespace] and not self._db[namespace][key].expired():
                return self._db[namespace][key].value
            elif action is not None:
                action_kwargs = action_kwargs or dict()
                ret = action(**action_kwargs)
                entry = CacheEntry(key, ret, expires=expires, ttl=ttl, action=action, action_kwargs=action_kwargs)
                self._db[namespace][key] = entry
                return self._db[namespace][key].value
            else:
                raise NotFoundInCache()

    def put(self, key, value, action=None, action_kwargs=None, namespace=DEFAULT_NAMESPACE,
            expires=None, ttl=None):
        if expires is None: expires = self.expires
        if ttl is None: ttl = self.ttl
        with self._lock:
            self._auto_clean()
            if namespace not in self._db:
                self._db[namespace] = dict()
            entry = CacheEntry(key, value, expires=expires, ttl=ttl, action=action, action_kwargs=action_kwargs)
            self._db[namespace][key] = entry

    def cached(self, func=None, expires=None, ttl=None, namespace=DEFAULT_NAMESPACE):
        def decorator(func):
            def wrapper(*a, **ka):
                expires_ = self.expires if expires is None else expires
                ttl_ = self.ttl if ttl is None else ttl
                namespace_ = namespace + "." + func.__name__
                key = _get_key(a, ka)
                try:
                    return self.get(key, namespace=namespace_)
                except NotFoundInCache:
                    value = func(*a, **ka)
                    self.put(key, value, expires=expires_, ttl=ttl_, namespace=namespace_)
                    return value
            return wrapper

        if callable(func):
            return decorator(func)
        else:
            return decorator

    def get_namespace_cache(self, namespace, expires=None, ttl=None):
        if expires is None: expires = self.expires
        if ttl is None: ttl = self.ttl
        return NamespaceCache(self, namespace, expires=expires, ttl=ttl)

    def _auto_clean(self):
        if time.time() - self._last_clean > self.clean_interval:
            self.clean()

    def clean(self):
        for sp in self._db:
            to_remove = list()
            for k,v in self._db[sp].items():
                if v.expired():
                    to_remove.append(k)
            for k in to_remove:
                del self._db[sp][k]
        self._last_clean = time.time()


class NamespaceCache:
    def __init__(self, maincache, namespace, expires=True, ttl=DEFAULT_TTL):
        self.namespace = namespace
        self.cache = maincache
        self.expires = expires
        self.ttl = ttl

    def get(self, key, action=None, action_kwargs=None, expires=None, ttl=None):
        if expires is None: expires = self.expires
        if ttl is None: ttl = self.ttl
        return self.cache.get(key, action=action, action_kwargs=action_kwargs, expires=expires, ttl=ttl,
                       namespace=self.namespace)

    def put(self, key, value, action=None, action_kwargs=None, expires=None, ttl=None):
        if expires is None: expires = self.expires
        if ttl is None: ttl = self.ttl
        self.cache.put(key, value, action=action, action_kwargs=action_kwargs, expires=expires, ttl=ttl,
                       namespace=self.namespace)

    def cached(self, func=None, expires=None, ttl=None):
        if expires is None: expires = self.expires
        if ttl is None: ttl = self.ttl
        return self.cache.cached(func, expires, ttl, namespace=self.namespace)


class NotFoundInCache(Exception):
    pass


class CacheEntry:
    def __init__(self, key, value, expires=True, ttl=DEFAULT_TTL, action=None, action_kwargs=None):
        self.key = key
        self.value = value
        self.expires = expires
        self.ttl = ttl
        self.creation_time = time.time()
        self.expire_time = self.creation_time + ttl
        self.action = action
        self.action_kwargs = action_kwargs

    def expired(self):
        return self.expires and time.time() > self.expire_time


class _KeyEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            return json.JSONEncoder.default(self, obj)
        except:
            return str(obj)


def _get_key(args, kwargs):
    return json.dumps({'args':args, 'kwargs': kwargs}, sort_keys=True, cls=_KeyEncoder)


