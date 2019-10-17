# -*- coding: utf-8 -*-

def add_sum(a):
    '''
    计算从1+到a
    :param a:
    :return:
    '''
    res = False
    if type(a) == int:
        sum = 0
        for i in range(a + 1):  # 实际遍历到n
            sum += i
        res = True
    else:
        sum = '{0}不是整型，无法计算'.format(a)
    return res, sum
