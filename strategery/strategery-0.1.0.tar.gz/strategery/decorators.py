def fed_by(*args, **kwargs):
    """This is a decorator to indicate you'd like your Feature task to get other Feature tasks injected into it"""

    def decorator(function):
        function.dependencies = args
        return function
    return decorator
