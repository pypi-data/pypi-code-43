#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2019 NetEase.com, Inc. All Rights Reserved.
# Copyright 2019, The NSH Recommendation Project, The User Persona Group, The Fuxi AI Lab.
"""
Transformer

Authors: wangkai02(wangkai02@corp.netease.com)
Phone: 17816029211
Date: 2019/9/11
"""

from .contrib import *

class Transformer(tf.keras.layers.Layer):
    def __init__(self, config):
        self.supports_masking = False
        self.config = config
        super(Transformer, self).__init__()

    def call(self, x, mask=None):
        # Embedding
        enc_embed_input = x[0]
        time = x[1]
        time_gap = x[2]
        hidden_units = self.config['transformer_hidden_units']
        mask = [tf.cast(mask[0],tf.float32),tf.cast(mask[1],tf.float32)]

        print('[transformer_model] enc_input', enc_embed_input.get_shape())
        with tf.variable_scope("encoder"):
            enc = enc_embed_input

            # temporal position encoding
            temporal_pe = None
            if self.config['transformer_is_temporal_pe']:
                temporal_pe = temporal_positional_encoding(enc_embed_input, num_units=hidden_units,
                                                           time_stamp=time,
                                                           scale=False,
                                                           scope='enc_temporal_pe')
                enc += temporal_pe
            if self.config['transformer_is_pe']:
                # Position Encoding
                enc += positional_encoding(enc_embed_input,
                                           num_units=hidden_units,
                                           scale=False,
                                           scope="enc_pe")

            # event-time joint embedding
            if self.config['transformer_is_event_time_joint_emb']:
                enc = event_time_joint_embed(enc, time_gap, proj_size=int(hidden_units / 2))

            if self.config['transformer_is_event_time_joint_emb_v2']:
                enc = event_time_joint_embed_ver2(enc, time_gap, proj_size=int(hidden_units / 8))

            # time mask
            if self.config['transformer_is_time_mask']:
                enc = time_mask(enc, time_gap, context_size=int(hidden_units / 2))

            # Combine time interval
            if self.config['transformer_is_combine_time']:
                enc = concat_time_interval(enc, time_gap)

            # Dropout
            if self.config['transformer_is_training']:
                enc = tf.layers.dropout(enc,
                                        rate=self.config['transformer_dropout_rate'],
                                        training=tf.convert_to_tensor(self.config['transformer_is_training']))
            # Blocks
            for i in range(self.config['transformer_num_blocks']):
                with tf.variable_scope("num_blocks_{}".format(i)):
                    if self.config['transformer_is_hetero_temporal_mask']:
                        # Hetero-Temporal Multihead Attention
                        enc, align_score = hetero_temporal_multihead_attention(queries=enc,
                                                                               keys=enc,
                                                                               num_units=hidden_units,
                                                                               num_heads=self.config['transformer_num_heads'],
                                                                               dropout_rate=self.config['transformer_dropout_rate'],
                                                                               is_training=self.config['transformer_is_training'],
                                                                               T_input=time,
                                                                               avg=self.config['transformer_avg_time_gap'],
                                                                               band=float(self.config[
                                                                                              'transformer_avg_time_gap'] / 2),
                                                                               mask = mask)
                    elif self.config['transformer_is_temporal_mask']:
                        # Temporal Mask Multihead Attention
                        enc, align_score = temporal_mask_multihead_attention(queries=enc,
                                                                             keys=enc,
                                                                             num_units=hidden_units,
                                                                             num_heads=self.config['transformer_num_heads'],
                                                                             dropout_rate=self.config['transformer_dropout_rate'],
                                                                             is_training=self.config['transformer_is_training'],
                                                                             T_input=time,
                                                                             band=float(self.config['transformer_avg_time_gap'] / 2),
                                                                             mask = mask)
                    elif self.config['transformer_is_relative_temporal_attention'] and self.config['transformer_is_temporal_pe']:
                        # Relative Temporal Multihead Attention
                        enc, align_score = relative_temporal_multihead_attention(queries=enc,
                                                                                 keys=enc,
                                                                                 num_units=hidden_units,
                                                                                 num_heads=self.config['transformer_num_heads'],
                                                                                 dropout_rate=self.config['transformer_dropout_rate'],
                                                                                 is_training=self.config['transformer_is_training'],
                                                                                 temporal_pos_enc=temporal_pe,
                                                                                 mask = mask)
                    else:
                        # Multihead Attention
                        enc, align_score = multihead_attention(queries=enc,
                                                               keys=enc,
                                                               num_units=hidden_units,
                                                               num_heads=self.config['transformer_num_heads'],
                                                               dropout_rate=self.config['transformer_dropout_rate'],
                                                               is_training=self.config['transformer_is_training'],
                                                               mask = mask)
                    enc = feedforward(enc, num_units=[4 * hidden_units, hidden_units])

            query_encoding = tf.keras.layers.GlobalAveragePooling1D()(enc)
            enc3 = tf.reshape(query_encoding, [-1, hidden_units])

        return enc3

    # def compute_output_shape(self, input_shape):
    #     return (input_shape[0][0],input_shape[0][1])

    def compute_mask(self, input, input_mask=None):
        # need not to pass the mask to next layers
        return None
