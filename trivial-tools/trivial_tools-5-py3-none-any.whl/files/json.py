# -*- coding: utf-8 -*-
"""

    Инструменты обработки JSON файлов

"""
# встроенные модули
import os
import sys
import json
from typing import Dict, Any

# сторонние модули
from loguru import logger


def json_config_load(file_name: str, config_name: str) -> Dict[str, Any]:
    """
    Открыть указанный файл и прочитать его содержимое
    """
    path = os.path.join(os.getcwd(), file_name)
    try:
        with open(path, mode='r', encoding='utf-8') as file:
            data = json.load(file)
            config_data = data[config_name]
            return config_data

    except FileNotFoundError:
        logger.critical(f'Не найден файл конфигурации: "{path}"')

    except KeyError:
        logger.critical(f'Не удалось загрузить конфигурацию "{config_name}" из файла: "{path}"')

    sys.exit(1)
