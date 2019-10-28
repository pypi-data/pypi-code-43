# -*- coding: utf-8 -*-
"""

    Инструменты для работы с именами в АПК "ПАУК"

"""
# встроенные модули
import re
from contextlib import suppress

# шаблон имени паука
from datetime import date
from typing import Optional

# шаблон для проверки spider_id
SPIDER_ID_PATTERN = re.compile(r'^\d{2}-\d{5}$')

# шаблон для извлечения даты из имени CSV файла
CSV_DATE_PATTERN = re.compile(r'\d{2}-\d{5}_(\d{4})-(\d{2})-(\d{2}).csv$')

# шаблон для извлечения spider_id из имени CSV файла
CSV_ID_PATTERN = re.compile(r'(\d{2}-\d{5})_\d{4}-\d{2}-\d{2}.csv$')


def spider_sorter(key: str) -> int:
    """
    Ключевая функция для сортировки пауков. Сортирует по номеру паука без учёта серии

    >>> spider_sorter('02-00241')
    241
    """
    result = -1
    if isinstance(key, str) and len(key) == 8:
        with suppress:
            result = int(key[3:])
    return result


def is_spider_id(string: str, pattern: re.Pattern = SPIDER_ID_PATTERN) -> bool:
    """
    Проверить, является ли строка валидным id паука

    >>> is_spider_id('02-00125')
    True
    >>> is_spider_id('asd kjk')
    False
    """
    result = pattern.match(string) is not None
    return result


def date_from_spider_csv(filename: str, pattern: re.Pattern = CSV_DATE_PATTERN) -> Optional[date]:
    """
    Извлечь дату из имени CSV файла паука

    >>> date_from_spider_csv('02-00183_2019-07-24.csv')
    datetime.date(2019, 7, 24)
    """
    data = pattern.search(filename)
    if data:
        year, month, day = data.groups()
        spider_date = date(int(year), int(month), int(day))
        return spider_date
    return None


def spider_id_from_spider_csv(filename: str, pattern: re.Pattern = CSV_ID_PATTERN) -> Optional[str]:
    """
    Извлечь id паука из имени файла

    >>> spider_id_from_spider_csv('02-00183_2019-07-24.csv')
    '02-00183'

    >>> spider_id_from_spider_csv('02-00183_201s9-07-24.csv')

    """
    spider_id = pattern.search(filename)
    if spider_id:
        spider_id = spider_id.group(1)
        return spider_id
    return None
