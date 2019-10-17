from enum import Enum, unique


@unique
class EnumFutureType(Enum):
    Normal = 0
    Index = 1,
    Reference = 2
