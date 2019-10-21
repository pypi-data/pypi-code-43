#!/usr/bin/env python
'''
time_machine
Created by Seria at 23/12/2018 8:34 PM
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

def TimeMachine(config=None, ckpt_path=None, ckpt_scope=None,
                 save_path=None, save_scope=None, thawed_path=None, frozen_path=None):
    if config is None:
        param = {'ckpt_path': ckpt_path, 'ckpt_scope': ckpt_scope,
                      'save_path': save_path, 'save_scope': save_scope,
                      'thawed_path': thawed_path, 'frozen_path': frozen_path}
    else:
        config['ckpt_path'] = config.get('ckpt_path', ckpt_path)
        config['ckpt_scope'] = config.get('ckpt_scope', ckpt_scope)
        config['save_path'] = config.get('save_path', save_path)
        config['save_scope'] = config.get('save_scope', save_scope)
        config['thawed_path'] = config.get('thawed_path', thawed_path)
        config['frozen_path'] = config.get('frozen_path', frozen_path)
        param = config

    core = Law.CORE.upper()
    if core == 'TENSORFLOW':
        from .time_machine_tf import TimeMachineTF
        return TimeMachineTF(param)
    elif core == 'MXNET':
        from .time_machine_mx import TimeMachineMX
        return TimeMachineMX(param)
    else:
        raise ValueError('NEBULAE ERROR ⨷ %s is an unsupported core.' % core)