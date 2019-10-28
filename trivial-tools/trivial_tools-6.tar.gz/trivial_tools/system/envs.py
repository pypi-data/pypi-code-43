# -*- coding: utf-8 -*-
"""

    Работа с переменными среды

"""
# встроенные модули
import os
import sys

# сторонние модули
from loguru import logger


def get_env_variable(key: str) -> str:
    """
    Получить переменную окружения
    """
    value = os.getenv(key)

    if value is None:
        logger.critical(f'Не установлена переменная окружения "{key}"')
        sys.exit(1)

    return value


def get_path_from_env(key: str) -> str:
    """
    Обратиться к переменным окружения и получить сохранённый путь
    """
    path = get_env_variable(key)

    if not os.path.exists(path):
        logger.critical(f'Не найден каталог по пути "{path}"')
        sys.exit(1)

    return path


def get_full_path(key: str, *args: str) -> str:
    """
    Получить путь к каталогу по ключу переменной среды
    При наличии суффикса мы добавляем его в путь как подкаталог
    """
    path = get_path_from_env(key)
    if args:
        path = os.path.join(path, *args)
    return path
