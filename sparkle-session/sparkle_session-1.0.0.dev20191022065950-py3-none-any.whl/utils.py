import inspect


def _to_instance(n):
    if inspect.isclass(n):
        return n()
    else:
        return n


def _to_type(n):
    if inspect.isclass(n):
        return n
    else:
        return type(n)


def _get_class_name(fr):
    c = _get_class_from_frame(fr)
    if c:
        return c.__name__
    else:
        return None


def _get_class_from_frame(fr):
    args, _, _, value_dict = inspect.getargvalues(fr)
    # we check the first parameter for the frame function is
    # named 'self'
    if len(args) and args[0] == 'self':
        # in that case, 'self' will be referenced in value_dict
        instance = value_dict.get('self', None)
        if instance:
            # return its class
            return getattr(instance, '__class__', None)
    # return None otherwise
    return None
