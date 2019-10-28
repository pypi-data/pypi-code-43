#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2019 NetEase.com, Inc. All Rights Reserved.
# Copyright 2019, The NSH Recommendation Project, The User Persona Group, The Fuxi AI Lab.
"""
FeatureUtil

Authors: wangkai02(wangkai02@corp.netease.com)
Phone: 17816029211
Date: 2019/9/11
"""
from tensorflow.python.data.ops import dataset_ops
import tensorflow as tf
import numpy as np
import scipy
from tensorflow.python.keras.preprocessing import sequence


class FeatureUtil():
    def __init__(self, config):
        self.config = config
        self.maxlen = config['maxlen']
        self.batchsize = config['batchsize']
        self.class_num = config['class_num']
        self.cross_size = config['cross_size']
        self.user_feature_size = config['user_feature_size']

    def feature_extraction(self, data, padding=False, sparse=True):
        role_id_list = [int(sample.split('@')[0]) for sample in data]
        label = [int(sample.split('@')[-2].split(':')[0]) for sample in data]
        label_time = [int(sample.split('@')[-2].split(':')[2]) for sample in data]
        hist_id = [[int(x.split(':')[0]) for x in sorted(sample.split('@')[1].split(', '), key=lambda x: x.split(':')[-1])][-self.maxlen:] for sample in data]  # 按时间排序，历史购买的物品id
        hist_week_id = [[int(x.split(':')[1]) for x in sorted(sample.split('@')[1].split(', '), key=lambda x: x.split(':')[-1])][-self.maxlen:] for sample in data]  # 星期几 取最近购买最大200条记录
        hist_time = [[int(sample.split('@')[-2].split(':')[2]) - int(x.split(':')[2]) for x in sorted(sample.split('@')[1].split(', '), key=lambda x: x.split(':')[-1])][-self.maxlen:] for sample in
                     data]  # 购买时间
        hist_time_gaps = [[0] + [abs(sample[i] - sample[i - 1])] for sample in hist_time for i in range(1, len(sample))]
        cross_features_id = [[int(y.split(':')[0]) for y in sample.split('@')[2].split(', ')] for sample in data]  # id+maxid*daygap
        cross_features_val = [[float(y.split(':')[1]) for y in sample.split('@')[2].split(', ')] for sample in data]  # value
        user_features_id = [[int(y.split(':')[0]) for y in sample.split('@')[3].split(', ')] for sample in data]  # id+maxid*daygap
        user_features_val = [[float(y.split(':')[1]) for y in sample.split('@')[3].split(', ')] for sample in data]  # value
        label_week_id = [[int(data[i].split('@')[-2].split(':')[1])] * len(hist_id[i]) for i in range(len(data))]
        return [hist_id, hist_week_id, cross_features_id, cross_features_val, user_features_id, user_features_val, hist_time, hist_time_gaps, label_week_id], np.array(label)

    def to_tfrecord(self, csvfile, filename):
        writer = tf.python_io.TFRecordWriter(filename)
        data = open(csvfile, 'r',encoding='utf8').read().split('\n')[1:-1]
        [hist_ids, hist_week_ids, cross_features_ids, cross_features_vals, user_features_ids, user_features_vals, hist_times, hist_time_gapss, label_week_ids], labels = self.feature_extraction(data)
        for i in range(len(data)):
            hist_id = hist_ids[i]
            hist_week_id = hist_week_ids[i]
            cross_features_id = cross_features_ids[i]
            cross_features_val = cross_features_vals[i]
            user_features_id = user_features_ids[i]
            user_features_val = user_features_vals[i]
            hist_time = hist_times[i]
            hist_time_gaps = hist_time_gapss[i]
            label_week_id = label_week_ids[i]
            label = labels[i]

            label_feature = tf.train.Feature(int64_list=tf.train.Int64List(value=[label]))
            hist_id_feature = tf.train.Feature(int64_list=tf.train.Int64List(value=hist_id))
            hist_week_id_feature = tf.train.Feature(int64_list=tf.train.Int64List(value=hist_week_id))
            cross_features_id_feature = tf.train.Feature(int64_list=tf.train.Int64List(value=cross_features_id))
            cross_features_val_feature = tf.train.Feature(float_list=tf.train.FloatList(value=cross_features_val))
            user_features_id_feature = tf.train.Feature(int64_list=tf.train.Int64List(value=user_features_id))
            user_features_val_feature = tf.train.Feature(float_list=tf.train.FloatList(value=user_features_val))
            hist_time_feature = tf.train.Feature(int64_list=tf.train.Int64List(value=hist_time))
            hist_time_gaps_feature = tf.train.Feature(int64_list=tf.train.Int64List(value=hist_time_gaps))
            label_week_id_feature = tf.train.Feature(int64_list=tf.train.Int64List(value=label_week_id))

            seq_example = tf.train.Example(
                features=tf.train.Features(feature={
                    "label": label_feature,
                    "hist_id": hist_id_feature,
                    "hist_week_id": hist_week_id_feature,
                    "cross_features_id": cross_features_id_feature,
                    "cross_features_val": cross_features_val_feature,
                    "user_features_id": user_features_id_feature,
                    "user_features_val": user_features_val_feature,
                    "hist_time": hist_time_feature,
                    "hist_time_gaps": hist_time_gaps_feature,
                    "label_week_id": label_week_id_feature
                })
            )
            writer.write(seq_example.SerializeToString())
        writer.close()

    def read_tfrecord(self, filename, is_pred=False):
        def _parse_exmp(serial_exmp):
            context_features = {
                "label": tf.io.FixedLenFeature([], dtype=tf.int64),
                "hist_id": tf.io.VarLenFeature(dtype=tf.int64),
                "hist_week_id": tf.io.VarLenFeature(dtype=tf.int64),
                "cross_features_id": tf.io.VarLenFeature(dtype=tf.int64),
                "cross_features_val": tf.io.VarLenFeature(dtype=tf.float32),
                "user_features_id": tf.io.VarLenFeature(dtype=tf.int64),
                "user_features_val": tf.io.VarLenFeature(dtype=tf.float32),
                "hist_time": tf.io.VarLenFeature(dtype=tf.int64),
                "hist_time_gaps": tf.io.VarLenFeature(dtype=tf.int64),
                "label_week_id": tf.io.VarLenFeature(dtype=tf.int64)
            }

            context_parsed = tf.io.parse_single_example(serialized=serial_exmp, features=context_features)
            label = context_parsed['label']
            hist_id = tf.sparse.to_dense(context_parsed['hist_id'])
            hist_week_id = tf.sparse.to_dense(context_parsed['hist_week_id'])
            cross_features_id = tf.sparse.to_dense(context_parsed['cross_features_id'])
            cross_features_val = tf.sparse.to_dense(context_parsed['cross_features_val'])
            user_features_id = tf.sparse.to_dense(context_parsed['user_features_id'])
            user_features_val = tf.sparse.to_dense(context_parsed['user_features_val'])
            cross_feature = tf.SparseTensor(values=cross_features_val, indices=tf.expand_dims(cross_features_id, -1), dense_shape=[self.cross_size])
            user_feature = tf.SparseTensor(values=user_features_val, indices=tf.expand_dims(user_features_id, -1), dense_shape=[self.user_feature_size])
            hist_time = tf.sparse.to_dense(context_parsed['hist_time'])
            hist_time_gaps = tf.sparse.to_dense(context_parsed['hist_time_gaps'])
            label_week_id = tf.sparse.to_dense(context_parsed['label_week_id'])
            return hist_id, hist_week_id, cross_feature, user_feature, hist_time, hist_time_gaps, label_week_id, label

        def _flat_map_fn(a, b, c, u, t, g, h, z):
            return dataset_ops.Dataset.zip((a.padded_batch(self.batchsize, padded_shapes=([self.maxlen])),
                                            b.padded_batch(self.batchsize, padded_shapes=([self.maxlen])),
                                            c.batch(batch_size=self.batchsize),
                                            u.batch(batch_size=self.batchsize),
                                            t.padded_batch(self.batchsize, padded_shapes=([self.maxlen])),
                                            g.padded_batch(self.batchsize, padded_shapes=([self.maxlen])),
                                            h.padded_batch(self.batchsize, padded_shapes=([self.maxlen])),
                                            z.batch(batch_size=self.batchsize)
                                            ))

        def preprocess_fn(a, b, c, u, t, g, h, z):
            '''A transformation function to preprocess raw data
            into trainable input. '''
            return (a, b, c, u, t, g, h), tf.one_hot(z, self.class_num)

        # tf.enable_eager_execution()
        dataset = tf.data.TFRecordDataset(filename)
        if is_pred:
            dataset_train = dataset \
                .map(_parse_exmp, num_parallel_calls=1) \
                .window(size=self.batchsize, drop_remainder=False) \
                .flat_map(_flat_map_fn) \
                .map(preprocess_fn)
        else:
            dataset_train = dataset \
                .map(_parse_exmp, num_parallel_calls=4) \
                .shuffle(10000) \
                .window(size=self.batchsize, drop_remainder=True) \
                .flat_map(_flat_map_fn) \
                .map(preprocess_fn) \
                .repeat()
        # print(dataset_train.make_one_shot_iterator().get_next())
        return dataset_train
