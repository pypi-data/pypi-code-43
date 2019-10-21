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
import tensorflow as tf
import time
from copy import deepcopy
from collections import defaultdict
import os
from ..toolkit import parseConfig, recordConfig
from .navigator import Stage

# class NavigatorTF(object):
#     roman_numeral = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X']
#     def __init__(self, dashboard, time_machine, fuel_depot, spacecraft):
#         config = {'NG': spacecraft.engine.param, 'TM':time_machine.param,
#                   'FD': {}, 'DB': dashboard.param, 'BP': spacecraft.blueprint.param}
#         ft = fuel_depot.tanks
#         for k in ft.keys():
#             config['FD'][k] = ft[k].param
#
#         self.propellants = defaultdict(list)
#         self.epoch = 0
#         self.mile = 0
#         self.mpe = 0
#         self.batch = {}
#         self.destination = {}
#         self.macro_stage = ''
#         # start a session
#         self.sess = tf.Session(config=spacecraft.engine.config_proto)
#         self.time_machine = time_machine
#         self.fuel_depot = fuel_depot
#         self.spacecraft = spacecraft
#         self.dashboard = dashboard
#         self.feed(Stage.START, self.time_machine._setParams,
#                             sess=self.sess, mile=self.spacecraft.layout['_MEDIA'],
#                             scope=self.spacecraft.scope, config=config)
#         self.feed(Stage.START, self.time_machine.backTo)
#
#     def feed(self, stage, propellant, position=None, condition='True', **kwargs):
#         if isinstance(position, int):
#             quantity = len(self.propellants[stage])
#             if position < quantity:
#                 self.propellants[stage][position] = (propellant, condition, kwargs)
#             else:
#                 for p in range(quantity, position):
#                     self.propellants[stage].append((None, 'False'))
#         self.propellants[stage].append((propellant, condition, kwargs))
#
#     def _airDrop(self, stage, n, **kwargs):
#         # kwargs.update(self.propellants[stage][n][2])
#         self.propellants[stage][n] = self.propellants[stage][n][0:2] + (kwargs,)
#
#     def _triggerStage(self, curr_stage):
#         for stg in Stage.stages:
#             exec('%s = "%s"' % (stg, stg))
#         mile = self.mile+1
#         epoch = self.epoch+1
#         stage = self.macro_stage
#         stats = []
#         cnt = 0
#         for ppl, cond, kwargs in self.propellants[curr_stage]:
#             cnt += 1
#             if_meet = eval(cond)
#             if (ppl is None) or (not if_meet):
#                 stats.append(None)
#                 continue
#             stats.append(ppl(**kwargs))
#         return stats
#
#     def runAMile(self, fuel_line, pass_by=(), destination=(), interval=1):
#         assert len(pass_by)+len(destination) > 0
#         start = time.time()
#         fl = {} # feed dict
#         filled_fl = {}
#         quan_preflight = len(self.propellants[Stage.PREFLIGHT])
#
#         for k in fuel_line.keys():
#             if isinstance(fuel_line[k], str):
#                 pipe_out = self.batch[fuel_line[k]]
#             else:
#                 pipe_out = fuel_line[k]
#             fl[self.spacecraft.layout[k]] = pipe_out
#             filled_fl[k] = pipe_out
#         if quan_preflight > 0:  # there is propellant in Preflight stage
#             for i in range(quan_preflight):
#                 self._airDrop(Stage.PREFLIGHT, i, fuel_line=filled_fl)
#             temp_fl = self._triggerStage(Stage.PREFLIGHT)
#             for tfl in temp_fl:
#                 if not tfl is None:
#                     for k in tfl.keys():
#                         fl[self.spacecraft.layout[k]] = tfl[k]
#                     break
#
#         pb = [self.spacecraft.layout[k] for k in pass_by]
#         dst = [self.spacecraft.layout[k] for k in destination]
#         spot = self.sess.run(pb + dst, fl)
#         spot = spot[len(pass_by):len(pass_by)+len(destination)]
#         sp = {}
#         filled_sp = {}
#         for j in range(len(destination)):
#             filled_sp[destination[j]] = spot[j]
#         quan_analyzer = len(self.propellants[Stage.ANALYZE])
#         if quan_analyzer == 0:  # no propellants in Analyze stage
#             sp = deepcopy(filled_sp)
#         else:
#             for j in range(quan_analyzer):
#                 self._airDrop(Stage.ANALYZE, j, fuel_line=filled_fl, destination=filled_sp)
#             temp_sp = self._triggerStage(Stage.ANALYZE)
#             for tsp in temp_sp:
#                 if not tsp is None:
#                     sp = tsp
#                     break
#
#         prefix = self.macro_stage + ':'
#         for k in sp.keys():
#             self.destination[prefix + k] = sp[k]
#         self.dashboard._gauge(self.destination.items(), self.mile, self.epoch, self.mpe,
#                                   time.time()-start, interval)
#
#     def runAnEpoch(self, fuel_tank, miles=-1):
#         self.mpe = self.fuel_depot.MPE[fuel_tank]
#         if miles < 0:
#             miles = self.mpe
#         # cores = cpu_count() // 1
#         # print("Creating %d-process pool" % cores)
#         # pool = Pool(cores)
#         for mi in range(miles):
#             self.mile = mi
#             # begin = time.time()
#             self.batch = self.fuel_depot.nextBatch(fuel_tank)
#             # print('%.3fs' % (time.time() - begin))
#             for stg in Stage.phases[-1]:
#                 self._triggerStage(stg)
#
#         self.destination = {}
#
#     def log(self, guage=True, tachograph=True, blueprint=True):
#         self.dashboard._log(guage, tachograph)
#         if blueprint:
#             self.spacecraft.blueprint.log(self.dashboard.param['log_path'])
#
#     def launch(self, epochs=1):
#         try:
#             print('+' + 35 * '-' + '+')
#             print('| The Spacecraft is being launched. |')
#             print('+' + 35 * '-' + '+')
#             self._triggerStage(Stage.START)
#             if epochs < 0 or not isinstance(epochs, int):
#                 raise ValueError('NEBULAE ERROR ⨷ epochs must be a non-positive integer.')
#             for ep in range(epochs):
#                 self.epoch = ep
#                 for stg in Stage.phases[0]:
#                     self.macro_stage = stg
#                     self._triggerStage(stg)
#             self._triggerStage(Stage.END)
#             print('+' + 44 * '-' + '+')
#             print('| The Spacecraft has arrived at destination. |')
#             print('+' + 44 * '-' + '+')
#
#         except BaseException as e:
#             if Stage.BREAK_DOWN in self.propellants:
#                 self._triggerStage(Stage.BREAK_DOWN)
#             else:
#                 raise e















class NavigatorTF(object):
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
        # start a session
        self.sess = tf.Session(config=self.sc.engine.config_proto)
        self.feed(Stage.START, time_machine._setParams, external=False,
                            sess=self.sess, mile=spacecraft.layout['_MEDIA'],
                            scope=spacecraft.scope)

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
        ent = {}
        for k in entrance.keys():
            ent[self.sc.layout[k]] = entrance[k]

        if thruster is None:
            ext = exit
        else:
            ext = exit + (thruster,)
        ext = [self.sc.layout[k] for k in ext]
        tmp = self.sess.run(ext, ent)

        ret = {}
        for i, key in enumerate(exit):
            ret[key] = tmp[i]
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
            self.feed(Stage.START, self.sc.blueprint.log, external=False, log_path=self.db.param['log_path'])
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