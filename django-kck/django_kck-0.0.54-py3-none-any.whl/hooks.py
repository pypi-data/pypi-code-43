import logging

logger = logging.getLogger(__name__)


class UncallableHook(Exception):
    pass


class BaseHook(object):
    hook_type = None
    callable = None
    _key = None

    def __init__(self, callable=None):
        if callable:
            self.callable = callable

    def run(self, hints, cache, **kwargs):
        if self.callable:
            try:
                if 'key' not in kwargs:
                    kwargs['key'] = self.key()
                self.callable(hints=hints, cache=cache, **kwargs)
            except TypeError:
                raise UncallableHook()

    def run_if_type_matches(self, hook_type, hints, cache, **kwargs):
        if hook_type != self.hook_type:
            return
        self.run(hints=hints, cache=cache, **kwargs)

    def key(self, k=None):
        if k:
            self._key = k
        return self._key


class PreSetHook(BaseHook):
    hook_type = 'pre-set'


class PostSetHook(BaseHook):
    hook_type = 'post-set'


class PrePrimeHook(BaseHook):
    hook_type = 'pre-prime'


class PostPrimeHook(BaseHook):
    hook_type = 'post-prime'


class PostSetRefreshHook(PostSetHook):
    def __init__(self, refresh_key=None, param_func=None):
        self.refresh_key = refresh_key
        self.param_func = param_func

    def run(self, hints, cache, **kwargs):
        if self.refresh_key:
            key = cache.build_key(
                self.refresh_key,
                **self.param_func(**cache.primer_instance(self.key()).parameter_dict()))
            logger.debug('PostSetRefreshHook.run() - refreshing key: {}'.format(key))
            cache.refresh(key, queued=True)
