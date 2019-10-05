from aufbau.core.graph import graph

VERSION = '0.1.0'

def target(func):
    """
    Decorates a callable (function or class) as a target in the build file.
    :param func: The callable to register as a target.
    """
    graph.register_target(func, func.__name__)
    return func

def depends_on(*deps):
    """
    Decorates a target as depending on one or more other targets.
    :param deps: The target's dependencies. These may be specified either as
        callables or target names.
    """
    def add_dependency(func):
        for dep in deps:
            name = dep.__name__ if callable(dep) else dep
            graph.register_dependency(func.__name__, name)
        return func

    return add_dependency
