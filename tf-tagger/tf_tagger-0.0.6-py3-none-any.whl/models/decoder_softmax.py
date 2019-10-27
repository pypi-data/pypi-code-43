# -*- coding: utf-8 -*-
import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

import numpy as np
import tensorflow as tf


class DecoderSoftmax(tf.keras.Model):

    def __init__(self, tag_size):
        super(DecoderSoftmax, self).__init__(self)
        self.tag_size = tag_size

    def call(self, inputs, lengths):
        """
        parameters:
            inputs [B, L, T]
            lengths [B]
        returns: [B, L]
        """
        tags_prob = tf.nn.softmax(inputs)
        tags_id = tf.argmax(tags_prob, axis=2)
        return tags_id

    def compute_loss(self, inputs, lengths, tags):
        """
        parameters:
            inputs [B, L, T]
            lengths [B]
            tags [B, L, N]
        returns: loss
        """
        loss =  tf.nn.sparse_softmax_cross_entropy_with_logits(
            tags, inputs)
        loss = tf.reduce_mean(loss)
        return loss