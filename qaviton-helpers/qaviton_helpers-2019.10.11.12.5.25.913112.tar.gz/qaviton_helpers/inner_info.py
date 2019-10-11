import inspect


def funcname(): return inspect.stack()[1][3]


def classname(frame=None):
    if frame is None:
        frame = inspect.stack()[1][0]
    args, _, _, value_dict = inspect.getargvalues(frame)
    # now lets check if the 1st parameter in the frame is named 'self'
    if len(args) and args[0] == 'self':
        # in that case self will be referenced in value_dict
        instance = value_dict.get('self', None)
        if instance:
            # return its class
            return getattr(instance, '__class__', None).__name__
    return None


def get_module_name(module):
    """in case you have a module.dir.name and you want the name"""
    return module.__name__.rsplit('.', 1)[-1]
