#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

def get_padded_int(integer):
    integer_string = str(integer)
    zeros = 16 - len(integer_string)
    if zeros < 0:
        raise ValueError
    integer_string = f"{zeros * '0'}{integer_string}"
    return integer_string

def dump_dict(input_dict):
    return json.dumps(input_dict, separators=(',', ':'), ensure_ascii=False)

def dump_pretty_dict(input_dict):
    return json.dumps(input_dict, indent=4, ensure_ascii=False)