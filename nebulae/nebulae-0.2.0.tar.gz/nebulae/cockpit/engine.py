#!/usr/bin/env python
'''
engine
Created by Seria at 23/11/2018 2:36 PM
Email: zzqsummerai@yeah.net

                    _ooOoo_
                  o888888888o
                 o88`_ . _`88o
                 (|  0   0  |)
                 O \   。   / O
              _____/`-----‘\_____
            .’   \||  _ _  ||/   `.
            |  _ |||   |   ||| _  |
            |  |  \\       //  |  |
            |  |    \-----/    |  |
             \ .\ ___/- -\___ /. /
         ,--- /   ___\<|>/___   \ ---,
         | |:    \    \ /    /    :| |
         `\--\_    -. ___ .-    _/--/‘
   ===========  \__  NOBUG  __/  ===========
   
'''
# -*- coding:utf-8 -*-
from ..law import Law

def Engine(config=None, device=None, ngpus=1, least_mem=2048,
           available_gpus=(), gpu_mem_fraction=0.9, if_conserve=True):
    if config is None:
        param = {'device': device, 'ngpus': ngpus, 'least_mem': least_mem,
                 'available_gpus': available_gpus, 'gpu_mem_fraction': gpu_mem_fraction, 'if_conserve': if_conserve}
    else:
        config['ngpus'] = config.get('ngpus', ngpus)
        config['least_mem'] = config.get('least_mem', least_mem)
        config['available_gpus'] = config.get('available_gpus', available_gpus)
        config['gpu_mem_fraction'] = config.get('gpu_mem_fraction', gpu_mem_fraction)
        config['if_conserve'] = config.get('if_conserve', if_conserve)
        param = config
    if not isinstance(param['ngpus'], int):
        raise TypeError('NEBULAE ERROR ⨷ number of gpus must be an integer.')
    if param['gpu_mem_fraction']<=0 or param['gpu_mem_fraction']>1:
        raise ValueError('NEBULAE ERROR ⨷ gpu memory fraction should belong to (0, 1].')

    core = Law.CORE.upper()
    if core == 'TENSORFLOW':
        from .engine_tf import EngineTF
        return EngineTF(param)
    elif core == 'MXNET':
        from .engine_mx import EngineMX
        return EngineMX(param)
    else:
        raise ValueError('NEBULAE ERROR ⨷ %s is an unsupported core.' % core)