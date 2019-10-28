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

    def __str__(self):
        """
        Текстовое представление
        """
        name = type(self).__name__

        longest = 1
        fields = []

        for field_name in vars(self):
            value = getattr(self, field_name)
            fields.append((field_name, value))
            longest = max(longest, len(field_name))

        result = [f'{name}(']
        for i, (field_name, value) in enumerate(fields, start=1):
            if isinstance(value, (list, tuple)) and value:
                result.append(
                    ('\t{0:02d}. {1:' + str(longest) + '} = [').format(i, field_name)
                )
                for sub_element in value:
                    result.append(f'\t        ' + ' ' * longest * 1 + f'{sub_element},')
                result.append(f'\t       ' + ' ' * longest * 1 + ']')
            else:
                result.append(
                    ('\t{0:02d}. {1:' + str(longest) + '} = {2}').format(i, field_name, value)
                )
        result.append(')')
        return '\n'.join(result)

    def __repr__(self):
        """
        Текстовое представление
        """
        name = type(self).__name__
        result = []
        for field_name in vars(self):
            value = getattr(self, field_name)
            result.append(f'{field_name}={value!r}')
        return f'{name}(' + ', '.join(result) + ')'
