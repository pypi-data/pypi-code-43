#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2019 NetEase.com, Inc. All Rights Reserved.
# Copyright 2019, The NSH Recommendation Project, The User Persona Group, The Fuxi AI Lab.
"""
ConvAlignTransformer

Authors: wangkai02(wangkai02@corp.netease.com)
Phone: 17816029211
Date: 2019/9/11
"""

from .contrib import *


class ConvAlignTransformer(tf.keras.layers.Layer):
    def __init__(self, config):
        self.supports_masking = False
        self.config = config
        super(ConvAlignTransformer, self).__init__()

    def call(self, x, mask=None):
        # Embedding
        embed_inputs = x[0]
        time = x[1]
        convtransformer_hidden_units = self.config['convtransformer_hidden_units']
        maxlen = self.config['maxlen']

        print('embed_inputs:', embed_inputs.get_shape())

        with tf.variable_scope("encoder"):
            # build implicit behavior embedding
            behavior_emb = convolution_align(embed_inputs, self.config['convtransformer_align_len'])

            # get lastlen embedding, time
            last_emb, last_time = get_last_emb(embed_inputs, time, self.config['convtransformer_lastlen'])

            # behavior encoder 以前购买序列encoder
            with tf.variable_scope("behavior_encoder"):
                pos_enc = positional_encoding(behavior_emb, convtransformer_hidden_units)

                with tf.variable_scope("behavior_attention"):
                    enc = behavior_emb
                    enc_a = normalize(enc)
                    enc_a = relative_multihead_attention(queries=enc_a,
                                                         keys=enc_a,
                                                         num_units=convtransformer_hidden_units,
                                                         num_heads=self.config['convtransformer_num_heads'],
                                                         temporal_pos_enc=pos_enc,
                                                         causality=True)
                    enc_a = tf.layers.dropout(enc_a, rate=self.config['convtransformer_dropout_rate'],
                                              training=tf.convert_to_tensor(self.config['convtransformer_is_training']))
                    enc_b = normalize(enc + enc_a)
                    enc_b = feedforward_sparse(enc_b,
                                               num_units=[4 * convtransformer_hidden_units, convtransformer_hidden_units])
                    enc_b = tf.layers.dropout(enc_b, rate=self.config['convtransformer_dropout_rate'],
                                              training=tf.convert_to_tensor(self.config['convtransformer_is_training']))
                    enc += enc_a + enc_b
                    enc_behavior = enc

            # lastlen decoder
            with tf.variable_scope("lastlen_decoder"):
                temporal_log_pe = temporal_log_time_positional_encoding(last_emb, convtransformer_hidden_units,
                                                                        last_time)
                with tf.variable_scope("lastlen_attention"):
                    enc = last_emb
                    enc_a = normalize(enc)
                    enc_a = relative_multihead_attention(queries=enc_a,
                                                         keys=enc_a,
                                                         num_units=convtransformer_hidden_units,
                                                         num_heads=self.config['convtransformer_num_heads'],
                                                         temporal_pos_enc=temporal_log_pe,
                                                         causality=True)
                    enc_a = tf.layers.dropout(enc_a, rate=self.config['convtransformer_dropout_rate'],
                                              training=tf.convert_to_tensor(self.config['convtransformer_is_training']))
                    enc_b = normalize(enc + enc_a)
                    enc_b = feedforward_sparse(enc_b,
                                               num_units=[4 * convtransformer_hidden_units, convtransformer_hidden_units])
                    enc_b = tf.layers.dropout(enc_b, rate=self.config['convtransformer_dropout_rate'],
                                              training=tf.convert_to_tensor(self.config['convtransformer_is_training']))
                    enc += enc_a + enc_b
                    enc_last = enc

            # # long-short-term decoder
            with tf.variable_scope("long_short_term_decoder"):
                # enc_behavior = behavior_emb
                # pos_enc = positional_encoding(behavior_emb, hp.hidden_units)
                with tf.variable_scope("long_short_attention"):
                    enc = enc_last
                    enc_k = normalize(enc_behavior)
                    enc_a = normalize(enc)
                    enc_a = relative_multihead_attention(queries=enc_a,
                                                         keys=enc_k,
                                                         num_units=convtransformer_hidden_units,
                                                         num_heads=self.config['convtransformer_num_heads'],
                                                         temporal_pos_enc=pos_enc)
                    enc_a = tf.layers.dropout(enc_a, rate=self.config['convtransformer_dropout_rate'],
                                              training=tf.convert_to_tensor(self.config['convtransformer_is_training']))
                    enc_b = normalize(enc + enc_a)
                    enc_b = feedforward_sparse(enc_b,
                                               num_units=[4 * convtransformer_hidden_units, convtransformer_hidden_units])
                    enc_b = tf.layers.dropout(enc_b, rate=self.config['convtransformer_dropout_rate'],
                                              training=tf.convert_to_tensor(self.config['convtransformer_is_training']))
                    enc += enc_a + enc_b
                    enc_long_short = enc

            # flatten
            enc_long_short = normalize(enc_long_short)
            enc_flat = tf.reshape(enc_long_short, [-1, self.config['convtransformer_lastlen'] * convtransformer_hidden_units])
            # MLP
            enc_mlp = tf.layers.dense(enc_flat, units=self.config['convtransformer_num_heads'] * convtransformer_hidden_units,
                                      activation=tf.nn.relu)
            print('enc_mlp', enc_mlp.get_shape())

        return enc_mlp

    # def compute_output_shape(self, input_shape):
    #     return (input_shape[0][0],input_shape[0][1])

    def compute_mask(self, input, input_mask=None):
        # need not to pass the mask to next layers
        return None
