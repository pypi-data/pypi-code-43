# -*- coding: utf-8 -*-
""" test_phiola_data_writer.py

This script tests the PhiolaDataWiter class.

Author: Dima Pustakhod

Changelog
---------
2018.05.15
    Initial version

"""
import logging
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from openepda import OpenEpdaDataLoader

fname_02 = '_data/openepda_data_v.0.2.csv'
fname_03 = '_data/openepda_data_v.0.3.csv'

w = OpenEpdaDataLoader()
# w._l.setLevel(logging.DEBUG)

data_02 = w.read_file(fname_02)
data_03 = w.read_file_03(fname_03)

print(data_02.keys())
print(data_03.keys())


data_02 = pd.read_csv(fname_02, header=23)
data_03 = pd.read_csv(fname_03, header=23)
