#!/usr/bin/env python
# -*- coding: utf-8 -*-

import string
import hashlib

CHINESE_PUNCTUATION = u'，。！￥？——；“”：《》（）'
ENGLISH_PUNCTUATION = string.punctuation


def is_chinese_punctuation(char):
    return char in CHINESE_PUNCTUATION


def remove_chinese_punctuation(s):
    ret = u''
    for c in s:
        if not is_chinese_punctuation(c):
            ret += c
    return ret


def is_english_punctuation(char):
    return char in ENGLISH_PUNCTUATION


def remove_english_punctuation(s):
    ret = u''
    for c in s:
        if not is_english_punctuation(c):
            ret += c
    return ret


def is_pure_english(s):
    yes = True
    for e in s:
        if ord(e) > 127:
            yes = False
            break
    if yes:
        return True
    else:
        return False


def english_words(s):
    return ''.join([e for e in s if ord(e) <= 127]).strip()


def common_suffix(s1, s2):
    """
    get common suffix of two string
    @param s1: first string
    @param s2: second string
    @return: the common suffix

    """
    min_len = min(len(s1), len(s2))
    if min_len == 0:
        return ''
    for i in range(-1, -min_len - 1, -1):
        if s1[i] != s2[i]:
            break
    if i == -1:
        return ''
    elif i == -min_len:
        return s1[i:]
    else:
        return s1[i + 1:]


def md5(s):
    return hashlib.md5(s.encode('utf-8')).hexdigest()


def test():
    def print_list(lst):
        for e in lst:
            print(e.encode('utf-8'))


if __name__ == '__main__':
    test()
