# -*- coding: utf-8 -*-
# @Time     : 2019/10/3 22:02
# @Author   : Run 
# @File     : numbers.py
# @Software : PyCharm


def fibonacci(num: 'int > 0') -> list:
    res = [1, 1]
    while len(res) <= num:
        res.append(res[-2] + res[-1])

    return res


if __name__ == "__main__":
    print(fibonacci(10))
    print()