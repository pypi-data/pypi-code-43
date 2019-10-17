import json

from bitfield import BitField, BitHandler
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.fields.files import FieldFile
from django.http import HttpResponse

from isc_common import setAttr, getAttr


class JsonResponse(HttpResponse):
    """
    An HTTP response class that consumes data to be serialized to JSON.

    :param data: Data to be dumped into json. By default only ``dict`` objects
      are allowed to be passed due to a security flaw before EcmaScript 5. See
    :param encoder: Should be a json encoder class. Defaults to
      ``django.core.serializers.json.DjangoJSONEncoder``.
    :param safe: Controls if only ``dict`` objects may be serialized. Defaults
      to ``True``.
    :param json_dumps_params: A dictionary of kwargs passed to json.dumps().
    """

    def __init__(self, data, encoder=DjangoJSONEncoder, safe=True, json_dumps_params=None, **kwargs):
        if safe and not isinstance(data, dict):
            raise TypeError(
                'In order to allow non-dict objects to be serialized set the '
                'safe parameter to False.'
            )
        if json_dumps_params is None:
            json_dumps_params = dict()
        kwargs.setdefault('content_type', 'application/json')
        self.container_data = data
        data = json.dumps(data, cls=encoder, **json_dumps_params)
        super().__init__(content=data, **kwargs)


class JsonResponseLookup(HttpResponse):

    def __init__(self, data, encoder=DjangoJSONEncoder, safe=True, json_dumps_params=None, **kwargs):
        if safe and not isinstance(data, dict):
            raise TypeError(
                'In order to allow non-dict objects to be serialized set the '
                'safe parameter to False.'
            )
        if json_dumps_params is None:
            json_dumps_params = dict()

        kwargs.setdefault('content_type', 'application/json')
        self.container_data = data.copy()

        _data = getAttr(getAttr(self.container_data, 'response'), 'data')
        _data_clear = dict()

        for key, value in _data.items():
            if not isinstance(value, FieldFile):
                setAttr(_data_clear, key, value)
            if isinstance(value, BitHandler):
                setAttr(_data_clear, key, value._value)

        data['response']['data'] = _data_clear

        data = json.dumps(data, cls=encoder, **json_dumps_params)
        super().__init__(content=data, **kwargs)
