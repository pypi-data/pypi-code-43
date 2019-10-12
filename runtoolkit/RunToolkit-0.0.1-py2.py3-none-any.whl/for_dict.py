# -*- coding: utf-8 -*-
# @Time     : 2019/10/2 23:43
# @Author   : Run 
# @File     : for_dict.py
# @Software : PyCharm


from collections import ChainMap


def merge_dicts(*args):
    """

    :param args: d1, d2, ...
    :return:
    :Notes: dicts: d1, d2
        1. d1.update(d2), d1 changed
        2. {**d1, **d2}
        3. collections.ChainMap(d2, d1), share space with d1 and d2
        4. dict(collections.ChainMap(d2, d1))

        * cost time: 3 << 1 < 2 < 4
        * If d1 >> d2, d1.update(d2) faster than d2.update(d1), but the results might be different.
    """
    # return ChainMap(*args[::-1])
    return dict(ChainMap(*args[::-1]))


if __name__ == "__main__":
    d1 = {'a': 1, 'b': 2}
    d2 = {'a': 10, 'c': 3}
    print(merge_dicts(d1, d2))
    print(d1, d2)
    print()