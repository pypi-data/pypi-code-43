#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: misiak
"""

from scipy import stats
import math as m
import json

def mcmc_config(filepath, param_opt):
    
    ndim = len(param_opt)
    
    config = dict()
    
    config['Data'] = {
            'directory': '/home/misiak/Data/data_run59',
            'run': 'ti04l001',
            'detector': 'RED71',         
    }
    
    config['Parameters'] = {
            'label': ['p{}'.format(i) for i in range(ndim)],
            'pinit': list(param_opt),
    }
    
    # by default, normal distribution centered in pinit
    # and with a relative sigma of 0.1
    config['Prior'] = {
            'distribution': ['norm',]*ndim,
            'arg1' : list(param_opt),
            'arg2' : [0.1*p for p in param_opt],
    }
    
    config['Model'] = {
            'type': 'unknown',
            'subtype': None,
            'configpath': None,
    }
    
    with open(filepath, 'w') as configfile:
        json.dump(config, configfile, indent=4)
        
        

def logpdf(x, arg1, arg2, dist='norm'):
    dist = dist.lower()
    if dist == 'norm':
        lnpdf = stats.norm.logpdf(x, loc=arg1, scale=arg2)
    elif dist == 'lognorm':
        lnpdf = stats.lognorm.logpdf(x, s=m.log(10)*arg2, loc=0, scale=arg1)
    elif dist == 'uniform':
        lnpdf = stats.uniform.logpdf(x, loc=arg1, scale=arg2)  
    return lnpdf

def rvs(arg1, arg2, dist='norm', **kwargs):
    dist = dist.lower()
    if dist == 'norm':
        rvs = stats.norm.rvs(loc=arg1, scale=arg2, **kwargs)
    elif dist == 'lognorm':
        rvs = stats.lognorm.rvs(s=m.log(10)*arg2, loc=0, scale=arg1, **kwargs)
    elif dist == 'uniform':
        rvs = stats.uniform.rvs(loc=arg1, scale=arg2, **kwargs)  
    return rvs
#
#def lnprior_list(theta):
#    lnprior_list = list()
#    for p, dist, arg1, arg2 in zip(theta, prior_dist, prior_arg1, prior_arg2):
#        lnpdf = logpdf(p, arg1, arg2, dist)
#        lnprior_list.append(lnpdf)
#    return lnprior_list
#
#def lnprior(theta):
#    return np.sum(lnprior_list(theta))
