# -*- coding: utf-8 -*-
import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

import numpy as np
import tensorflow as tf


class Encoder(tf.keras.Model):

    def __init__(self, embedding_size, hidden_size, layer_size, bidirectional):
        super(Encoder, self).__init__(self)
        inputs = tf.keras.layers.Input(
            shape=(None, embedding_size,),
            dtype=tf.float32)
        mask = tf.keras.layers.Input(
            shape=(None,),
            dtype=tf.bool)
        x = inputs
        for _ in range(layer_size):
            if bidirectional:
                l = tf.keras.layers.Bidirectional(
                    tf.keras.layers.LSTM(
                        hidden_size // 2, return_sequences=True
                    )
                )
            else:
                l = tf.keras.layers.LSTM(hidden_size, return_sequences=True)
            x = l(x, mask=mask)

        self.model = tf.keras.Model(inputs=[inputs, mask], outputs=[x])

    def call(self, inputs, mask):
        return self.model([inputs, mask])
