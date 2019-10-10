from abc import abstractmethod, ABC
from functools import partial
from typing import Callable, Union

from tartiflette import Resolver

from .dataloaders import BaseDataLoader, BaseDataLoaderImpl


class EndpointABC(ABC):

    @abstractmethod
    async def __call__(self, *args, **kwargs):
        pass


class BaseResolver:
    endpoint: Union[str, None] = None

    _client = None
    _service = None
    _endpoint_name = None
    _endpoint_obj: EndpointABC = None

    def get_endpoint(self, request):
        if self._endpoint_obj is not None:
            return self._endpoint_obj
        if not self.endpoint:
            return
        try:
            self._client, self._service, self._endpoint_name = self.endpoint.split('.')
        except ValueError:
            raise RuntimeError(f'error with parse endpoint name {self.endpoint}. User client.service.endpoint format')

        if (self._service is None) or (self._endpoint_name is None):
            raise NotImplementedError('You must implement service and endpoint for make request')

        try:
            if self._client == 'rest':
                service = request.app.rest_client.get(self._service)
            elif self._client == 'db':
                service = request.app.db_client.get(self._service)
            else:
                raise RuntimeError('Only "db" and "rest" clients is supported')
            self._endpoint_obj = getattr(service, self._endpoint_name)
        except AttributeError as e:
            raise RuntimeError(f'Cant get source method or endpoint: {e}')

    async def execute(self, parent, args, ctx, info):
        raise NotImplementedError


class MutationResolver(BaseResolver):

    async def execute(self, parent, args, ctx, info):
        self.get_endpoint(ctx['request'])
        return await self.load(parent, args, ctx, info)

    async def load(self, parent, args, ctx, info):
        return await self._endpoint_obj(**args, headers=ctx['request'].headers)


class QueryResolver(BaseResolver):
    batch = False
    dataloader_class: Union[BaseDataLoader, None] = BaseDataLoaderImpl

    _dataloader_obj = None

    def get_dataloader(self, request):
        self.get_endpoint(request)
        if not self._endpoint_obj:
            raise NotImplementedError('Cant use dataloader without any endpoint')

        loader = getattr(request, self.endpoint, None)
        if loader is None:
            loader = self.dataloader_class(endpoint=self._endpoint_obj, request=request)
            setattr(request, self.endpoint, loader)
        self._dataloader_obj = loader

    @property
    def call_dataloader(self):
        return partial(self._dataloader_obj, _batch=self.batch)

    async def load(self, parent, args, ctx, info):
        return await self.call_dataloader(**args)

    async def execute(self, parent, args, ctx, info):
        self.get_endpoint(ctx['request'])
        self.get_dataloader(ctx['request'])
        return await self.load(parent, args, ctx, info)


class ResolverDec(Resolver):
    def __call__(self, resolver: Callable) -> Callable:
        if issubclass(resolver, BaseResolver):
            resolver = resolver().execute
        return super().__call__(resolver)
