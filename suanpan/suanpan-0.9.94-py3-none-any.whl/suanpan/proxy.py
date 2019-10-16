# coding=utf-8
from __future__ import absolute_import, print_function

import functools

from suanpan.imports import imports
from suanpan.objects import HasName


class Proxy(HasName):
    TYPE_KEY = "type"
    DEFAULT_TYPE = None
    MAPPING = {}

    def __init__(self, *args, **kwargs):
        super(Proxy, self).__init__()
        self._backend = None
        self._args = args
        self._kwargs = kwargs
        setattr(self, self.TYPE_KEY, kwargs.get(self.TYPE_KEY, self.DEFAULT_TYPE))

    def __call__(self, *args, **kwargs):
        return self.backend(*args, **kwargs)  # pylint: disable=not-callable

    def __getattr__(self, key):
        return getattr(self.__getattribute__("backend"), key)

    @property
    def backend(self):
        if self._backend is None:
            if getattr(self, self.TYPE_KEY, None) is None:
                raise Exception("{} error: backend isn't set.".format(self.name))
            self.setBackend(*self._args, **self._kwargs)
        if isinstance(self._backend, functools.partial):
            self._backend = self._backend()
        return self._backend

    def setBackend(self, *args, **kwargs):
        backendType = kwargs.get(self.TYPE_KEY)
        if not backendType:
            raise Exception(
                "{} set error: backend type is required - {}: {}".format(
                    self.name, self.TYPE_KEY, backendType
                )
            )
        BackendClass = self.MAPPING.get(backendType)
        if not BackendClass:
            raise Exception(
                "{} don't supported backend type: {}".format(self.name, backendType)
            )
        if isinstance(BackendClass, str):
            BackendClass = imports(BackendClass)
        _args = [*self._args, *args]
        _kwargs = {**self._kwargs, **kwargs}
        self._backend = self._setBackend(BackendClass, *_args, **_kwargs)
        setattr(self, self.TYPE_KEY, backendType)
        return self

    def setDefaultBackend(self, *args, **kwargs):
        kwargs.update({self.TYPE_KEY: self.DEFAULT_TYPE})
        return self.setBackend(*args, **kwargs)

    def _setBackend(self, BackendClass, *args, **kwargs):
        kwargs.pop(self.TYPE_KEY)
        return functools.partial(BackendClass, *args, **kwargs)
