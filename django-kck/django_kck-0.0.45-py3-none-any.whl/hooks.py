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


