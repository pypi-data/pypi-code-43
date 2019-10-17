#!/usr/bin/env python
# encoding=utf-8

import numpy as np
from scipy import stats
import math

def mw_utest(a,b,effect_size_type = 'd'):
    p_value = stats.mannwhitneyu(a,b)[1]
    pool_std = math.sqrt((np.var(a)+np.var(b))/2)
    a_mean = np.mean(a)
    b_mean = np.mean(b)
    d_size = (a_mean-b_mean)/pool_std
    if (effect_size_type=='d'):
        final_size = d_size
    elif(effect_size_type=='r'):
        final_size = d_size/math.sqrt(d_size**2+4) 
    return final_size, p_value