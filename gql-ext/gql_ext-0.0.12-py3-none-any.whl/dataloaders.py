from abc import abstractmethod
from logging import getLogger

from aiodataloader import DataLoader

logger = getLogger(__name__)


class BaseDataLoader(DataLoader):
    def __init__(self, batch_load_fn=None, batch=None, max_batch_size=None, cache=None, get_cache_key=None,
                 cache_map=None, loop=None, request=None, memo_cache=False, endpoint=None):
        super().__init__(batch_load_fn, batch, max_batch_size, cache, get_cache_key, cache_map, loop)
        self.request = request
        self.memo_cache = memo_cache
        self.endpoint = endpoint

    @abstractmethod
    async def __call__(self, **kwargs):
        raise NotImplementedError


class BaseDataLoaderImpl(BaseDataLoader):
    max_batch_size = 50

    def __call__(self, _batch: bool = False, **kwargs):
        if len(kwargs) == 1 and _batch:
            keys = self.kwargs_to_keys(**kwargs)
            return self.load_many(keys)
        return self.non_batch_load_fn(**kwargs)

    def prime_results(self, result):
        if isinstance(result, list):
            res = result
        elif isinstance(result, dict):
            res = result.get('result') or []
        else:
            res = []
        for item in res or []:
            if item.get('id'):
                self.prime(('id', item.get('id')), item)

    async def non_batch_load_fn(self, **kwargs):
        result = await self.endpoint(**kwargs, headers=self.request.headers)
        self.prime_results(result)

        return result

    @staticmethod
    def kwargs_to_keys(**kwargs):
        out = []
        for key, value in kwargs.items():
            if isinstance(value, (list, tuple)):
                for v in value:
                    out.append((key, v))
            else:
                out.append((key, value))
        return tuple(out)

    @staticmethod
    def keys_to_kwargs(keys):
        d = {}
        for k, v in keys:
            if k in d:
                d[k].append(v)
            else:
                d[k] = [v]
        return d

    async def batch_load_fn(self, keys):
        kwargs = self.keys_to_kwargs(keys)
        result = await self.endpoint(**kwargs, headers=self.request.headers)

        dct = {}
        for key in keys:
            for item in (result.get('result') or []):
                if key in item.items():
                    dct[key] = item

        return [dct.get(key) for key in keys]
