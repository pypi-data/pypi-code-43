import inspect


def get_name(obj):
    """ Get name of the given object.

    Returns:
        Class: ClassName
        Function: function_name()
        Method: method_name()
        Default: str(obj)
    """
    if inspect.isclass(obj):
        return obj.__name__
    elif inspect.isfunction(obj):
        return obj.__name__ + "()"
    elif inspect.ismethod(obj):
        return obj.__name__ + "()"
    return obj.__class__.__name__


