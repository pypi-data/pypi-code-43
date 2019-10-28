from enum import Enum, unique


@unique
class EnumMarket(Enum):
    股票 = 0,
    期货 = 1,
    股票期权 = 2,
    期货期权 = 3,
    指数 = 4,
    外盘 = 5,
    现货 = 6
