# -*- coding: utf-8 -*-
import json
from copy import copy


class AdapterJSONEncoder(json.JSONEncoder):
    """
    A JSONEncoder which has a dict of adapters to map classes to json.

    Each class has its own custom 'adapter' method which can turn an instance
    of this class into a dict.
    By default these adapter methods take only the object as parameter, but
    extra kwargs can optionally be added with the 'extra_kwargs' parameter.
    """

    def __init__(self, adapters, extra_kwargs, json_dump_kwargs):
        super(AdapterJSONEncoder, self).__init__(**json_dump_kwargs)
        self.adapters = adapters
        self.extra_kwargs = extra_kwargs

    def default(self, obj):
        object_type = type(obj)
        try:
            return self.adapters[object_type](obj, **self.extra_kwargs)
        except KeyError:
            return json.JSONEncoder.default(self, obj)


class CustomizableJSONifier(object):

    def __init__(self, json_dump_kwargs=None, **adapter_kwargs):
        """
        Create an object to which custom adapters can be registered.

        Once registered, this class can turn custom class instances into json.

        :type json_dump_kwargs: dict
        :param json_dump_kwargs: kwargs which will be passed on to the json
           dump / dumps methods. For example 'indent', 'sort_keys'
        :param adapter_kwargs: Any extra kwarg will be passed to the
           registered adapters.
        """
        super(CustomizableJSONifier, self).__init__()
        self.adapters = {}
        self.default_json_dump_kwargs = json_dump_kwargs or {}
        self.default_adapter_kwargs = adapter_kwargs

    def __call__(self, custom_adapter_kwargs, custom_dump_kwargs=None,
                 *args, **kwargs):
        kwargs.update(custom_dump_kwargs)
        return AdapterJSONEncoder(self.adapters, custom_adapter_kwargs, kwargs)

    def register_adapter(self, class_):
        """Register a method to be used when serializing the class to json."""
        def decorator(fn):
            self.adapters[class_] = fn
            return fn
        return decorator

    def dumps(self, obj, json_dump_kwargs=None, **adapter_kwargs):
        """
        Turn an object into a json string.

        :param obj: The object to turn into json.
        :type json_dump_kwargs: dict
        :param json_dump_kwargs: kwargs which will be passed on to the json
           dump / dumps methods. For example 'indent', 'sort_keys'. These
           kwargs will take precedence over the ones set on the encoder.
        :param adapter_kwargs: Any extra kwarg will be passed to the
           registered adapters.
        :rtype: str
        :return: a json string.
        """
        custom_adapter_kwargs, custom_dump_kwargs = self._prepare_kwargs(
            adapter_kwargs, json_dump_kwargs
        )
        return json.dumps(obj, cls=self,
                          custom_adapter_kwargs=custom_adapter_kwargs,
                          custom_dump_kwargs=custom_dump_kwargs)

    def to_dict(self, obj, json_dump_kwargs=None, **adapter_kwargs):
        """
        Turn an object into a dict.

        This method simply uses dumps to turn the object into a string and
        then loads it back with json.loads.

        :param obj: The object to turn into json.
        :type json_dump_kwargs: dict
        :param json_dump_kwargs: kwargs which will be passed on to the json
           dump / dumps methods. For example 'indent', 'sort_keys'. These
           kwargs will take precedence over the ones set on the encoder.
        :param adapter_kwargs: Any extra kwarg will be passed to the
           registered adapters.
        :return: a json object. Probably dict or list.
        """
        json_string = self.dumps(obj, json_dump_kwargs=json_dump_kwargs,
                                 **adapter_kwargs)
        return json.loads(json_string)

    def dump(self, obj, fp, json_dump_kwargs=None, **adapter_kwargs):
        """Turn an object into a json string written to a file.

        :param fp: a file-like object. (has .write() method)
        :param obj: The object to turn into json.
        :type json_dump_kwargs: dict
        :param json_dump_kwargs: kwargs which will be passed on to the json
           dump / dumps methods. For example 'indent', 'sort_keys'. These
           kwargs will take precedence over the ones set on the encoder.
        :param adapter_kwargs: Any extra kwarg will be passed to the
           registered adapters.
        :rtype: str
        :return: a json string.
        """
        custom_adapter_kwargs, custom_dump_kwargs = self._prepare_kwargs(
            adapter_kwargs, json_dump_kwargs
        )
        return json.dump(obj, fp, cls=self,
                         custom_adapter_kwargs=custom_adapter_kwargs,
                         custom_dump_kwargs=custom_dump_kwargs)

    def _prepare_kwargs(self, adapter_kwargs, json_dump_kwargs):
        custom_dump_kwargs = copy(self.default_json_dump_kwargs)
        if json_dump_kwargs is not None:
            custom_dump_kwargs.update(json_dump_kwargs)
        custom_adapter_kwargs = copy(self.default_adapter_kwargs)
        if adapter_kwargs is not None:
            custom_adapter_kwargs.update(adapter_kwargs)
        return custom_adapter_kwargs, custom_dump_kwargs


_global_encoder = CustomizableJSONifier()
register_adapter = _global_encoder.register_adapter
dump = _global_encoder.dump
dumps = _global_encoder.dumps
to_dict = _global_encoder.to_dict
