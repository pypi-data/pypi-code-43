from functools import partial
from time import time
from datetime import datetime
from random import randint

from .randomize import random_datetime as r_dtime, \
    random_float as r_float

__all__ = ['random_unix_time', 'random_dt_now', 'random_positive_float',
           'random_tinyint', 'random_smallint', 'random_mediumint',
           'random_int', 'random_bigint']


def random_unix_time():
    """
    return a float value from 0 to the current time
    with 7 digit after coma
     """
    return round(r_float(0, time()), 7)


def random_positive_float(max_value: [int, float]) -> float:
    """
    :param max_value: maximum value
    :return: random positive float with 14 digit after come
    """
    return r_float(0, max_value)


# return a datetime object from 1.1.1980 to the current datetime without timezone
random_dt_now = partial(r_dtime, datetime(1980, 1, 1, 0, 0, 0, 0), datetime.now())


"""
:return random digit from table Minimum to table Maximum
Type        Bytes    Minimum       Maximum
___________________________________________
TINYINT	    1	    -128		   127
SMALLINT	2	    -32768		   32767
MEDIUMINT	3	    -8388608	   8388607
INT	        4	    -2147483648	   2147483647
BIGINT	    8	    -2**63		   (2**63)-1
"""
random_tinyint = partial(randint, 0, 255)
random_smallint = partial(randint, -32768, 32767)
random_mediumint = partial(randint, -8388608, 8388607)
random_int = partial(randint, -2147483648, 2147483647)
random_bigint = partial(randint, -9223372036854775808, 9223372036854775807)
