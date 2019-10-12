# -*- coding: utf-8 -*-
# @Time     : 2019/10/11 16:02
# @Author   : Run 
# @File     : interval.py
# @Software : PyCharm

from typing import List


def list2ranges(nums: List[int]):
    """
    LeetCode 228: Summary Ranges
    Given a sorted integer array without duplicates, return the summary of its ranges(continuous int).
    Examples:
        1. [1] -> [[1, 1]]
        2. [0, 1, 2, 4, 5, 7] -> [[0, 2], [4, 5], [7, 7]]
        3. [0, 2, 3, 4, 6, 8, 9, 10, 11] -> [[0, 0], [2, 4], [6, 6], [8, 11]]
    :param nums: sorted int list without duplicates
    :return:
    """
    l = len(nums)
    if l == 0:
        return []
    elif l == 1:
        return [nums * 2]

    start = end = 0
    res = []
    while end < l:
        if end + 1 < l and nums[end + 1] == nums[end] + 1:
            end += 1
        else:
            res.append([nums[start], nums[end]])
            start = end = end + 1
    return res


if __name__ == '__main__':
    print(list2ranges([1]))
    print(list2ranges([0, 1, 2, 4, 5, 7]))
    print(list2ranges([0, 2, 3, 4, 6, 8, 9, 10, 11]))
    print()