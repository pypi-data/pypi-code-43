# -*- coding: utf-8 -*-

import string
import random

letters = string.digits + string.ascii_letters


def get_password(num=10):
    """
    获取密码
    :param num: int 字符串长度 default 10
    :return: str
    """
    return "".join(random.sample(letters, num))


if __name__ == '__main__':
    print(get_password())
