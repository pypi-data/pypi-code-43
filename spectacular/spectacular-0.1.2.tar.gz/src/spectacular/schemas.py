from enum import Enum, auto
from jsonschema import Draft7Validator


def any_value(description=None):
    if description:
        return {"description": description}
    return {}


def primitive(model, description=None):
    if description is None:
        return {"type": model}
    return {"type": model, "description": description}


def string(description=None):
    return primitive("string", description)


def integer(description=None):
    return primitive("integer", description)


def number(description=None):
    return primitive("number", description)


def boolean(description=None):
    return primitive("boolean", description)


def null(description=None):
    return primitive("null", description)


def with_format(fmt, description=None):
    schema = string(description)
    schema["format"] = fmt
    return schema


def nullable(schema):
    return union(schema, null())


def date(description=None):
    return with_format("date", description)


def email(description=None):
    return with_format("email", description)


def host(description=None):
    return with_format("hostname", description)


def array(schema):
    return {"type": "array", "items": schema}


def obj(**properties):
    return {"type": "object", "properties": properties}


class Context(Enum):
    "The usage context of an object schema." ""
    CREATE = auto()
    UPDATE = auto()
    VERIFY = auto()


def select(schema, context=Context.CREATE, ignored=None):
    if not "properties" in schema:
        raise ValueError("Not an object schema")
    properties = {}
    ignored = set(ignored or [])
    required = []
    for (name, subschema) in schema["properties"].items():
        if not name in ignored:
            properties[name] = subschema
            if context is Context.VERIFY:
                required.append(name)
            elif not allows_null(subschema) and context is Context.CREATE:
                required.append(name)
    return {"properties": properties, "required": required, "type": "object"}


def allows_null(schema):
    return Draft7Validator(schema).is_valid(None)


def enumeration(values, description=None):
    if isinstance(values, list):
        schema = string(description)
        schema["enum"] = values
        return schema
    if issubclass(values, Enum):
        return enumeration([e.name for e in values], description)
    raise ValueError("Cannot create enumeration schema from {}".format(values))


def union(*schemas):
    return {"anyOf": list(schemas)}
