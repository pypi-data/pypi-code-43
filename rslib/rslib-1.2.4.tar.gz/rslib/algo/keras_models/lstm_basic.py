#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2019 NetEase.com, Inc. All Rights Reserved.
# Copyright 2019, The NSH Recommendation Project, The User Persona Group, The Fuxi AI Lab.
"""
keras_lstm

Authors: wangkai02(wangkai02@corp.netease.com)
Phone: 17816029211
Date: 2019/9/11
"""

import tensorflow as tf

from tensorflow.python.keras import layers
from tensorflow.python.keras.models import Model
from tensorflow.python.keras import backend as K
from ..sparse_dnn.DenseLayerForSparse import DenseLayerForSparse


def get_model(config):
    maxlen = config['maxlen']
    cross_size = config['cross_size']
    user_feature_size = config['user_feature_size']
    class_num = config['class_num']
    hist_id_output = config['hist_id_output']
    hist_week_id_output = config['hist_week_id_output']

    hist_id_input = layers.Input(shape=(maxlen,), dtype='int32')
    hist_week_id_input = layers.Input(shape=(maxlen,), dtype='int32')
    cross_feature_input = layers.Input(shape=(cross_size,), dtype='float32', sparse=True)
    user_feature_input = layers.Input(shape=(user_feature_size,), dtype='float32', sparse=True)

    hist_id_embeddings = layers.Embedding(class_num, hist_id_output, mask_zero=True)(hist_id_input)
    hist_week_id_embeddings = layers.Embedding(7, hist_week_id_output, mask_zero=True)(hist_week_id_input)
    embeddings = layers.Concatenate(axis=-1)([hist_id_embeddings, hist_week_id_embeddings])
    input_lstm = layers.LSTM(units=128)(embeddings)
    cross_feature = DenseLayerForSparse(cross_size, 64, 'relu')(cross_feature_input)
    user_feature = DenseLayerForSparse(user_feature_size, 64, 'relu')(user_feature_input)
    all_feature = layers.Concatenate(axis=-1)([input_lstm, cross_feature, user_feature])
    hidden = layers.Dense(class_num, activation='relu')(all_feature)
    output = layers.Softmax()(hidden)
    model = Model(inputs=[hist_id_input, hist_week_id_input, cross_feature_input, user_feature_input], outputs=[output])
    sess = tf.compat.v1.Session()
    sess.run(tf.compat.v1.local_variables_initializer())
    sess.run(tf.compat.v1.global_variables_initializer())
    sess.run(tf.compat.v1.tables_initializer())
    K.set_session(sess)
    model.compile(loss='categorical_crossentropy',
                  optimizer='adam',
                  metrics=[])
    print(model.summary())
    return model
