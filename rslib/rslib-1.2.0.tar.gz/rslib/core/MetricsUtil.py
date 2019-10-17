#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2019 NetEase.com, Inc. All Rights Reserved.
# Copyright 2019, The NSH Recommendation Project, The User Persona Group, The Fuxi AI Lab.
"""
MetricsUtil

Authors: wangkai02(wangkai02@corp.netease.com)
Phone: 17816029211
Date: 2019/9/11
"""

import tensorflow as tf
import numpy as np


class MetricsUtil():

    def print_list(self, l):
        return '\n' + '\n'.join([str(x) for x in l]) if type(l) == type([]) else '\n' + str(l)

    def class_statistic(self, data, n):
        tmp = []
        for i in range(1, n):
            tmp.append(len([x for x in data if x.split(' ')[-1] == str(i)]))
        print("num_per_class: ", self.print_list(tmp))

    # 没有区分同一个用户的多次购买
    def gauc_all(self, data, n):
        gauc = []
        for x in data:
            pred = list(map(float, [y for y in x.split(' ')[-2].split(',')]))
            label = int(x.split(' ')[-1])
            p = pred[label]
            auc = 1 - sum([1 for x in pred if x > p]) / (n - 1)
            gauc.append(auc)
        print("gauc: ", sum(gauc) / len(gauc))

    def auc_all(self, data, n):
        pred = tf.identity(list(map(float, [y for x in data for y in x.split(' ')[-2].split(',')]))[:200000])
        label = tf.identity([1 if x.split(' ')[-1] == str(j) else 0 for x in data for j in range(len(x.split(' ')[-2].split(',')))][:200000])
        auc_all_op = tf.metrics.auc(label, pred)[1]
        with tf.Session() as sess:
            sess.run(tf.local_variables_initializer())
            print("auc_all: ", self.print_list(sess.run(auc_all_op)))

    def auc_per_class(self, data, n):
        auc_op = []
        for i in range(1, n):
            tmp = [x for x in data if x.split(' ')[-1] == str(i)]
            pred = tf.identity(list(map(float, [y for x in tmp for y in x.split(' ')[-2].split(',')])))
            label = tf.identity([1 if x.split(' ')[-1] == str(j) else 0 for x in tmp for j in range(len(x.split(' ')[-2].split(',')))])
            auc_op.append(tf.metrics.auc(label, pred)[1] if len(tmp) > 1 else tf.identity(0))
        with tf.Session() as sess:
            sess.run(tf.local_variables_initializer())
            print("auc: ", self.print_list(sess.run(auc_op)))
            # print("auc_all: ", self.print_list(sess.run(auc_all_op)))

    def topk_all(self, data, n, k):
        assert np.min([int(x.split(' ')[-1]) for x in data]) > 0
        y_true = tf.identity(np.array([int(x.split(' ')[-1]) for x in data]).astype(np.int64))
        y_pred = tf.identity(np.array([list(map(float, x.split(' ')[-2].split(','))) for x in data]))
        recall_all = tf.metrics.recall_at_k(y_true, y_pred, k)[1]
        precision_all = tf.metrics.precision_at_k(y_true, y_pred, k)[1]
        with tf.Session() as sess:
            sess.run(tf.local_variables_initializer())
            print("update_recall_all_at_%s: " % (k), self.print_list(sess.run(recall_all)))
            print("update_precision_all_at_%s: " % (k), self.print_list(sess.run(precision_all)))

    def topk_per_class(self, data, n, k):
        recall_op = []
        precision_op = []
        assert np.min([int(x.split(' ')[-1]) for x in data]) > 0
        for i in range(1, n):
            tmp = [x for x in data if x.split(' ')[-1] == str(i)]
            y_true = tf.identity(np.array([int(x.split(' ')[-1]) for x in tmp]).astype(np.int64))
            y_pred = tf.identity(np.array([list(map(float, x.split(' ')[-2].split(','))) for x in tmp]))
            recall_op.append(tf.metrics.recall_at_k(y_true, y_pred, k)[1] if len(tmp) > 1 else tf.identity(0))
            precision_op.append(tf.metrics.precision_at_k(y_true, y_pred, k)[1] if len(tmp) > 1 else tf.identity(0))
        with tf.Session() as sess:
            sess.run(tf.local_variables_initializer())
            print(sess.run([y_true, y_pred]))
            print("update_recall_at_%s: " % (k), self.print_list(sess.run(recall_op)))
            print("update_precision_at_%s: " % (k), self.print_list(sess.run(precision_op)))

