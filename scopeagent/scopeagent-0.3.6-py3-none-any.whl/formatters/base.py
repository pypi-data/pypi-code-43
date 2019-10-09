from abc import abstractmethod, ABCMeta

import six


class Formatter(six.with_metaclass(ABCMeta, object)):
    @classmethod
    @abstractmethod
    def dumps(cls, span):
        raise NotImplementedError()
