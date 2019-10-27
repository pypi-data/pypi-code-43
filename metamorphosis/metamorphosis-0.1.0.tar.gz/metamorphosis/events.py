import importlib
from uuid import uuid4, UUID

import graphene as g

_event_registry = {}


class BaseEventMixin:
    """Base class for serializing events with an uuid"""
    id = g.String()

    def resolve_id(self, *args, **kwargs):
        if not self.id:
            self.id = str(uuid4())
        return self.id


class ExceptionEvent(g.ObjectType,  BaseEventMixin):
    """Base class for serializing and deserializing exceptions"""
    src_id = g.String()
    ns = g.String()
    classname = g.String()
    code = g.String()
    msg = g.String()
    data = g.JSONString()
    stacktrace = g.String()


def dump_objecttype(o: g.ObjectType) -> dict:
    """
    Dump a populated Graphene object to a dict.

    Args:
        o: The object itself

    Returns:
        A serialized dict that contains the data itself and two special members, `_type`, and `_ns`, which
        are the classname and module respectively.  It can be reloaded and rehydrated with the original type using
        `load_objecttype`
    """
    value = {"_type": o.__class__.__name__, "_ns": o.__class__.__module__}

    for field in o._meta.fields:
        oval = getattr(o, field)
        if field == 'id':
            value['id'] = str(oval)
        else:
            f = o._meta.fields[field]
            if oval is not None:
                if hasattr(f.type, 'serialize'):  # then the type is scalar
                    value[field] = f.type.serialize(oval)
                else:
                    value[field] = dump_objecttype(oval)

    return value


def load_objecttype(value: dict) -> g.ObjectType:
    """
    Load an object serialized by `dump_objecttype` back into its original event form.

    Args:
        value: The serialized dict

    Returns:
        The original event, rehydrated from the dict.
    """
    ns = value['_ns']
    etype = value['_type']
    fqcn = f'{ns}.{etype}'

    if fqcn in _event_registry:
        oclass = _event_registry[fqcn]
    else:
        oclass = _event_registry[fqcn] = getattr(
            importlib.import_module(value['_ns']), value['_type'])

    vargs = {}
    for field in oclass._meta.fields:
        oval = value.get(field)
        f = oclass._meta.fields[field]
        if oval is not None:
            if hasattr(f.type, 'parse_value'):
                vargs[field] = f.type.parse_value(oval)
            elif field == 'id':
                vargs[field] = UUID(oval)
            else:
                vargs[field] = load_objecttype(oval)
    return oclass(**vargs)
