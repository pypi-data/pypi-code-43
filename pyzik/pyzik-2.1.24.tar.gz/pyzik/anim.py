# -*- coding: utf-8 -*-
"""
Created on Fri Aug  9 06:46:19 2019

@author: jittima
"""

import plotly.express as px
import pandas as pd
import numpy as np 

def anim(x,y_func,param_name='param',param_limit=(0.05,1,0.05),xlabel='x',ylabel='',mode='o',**d):
    ylabel = y_func.__name__ if ylabel == '' else ylabel
    param_i = float(param_limit[0])
    param_f = float(param_limit[1])
    dparam = float(param_limit[2])
    if int((param_f-param_i)/dparam)>100:
        dparam = (param_f-param_i)/100
    nb_param = int((param_f-param_i)/dparam)
    df,fd = pd.DataFrame({xlabel:[],ylabel:[],param_name:[]}),pd.DataFrame({xlabel:[],ylabel:[],param_name:[]})
    for p in np.linspace(param_i,param_f,nb_param):
        fd[ylabel] = y_func(p)
        fd[param_name] = p
        fd[xlabel] = x
        df=df.append(fd)
    if mode == 'o':
        return px.scatter(df,x=xlabel,y=ylabel,animation_frame=param_name,**d)
    else:
        return px.line(df,x=xlabel,y=ylabel,animation_frame=param_name,**d)
    