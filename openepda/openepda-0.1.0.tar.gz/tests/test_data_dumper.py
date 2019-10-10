# -*- coding: utf-8 -*-
""" test_data_dumper.py

This script tests the OpenEpdaDataDumper class.

Author: Dima Pustakhod

Changelog
---------
2019.07.19
    Initial version

"""
import logging
import numpy as np
import matplotlib.pyplot as plt
from openepda import OpenEpdaDataDumper

fname_02 = '_output_data/openepda_data_v.0.2.csv'
fname_03 = '_output_data/openepda_data_v.0.3.csv'

N = 1000000

list3 = ['text'] * N
list1 = list(range(N))
array1 = np.linspace(0, 50, num=len(list1))

data = {'string1': 'example1',  # string
        'string2': 'example2',  # string
        'integer1': 1000,  # int
        'integer2': -500,  # int
        'float1': 1.10,  # float
        'float2': 0.1e-18,  # float
        'dict1': {
                'd1s1': 'd1v1', 'd1s2': 'd1v1', 'd1i1': 1000, 'd1i2': -500,
                'd1f1': 1.10, 'd1f2': 0.1e-18},  # dict
        'dict2': {
               'd2s1': 'v1', 'd2s2': 'v1', 'd2i1': 1000, 'd2i2': -500,
               'd2f1': 1.10, 'd2f2': 0.1e-18},  # dict
        # 'list': list3,
        'l1,3': list1,  # list len1
        'l2': array1,  # np array len1
        # 'l1': 1.10,  # list len2
        # 'l2': 0.1e-18,  # list len2
        }

w = OpenEpdaDataDumper()
# w._l.setLevel(logging.DEBUG)

with open(fname_02, 'w') as f:
    w.write(f, **data)

with open(fname_03, 'w') as f:
    w.write_1(f, **data)
