# -*- coding: future_fstrings -*-
import six
from abc import ABCMeta, abstractmethod
from common.logger import get_logger
from common.utils import compatibleabstractproperty


@six.add_metaclass(ABCMeta)
class Provider(object):

    def __init__(self, *args, **kwargs):
        self.setup(*args, **kwargs)

    def get_storage(self, storage_type, *args, **kwargs):
        storage_type_map = {
            "keyvalue": self.get_kvstorage
        }

        if storage_type in storage_type_map:
            instance = storage_type_map[storage_type](*args, **kwargs)
            return instance
        else:
            raise Exception("%s storage_type not found" % storage_type)


    @abstractmethod
    def get_kvstorage(self, *args, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    def setup(self, *args, **kwargs):
        raise NotImplementedError()


@six.add_metaclass(ABCMeta)
class KeyValueStorage(object):
    #Todo support atomic + updates + batch get/set


    def __init__(self, *args, **kwargs):
        self.log = get_logger(__name__) if not kwargs.get('logger') else kwargs['logger']
        self.setup(*args, **kwargs)


    @abstractmethod
    def setup(self, *args, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    def get(self, key):
        # returns  none if no key found
        raise NotImplementedError()

    @abstractmethod
    def set(self, key, value):
        raise NotImplementedError()

    @abstractmethod
    def delete(self, key):
        # does not throw exception if no key exists
        raise NotImplementedError()

    @abstractmethod
    def has_key(self, key):
        raise NotImplementedError()

    @abstractmethod
    def destroy(self):
        raise NotImplementedError()

    @abstractmethod
    def acquire_lock(self, key):
        raise NotImplementedError()

    @abstractmethod
    def release_lock(self, key):
        raise NotImplementedError()

    def _get_lock_key(self, key):
        return "lockon_%s" % key

    def release_lock_on_expired_key(self, key):
        raise NotImplementedError()

    @compatibleabstractproperty
    def env(self):
        raise NotImplementedError()


