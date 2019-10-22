#!/usr/bin/env python
'''
navigator_tf
Created by Seria at 04/02/2019 4:48 PM
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
from mxnet import nd, autograd
import numpy as np
import time
from copy import deepcopy
from collections import defaultdict
import os
from ..toolkit import parseConfig, recordConfig
from .navigator import Stage



class NavigatorMX(object):
    roman_numeral = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X']
    def __init__(self, dashboard, time_machine, fuel_depot, spacecraft):
        self.db = dashboard
        self.tm = time_machine
        self.fd = fuel_depot
        self.sc = spacecraft
        if spacecraft is None:
            self.flag_empty = True
        else:
            self.flag_empty = False
        self.propellants = defaultdict(list)
        self.epoch = 0
        self.mile = 0
        self.mpe = 0
        self.stage = 'UNKNOWN'
        self.feed(Stage.START, time_machine._setParams, external=False, spacecraft=spacecraft)
        self.feed(Stage.START, spacecraft._finalize, external=False, first_call=True) # finalize the architecture
        self.feed(Stage.RUN, self.sc._finalize, external=False, first_call=False)

    def feed(self, stage, propellant, position=None, external=True, **kwargs):
        if external:
            kwargs['nvg'] = self
        if isinstance(position, int):
            quantity = len(self.propellants[stage])
            if position < quantity:
                self.propellants[stage][position] = (propellant, kwargs)
            else:
                for p in range(quantity, position):
                    self.propellants[stage].append((None, 'False'))
        self.propellants[stage].append((propellant, kwargs))

    def _airDrop(self, stage, n, **kwargs):
        # kwargs.update(self.propellants[stage][n][2])
        self.propellants[stage][n] = self.propellants[stage][n][0:2] + (kwargs,)

    def _triggerStage(self, curr_stage):
        self.stage = curr_stage
        for ppl, kwargs in self.propellants[curr_stage]:
            ppl(**kwargs)

    def cruise(self, exit, feedback=None, thruster=None, **entrance):
        '''
        exit: which node to output
        feedback: loss name
        thruster: optimizer name
        entrance: input (formated as keyword arguments)
        '''
        ent = []
        bs = -1
        for k in entrance.keys():
            if isinstance(entrance[k], np.ndarray):
                ent.append(nd.array(entrance[k]).as_in_context(self.sc.engine.context))
                if bs < 0:
                    bs = entrance[k].shape[0]

        if not(feedback is None or feedback in exit):
            exit = exit + (feedback,)

        if thruster is None:
            self.sc.out_node = exit
            with autograd.predict_mode():
                ext = self.sc(*tuple(ent))
        else:
            self.sc.out_node = exit + (thruster,)
            with autograd.record():
                ext = self.sc(*tuple(ent))
            ext[feedback].backward()
            ext[thruster].step(bs)

        ret = {}
        for key in exit:
            if ext[key].size == 1:
                ret[key] = ext[key].asscalar()
            else:
                ret[key] = ext[key].asnumpy()
        return ret

    def execute(self):
        root_stage = self.stage
        for stg in Stage.groups[root_stage]:
            self._triggerStage(stg)
        self.stage = root_stage

    def _scribe(self):
        if self.flag_empty:
            bp_cfg = {}
        else:
            bp_cfg = self.sc.blueprint.param
        config = {'NG': self.sc.engine.param, 'TM': self.tm.param,
                  'FD': {}, 'DB': self.db.param, 'BP': bp_cfg}
        ft = self.fd.tanks
        for k in ft.keys():
            config['FD'][k] = ft[k].param

        temp_config = os.path.join(os.getcwd(), 'temp_config.json')
        if os.path.exists(temp_config):
            hyper_param = parseConfig(temp_config)
            config['SC'] = hyper_param
            if not os.path.exists(self.tm.param['save_path']):
                os.mkdir(self.tm.param['save_path'])
            recordConfig(os.path.join(self.tm.param['save_path'], 'config.json'), config)
            os.remove(os.path.join(os.getcwd(), 'temp_config.json'))

    def log(self, gauge=True, tachograph=True, blueprint=True, setting=True):
        self.feed(Stage.END, self.db._log, external=False, gauge=gauge, tachograph=tachograph)

        if blueprint:
            self.sc.blueprint._await = True
            self.sc.blueprint._path = self.db.param['log_path']
        if setting:
            self.feed(Stage.START, self._scribe, external=False)

    def launch(self):
        try:
            print('+' + 35 * '-' + '+')
            print('| The Spacecraft is being launched. |')
            print('+' + 35 * '-' + '+')
            self._triggerStage(Stage.START)
            self._triggerStage(Stage.RUN)
            self._triggerStage(Stage.END)
            print('+' + 44 * '-' + '+')
            print('| The Spacecraft has arrived at destination. |')
            print('+' + 44 * '-' + '+')

        except BaseException as e:
            if Stage.BREAK_DOWN in self.propellants:
                self._triggerStage(Stage.BREAK_DOWN)
            else:
                raise e