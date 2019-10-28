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
import tensorflow as tf
from tensorflow.python.framework import graph_util
import os

class TimeMachineTF(object):
    def __init__(self, param):
        '''
        Time Machine saves current states or restores saved states
        '''
        self.param = param



    def _setParams(self, sess, mile, scope):
        self.sess = sess
        self.mile = mile
        if scope:
            self.scope = scope[:-1]
        else:
            self.scope = 'ckpt'
        self.sess.run(tf.global_variables_initializer())

    def backTo(self, frozen=False, ins=None, outs=None):
        if frozen:
            self._thaw(ins, outs)
        else:
            self._backTo()

    def dropAnchor(self, frozen=False, anchor=None):
        if frozen:
            self._freeze(anchor)
        else:
            self._dropAnchor()

    def _backTo(self):
        if self.param['ckpt_path'] is None:
            raise Exception('NEBULAE ERROR ⨷ anchor location is not provided.')
        else:
            if self.param['ckpt_scope'] is None:
                to_be_restored = tf.global_variables()
            else:
                to_be_restored = tf.global_variables(scope=self.param['ckpt_scope'])
            self.restorer = tf.train.Saver(to_be_restored)
            if os.path.isfile(self.param['ckpt_path']):
                ckpt = self.param['ckpt_path']
            else:
                ckpt = tf.train.latest_checkpoint(self.param['ckpt_path'])
            self.restorer.restore(self.sess, ckpt)
            print('+' + ((10 + len(self.param['ckpt_path'])) * '-') + '+')
            print('| Back to \033[1;34m%s\033[0m |' % self.param['ckpt_path'])
            print('+' + ((10 + len(self.param['ckpt_path'])) * '-') + '+')

    def _dropAnchor(self):
        if self.param['save_path'] is None:
            raise Exception('NEBULAE ERROR ⨷ there is nowhere to drop anchor.')
        else:
            to_be_saved = tf.global_variables()
            self.saver = tf.train.Saver(to_be_saved, max_to_keep=1)

            self.saver.save(self.sess, os.path.join(self.param['save_path'], self.scope),
                            global_step=self.mile, write_meta_graph=True)
            print('| Anchor is dropped at \033[1;34m%s\033[0m |' % self.param['save_path'])

    def _thaw(self, fuel_line, moments):
        if self.param['ckpt_path'] is None:
            raise Exception('NEBULAE ERROR ⨷ checkpoint path is not provided.')
        else:
            self.time_point = tf.GraphDef()
            with open(self.param['ckpt_path'], 'rb') as thawing:
                self.time_point.ParseFromString(thawing.read())
            moments = [m.name for m in moments]
            print('+' + ((23 + len(self.param['ckpt_path'])) * '-') + '+')
            print('| Moment is thawed out from \033[1;34m%s\033[0m |' % self.param['ckpt_path'])
            print('+' + ((23 + len(self.param['ckpt_path'])) * '-') + '+')
            return tf.import_graph_def(self.time_point, fuel_line, return_elements=moments)

    def _freeze(self, moments):
        if self.param['save_path'] is None:
            return
        else:
            moments = [m.op.name for m in moments]
            out_graph_def = graph_util.convert_variables_to_constants(self.sess, self.sess.graph_def, moments)
            tf.train.write_graph(out_graph_def, os.path.dirname(self.param['save_path']),
                                 os.path.basename(self.param['save_path']), as_text=False)
            print('+' + ((23 + len(self.param['save_path'])) * '-') + '+')
            print('| Moment is frozen in \033[1;34m%s\033[0m |' % self.param['save_path'])
            print('+' + ((23 + len(self.param['save_path'])) * '-') + '+')