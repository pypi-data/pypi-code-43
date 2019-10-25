import importlib


def get_attribute(doted_string):
    module_str, attr_str = doted_string.rsplit('.', 1)
    module = importlib.import_module(module_str)
    attribute = getattr(module, attr_str)
    return attribute
