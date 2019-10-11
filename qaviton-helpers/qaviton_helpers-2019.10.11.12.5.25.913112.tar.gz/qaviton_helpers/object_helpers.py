class DynamicClass:
    """ do not touch this class!
        it is intended for dynamic objects
    """
    def __init__(self): ...


def lists_to_object(keys: list, values: list)->DynamicClass:
    """
    parse lists and return a dynamic object.
    keys & values are lists/tuples with equal length
    """
    obj = DynamicClass()
    for i in range(len(keys)):
        setattr(obj, keys[i], values[i])
    return obj


def dict_to_object(dictionary: dict)->DynamicClass:
    """parse a dictionary and return a dynamic object"""
    obj = DynamicClass()
    for key in dictionary:
        setattr(obj, key, dictionary[key])
    return obj


def object_to_dict(obj: object):
    """parse an object and return a dictionary"""
    obj_dict = obj.__dict__
    return {key: obj_dict[key] for key in obj_dict if not key.startswith('__')}


def object_to_list(obj: object):
    """parse an object and return a list of values"""
    obj_dict = obj.__dict__
    return [obj_dict[key] for key in obj_dict if not key.startswith('__')]


def remove_dict_keys(d: dict, *keys):
    """usage:
    from qaviton_helpers import remove_dict_keys
    d = {'a':1,'b':2,'c':3}
    remove_dict_keys(d, 'a','b','c')
    d
    >{}
    """
    for k in keys: del d[k]
