#!/usr/bin/env python
# -*- coding: utf-8 -*-
# from pprint import pprint
# from deepdiff import DeepDiff
# from decimal import Decimal

# from deepdiff.helper import number_to_string


# def custom_number_to_string(number, *args, **kwargs):
#     number = 100 if number < 100 else number
#     return number_to_string(number, *args, **kwargs)

# t1 = [10, 12, 100000]
# t2 = [20, 22, 100000]

# ddiff = DeepDiff(t1, t2, significant_digits=3, number_format_notation="e",
#                          number_to_string_func=custom_number_to_string)

# print(ddiff)

from collections import deque


def permute(items, current):
    current_set = set(current)
    result = []
    for item in items:
        if item not in current_set:
            result.append(current[:] + [item])
    return result


def main():
    ITEMS = [1, 2, 3, 4]

    queue = deque()
    queue.append([])

    while queue:
        current = queue.popleft()
        new_items = permute(items=ITEMS, current=current)
        if new_items:
            queue.extend(new_items)
        else:
            queue.appendleft(current)
            break

    print(queue)


if __name__ == '__main__':
    main()
