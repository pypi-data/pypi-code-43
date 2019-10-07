#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  4 10:38:11 2018

@author: jamie
"""
import pandas as pd
import pkg_resources

def load_data():
    resource_path = '/'.join(('data','movies.zip'))
    return pd.read_csv(pkg_resources.resource_filename(__name__, resource_path) )
