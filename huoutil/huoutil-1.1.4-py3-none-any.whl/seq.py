#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest


def longest_range(index_list):
    """
    select longest index range
        eg. [1, 0, 1, 1, 1] ==> (2, 5)
    @param index_list: list, element is 0 or 1
    @return: a tuple (a, b). a is the range begin, and b is the range off end.
    """
    range_list = []
    begin = 0
    for i in range(len(index_list) - 1):
        if index_list[i] == 0 and index_list[i + 1] == 1:
            begin = i + 1
        if index_list[i] == 1 and index_list[i + 1] == 0:
            range_list.append((begin, i + 1))
    if index_list[-1] == 1:
        range_list.append((begin, len(index_list)))
    if range_list:
        range_list.sort(key=lambda x: x[1] - x[0], reverse=True)
        return range_list[0]
    else:
        return None


class HuoListTest(unittest.TestCase):
    def test_longest_range(self):
        self.assertEqual(longest_range([1, 0, 1, 1, 1]), (2, 5))
        self.assertEqual(longest_range([1, 1, 1, 1, 1]), (0, 5))
        self.assertEqual(longest_range([0, 0, 1, 1, 1]), (2, 5))
        self.assertEqual(longest_range([1, 1, 1, 0, 0]), (0, 3))
        self.assertEqual(longest_range([1, 1, 1, 0, 0, 1, 1, 1]), (0, 3))
        self.assertEqual(longest_range([0, 0, 0, 0, 0]), None)
        self.assertEqual(longest_range([0, 1, 1, 1, 1, 0, 1, 1, 1, 0, 0]), (1, 5))


if __name__ == '__main__':
    unittest.main()
