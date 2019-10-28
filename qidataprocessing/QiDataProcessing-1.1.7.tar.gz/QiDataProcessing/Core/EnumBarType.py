from enum import Enum, unique


@unique
class EnumBarType(Enum):
    tick = 0,
    second = 1,
    minute = 2,
    hour = 3,
    day = 4,
    week = 5,
    month = 6,
    year = 7
