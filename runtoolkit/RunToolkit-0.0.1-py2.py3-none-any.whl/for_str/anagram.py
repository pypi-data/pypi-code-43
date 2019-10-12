# -*- coding: utf-8 -*-
# @Time     : 2019/10/3 1:47
# @Author   : Run 
# @File     : anagram.py
# @Software : PyCharm


from collections import Counter, defaultdict
from typing import List


def check_anagram(str1: str, str2: str) -> bool:
    """
    LeetCode 242: Valid Anagram
    Given two strings str1 and str2 , write a function to determine if str2 is an anagram of str1.
    todo compare speeds
    """
    if len(str1) != len(str2):
        return False
    # return Counter(str1) == Counter(str2)  # method1
    # return sorted(str1) == sorted(str2)  # method2
    for c in set(str1):
        if str1.count(c) != str2.count(c):
            return False
    return True


def group_anagrams(strs: List[str]) -> List[List[str]]:
    """
    LeetCode 49: Group Anagrams
    Given an array of strings, group anagrams together.
    """
    str_map = {}
    res = []
    for s in strs:
        temp = ''.join(sorted(s))
        if temp not in str_map:
            str_map[temp] = len(res)
            res.append([s])
        else:
            res[str_map[temp]].append(s)
    return res


def find_anagrams(s: str, p: str) -> List[int]:
    """
    LeetCode 438: Find All Anagrams in a String
    Given a string s and a non-empty string p, find all the start indices of p's anagrams in s.
    solved by sliding window.
    """
    res = []
    l1, l2 = len(s), len(p)
    needs = Counter(p)
    window = defaultdict(int)
    left = right = 0
    while right < l1:
        c = s[right]
        if c not in needs:
            window.clear()
            left = right = right + 1
        else:
            window[c] += 1
            if right - left + 1 == l2:
                if window == needs:
                    res.append(left)
                window[s[left]] -= 1
                left += 1
            right += 1
    return res


if __name__ == "__main__":
    print(check_anagram("anagram", "nagaram"))
    print(check_anagram('rat', 'car'))
    print()

    print(group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"]))
    print()

    print(find_anagrams("cbaebabacd", "abc"))
    print(find_anagrams("abab", "ab"))
    print()