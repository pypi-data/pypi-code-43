# -*- coding: utf-8 -*-
"""

    Простые инструменты для работы с JSON-RPC

"""
# встроенные модули
from typing import Dict, Callable


def method(container: Dict[str, Callable]) -> Callable:
    """
    Декоратор регистрации методов в JSON-RPC API
    """
    def wrapper(func: Callable) -> Callable:
        """
        Объёртка для создания замыкания для передачи container
        """
        container[func.__name__] = func
        return func
    return wrapper
