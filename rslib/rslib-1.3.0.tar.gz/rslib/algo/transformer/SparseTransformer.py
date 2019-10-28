#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2019 NetEase.com, Inc. All Rights Reserved.
# Copyright 2019, The NSH Recommendation Project, The User Persona Group, The Fuxi AI Lab.
"""
SparseTransformer

Authors: wangkai02(wangkai02@corp.netease.com)
Phone: 17816029211
Date: 2019/9/11
"""

from .contrib import *

class SparseTransformer(tf.keras.layers.Layer):
    def __init__(self, config):
        self.supports_masking = False
        self.config = config
        super(SparseTransformer, self).__init__()

    def call(self, x, mask=None):
        # Embedding
        embed_inputs = x[0]
        time = x[1]
        sptransformer_hidden_units = self.config['sptransformer_hidden_units']
        maxlen = self.config['maxlen']

        # Encoder
        print('[sptransformer_model] enc_input', embed_inputs.get_shape())
        with tf.variable_scope("encoder"):
            # fuse temporal info
            temporal_log_pe = temporal_log_time_positional_encoding(embed_inputs, sptransformer_hidden_units, time)
            embed_inputs += temporal_log_pe

            # gated_conv
            gated_conv = gated_convolution(embed_inputs, sptransformer_hidden_units)

            # fixed sparse residual attention module
            # Blocks
            pos_mask = construct_pos_mask(maxlen)

            enc = gated_conv
            for i in range(self.config['sptransformer_num_blocks']):
                with tf.variable_scope("num_blocks_{}".format(i)):
                    enc_a = normalize(enc)
                    enc_a = sparse_attention(enc_a,
                                             num_unit=sptransformer_hidden_units,
                                             num_heads=self.config['sptransformer_num_heads'],
                                             pos_mask=pos_mask)
                    enc_a = tf.layers.dropout(enc_a, rate=self.config['sptransformer_dropout_rate'],
                                              training=tf.convert_to_tensor(self.config['sptransformer_is_training']))
                    enc_b = normalize(enc + enc_a)
                    enc_b = feedforward_sparse(enc_b,
                                               num_units=[4 * sptransformer_hidden_units, sptransformer_hidden_units])
                    enc_b = tf.layers.dropout(enc_b, rate=self.config['sptransformer_dropout_rate'],
                                              training=tf.convert_to_tensor(self.config['sptransformer_is_training']))
                    enc += enc_a + enc_b

            # flatten
            enc = normalize(enc)
            enc_flat = tf.reshape(enc, [-1, maxlen * sptransformer_hidden_units])
            # MLP
            enc_mlp = tf.layers.dense(enc_flat, units=self.config['sptransformer_num_heads'] * sptransformer_hidden_units,
                                      activation=tf.nn.relu)
            print('enc_mlp', enc_flat.get_shape())

        return enc_mlp

    # def compute_output_shape(self, input_shape):
    #     return (input_shape[0][0],input_shape[0][1])

    def compute_mask(self, input, input_mask=None):
        # need not to pass the mask to next layers
        return None
