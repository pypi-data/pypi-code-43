# -*- coding: utf-8 -*-
"""

    Базовый класс для управления конфигурациями

"""
# модули проекта
from trivial_tools.files.json import json_config_load


class BaseConfig:
    """
    Базовый класс для хранения параметров
    """
    def __init__(self, **kwargs):
        """
        Автоматическая инициация
        """
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    def from_json(cls, file_name: str, config_name: str):
        """
        Загрузить настройки из json файла
        """
        parameters = json_config_load(file_name, config_name)
        instance = cls(**parameters)
        return instance
