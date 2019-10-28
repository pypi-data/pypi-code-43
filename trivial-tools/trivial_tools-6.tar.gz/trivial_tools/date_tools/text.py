# -*- coding: utf-8 -*-
"""

    Инструменты обработки текстового представления дат

"""
# встроенные модули
from typing import Optional
from datetime import date, datetime


def parse_date(string: Optional[str]) -> Optional[date]:
    """
    Обработка даты (при возможности)
    """
    if string is not None:
        return datetime.strptime(string, '%Y-%m-%d').date()
    return None
