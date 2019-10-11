from importlib import import_module

def convertpath(path: str) -> tuple:
    if ':' in path:
        return tuple(path.split(':'))
    else:
        return tuple(path.rsplit('.', 1))

def imported(module, attribute=[]):
    obj = import_module(module)
    if isinstance(attribute, (bytes, str)):
        attribute = attribute.split('.')
    for attr in attribute:
        obj = getattr(obj, attr)
    return obj