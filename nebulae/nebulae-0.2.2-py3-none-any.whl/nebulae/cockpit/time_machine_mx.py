#!/usr/bin/env python
'''
time_machine_tf
Created by Seria at 04/02/2019 4:35 PM
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
from mxnet.gluon import nn, SymbolBlock, HybridBlock
import os
from glob import glob


class TimeMachineMX(object):
    def __init__(self, param):
        '''
        Time Machine saves current states or restores saved states
        '''
        self.param = param



    def _setParams(self, spacecraft):
        self.counter = 0
        self.sc = spacecraft

    def backTo(self, frozen=False, ins=None, outs=None):
        if self.param['ckpt_path'] is None:
            raise Exception('NEBULAE ERROR ⨷ anchor location is not provided.')
        else:
            # spot = SymbolBlock.imports(self.param['ckpt_path'] + '.json', self.sc.in_node,
            #                            self.param['ckpt_path'] + '.params')
            architecture = glob(os.path.join(self.param['ckpt_path'],'*.params'))
            max_saved = -1
            for arch in architecture:
                saved_no = int(arch.split('.')[0].split('-')[-1])
                if saved_no > max_saved:
                    moment = arch
                    max_saved = saved_no
            if frozen:
                self.sc.load_parameters(moment, self.sc.engine.context)
            else:
                missing = True
                extra = True
                self.sc.load_parameters(moment, self.sc.engine.context, allow_missing=missing, ignore_extra=extra)
            print('+' + ((10 + len(self.param['ckpt_path'])) * '-') + '+')
            print('| Back to \033[1;34m%s\033[0m |' % self.param['ckpt_path'])
            print('+' + ((10 + len(self.param['ckpt_path'])) * '-') + '+')

    def dropAnchor(self, frozen=False, anchor=None):
        if self.param['save_path'] is None:
            raise Exception('NEBULAE ERROR ⨷ there is nowhere to drop anchor.')
        else:
            if self.sc.scope:
                scope = self.sc.scope[:-1]
            else:
                scope = 'ckpt'
            if frozen:
                self.sc.export(os.path.join(self.param['save_path'], scope), epoch=self.counter)
            self.sc.save_parameters(os.path.join(self.param['save_path'], '%s-%d.params'%(scope, self.counter)))
            self.counter += 1
            print('| Anchor is dropped at \033[1;34m%s\033[0m |' % self.param['save_path'])