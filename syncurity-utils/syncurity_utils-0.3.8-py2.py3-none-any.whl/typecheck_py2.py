import functools

__all__ = ['typecheck']

def typecheck(*args1, **kwargs1):
    """
    Silently do nothing, since our typechecking solution is limited to python3
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args2, **keywords):
            return func(*args2, **keywords)
        return wrapper
    return decorator
