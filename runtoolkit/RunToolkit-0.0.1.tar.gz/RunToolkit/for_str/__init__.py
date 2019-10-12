# -*- coding: utf-8 -*-
# @Time     : 2019/10/3 1:45
# @Author   : Run 
# @File     : __init__.py.py
# @Software : PyCharm


import re
from typing import List
import math


def equal_split(s: str, width: int) -> List[str]:
    """
    Split the string, each split has length `width` except the last one.
    """
    num = int(math.ceil(len(s) / width))  # python3
    return [s[i * width: (i + 1) * width] for i in range(num)]


def split_to_words(s: str) -> List[str]:
    """
    Break the string into words.
    e.g.
        1. 'a b' -> ['a', 'b']
        2. 'a-b' -> ['a', 'b']
        3. 'a_b' -> ['a', 'b']
        4. 'AbcDef' -> ['Abc', 'Def']
    """
    return re.sub(r'(\s|_|-)+', ' ', re.sub('([A-Z]+)', r' \1', s)).split()


def check_brackets(s: str) -> bool:
    """
    LeetCode 20: Valid Parentheses
    check if brackets(and parentheses) come in pairs, besides, left should occur before right.
    """
    rights = {')', ']', '}'}
    lefts = {'(': ')', '[': ']', '{': '}'}
    l = []
    for i, c in enumerate(s):
        if c in lefts:
            l.append((i, c))
        elif c in rights:
            if len(l) == 0:
                print("redundant '{}' at position {}".format(c, i))
                return False
            i0, c0 = l.pop()
            if lefts[c0] != c:
                print("unmatched '{}' at position {} with '{}' at position {}".format(c0, i0, c, i))
                return False
    if len(l) > 0:
        print("redundant parentheses and their positions: {}".format(l))
        return False
    return True


def count_vowels(target_str: str) -> int:
    return len(re.findall('[aeiou]', target_str, re.IGNORECASE))


if __name__ == "__main__":
    print(equal_split("helloworld", 5))
    print(equal_split("helloworld.", 5))
    print()
    
    print(split_to_words('HelloWorld I_am-python'))
    print()

    print(check_brackets("{(a, b): {c, ...}, ...}"))
    print(check_brackets("{"))
    print(check_brackets("{)(}"))
    print()

    print(count_vowels('fooBAar'))
    print(count_vowels('gym'))
    print()