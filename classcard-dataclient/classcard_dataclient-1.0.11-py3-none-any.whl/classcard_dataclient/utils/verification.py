# -*- coding: utf-8 -*-
"""
Created By Murray(m18527) on 2019/9/6 17:28
"""
from __future__ import absolute_import, unicode_literals


def _verify_dict(d_dict, required_fields):
    if not isinstance(d_dict, dict):
        return False
    for field in required_fields:
        if d_dict.get(field):
            return True
    return False


def _verify_dict_list(d_list, required_fields):
    if not isinstance(d_list, list):
        return False
    is_valid = True
    for d in d_list:
        if not _verify_dict(d, required_fields):
            is_valid = False
            break
    return is_valid


def verify_teacher(d_list):
    required_fields = ['school', 'name', 'number', 'password', 'gender', 'email', 'phone']
    return _verify_dict_list(d_list, required_fields)


def verify_student(d_list):
    required_fields = ['school', 'name', 'number', 'password', 'gender', 'email', 'phone']
    return _verify_dict_list(d_list, required_fields)


def verify_section(d_list):
    required_fields = ['school', 'name', 'number', 'grade']
    return _verify_dict_list(d_list, required_fields)


def verify_classroom(d_list):
    required_fields = ['school', 'name', 'num']
    return _verify_dict_list(d_list, required_fields)
