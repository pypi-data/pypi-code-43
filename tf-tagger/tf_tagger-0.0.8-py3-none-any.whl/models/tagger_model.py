# -*- coding: utf-8 -*-
import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

import numpy as np
import tensorflow as tf
# import tensorflow_addons as tfa

from .embed import Embed
from .encoder import Encoder
from .decoder import Decoder

class TaggerModel(tf.keras.Model):
    def __init__(self,
                 embedding_size,
                 hidden_size,
                 vocab_size,
                 tag_size,
                 dropout,
                 layer_size,
                 bidirectional):
        super(TaggerModel, self).__init__(self)
        self.emb = Embed(
            embedding_size=embedding_size,
            vocab_size=vocab_size
        )
        self.en = Encoder(
            embedding_size=embedding_size,
            hidden_size=hidden_size,
            layer_size=layer_size,
            bidirectional=bidirectional
        )
        self.project = tf.keras.models.Sequential([
            tf.keras.layers.Dense(tag_size)
        ])
        self.project.build(input_shape=(None, hidden_size))
        self.de = Decoder(
            tag_size=tag_size
        )
        self.dropout = tf.keras.layers.Dropout(
            dropout, noise_shape=None, seed=None)

    def logits(self, inputs, training=False):
        lengths = tf.reduce_sum(tf.cast(tf.math.greater(inputs, 0), tf.int32), axis=-1)
        mask = tf.greater(inputs, 0)
        x = inputs
        x = self.emb(x)
        if training:
            x = self.dropout(x)
        x = self.en(x, mask)
        if training:
            x = self.dropout(x)
        x = self.project(x)
        if training:
            x = self.dropout(x)
        # x = tf.cast(tf.expand_dims(mask, 2), tf.float32) * x
        return x, lengths

    def call(self, inputs):
        logits, lengths = self.logits(inputs)
        return self.de(logits, lengths)

    def compute_loss(self, inputs, tags):
        logits, lengths = self.logits(inputs, training=True)
        return self.de.compute_loss(logits, lengths, tags)

