import logging

from abc import ABC, abstractmethod, abstractproperty

_logger = logging.getLogger(__name__)

class LibraryContent(ABC):
    """
    Abstract Base Class for a library storage data type.
    """
    @abstractproperty
    def records(self):
        """Database records wrapped in a utility class"""
        ...
        raise NotImplementedError("Method Not Implemented")
        return []

    @abstractproperty
    def mrls(self):
        """List of MRL strings accessible contained by this class"""
        raise NotImplementedError("Method Not Implemented")
        return []

    @abstractmethod
    def read(self, filename):
        """Read database file content"""
        raise NotImplementedError("Method Not Implemented")

    @abstractmethod
    def filter(self, query, content=None):
        """Filter the records using a test query function.

        The 'query' function must accept a Mapping object (which will be a database record)
        and return 'True' if the Mapping object should be included in the filter.

        If 'content' is None: filter the storage content
        If 'content' is Not None: filter the provided content array
        """

        raise NotImplementedError("Method Not Implemented")

    @abstractmethod
    def __getitem__(self, item):
        raise NotImplementedError("Method Not Implemented")

    @abstractmethod
    def __len__(self):
        raise NotImplementedError("Method Not Implemented")

    @abstractmethod
    def __iter__(self):
        raise NotImplementedError("Method Not Implemented")

    @abstractmethod
    def configSave(self, doc, cls):
        """
        Save the configuration dictionary 'doc' for class 'cls'
        """
        raise NotImplementedError("Method Not Implemented")

    @abstractmethod
    def configLoad(self, cls):
        """
        Load the configuration dictionary for class 'cls'
        """
        raise NotImplementedError("Method Not Implemented")
