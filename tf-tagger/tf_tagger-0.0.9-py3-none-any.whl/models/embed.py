# -*- coding: utf-8 -*-
import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

import numpy as np
import tensorflow as tf


class Embed(tf.keras.Model):

    def __init__(self, embedding_size, vocab_size):
        super(Embed, self).__init__(self)
        model = tf.keras.Sequential()
        model.add(tf.keras.layers.Embedding(
            vocab_size,
            embedding_size
        ))
        self.model = model

    def call(self, inputs):
        x = inputs
        x = self.model(inputs)
        return x

