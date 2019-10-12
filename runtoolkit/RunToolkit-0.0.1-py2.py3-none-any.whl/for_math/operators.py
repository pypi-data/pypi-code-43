# -*- coding: utf-8 -*-
# @Time     : 2019/10/3 22:02
# @Author   : Run 
# @File     : operators.py
# @Software : PyCharm


"""
Notes:
    1. np.math == scipy.math == math
"""


from typing import List
from functools import reduce
import math
from RunToolkit.for_list import flatten_iterable


def clamp_number(num, a, b):
    """
    Clamps num within the inclusive range specified by the boundary values a and b.
    If num falls within the range, return itself. Otherwise, return the nearest number in the range.
    """
    return max(min(num, max(a, b)), min(a, b))


def digitize(num: int) -> List[int]:
    """
    Converts a number to a list of digits.
    """
    return list(map(int, str(abs(num))))


def gcd(*args) -> int:
    """
    Calculates the greatest common divisor of two or more numbers.
    by `math.gcd`
    Algorithms:
        1. 辗转相除法，也叫欧几里德算法。
        2. 更相减损法，也叫更相减损术，出自《九章算术》。
    """
    numbers = flatten_iterable(args)
    return reduce(math.gcd, numbers)


def lcm(*args) -> int:
    """
    Calculates the least common multiple of two or more numbers.
    :param args:
    :return:
    """
    numbers = flatten_iterable(args)
    return reduce(lambda x, y: x * y // math.gcd(x, y), numbers)


# def factorial(num: int) -> int:
#     """
#     math.factorial
#     :param num: non-negative integer
#     :return:
#     """
#     # return 1 if num == 0 else num * factorial(num - 1)  # recursive inefficient
#     return reduce(lambda x, y: x * y, range(1, num + 1))


if __name__ == "__main__":
    print(clamp_number(2, 1, 3))
    print(clamp_number(2, 3, 5))
    print(clamp_number(1, -1, -5))
    print()

    print(digitize(12345))
    print(digitize(-321))
    print()

    print(gcd([12, 18, 24]))
    print(gcd(12, 18, 24))
    print()

    print(lcm(12, 7))
    print(lcm([1, 3, 4], 5))
    print()

    # print(factorial(5))
    # print()
