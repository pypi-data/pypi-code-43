#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2019 NetEase.com, Inc. All Rights Reserved.
# Copyright 2019, The NSH Recommendation Project, The User Persona Group, The Fuxi AI Lab.
"""
contrib

Authors: wangkai02(wangkai02@corp.netease.com)
Phone: 17816029211
Date: 2019/9/11
"""

import tensorflow as tf
import numpy as np


def normalize(inputs, epsilon=1e-8, scope="ln", reuse=None):
    # layer normalize
    with tf.variable_scope(scope, reuse=reuse):
        inputs_shape = inputs.get_shape()
        params_shape = inputs_shape[-1:]

        mean, variance = tf.nn.moments(inputs, [-1], keep_dims=True)
        beta = tf.Variable(tf.zeros(params_shape))
        gamma = tf.Variable(tf.ones(params_shape))
        normalized = (inputs - mean) / ((variance + epsilon) ** (.5))
        outputs = gamma * normalized + beta
        return outputs


def embedding(inputs, vocab_size, num_units, scale=True, scope="embedding", reuse=None):
    with tf.variable_scope(scope, reuse=reuse):
        lookup_table = tf.get_variable('lookup_table',
                                       dtype=tf.float32,
                                       shape=[vocab_size + 1, num_units],
                                       initializer=tf.contrib.layers.xavier_initializer())

        outputs = tf.nn.embedding_lookup(lookup_table, inputs)

        if scale:
            outputs = outputs * (num_units ** 0.5)
    return outputs


def positional_encoding(inputs, num_units, scale=True, scope="positional_encoding", reuse=None):
    inputs = tf.convert_to_tensor(inputs, np.float32)
    N = tf.shape(inputs)[0]  # N:32,T:length
    T = inputs.get_shape().as_list()[1]

    with tf.variable_scope(scope, reuse=reuse):
        position_ind = tf.tile(tf.expand_dims(tf.range(T), 0), [N, 1])

        # First part of the PE function: sin and cos argument
        position_enc = np.array([
            [pos / np.power(10000, (i - i % 2) / num_units) for i in range(num_units)]
            for pos in range(T)])

        # Second part, apply the cosine to even columns and sin to odds.
        position_enc[:, 0::2] = np.sin(position_enc[:, 0::2])  # dim 2i
        position_enc[:, 1::2] = np.cos(position_enc[:, 1::2])  # dim 2i+1

        # Convert to a tensor
        lookup_table = tf.convert_to_tensor(position_enc, np.float32)

        outputs = tf.nn.embedding_lookup(lookup_table, position_ind)

        if scale:
            outputs = outputs * num_units ** 0.5

        return outputs


def temporal_log_time_positional_encoding(inputs, num_units, time_stamp, scale=True, scope="temporal_log_positional_encoding", reuse=None):
    inputs = tf.convert_to_tensor(inputs, np.float32)
    N = tf.shape(inputs)[0]  # N:32,T:length
    T = tf.shape(inputs)[1]
    # st = tf.tile(tf.expand_dims(time_stamp[:, 0], 1), [1, T]) # [batch_size, max_len]
    # ti = time_stamp - st  # [batch_size, max_len]
    time_stamp = tf.cast(time_stamp, tf.float32)
    ti = tf.log(time_stamp + 1)  # natural logarithm to deal with the skewed dist.
    ti = tf.tile(tf.expand_dims(ti, 2), [1, 1, num_units])  # [batch_size, max_len, num_units]
    ti = tf.cast(ti, tf.float32)

    with tf.variable_scope(scope, reuse=reuse):
        position_ind = tf.tile(tf.expand_dims(tf.range(T), 0), [N, 1])

        # First part of the PE function: sin and cos argument
        # position_enc = tf.zeros([N, T, num_units])
        # base = [tf.pow(1000000.0, (i - i % 2) / num_units) for i in range(num_units)]  # no log time
        base = [tf.pow(20.0, (i - i % 2) / num_units) for i in range(num_units)]  # for log(time)
        base = tf.tile(tf.expand_dims(base, 0), [T, 1])
        base = tf.tile(tf.expand_dims(base, 0), [N, 1, 1])
        position_enc = ti / base

        # # Second part, apply the cosine to even columns and sin to odds.
        pos_sin = tf.sin(position_enc)
        pos_cos = tf.cos(position_enc)
        pos_ind = [i % 2 for i in range(num_units)]
        pos_ind = tf.tile(tf.expand_dims(pos_ind, 0), [T, 1])
        pos_ind = tf.tile(tf.expand_dims(pos_ind, 0), [N, 1, 1])
        pos_sin_ind = tf.cast(1 - pos_ind, tf.float32)
        pos_cos_ind = tf.cast(pos_ind, tf.float32)
        position_enc = tf.multiply(pos_sin, pos_sin_ind) + tf.multiply(pos_cos, pos_cos_ind)

        outputs = position_enc

        if scale:
            outputs = outputs * num_units ** 0.5

        return outputs


def feedforward(inputs, num_units=[4 * 64, 64], scope="multihead_attention", reuse=None):
    with tf.variable_scope(scope, reuse=reuse):
        # Inner layer
        params = {"inputs": inputs, "filters": num_units[0], "kernel_size": 1,
                  "activation": tf.nn.relu, "use_bias": True}
        outputs = tf.layers.conv1d(**params)

        # Readout layer
        params = {"inputs": outputs, "filters": num_units[1], "kernel_size": 1,
                  "activation": None, "use_bias": True}
        outputs = tf.layers.conv1d(**params)

        # Residual connection
        outputs += inputs

        # Normalize
        outputs = normalize(outputs)

    return outputs  # (batch_size, maxlen, hidden_units)


def multihead_attention(queries, keys, num_units=None, num_heads=4, dropout_rate=0, is_training=True,
                        causality=False, scope="multihead_attention", reuse=None, T_input=None, mask=None):
    with tf.variable_scope(scope, reuse=reuse):
        # Set the fall back option for num_units
        if num_units is None:
            num_units = queries.get_shape().as_list[-1]

        # Linear projections
        Q = tf.layers.dense(queries, num_units, activation=tf.nn.relu)  # (N, T_q, C)
        K = tf.layers.dense(keys, num_units, activation=tf.nn.relu)  # (N, T_k, C)
        V = tf.layers.dense(keys, num_units, activation=tf.nn.relu)  # (N, T_k, C)

        # Split and concat
        Q_ = tf.concat(tf.split(Q, num_heads, axis=2), axis=0)  # (h*N, T_q, C/h)
        K_ = tf.concat(tf.split(K, num_heads, axis=2), axis=0)  # (h*N, T_k, C/h)
        V_ = tf.concat(tf.split(V, num_heads, axis=2), axis=0)  # (h*N, T_k, C/h)

        # Multiplication
        outputs = tf.matmul(Q_, tf.transpose(K_, [0, 2, 1]))  # (h*N, T_q, T_k)

        # Scale
        outputs = outputs / (K_.get_shape().as_list()[-1] ** 0.5)

        # Key Masking
        key_masks = mask[0]  # (N, T_k)
        key_masks = tf.tile(key_masks, [num_heads, 1])  # (h*N, T_k)
        key_masks = tf.tile(tf.expand_dims(key_masks, 1), [1, tf.shape(queries)[1], 1])  # (h*N, T_q, T_k)

        paddings = tf.ones_like(outputs) * (-2 ** 32 + 1)
        outputs = tf.where(tf.equal(key_masks, 0), paddings, outputs)  # (h*N, T_q, T_k)

        # Causality = Future blinding
        if causality:
            diag_vals = tf.ones_like(outputs[0, :, :])  # (T_q, T_k)
            tril = tf.linalg.LinearOperatorLowerTriangular(diag_vals).to_dense()  # (T_q, T_k)
            masks = tf.tile(tf.expand_dims(tril, 0), [tf.shape(outputs)[0], 1, 1])  # (h*N, T_q, T_k)

            paddings = tf.ones_like(masks) * (-2 ** 32 + 1)
            outputs = tf.where(tf.equal(masks, 0), paddings, outputs)  # (h*N, T_q, T_k)

        # Activation
        outputs = tf.nn.softmax(outputs)  # (h*N, T_q, T_k)

        # Query Masking
        query_masks = mask[1]  # (N, T_q)
        query_masks = tf.tile(query_masks, [num_heads, 1])  # (h*N, T_q)
        query_masks = tf.tile(tf.expand_dims(query_masks, -1), [1, 1, tf.shape(keys)[1]])  # (h*N, T_q, T_k)
        outputs *= query_masks  # broadcasting. (h*N, T_q, T_k)

        # Dropouts
        outputs2 = tf.layers.dropout(outputs, rate=dropout_rate, training=tf.convert_to_tensor(is_training))

        # Weighted sum
        outputs2 = tf.matmul(outputs2, V_)  # ( h*N, T_q, C/h)

        # Restore shape
        outputs2 = tf.concat(tf.split(outputs2, num_heads, axis=0), axis=2)  # (N, T_q, C)

        # Residual connection
        outputs2 += queries

        # Normalize
        outputs2 = normalize(outputs2)  # (N, T_q, C)

    return outputs2, outputs


def multihead_attention_keras(queries, keys, hidden_units=64, size_per_head=None, nb_head=4, dropout_rate=0, is_training=True,
                              causality=False, scope="multihead_attention", reuse=None, T_input=None):
    with tf.variable_scope(scope):

        maxlen = queries.get_shape().as_list()[1]

        WQ = tf.Variable(tf.random_uniform([hidden_units, size_per_head * nb_head], -1.0, 1.0))
        WK = tf.Variable(tf.random_uniform([hidden_units, size_per_head * nb_head], -1.0, 1.0))
        WV = tf.Variable(tf.random_uniform([hidden_units, size_per_head * nb_head], -1.0, 1.0))

        # WQ = tf.get_variable('WQ',[32,size_per_head*nb_head],initializer=tf.glorot_uniform_initializer)
        # WK = tf.get_variable('WK',[tf.shape(queries)[2],size_per_head*nb_head],tf.float32,initializer=tf.glorot_uniform_initializer)
        # WV = tf.get_variable('WV',[tf.shape(queries)[2],size_per_head*nb_head],tf.float32,initializer=tf.glorot_uniform_initializer)
        import keras
        Q_seq = keras.backend.dot(queries, WQ)
        # print('T_seq shape:',Q_seq.shape,self.WQ.shape)
        Q_seq = tf.reshape(Q_seq, (-1, maxlen, 8, size_per_head))
        Q_seq = tf.transpose(Q_seq, [0, 2, 1, 3])
        K_seq = keras.backend.dot(queries, WK)
        K_seq = tf.reshape(K_seq, (-1, maxlen, 8, size_per_head))
        K_seq = tf.transpose(K_seq, [0, 2, 1, 3])
        V_seq = keras.backend.dot(queries, WV)
        V_seq = tf.reshape(V_seq, (-1, maxlen, nb_head, size_per_head))
        V_seq = tf.transpose(V_seq, [0, 2, 1, 3])

        A = keras.backend.batch_dot(Q_seq, K_seq, axes=[3, 3]) / size_per_head ** 0.5
        # print('T_seq shape:',tf.matmul(Q_seq, K_seq, adjoint_a=None, adjoint_b=True).shape)
        # print('T_seq shape:',Q_seq.shape,K_seq.shape,A.shape)
        Q_len, V_len = None, None

        def Mask(inputs, seq_len, mode='mul'):
            if seq_len == None:
                return inputs
            else:
                mask = tf.one_hot(seq_len[:, 0], tf.shape(inputs)[1])
                mask = 1 - tf.cumsum(mask, 1)
                for _ in range(len(inputs.shape) - 2):
                    mask = tf.expand_dims(mask, 2)
                if mode == 'mul':
                    return inputs * mask
                if mode == 'add':
                    return inputs - (1 - mask) * 1e12

        A = tf.transpose(A, [0, 3, 2, 1])
        A = Mask(A, V_len, 'add')
        A = tf.transpose(A, [0, 3, 2, 1])
        A = tf.nn.softmax(A)
        # 输出并mask
        O_seq = keras.backend.batch_dot(A, V_seq, axes=[3, 2])
        O_seq = tf.transpose(O_seq, [0, 2, 1, 3])
        O_seq = tf.reshape(O_seq, (-1, maxlen, size_per_head * nb_head))
        O_seq = Mask(O_seq, Q_len, 'mul')
        return O_seq


def multihead_attention_time(queries, keys, num_units=None, num_heads=4, dropout_rate=0, is_training=True,
                             causality=False, scope="multihead_attention", reuse=None, T_input=None):
    with tf.variable_scope(scope, reuse=reuse):
        # Set the fall back option for num_units
        if num_units is None:
            num_units = queries.get_shape().as_list[-1]

        T = tf.reshape(T_input, (-1, queries.shape[1], 1))
        T = T * np.ones((1, queries.shape[2]))
        T = tf.cast(T, tf.float32)
        queries = tf.multiply(queries, T)

        # Linear projections
        Q = tf.layers.dense(queries, num_units, activation=tf.nn.relu)  # (N, T_q, C)
        K = tf.layers.dense(keys, num_units, activation=tf.nn.relu)  # (N, T_k, C)
        V = tf.layers.dense(keys, num_units, activation=tf.nn.relu)  # (N, T_k, C)

        # Split and concat
        Q_ = tf.concat(tf.split(Q, num_heads, axis=2), axis=0)  # (h*N, T_q, C/h)
        K_ = tf.concat(tf.split(K, num_heads, axis=2), axis=0)  # (h*N, T_k, C/h)
        V_ = tf.concat(tf.split(V, num_heads, axis=2), axis=0)  # (h*N, T_k, C/h)

        # Multiplication
        outputs = tf.matmul(Q_, tf.transpose(K_, [0, 2, 1]))  # (h*N, T_q, T_k)

        # Scale
        outputs = outputs / (K_.get_shape().as_list()[-1] ** 0.5)

        # Key Masking
        key_masks = tf.sign(tf.abs(tf.reduce_sum(keys, axis=-1)))  # (N, T_k)
        key_masks = tf.tile(key_masks, [num_heads, 1])  # (h*N, T_k)
        key_masks = tf.tile(tf.expand_dims(key_masks, 1), [1, tf.shape(queries)[1], 1])  # (h*N, T_q, T_k)

        paddings = tf.ones_like(outputs) * (-2 ** 32 + 1)
        outputs = tf.where(tf.equal(key_masks, 0), paddings, outputs)  # (h*N, T_q, T_k)

        # Causality = Future blinding
        if causality:
            diag_vals = tf.ones_like(outputs[0, :, :])  # (T_q, T_k)
            tril = tf.linalg.LinearOperatorLowerTriangular(diag_vals).to_dense()  # (T_q, T_k)
            masks = tf.tile(tf.expand_dims(tril, 0), [tf.shape(outputs)[0], 1, 1])  # (h*N, T_q, T_k)

            paddings = tf.ones_like(masks) * (-2 ** 32 + 1)
            outputs = tf.where(tf.equal(masks, 0), paddings, outputs)  # (h*N, T_q, T_k)

        # Activation
        outputs = tf.nn.softmax(outputs)  # (h*N, T_q, T_k)

        # Query Masking
        query_masks = tf.sign(tf.abs(tf.reduce_sum(queries, axis=-1)))  # (N, T_q)
        query_masks = tf.tile(query_masks, [num_heads, 1])  # (h*N, T_q)
        query_masks = tf.tile(tf.expand_dims(query_masks, -1), [1, 1, tf.shape(keys)[1]])  # (h*N, T_q, T_k)
        outputs *= query_masks  # broadcasting. (N, T_q, C)

        # Dropouts
        outputs2 = tf.layers.dropout(outputs, rate=dropout_rate, training=tf.convert_to_tensor(is_training))

        # Weighted sum
        outputs2 = tf.matmul(outputs2, V_)  # ( h*N, T_q, C/h)

        # Restore shape
        outputs2 = tf.concat(tf.split(outputs2, num_heads, axis=0), axis=2)  # (N, T_q, C)

        # Residual connection
        outputs2 += queries

        # Normalize
        outputs2 = normalize(outputs2)  # (N, T_q, C)

    return outputs2, outputs


def multihead_attention_time_mask(queries, keys, num_units=None, num_heads=4, dropout_rate=0, is_training=True,
                                  causality=True, scope="multihead_attention", reuse=None, T_input=None):
    with tf.variable_scope(scope, reuse=reuse):
        # Set the fall back option for num_units
        if num_units is None:
            num_units = queries.get_shape().as_list[-1]

        T = tf.reshape(T_input, (-1, queries.shape[1], 1))
        T = T * np.ones((1, queries.shape[2]))
        T = tf.cast(T, tf.float32)
        queries = tf.multiply(queries, T)

        # Linear projections
        Q = tf.layers.dense(queries, num_units, activation=tf.nn.relu)  # (N, T_q, C)
        K = tf.layers.dense(keys, num_units, activation=tf.nn.relu)  # (N, T_k, C)
        V = tf.layers.dense(keys, num_units, activation=tf.nn.relu)  # (N, T_k, C)

        # Split and concat
        Q_ = tf.concat(tf.split(Q, num_heads, axis=2), axis=0)  # (h*N, T_q, C/h)
        K_ = tf.concat(tf.split(K, num_heads, axis=2), axis=0)  # (h*N, T_k, C/h)
        V_ = tf.concat(tf.split(V, num_heads, axis=2), axis=0)  # (h*N, T_k, C/h)

        # Multiplication
        outputs = tf.matmul(Q_, tf.transpose(K_, [0, 2, 1]))  # (h*N, T_q, T_k)

        # Scale
        outputs = outputs / (K_.get_shape().as_list()[-1] ** 0.5)

        # Key Masking
        key_masks = tf.sign(tf.abs(tf.reduce_sum(keys, axis=-1)))  # (N, T_k)
        key_masks = tf.tile(key_masks, [num_heads, 1])  # (h*N, T_k)
        key_masks = tf.tile(tf.expand_dims(key_masks, 1), [1, tf.shape(queries)[1], 1])  # (h*N, T_q, T_k)

        paddings = tf.ones_like(outputs) * (-2 ** 32 + 1)
        outputs = tf.where(tf.equal(key_masks, 0), paddings, outputs)  # (h*N, T_q, T_k)

        # Causality = Future blinding
        if causality:
            diag_vals = tf.ones_like(outputs[0, :, :])  # (T_q, T_k)
            #########Causality=True#########
            tril = tf.linalg.LinearOperatorLowerTriangular(diag_vals).to_dense()  # (T_q, T_k)
            masks = tf.tile(tf.expand_dims(tril, 0), [tf.shape(outputs)[0], 1, 1])  # (h*N, T_q, T_k)

            paddings = tf.ones_like(masks) * (-2 ** 32 + 1)
            outputs = tf.where(tf.equal(masks, 0), paddings, outputs)  # (h*N, T_q, T_k)

        # Activation
        outputs = tf.nn.softmax(outputs)  # (h*N, T_q, T_k)

        # Query Masking
        query_masks = tf.sign(tf.abs(tf.reduce_sum(queries, axis=-1)))  # (N, T_q)
        query_masks = tf.tile(query_masks, [num_heads, 1])  # (h*N, T_q)
        query_masks = tf.tile(tf.expand_dims(query_masks, -1), [1, 1, tf.shape(keys)[1]])  # (h*N, T_q, T_k)
        outputs *= query_masks  # broadcasting. (N, T_q, C)

        # Dropouts
        # outputs2 = tf.layers.dropout(outputs, rate=dropout_rate, training=tf.convert_to_tensor(is_training))

        # Weighted sum
        # outputs2=tf.transpose(outputs2, perm=[0,2,1,3])

        outputs2 = tf.matmul(outputs, V_)  # ( h*N, T_q, C/h)
        print(tf.shape(outputs2))

        # Restore shape
        outputs2 = tf.concat(tf.split(outputs2, num_heads, axis=0), axis=2)  # (N, T_q, C)

        # Residual connection
        outputs2 += queries

        # Normalize
        outputs2 = normalize(outputs2)  # (N, T_q, C)

    return outputs2, outputs


def point_process(context, output_unit, is_training=False):
    hidden_units = context.get_shape().as_list[-1]
    maxlen = context.get_shape().as_list[1]
    b = tf.Variable(tf.random_uniform([output_unit, 1], -1.0, 1.0))
    Wt = tf.Variable(tf.random_uniform([output_unit, 1], -1.0, 1.0))
    Wh = tf.Variable(tf.random_uniform([output_unit, maxlen * hidden_units, 1], -1.0, 1.0))

    # (-1,maxlen,hidden_units)
    # print(tf.shape(context))
    context = tf.reshape(context, [-1, maxlen * hidden_units])
    context = tf.expand_dims(context, 1)
    # (-1,38,maxlen*hidden_units)
    context = tf.tile(context, [1, output_unit, 1])
    lambda_all_0 = tf.squeeze(tf.matmul(tf.expand_dims(context, -1), tf.tile(tf.expand_dims(Wh, 0), [tf.shape(context)[0], 1, 1, 1]), transpose_a=True), -1) + b


def point_process_loss(batch_y, batch_t, lambda_all_0, Wt):
    loss_time = tf.log(tf.reduce_sum(tf.exp(lambda_all_0 + tf.matmul(batch_t, Wt, transpose_b=True)), axis=0))
    # loss_time = tf.scan(lambda a,t: tf.log(tf.reduce_sum(tf.exp(lambda_all_0+tf.multiply(Wt,t)),axis=0)),batch_t)

    loss_event = tf.reduce_sum(
        tf.scan(lambda a, event_t: tf.multiply((tf.exp(lambda_all_0 + tf.multiply(Wt, event_t[1]))[event_t[0]] - tf.exp(lambda_all_0)[event_t[0]]), 1 / Wt[event_t[0]]), (batch_y, batch_t)), axis=1)
    return tf.reduce_sum(loss_time - loss_event)


def label_smoothing(inputs, epsilon=0.1):
    inputs = tf.cast(inputs, tf.float32)
    K = inputs.get_shape().as_list()[-1]  # number of channels
    return ((1 - epsilon) * inputs) + (epsilon / K)


def cross_entropy(logits, labels, class_num, isSmoothing=False):
    '''compute loss of cross_entropy'''
    if isSmoothing:  # label smoothing
        one_hot_label = tf.one_hot(tf.cast(labels, tf.int32), depth=class_num)
        smoothed_label = label_smoothing(one_hot_label)
        loss_entropy_event = tf.nn.softmax_cross_entropy_with_logits_v2(labels=smoothed_label, logits=logits)
    else:
        loss_entropy_event = tf.nn.sparse_softmax_cross_entropy_with_logits(logits=logits, labels=tf.cast(labels, tf.int32))
    # # wighted_loss
    # weight = tf.cast(tf.gather(self.weight_per_class, tf.cast(batch_target, tf.int32)), loss_entropy_event.dtype)
    # loss_entropy_event = tf.multiply(loss_entropy_event, weight)
    cost = tf.reduce_mean(loss_entropy_event)
    return cost


def focal_loss(logits, labels, class_num, alpha=1.0, gamma=2, isSmoothing=False):
    '''Focal loss: to balance the imbalanced multi-class classification'''
    labels = tf.one_hot(tf.cast(labels, tf.int32), depth=class_num)
    if isSmoothing:
        labels = label_smoothing(labels)
    y_pred = tf.nn.softmax(logits=logits) + 1e-10
    ce = tf.multiply(labels, -tf.log(y_pred))
    weight = alpha * tf.pow(tf.subtract(1., y_pred), gamma)
    fl = tf.multiply(weight, ce)
    cost = tf.reduce_max(fl, axis=1)
    # weighted_label = tf.multiply(labels, tf.pow(tf.subtract(1., y_pred), gamma))
    # ce = tf.nn.softmax_cross_entropy_with_logits_v2(labels=weighted_label, logits=logits)
    # fl = alpha * ce
    # cost = tf.reduce_max(fl, axis=1)
    cost = tf.reduce_mean(cost)
    return cost


def dense_interpolation(inputs, dense_factor):
    '''
    dense interpolation module: condense the raw concat of flattened output of the encoder
    See [AAAI 2018] Attend and Diagnose Clinical Time Series Analysis Using Attention Models
    :param inputs: output of the encoder  [batch_size, max_len, hidden_unit]
    :param dense_factor: determines dimension of the final interpolation output after the encoder layer. [1]
    Usually, dense factor is greatly less than the length of input sequence.
    :return: output, the dense interpolation of the final layer of encoder
    '''
    inputs = tf.cast(inputs, tf.float32)  # [batch_size, max_len, hidden_unit]
    N = tf.shape(inputs)[0]  # batch_size
    T = tf.shape(inputs)[1]  # max_len
    M = dense_factor  # dense_factor
    s = 1.0 * M * tf.range(1, T + 1, 1.0, dtype=tf.float32) / T
    m = tf.range(1, M + 1, 1.0, dtype=tf.float32)
    W = tf.transpose(tf.tile(tf.expand_dims(s, 1), [1, M])) - tf.tile(tf.expand_dims(m, 1), [1, T])  # [dense_factor, max_len]
    W = tf.pow(1 - tf.abs(W) / M, 2)
    W = tf.tile(tf.expand_dims(W, 0), [N, 1, 1])  # [batch_size, dense_factor, max_len]
    output = tf.matmul(W, inputs)  # [batch_size, dense_factor, hidden_unit]
    return output


def get_dense_interpolation(batchsize,maxlen,transformer_dense_factor):
    N = batchsize
    T = maxlen
    M = transformer_dense_factor
    s = 1.0 * M * tf.range(1, T + 1, 1.0, dtype=tf.float32) / T
    m = tf.range(1, M + 1, 1.0, dtype=tf.float32)
    W = tf.transpose(tf.tile(tf.expand_dims(s, 1), [1, M])) - tf.tile(tf.expand_dims(m, 1),
                                                                      [1, T])  # [dense_factor, max_len]
    W = tf.pow(1 - tf.abs(W) / M, 2)
    W = tf.tile(tf.expand_dims(W, 0), [N, 1, 1])  # [batch_size, dense_factor, max_len]
    return W


def concat_time_interval(inputs, time_interval):
    '''
    concat_time_interval, one of the simplest way to combine the irregular time stamps into the model
    See Recurrent Neural Networks for Multivariate Time Series DOI:10.1038/s41598-018-24271-9
    :param inputs: the embedding of the input token sequence [batch_size, max_len, hidden_unit]
    :param time_interval: the time interval of the sequence [batch_size, max_len]
    e.g., time stamp is [0, 10, 25, 60] then the time interval is defined as [0, 10, 15, 35]
    :return: the concatenation of the inputs and time interval [batch_size, max_len, hidden_unit]
    '''
    hidden_units = inputs.get_shape().as_list()[-1]
    inputs = tf.cast(inputs, tf.float32)  # [batch_size, max_len, hidden_unit]
    tmp_units = int(hidden_units / 2)
    inputs = tf.layers.dense(inputs, tmp_units)
    ti = tf.cast(time_interval, tf.float32)  # [batch_size, max_len]
    ti = tf.tile(tf.expand_dims(ti, 2), [1, 1, tmp_units])
    outputs = tf.concat([inputs, ti], axis=2)
    return outputs  # [batch_size, max_len, hidden_unit]


def concat_portrait(inputs, portrait, is_dense=True):
    '''
    concat the portrait information including 32-dimension BI portrait and 7-dimension one-hot weekday feature
    :param inputs: the output of attention module [batch_size, maxlen, hidden_unit]
    :param portrait: the portrait feature [batch_size, 39]
    :param is_dense: whether to use dense before concat
    :return: the concatenation of the inputs and portrait feature
    '''
    inputs = tf.cast(inputs, tf.float32)  # [batch_size, max_len, hidden_unit]
    shapes = inputs.get_shape().as_list()
    # flatten
    inputs = tf.reshape(inputs, [-1, shapes[1] * shapes[2]])  # [batch_size, max_len * hidden_unit]
    if is_dense:
        inputs = tf.layers.dense(inputs, units=shapes[-1], activation=tf.nn.relu)  # [batch_size, hidden_unit]
    outputs = tf.concat([inputs, portrait], axis=1)  # [batch_size, hidden_unit + 47]
    return outputs


def emb_concat_portrait(embbed_input, portrait):
    '''
    concat the portrait information including 32-dimension BI portrait and 7-dimension one-hot weekday feature
    :param embbed_input: the output of attention module [batch_size, maxlen, hidden_unit]
    :param portrait: the portrait feature [batch_size, 39]
    :return: the concatenation of the inputs and portrait feature
    '''
    maxlen = embbed_input.get_shape().as_list()[1]
    hidden_units = embbed_input.get_shape().as_list()[-1]
    inputs = tf.cast(embbed_input, tf.float32)  # [batch_size, max_len, hidden_unit]
    dense_units = hidden_units - 8
    portrait = tf.tile(tf.expand_dims(portrait[:, 0:8], 1), [1, maxlen, 1])
    inputs = tf.layers.dense(inputs, units=dense_units, activation=tf.nn.relu)  # [batch_size, maxlen, hidden_units-portrait_dim]
    outputs = tf.concat([inputs, portrait], axis=2)  # [batch_size, hidden_unit + 39]
    return outputs


def event_time_joint_embed(inputs, time_interval, proj_size=64):
    '''
    adopt the event-time joint embedding solution to fusing time information
    See [ICLR 2018]TIME-DEPENDENT REPRESENTATION FOR NEURAL EVENT SEQUENCE PREDICTION
    :param inputs: the embedding output of the event sequence   [batch_size, maxlen, hidden_unit]
    :param time_interval: the time interval of the map_id sequence  [batch_size, maxlen]
    e.g., time stamp is [0, 10, 25, 60] then the time interval is defined as [0, 10, 15, 35]
    :param proj_size: the dimension of the projection space for time interval
    :return:
    '''
    batch_size = tf.shape(inputs)[0]
    maxlen = tf.shape(inputs)[1]
    hidden_units = inputs.get_shape().as_list()[-1]
    N = batch_size
    T = maxlen
    ti = tf.cast(time_interval, tf.float32)
    inputs = tf.cast(inputs, tf.float32)

    # initialize
    proj_weight_mat = tf.get_variable('proj_weight_mat',
                                      dtype=tf.float32,
                                      shape=[1, proj_size],
                                      initializer=tf.contrib.layers.xavier_initializer())
    proj_bias = tf.get_variable('proj_bias',
                                dtype=tf.float32,
                                shape=[1, proj_size],
                                initializer=tf.contrib.layers.xavier_initializer())
    emb_weight_mat = tf.get_variable('emb_weight_mat',
                                     dtype=tf.float32,
                                     shape=[proj_size, hidden_units],
                                     initializer=tf.contrib.layers.xavier_initializer())

    # projection
    proj_weight_mat = tf.tile(tf.expand_dims(proj_weight_mat, 0), [N, T, 1])
    proj_bias = tf.tile(tf.expand_dims(proj_bias, 0), [N, T, 1])
    ti = tf.tile(tf.expand_dims(ti, 2), [1, 1, proj_size])
    ti_proj = tf.multiply(ti, proj_weight_mat) + proj_bias  # [batch_size, maxlen, proj_size]

    # soft one-hot encoding
    ti_soft_one_hot = tf.nn.softmax(ti_proj)  # [batch_size, maxlen, proj_size]

    # embedding
    emb_weight_mat = tf.tile(tf.expand_dims(emb_weight_mat, 0), [N, 1, 1])  # [batch_size, proj_size, hidden_unit]
    ti_emb = tf.matmul(ti_soft_one_hot, emb_weight_mat)

    # plus event embedding
    outputs = (inputs + ti_emb) / 2
    return outputs


def event_time_joint_embed_ver2(inputs, time_interval, proj_size=64):
    '''
    adopt the event-time joint embedding solution to fusing time information
    See [ICLR 2018]TIME-DEPENDENT REPRESENTATION FOR NEURAL EVENT SEQUENCE PREDICTION
    :param inputs: the embedding output of the event sequence   [batch_size, maxlen, hidden_unit]
    :param time_interval: the time interval of the map_id sequence  [batch_size, maxlen]
    e.g., time stamp is [0, 10, 25, 60] then the time interval is defined as [0, 10, 15, 35]
    :param proj_size: the dimension of the projection space for time interval
    :return:
    '''
    batch_size = tf.shape(inputs)[0]
    maxlen = tf.shape(inputs)[1]
    N = batch_size
    T = maxlen
    # st = tf.tile(tf.expand_dims(time_stamp[:, 0], 1), [1, T]) # [batch_size, max_len]
    # ti = time_stamp - st # [batch_size, max_len]
    inputs = tf.cast(inputs, tf.float32)
    ti = tf.cast(time_interval, tf.float32)

    # initialize
    proj_weight_mat = tf.get_variable('proj_weight_mat',
                                      dtype=tf.float32,
                                      shape=[1, proj_size],
                                      initializer=tf.contrib.layers.xavier_initializer())
    proj_bias = tf.get_variable('proj_bias',
                                dtype=tf.float32,
                                shape=[1, proj_size],
                                initializer=tf.contrib.layers.xavier_initializer())
    emb_weight_mat = tf.get_variable('emb_weight_mat',
                                     dtype=tf.float32,
                                     shape=[proj_size, 8],
                                     initializer=tf.contrib.layers.xavier_initializer())

    # projection
    proj_weight_mat = tf.tile(tf.expand_dims(proj_weight_mat, 0), [N, T, 1])
    proj_bias = tf.tile(tf.expand_dims(proj_bias, 0), [N, T, 1])
    ti = tf.tile(tf.expand_dims(ti, 2), [1, 1, proj_size])
    ti_proj = tf.multiply(ti, proj_weight_mat) + proj_bias  # [batch_size, maxlen, proj_size]

    # soft one-hot encoding
    ti_soft_one_hot = tf.nn.softmax(ti_proj)  # [batch_size, maxlen, proj_size]

    # embedding
    emb_weight_mat = tf.tile(tf.expand_dims(emb_weight_mat, 0), [N, 1, 1])  # [batch_size, proj_size, hidden_unit]
    ti_emb = tf.matmul(ti_soft_one_hot, emb_weight_mat)

    # plus event embedding
    outputs = tf.concat([inputs, ti_emb], axis=2)
    return outputs


def time_mask(inputs, time_interval, context_size=64):
    '''
    adopt the time mask solution to fusing time information
    See [ICLR 2018]TIME-DEPENDENT REPRESENTATION FOR NEURAL EVENT SEQUENCE PREDICTION
    :param inputs: the embedding output of the event sequence   [batch_size, maxlen, hidden_unit]
    :param time_interval: the time interval of the map_id sequence  [batch_size, maxlen]
    :param context_size: the dimension of the context vector for time mask
    e.g., time stamp is [0, 10, 25, 60] then the time interval is defined as [0, 10, 15, 35]
    '''
    batch_size = tf.shape(inputs)[0]
    maxlen = tf.shape(inputs)[1]
    hidden_units = inputs.get_shape().as_list()[-1]
    N = batch_size
    T = maxlen
    ti = tf.cast(time_interval, tf.float32)
    inputs = tf.cast(inputs, tf.float32)

    # Nonlinear transformation
    ti_log = tf.log(ti)
    ti_log = tf.tile(tf.expand_dims(ti, 2), [1, 1, context_size])
    ti_context = feedforward(ti_log,
                             num_units=[4 * context_size, context_size],
                             scope='time_mask')

    # Obtain mask
    ti_mask = tf.layers.dense(ti_context, units=hidden_units, activation=tf.nn.sigmoid)

    # Element-wise multiply event embedding
    outputs = tf.multiply(inputs, ti_mask)
    return outputs


def temporal_positional_encoding(inputs, num_units, time_stamp, scale=True, scope="temporal_positional_encoding", reuse=None):
    inputs = tf.convert_to_tensor(inputs, np.float32)
    batch_size = tf.shape(inputs)[0]
    maxlen = tf.shape(inputs)[1]
    N = batch_size  # N:32,T:length
    T = maxlen
    # st = tf.tile(tf.expand_dims(time_stamp[:, 0], 1), [1, T]) # [batch_size, max_len]
    # ti = time_stamp - st # [batch_size, max_len]
    ti = tf.tile(tf.expand_dims(time_stamp, 2), [1, 1, num_units])  # [batch_size, max_len, num_units]
    ti = tf.cast(ti, tf.float32)

    with tf.variable_scope(scope, reuse=reuse):
        position_ind = tf.tile(tf.expand_dims(tf.range(T), 0), [N, 1])

        base = [tf.pow(10000000.0, (i - i % 2) / num_units) for i in range(num_units)]
        base = tf.tile(tf.expand_dims(base, 0), [T, 1])
        base = tf.tile(tf.expand_dims(base, 0), [N, 1, 1])
        position_enc = ti / base

        # # Second part, apply the cosine to even columns and sin to odds.
        pos_sin = tf.sin(position_enc)
        pos_cos = tf.cos(position_enc)
        pos_ind = [i % 2 for i in range(num_units)]
        pos_ind = tf.tile(tf.expand_dims(pos_ind, 0), [T, 1])
        pos_ind = tf.tile(tf.expand_dims(pos_ind, 0), [N, 1, 1])
        pos_sin_ind = tf.cast(1 - pos_ind, tf.float32)
        pos_cos_ind = tf.cast(pos_ind, tf.float32)
        position_enc = tf.multiply(pos_sin, pos_sin_ind) + tf.multiply(pos_cos, pos_cos_ind)

        outputs = position_enc

        if scale:
            outputs = outputs * num_units ** 0.5

        return outputs


def hetero_temporal_multihead_attention(queries, keys, num_units=None, num_heads=4, dropout_rate=0, is_training=True,
                                        causality=False, scope="multihead_attention", reuse=None, T_input=None, avg=None,
                                        band=None,mask=None):
    '''
    Compute the hetero-temporal_mask to enhance the multihead attention module for irregularly temporal sequence
    See KDD Submission HSA-MTPP
    :param queries:
    :param keys:
    :param num_units:
    :param num_heads:
    :param dropout_rate:
    :param is_training:
    :param causality:
    :param scope:
    :param reuse:
    :param T_input: the input time stamp
    :param avg: the average inter-event time across the data
    :param band: the kernel band width of the defined hetero-temporal mask
    :return:
    '''
    with tf.variable_scope(scope, reuse=reuse):
        # Set the fall back option for num_units
        if num_units is None:
            num_units = queries.get_shape().as_list[-1]

        N = queries.get_shape().as_list[0]
        T = queries.get_shape().as_list[1]
        C = num_units

        # compute hetero-temporal kernel-based mask
        index_mat = tf.tile(tf.expand_dims(tf.range(1, T + 1), 0), [T, 1])  # [T, T]
        index_mat = tf.tile(tf.expand_dims(index_mat, 0), [N, 1, 1])  # [N, T, T]
        time_mat = tf.tile(tf.expand_dims(T_input, 1), [1, T, 1])  # [N, T, T]
        index_mat = tf.cast(index_mat, tf.float32)
        time_mat = tf.cast(time_mat, tf.float32)
        index_diff = tf.abs(index_mat - tf.transpose(index_mat, [0, 2, 1]))
        time_diff = tf.abs(time_mat - tf.transpose(time_mat, [0, 2, 1]))
        kernel_mask = tf.exp(-tf.square(time_diff - index_diff * avg) / band)  # [N, T, T]

        # Linear projections
        Q = tf.layers.dense(queries, num_units, activation=tf.nn.relu)  # (N, T_q, C)
        K = tf.layers.dense(keys, num_units, activation=tf.nn.relu)  # (N, T_k, C)
        V = tf.layers.dense(keys, num_units, activation=tf.nn.relu)  # (N, T_k, C)

        # Split and concat
        Q_ = tf.concat(tf.split(Q, num_heads, axis=2), axis=0)  # (h*N, T_q, C/h)
        K_ = tf.concat(tf.split(K, num_heads, axis=2), axis=0)  # (h*N, T_k, C/h)
        V_ = tf.concat(tf.split(V, num_heads, axis=2), axis=0)  # (h*N, T_k, C/h)

        # Multiplication
        outputs = tf.matmul(Q_, tf.transpose(K_, [0, 2, 1]))  # (h*N, T_q, T_k)

        # Scale
        outputs = outputs / (K_.get_shape().as_list()[-1] ** 0.5)

        # Key Masking
        key_masks = mask[0]  # (N, T_k)
        key_masks = tf.tile(key_masks, [num_heads, 1])  # (h*N, T_k)
        key_masks = tf.tile(tf.expand_dims(key_masks, 1), [1, tf.shape(queries)[1], 1])  # (h*N, T_q, T_k)

        paddings = tf.ones_like(outputs) * (-2 ** 32 + 1)
        outputs = tf.where(tf.equal(key_masks, 0), paddings, outputs)  # (h*N, T_q, T_k)

        # Causality = Future blinding
        if causality:
            diag_vals = tf.ones_like(outputs[0, :, :])  # (T_q, T_k)
            #########Causality=True#########
            # tril = tf.linalg.LinearOperatorLowerTriangular(diag_vals).to_dense()  # (T_q, T_k)
            tril = tf.linalg.LinearOperatorLowerTriangular(diag_vals).to_dense()  # (T_q, T_k)
            masks = tf.tile(tf.expand_dims(tril, 0), [tf.shape(outputs)[0], 1, 1])  # (h*N, T_q, T_k)

            paddings = tf.ones_like(masks) * (-2 ** 32 + 1)
            outputs = tf.where(tf.equal(masks, 0), paddings, outputs)  # (h*N, T_q, T_k)

        # Hetero-temporal Kernel-based Masking
        kernel_mask = tf.tile(kernel_mask, [num_heads, 1, 1])  # [N*h, T, T]
        outputs = tf.multiply(outputs, kernel_mask)

        # Activation
        outputs = tf.nn.softmax(outputs)  # (h*N, T_q, T_k)

        # Query Masking
        query_masks = mask[1]  # (N, T_q)
        query_masks = tf.tile(query_masks, [num_heads, 1])  # (h*N, T_q)
        query_masks = tf.tile(tf.expand_dims(query_masks, -1), [1, 1, tf.shape(keys)[1]])  # (h*N, T_q, T_k)
        outputs *= query_masks  # broadcasting. (N, T_q, C)

        # Dropouts
        # outputs2 = tf.layers.dropout(outputs, rate=dropout_rate, training=tf.convert_to_tensor(is_training))

        # Weighted sum
        # outputs2=tf.transpose(outputs2, perm=[0,2,1,3])

        outputs2 = tf.matmul(outputs, V_)  # ( h*N, T_q, C/h)
        # print(tf.shape(outputs2))

        # Restore shape
        outputs2 = tf.concat(tf.split(outputs2, num_heads, axis=0), axis=2)  # (N, T_q, C)

        # Residual connection
        outputs2 += queries

        # Normalize
        outputs2 = normalize(outputs2)  # (N, T_q, C)

    return outputs2, outputs


def temporal_mask_multihead_attention(queries, keys, num_units=None, num_heads=4, dropout_rate=0, is_training=True,
                                      causality=False, scope="multihead_attention", reuse=None, T_input=None, band=None, mask=None):
    '''
    Compute the temporal_mask to enhance the multihead attention module for irregularly temporal sequence.
    Adopt the assumpting: the longer the time-gap spans, the lesser the impact remains
    :param queries:
    :param keys:
    :param num_units:
    :param num_heads:
    :param dropout_rate:
    :param is_training:
    :param causality:
    :param scope:
    :param reuse:
    :param T_input: the input time stamp
    :param band: the kernel band width of the defined temporal mask
    :return:
    '''
    with tf.variable_scope(scope, reuse=reuse):
        # Set the fall back option for num_units
        if num_units is None:
            num_units = queries.get_shape().as_list[-1]

        N = queries.get_shape().as_list[0]
        T = queries.get_shape().as_list[1]
        C = num_units

        # compute temporal mask
        time_mat = tf.tile(tf.expand_dims(T_input, 1), [1, T, 1])  # [N, T, T]
        time_mat = tf.cast(time_mat, tf.float32)
        time_diff = time_mat - tf.transpose(time_mat, [0, 2, 1])
        temporal_mask = tf.exp(-tf.square(time_diff) / band)  # [N, T, T]

        # Linear projections
        Q = tf.layers.dense(queries, num_units, activation=tf.nn.relu)  # (N, T_q, C)
        K = tf.layers.dense(keys, num_units, activation=tf.nn.relu)  # (N, T_k, C)
        V = tf.layers.dense(keys, num_units, activation=tf.nn.relu)  # (N, T_k, C)

        # Split and concat
        Q_ = tf.concat(tf.split(Q, num_heads, axis=2), axis=0)  # (h*N, T_q, C/h)
        K_ = tf.concat(tf.split(K, num_heads, axis=2), axis=0)  # (h*N, T_k, C/h)
        V_ = tf.concat(tf.split(V, num_heads, axis=2), axis=0)  # (h*N, T_k, C/h)

        # Multiplication
        outputs = tf.matmul(Q_, tf.transpose(K_, [0, 2, 1]))  # (h*N, T_q, T_k)

        # Scale
        outputs = outputs / (K_.get_shape().as_list()[-1] ** 0.5)

        # Key Masking
        key_masks = mask[0]  # (N, T_k)
        key_masks = tf.tile(key_masks, [num_heads, 1])  # (h*N, T_k)
        key_masks = tf.tile(tf.expand_dims(key_masks, 1), [1, tf.shape(queries)[1], 1])  # (h*N, T_q, T_k)

        paddings = tf.ones_like(outputs) * (-2 ** 32 + 1)
        outputs = tf.where(tf.equal(key_masks, 0), paddings, outputs)  # (h*N, T_q, T_k)

        # Causality = Future blinding
        if causality:
            diag_vals = tf.ones_like(outputs[0, :, :])  # (T_q, T_k)
            #########Causality=True#########
            # tril = tf.linalg.LinearOperatorLowerTriangular(diag_vals).to_dense()  # (T_q, T_k)
            tril = tf.linalg.LinearOperatorLowerTriangular(diag_vals).to_dense()  # (T_q, T_k)
            masks = tf.tile(tf.expand_dims(tril, 0), [tf.shape(outputs)[0], 1, 1])  # (h*N, T_q, T_k)

            paddings = tf.ones_like(masks) * (-2 ** 32 + 1)
            outputs = tf.where(tf.equal(masks, 0), paddings, outputs)  # (h*N, T_q, T_k)

        # Temporal Masking
        temporal_mask = tf.tile(temporal_mask, [num_heads, 1, 1])  # [N*h, T, T]
        outputs = tf.multiply(outputs, temporal_mask)

        # Activation
        outputs = tf.nn.softmax(outputs)  # (h*N, T_q, T_k)

        # Query Masking
        query_masks = mask[1]  # (N, T_q)
        query_masks = tf.tile(query_masks, [num_heads, 1])  # (h*N, T_q)
        query_masks = tf.tile(tf.expand_dims(query_masks, -1), [1, 1, tf.shape(keys)[1]])  # (h*N, T_q, T_k)
        outputs *= query_masks  # broadcasting. (N, T_q, C)

        # Dropouts
        # outputs2 = tf.layers.dropout(outputs, rate=dropout_rate, training=tf.convert_to_tensor(is_training))

        # Weighted sum
        # outputs2=tf.transpose(outputs2, perm=[0,2,1,3])

        outputs2 = tf.matmul(outputs, V_)  # ( h*N, T_q, C/h)
        # print(tf.shape(outputs2))

        # Restore shape
        outputs2 = tf.concat(tf.split(outputs2, num_heads, axis=0), axis=2)  # (N, T_q, C)

        # Residual connection
        outputs2 += queries

        # Normalize
        outputs2 = normalize(outputs2)  # (N, T_q, C)

    return outputs2, outputs


def relative_temporal_multihead_attention(queries, keys, num_units=None, num_heads=4, dropout_rate=0, is_training=True,
                                          causality=False, scope="relative_temporal_multihead_attention", reuse=None,
                                          temporal_pos_enc=None, mask=None):
    '''
    Compute the relative temporal attention to fuse the time information
    Inspired by relative position encoding in Transformer-XL
    :param queries: the input embedding of the token seq
    :param keys: the input embedding of the token seq
    :param num_units:
    :param num_heads:
    :param dropout_rate:
    :param is_training:
    :param causality:
    :param scope:
    :param reuse:
    :param temporal_pos_enc: the temporal position encoding
    :return:
    '''
    with tf.variable_scope(scope, reuse=reuse):
        # Set the fall back option for num_units
        if num_units is None:
            num_units = queries.get_shape().as_list[-1]

        N = tf.shape(queries)[0]
        T = tf.shape(queries)[1]
        C = num_units

        # Initialization for relative temporal attention module
        u_vec = tf.get_variable('u_vec',
                                dtype=tf.float32,
                                shape=[1, num_units],
                                initializer=tf.contrib.layers.xavier_initializer())
        v_vec = tf.get_variable('v_vec',
                                dtype=tf.float32,
                                shape=[1, num_units],
                                initializer=tf.contrib.layers.xavier_initializer())
        u_vec = tf.tile(u_vec, [T, 1])  # [max_len, num_units]
        v_vec = tf.tile(v_vec, [T, 1])  # [max_len, num_nuits]
        u_vec = tf.tile(tf.expand_dims(u_vec, 0), [N, 1, 1])  # [batch_size, max_len, num_units]
        v_vec = tf.tile(tf.expand_dims(v_vec, 0), [N, 1, 1])  # [batch_size, max_len, num_units]

        # Linear projections
        Q = tf.layers.dense(queries, num_units, activation=tf.nn.relu)  # (N, T_q, C)
        K = tf.layers.dense(keys, num_units, activation=tf.nn.relu)  # (N, T_k, C)
        V = tf.layers.dense(keys, num_units, activation=tf.nn.relu)  # (N, T_k, C)
        PE = tf.layers.dense(temporal_pos_enc, num_units, activation=tf.nn.relu)  # [batch_size, max_len, num_units]

        # Split and concat
        Q_ = tf.concat(tf.split(Q, num_heads, axis=2), axis=0)  # (h*N, T_q, C/h)
        K_ = tf.concat(tf.split(K, num_heads, axis=2), axis=0)  # (h*N, T_k, C/h)
        V_ = tf.concat(tf.split(V, num_heads, axis=2), axis=0)  # (h*N, T_k, C/h)
        PE_ = tf.concat(tf.split(PE, num_heads, axis=2), axis=0)  # [num_heads*batch_size, max_len, num_units/num_heads]
        u_vec_ = tf.concat(tf.split(u_vec, num_heads, axis=2),
                           axis=0)  # [num_heads*batch_size, max_len, num_units/num_heads]
        v_vec_ = tf.concat(tf.split(v_vec, num_heads, axis=2),
                           axis=0)  # [num_heads*batch_size, max_len, num_units/num_heads]

        # Multiplication
        outputs = tf.matmul(Q_, tf.transpose(K_, [0, 2, 1]))  # (h*N, T_q, T_k)

        # Relative temporal attention
        outputs += tf.matmul(Q_, tf.transpose(PE_, [0, 2, 1]))
        outputs += tf.matmul(u_vec_, tf.transpose(K_, [0, 2, 1]))
        outputs += tf.matmul(v_vec_, tf.transpose(PE_, [0, 2, 1]))

        # Scale
        outputs = outputs / (K_.get_shape().as_list()[-1] ** 0.5)

        # Key Masking
        key_masks = mask[0]  # (N, T_k)
        key_masks = tf.tile(key_masks, [num_heads, 1])  # (h*N, T_k)
        key_masks = tf.tile(tf.expand_dims(key_masks, 1), [1, tf.shape(queries)[1], 1])  # (h*N, T_q, T_k)

        paddings = tf.ones_like(outputs) * (-2 ** 32 + 1)
        outputs = tf.where(tf.equal(key_masks, 0), paddings, outputs)  # (h*N, T_q, T_k)

        # Causality = Future blinding
        if causality:
            diag_vals = tf.ones_like(outputs[0, :, :])  # (T_q, T_k)
            #########Causality=True#########
            # tril = tf.linalg.LinearOperatorLowerTriangular(diag_vals).to_dense()  # (T_q, T_k)
            tril = tf.linalg.LinearOperatorLowerTriangular(diag_vals).to_dense()  # (T_q, T_k)
            masks = tf.tile(tf.expand_dims(tril, 0), [tf.shape(outputs)[0], 1, 1])  # (h*N, T_q, T_k)

            paddings = tf.ones_like(masks) * (-2 ** 32 + 1)
            outputs = tf.where(tf.equal(masks, 0), paddings, outputs)  # (h*N, T_q, T_k)

        # Activation
        outputs = tf.nn.softmax(outputs)  # (h*N, T_q, T_k)

        # Query Masking
        query_masks = mask[1]  # (N, T_q)
        query_masks = tf.tile(query_masks, [num_heads, 1])  # (h*N, T_q)
        query_masks = tf.tile(tf.expand_dims(query_masks, -1), [1, 1, tf.shape(keys)[1]])  # (h*N, T_q, T_k)
        outputs *= query_masks  # broadcasting. (N, T_q, C)

        # Dropouts
        # outputs2 = tf.layers.dropout(outputs, rate=dropout_rate, training=tf.convert_to_tensor(is_training))

        # Weighted sum
        # outputs2=tf.transpose(outputs2, perm=[0,2,1,3])

        outputs2 = tf.matmul(outputs, V_)  # ( h*N, T_q, C/h)
        # print(tf.shape(outputs2))

        # Restore shape
        outputs2 = tf.concat(tf.split(outputs2, num_heads, axis=0), axis=2)  # (N, T_q, C)

        # Residual connection
        outputs2 += queries + temporal_pos_enc

        # Normalize
        outputs2 = normalize(outputs2)  # (N, T_q, C)

    return outputs2, outputs


def gated_convolution(inputs, hidden_units, scope='gated_convolution', reuse=None):
    with tf.variable_scope(scope, reuse=reuse):
        inputs = tf.cast(inputs, tf.float32)  # [N, T, C]
        inputs_norm = normalize(inputs)
        params_A = {"inputs": inputs_norm, "filters": hidden_units, "kernel_size": 3, "padding": "same",
                    "activation": None, "use_bias": True}
        params_B = {"inputs": inputs_norm, "filters": hidden_units, "kernel_size": 3, "padding": "same",
                    "activation": tf.nn.sigmoid, "use_bias": True}
        A = tf.layers.conv1d(**params_A)
        B = tf.layers.conv1d(**params_B)
        outputs = tf.multiply(A, B)
        outputs += inputs
    return outputs


def construct_pos_mask(maxlen, stride=32, c=2):
    width = int(stride + (maxlen - stride) / stride * c)  # 可能attention的最大数量
    pos_mask_bool = np.zeros([maxlen, maxlen], dtype=bool)  # [T, T]
    pos_mask = -np.ones([maxlen, width], dtype=int)  # [T, width]
    for i in range(maxlen):
        for j in range(maxlen):
            if j <= i:
                if j // stride == i // stride:
                    pos_mask_bool[i, j] = True
                else:
                    if j % stride >= stride - c:
                        pos_mask_bool[i, j] = True
            else:
                break
        cur_pos_bool = pos_mask_bool[i, :]
        for jj, each in enumerate(np.where(cur_pos_bool)[0]):  # np.where返回索引，这里是返回行索引。jj为索引，each为值（这里指的是np.where的行索引）
            pos_mask[i, jj] = each
    return pos_mask  # [T, width]


def get_attend_inputs(inputs, pos_mask):  # get attention_inputs
    inputs = tf.cast(inputs, tf.float32)  # [N, T, C]
    N = tf.shape(inputs)[0]
    T = inputs.get_shape().as_list()[1]
    pos_mask_mat = tf.one_hot(pos_mask, depth=T, dtype=tf.float32)  # [T, width, T]
    pos_mask_mat = tf.tile(tf.expand_dims(pos_mask_mat, 0), [N, 1, 1, 1])  # [N, T, width, T]
    inputs = tf.tile(tf.expand_dims(inputs, 1), [1, T, 1, 1])  # [N, T, T, C]
    outputs = tf.matmul(pos_mask_mat, inputs)  # [N, T, width, C]
    return outputs


def sparse_attention(inputs, num_unit, num_heads,
                     scope='sparse_attention', reuse=None, pos_mask=None):
    """
    Fixed factorized attention of sparse transformer
    :param inputs:
    :param num_unit:
    :param num_heads:
    :param scope:
    :param reuse:
    :param pos_mask:
    :return:
    """
    with tf.variable_scope(scope, reuse=reuse):
        inputs = tf.cast(inputs, tf.float32)  # [N, T, C] C：hidden_unit
        pos_mask = tf.convert_to_tensor(pos_mask, tf.int32)  # [T, width]
        attend_inputs = get_attend_inputs(inputs, pos_mask)  # [N, T, width, C] as key and value
        inputs_exp = tf.expand_dims(inputs, 2)  # [N, T, 1, C]  as query

        query = tf.layers.dense(inputs_exp, units=num_unit, activation=tf.nn.relu)
        key = tf.layers.dense(attend_inputs, units=num_unit, activation=tf.nn.relu)
        value = tf.layers.dense(attend_inputs, units=num_unit, activation=tf.nn.relu)

        # split with multi heads
        q_ = tf.concat(tf.split(query, num_heads, axis=-1), axis=0)  # [h*N, T, 1, C/h]
        k_ = tf.concat(tf.split(key, num_heads, axis=-1), axis=0)  # [h*N, T, width, C/h]
        v_ = tf.concat(tf.split(value, num_heads, axis=-1), axis=0)  # [h*N, T, width, C/h]

        # Multiplication
        outputs = tf.matmul(q_, tf.transpose(k_, [0, 1, 3, 2]))  # (h*N, T, 1, width)

        # Scale
        outputs = outputs / (k_.get_shape().as_list()[-1] ** 0.5)

        # Key Masking
        key_masks = tf.sign(tf.abs(tf.reduce_sum(key, axis=-1)))  # (N, T, width)
        key_masks = tf.tile(key_masks, [num_heads, 1, 1])  # (h*N, T, width)
        key_masks = tf.expand_dims(key_masks, 2)  # (h*N, T, 1, width)
        paddings = tf.ones_like(outputs) * (-2 ** 32 + 1)
        outputs = tf.where(tf.equal(key_masks, 0), paddings, outputs)  # (h*N, T_q, T_k)

        # Activation
        outputs = tf.nn.softmax(outputs)

        # Multiplication
        outputs = tf.matmul(outputs, v_)  # [h*N, T, 1, C/h]

        # Restore shape
        outputs = tf.concat(tf.split(outputs, num_heads, axis=0), axis=-1)  # [N, T, 1, C]
        outputs = tf.reshape(outputs, tf.shape(inputs))

        # post attention weight
        outputs = tf.layers.dense(outputs, num_unit, use_bias=False)

        return outputs


def feedforward_sparse(inputs, num_units,
                       scope="multihead_attention_feedforward", reuse=None):
    with tf.variable_scope(scope, reuse=reuse):
        # Inner layer
        params = {"inputs": inputs, "filters": num_units[0], "kernel_size": 1,
                  "activation": tf.nn.elu, "use_bias": True}
        outputs = tf.layers.conv1d(**params)

        # Readout layer
        params = {"inputs": outputs, "filters": num_units[1], "kernel_size": 1,
                  "activation": None, "use_bias": True}
        outputs = tf.layers.conv1d(**params)
        #
        # # Residual connection
        # outputs += inputs
        #
        # # Normalize
        # outputs = normalize(outputs)

    return outputs  # (batch_size, maxlen, hidden_units)


def convolution_align(inputs, align_len, scope='convolution_align', reuse=None):
    with tf.variable_scope(scope, reuse=reuse):
        inputs = tf.cast(inputs, tf.float32)  # [N, T, C]
        maxlen = inputs.get_shape().as_list()[1]
        hidden_units = inputs.get_shape().as_list()[2]
        stride_size = align_len * 2
        kernel_size = maxlen - (align_len - 1) * stride_size
        assert kernel_size >= 1
        params = {"inputs": inputs, "filters": hidden_units, "kernel_size": kernel_size, "padding": "valid",
                  "strides": stride_size, "activation": tf.nn.relu, "use_bias": False}
        aligned_outputs = tf.layers.conv1d(**params)
        outputs = aligned_outputs
    return outputs


def get_last_emb(inputs, time, lastlen, scope='get_last_emb', reuse=None):
    with tf.variable_scope(scope, reuse=reuse):
        inputs = tf.cast(inputs, tf.float32)  # [N, T, C]
        maxlen = tf.shape(inputs)[1]
        inputs_trans = tf.transpose(inputs, [1, 0, 2])  # [T, N, C]
        outputs_trans = inputs_trans[maxlen - lastlen:, :, :]  # [lastlen, N, C]
        outputs = tf.transpose(outputs_trans, [1, 0, 2])  # [N, lastlen, C]
        time_trans = tf.transpose(time, [1, 0])  # [T, N]
        time_output_trans = time_trans[maxlen - lastlen:, :]
        time_output = tf.transpose(time_output_trans, [1, 0])
    return outputs, time_output


def relative_multihead_attention(queries, keys, num_units, num_heads=4, dropout_rate=0, is_training=True,
                                 causality=False, scope="relative_multihead_attention", reuse=None, temporal_pos_enc=None):
    '''
    Compute the relative temporal attention to fuse the time information
    Inspired by relative position encoding in Transformer-XL
    :param queries: the input embedding of the token seq
    :param keys: the input embedding of the token seq
    :param num_units:
    :param num_heads:
    :param dropout_rate:
    :param is_training:
    :param causality:
    :param scope:
    :param reuse:
    :param temporal_pos_enc: the temporal position encoding
    :return:
    '''
    with tf.variable_scope(scope, reuse=reuse):
        # Set the fall back option for num_units
        queries = tf.cast(queries, tf.float32)

        N = tf.shape(queries)[0]
        T = tf.shape(queries)[1]
        C = num_units

        # Initialization for relative temporal attention module
        u_vec = tf.get_variable('u_vec',
                                dtype=tf.float32,
                                shape=[1, num_units],
                                initializer=tf.contrib.layers.xavier_initializer(),
                                # regularizer=tf.contrib.layers.l2_regularizer(scale=0.1)
                                )
        v_vec = tf.get_variable('v_vec',
                                dtype=tf.float32,
                                shape=[1, num_units],
                                initializer=tf.contrib.layers.xavier_initializer(),
                                # regularizer=tf.contrib.layers.l2_regularizer(scale=0.1)
                                )
        u_vec = tf.tile(u_vec, [T, 1])  # [max_len, num_units]
        v_vec = tf.tile(v_vec, [T, 1])  # [max_len, num_nuits]
        u_vec = tf.tile(tf.expand_dims(u_vec, 0), [N, 1, 1])  # [batch_size, max_len, num_units]
        v_vec = tf.tile(tf.expand_dims(v_vec, 0), [N, 1, 1])  # [batch_size, max_len, num_units]

        # Linear projections
        Q = tf.layers.dense(queries, num_units, activation=tf.nn.relu)  # (N, T_q, C)
        K = tf.layers.dense(keys, num_units, activation=tf.nn.relu)  # (N, T_k, C)
        V = tf.layers.dense(keys, num_units, activation=tf.nn.relu)  # (N, T_k, C)
        PE = tf.layers.dense(temporal_pos_enc,
                             num_units,
                             activation=tf.nn.relu,
                             kernel_regularizer=tf.contrib.layers.l2_regularizer(scale=0.1))
        # [batch_size, max_len, num_units]

        # Split and concat
        Q_ = tf.concat(tf.split(Q, num_heads, axis=2), axis=0)  # (h*N, T_q, C/h)
        K_ = tf.concat(tf.split(K, num_heads, axis=2), axis=0)  # (h*N, T_k, C/h)
        V_ = tf.concat(tf.split(V, num_heads, axis=2), axis=0)  # (h*N, T_k, C/h)
        PE_ = tf.concat(tf.split(PE, num_heads, axis=2), axis=0)  # [num_heads*batch_size, max_len, num_units/num_heads]
        u_vec_ = tf.concat(tf.split(u_vec, num_heads, axis=2), axis=0)  # [num_heads*batch_size, max_len, num_units/num_heads]
        v_vec_ = tf.concat(tf.split(v_vec, num_heads, axis=2), axis=0)  # [num_heads*batch_size, max_len, num_units/num_heads]

        # Multiplication
        outputs = tf.matmul(Q_, tf.transpose(K_, [0, 2, 1]))  # (h*N, T_q, T_k)

        # Relative temporal attention
        outputs += tf.matmul(Q_, tf.transpose(PE_, [0, 2, 1]))
        outputs += tf.matmul(u_vec_, tf.transpose(K_, [0, 2, 1]))
        outputs += tf.matmul(v_vec_, tf.transpose(PE_, [0, 2, 1]))

        # Scale
        outputs = outputs / (K_.get_shape().as_list()[-1] ** 0.5)

        # Key Masking
        key_masks = tf.sign(tf.abs(tf.reduce_sum(keys + temporal_pos_enc, axis=-1)))  # (N, T_k)
        key_masks = tf.tile(key_masks, [num_heads, 1])  # (h*N, T_k)
        key_masks = tf.tile(tf.expand_dims(key_masks, 1), [1, tf.shape(queries)[1], 1])  # (h*N, T_q, T_k)

        paddings = tf.ones_like(outputs) * (-2 ** 32 + 1)
        outputs = tf.where(tf.equal(key_masks, 0), paddings, outputs)  # (h*N, T_q, T_k)

        # Causality = Future blinding
        if causality:
            diag_vals = tf.ones_like(outputs[0, :, :])  # (T_q, T_k)
            #########Causality=True#########
            # tril = tf.linalg.LinearOperatorLowerTriangular(diag_vals).to_dense()  # (T_q, T_k)
            tril = tf.linalg.LinearOperatorLowerTriangular(diag_vals).to_dense()  # (T_q, T_k)
            masks = tf.tile(tf.expand_dims(tril, 0), [tf.shape(outputs)[0], 1, 1])  # (h*N, T_q, T_k)

            paddings = tf.ones_like(masks) * (-2 ** 32 + 1)
            outputs = tf.where(tf.equal(masks, 0), paddings, outputs)  # (h*N, T_q, T_k)

        # Activation
        outputs = tf.nn.softmax(outputs)  # (h*N, T_q, T_k)

        # Query Masking
        query_masks = tf.sign(tf.abs(tf.reduce_sum(queries + temporal_pos_enc, axis=-1)))  # (N, T_q)
        query_masks = tf.tile(query_masks, [num_heads, 1])  # (h*N, T_q)
        query_masks = tf.tile(tf.expand_dims(query_masks, -1), [1, 1, tf.shape(keys)[1]])  # (h*N, T_q, T_k)
        outputs *= query_masks  # broadcasting. (N, T_q, C)

        outputs2 = tf.matmul(outputs, V_)  # ( h*N, T_q, C/h)

        # Restore shape
        outputs2 = tf.concat(tf.split(outputs2, num_heads, axis=0), axis=2)  # (N, T_q, C)
        outputs = outputs2

        # post attention weight
        outputs = tf.layers.dense(outputs, num_units, use_bias=False)

    return outputs
