import json
import importlib
import codecs
import logging
from easilyb.cache import SimpleCache

_cache = SimpleCache(expires=False)
logger = logging.getLogger(__name__)
PRINTABLE = b'0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&()*+,-./:;<=>?@[]^_`{|}~ '


class _BaseJsonSerializable(object):
    pass


@_cache.cached
def get_serializable_class(meta_prefix="_", ignore_local_vars=True):
    class _ParamJsonSerializable(_BaseJsonSerializable):
        def to_json_dict(self):
            return {k:self.__dict__[k] for k in self.__dict__ if not k.startswith(meta_prefix)
                    and not (ignore_local_vars and k.startswith('_')) and not k == 'to_json_dict'}

        def __getitem__(self, item):
            return self.__dict__.__getitem__(item)

        def __setitem__(self, key, value):
            return self.__dict__.__setitem__(key, value)

        def __contains__(self, item):
            return self.__dict__.__contains__(item)

        def __delitem__(self, key):
            return self.__dict__.__delitem__(key)

    return _ParamJsonSerializable


@_cache.cached
def get_encoder_class(meta_prefix="_", ignore_local_vars=True):
    _module = meta_prefix + 'module'
    _class = meta_prefix + 'class'
    _serializable = get_serializable_class(meta_prefix, ignore_local_vars)

    class _ParamJsonSerializeEncoder(json.JSONEncoder):
        def default(self, obj):
            try:
                if isinstance(obj, _BaseJsonSerializable):
                    # m = obj.__class__.__module__
                    # c = obj.__class__.__name__
                    # json_dict = obj.to_json_dict()
                    json_dict = _serializable.to_json_dict(obj)
                    json_dict[_module] = obj.__class__.__module__
                    json_dict[_class] = obj.__class__.__name__
                    # return {
                    #     "_module": m,
                    #     "_class": c,
                    #     "_value": obj.to_json_dict()
                    # }
                    return json_dict
                if isinstance(obj, bytes):
                    json_dict = {_class: 'bytes', _module:None}
                    try:
                        json_dict['utf8'] = obj.decode('utf8')
                    except:
                        json_dict['repr'] = repr_encode(obj)
                    return json_dict
                if isinstance(obj, set): # or isinstance(obj, tuple):
                    return {_class:obj.__class__.__name__, _module: None, 'lst': list(obj)}
                return json.JSONEncoder.default(self, obj)
            except:
                logger.error('Error serializing Json Object: %s; returning default serialization.', obj, exc_info=True)
                return json.JSONEncoder.default(self, obj)

    return _ParamJsonSerializeEncoder


@_cache.cached
def get_decoder_class(meta_prefix="_", ignore_local_vars=True):
    _module = meta_prefix + 'module'
    _class = meta_prefix + 'class'
    _serializable = get_serializable_class(meta_prefix, ignore_local_vars)

    class _ParamJsonSerializeDecoder(json.JSONDecoder):
        def __init__(self, *args, **kwargs):
            json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)
    
        def object_hook(self, obj):
            # if '_value' not in obj or _module not in obj or _class not in obj:
            try:
                if _module not in obj or _class not in obj:
                    return obj
                if obj[_module] is None:
                    if obj[_class] == 'bytes':
                        if 'utf8' in obj:
                            return obj['utf8'].encode()
                        else:
                            return repr_decode(obj['repr']) # security risk
                    elif obj[_class] == 'set':
                        return set(obj['lst'])
                    # elif obj[_class] == 'tuple':
                    #     return tuple(obj['lst'])
                    else:
                        return obj
                module_ = importlib.import_module(obj[_module])
                class_ = module_.__dict__[obj[_class]]
                obj_deser = _serializable()
                obj_deser.__module__ = obj[_module]
                obj_deser.__class__ = class_
                obj_deser.__dict__ = {k:obj[k] for k in obj if not k.startswith(meta_prefix) and not k == 'to_json_dict'}
                # return class_.from_json_dict(obj)
                return obj_deser
            except:
                logger.error('Error deserializing Json Object; returning dict: %s', obj, exc_info=True)
                return obj
    return _ParamJsonSerializeDecoder


JsonSerializable = get_serializable_class()
JsonSerializeEncoder = get_encoder_class()
JsonSerializeDecoder = get_decoder_class()


def load(*args, **kwargs):
    meta_prefix = kwargs.pop("meta_prefix", "_")
    ignore_local_vars = kwargs.pop("ignore_local_vars", True)
    if not 'cls' in kwargs or kwargs['cls'] is None:
        kwargs['cls'] = get_decoder_class(meta_prefix, ignore_local_vars)
    return json.load(*args, **kwargs)


def loads(*args, **kwargs):
    meta_prefix = kwargs.pop("meta_prefix", "_")
    ignore_local_vars = kwargs.pop("ignore_local_vars", True)
    if not 'cls' in kwargs or kwargs['cls'] is None:
        kwargs['cls'] = get_decoder_class(meta_prefix, ignore_local_vars)
    return json.loads(*args, **kwargs)


def dump(*args, **kwargs):
    meta_prefix = kwargs.pop("meta_prefix", "_")
    ignore_local_vars = kwargs.pop("ignore_local_vars", True)
    if not 'cls' in kwargs or kwargs['cls'] is None:
        kwargs['cls'] = get_encoder_class(meta_prefix, ignore_local_vars)
    return json.dump(*args, **kwargs)


def dumps(*args, **kwargs):
    meta_prefix = kwargs.pop("meta_prefix", "_")
    ignore_local_vars = kwargs.pop("ignore_local_vars", True)
    if not 'cls' in kwargs or kwargs['cls'] is None:
        kwargs['cls'] = get_encoder_class(meta_prefix, ignore_local_vars)
    return json.dumps(*args, **kwargs)


def repr_encode(bin):
    res = u''
    for ci in bin:
        if isinstance(ci, int):
            c = bytes([ci])
        else:
            c = ci
        if c in PRINTABLE:
            res += c.decode('utf8')
        else:
            # hex_ = hex(c)[2:]
            # if len(c) == 1:
            #     res += u'\\0'+ hex_
            # else:
            #     res += u'\\'+ hex_
            res += u'\\' + codecs.encode(c, "hex_codec").decode('utf8')
    return res


def repr_decode(repr_):
    res = b''
    i = 0
    while i < len(repr_):
        if repr_[i] != u'\\':
            res += repr_[i].encode('utf8')
            i += 1
        else:
            res += codecs.decode(repr_[i+1:i+3], "hex_codec")
            i += 3
    return res

