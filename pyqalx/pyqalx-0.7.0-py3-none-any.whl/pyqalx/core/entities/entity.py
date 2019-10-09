from itertools import zip_longest

from pyqalx.core.entities.object_dict import ObjectDict

from pyqalx.core.errors import QalxAPIResponseError, QalxEntityTypeNotFound


class QalxListEntity(ObjectDict):
    """
    Simple wrapper around a pyqalxapi_dict so we can keep extra keys
    on the API list response.  Instantiates each entity in `data` to the
    correct QalxEntity subclass
    """
    _data_key = 'data'

    def __new__(cls, child, pyqalxapi_list_response_dict):
        """
        :param child: A `QalxEntity` subclass that all `data` should be
                    instantiated as
        :param pyqalxapi_list_response_dict: A dict that gets returned from
                                             a pyqalxapi list endpoint.  This
                                             should at minimum have a `data`
                                             key but may have other keys which
                                             we preserve
        """
        cls.child = child
        return super(QalxListEntity, cls).__new__(cls, pyqalxapi_list_response_dict)

    def __init__(self, child, pyqalxapi_list_response_dict):
        super().__init__(pyqalxapi_list_response_dict)

        if not issubclass(self.child, (QalxEntity, )):
            raise QalxEntityTypeNotFound(f'Expected `child` to be a subclass of '
                                         f'`QalxEntity`.  Got `{self.child}`')

        if self._data_key not in pyqalxapi_list_response_dict or \
                not isinstance(pyqalxapi_list_response_dict[self._data_key], list):
            raise QalxAPIResponseError('Expected `{0}` key in '
                                       '`pyqalxapi_list_response_dict` and for'
                                       ' it to be a list'.format(self._data_key))
        # Cast all the entities in data to be an instance of `self.child`
        self[self._data_key] = [self.child(e) for e in
                                pyqalxapi_list_response_dict[self._data_key]]  # noqa

    def __str__(self):
        return f"[{self.child.entity_type} list]"


class QalxEntity(ObjectDict):
    """Base class for qalx entities_response.

    QalxEntity children need to be populated with either a `requests.models.Response` which is the type returned
    by the methods on `pyqalxapi.api.PyQalxAPI` or with a `dict`.

    Entities can behave either like a dict or attribute lookups can be used
    as getters/setters

    >>> class AnEntity(QalxEntity):
    ...     pass
    >>> c = AnEntity({"guid":"123456789", "info":{"some":"info"}})
    >>> # dict style lookups
    >>> c['guid']
    '123456789'
    >>> # attribute style lookups
    >>> c.guid
    '123456789'


    :param pyqalxapi_dict: a 'dict' representing a qalx entity object to populate the entity
    :type pyqalxapi_dict: dict
    """
    entity_type: str

    def __init__(self, pyqalxapi_dict):
        super().__init__(pyqalxapi_dict)

    def __str__(self):
        return f"[{self.entity_type}] {self['guid']}"

    @classmethod
    def _chunks(cls, _iterable, chunk_size, fillvalue=None):
        """
        Collect data into fixed-length chunks or blocks"
        # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx
        Taken from the itertools documentation
        """
        args = [iter(_iterable)] * chunk_size
        return zip_longest(fillvalue=fillvalue, *args)

    def __super_setattr__(self, name, value):
        """
        Convenience method for setting proper attributes on the entity class.
        Because we are using `ObjectDict` if we did
        `self.<name> = value` this would set the
        dict key of `<name>` which we don't want.  So we call
        the supermethod to properly set the attribute
        :param name: The name of the attribute to set
        :param value: The value of the attribute to set
        """
        super(ObjectDict, self).__setattr__(name, value)

    def __dir__(self):
        """
        By default `ObjectDict` __dir__ only returns the keys on the dict.
        We want it to return everything as normal as entities might have
        methods that the user needs to know about
        """
        return super(ObjectDict, self).__dir__()
