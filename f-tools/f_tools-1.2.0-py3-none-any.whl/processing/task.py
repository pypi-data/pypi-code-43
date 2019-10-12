from threading import Thread
from typing import Any, Callable


class Task(Thread):
    """ Task class
    Thread class abstraction
    """
    def __init__(self, target: Callable, *args: Any, **kwargs):
        Thread.__init__(self, target=target, args=args, kwargs=kwargs)
