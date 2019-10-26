
import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

import numpy as np
import tensorflow as tf
import tensorflow_addons as tfa


class Decoder(tf.keras.Model):

    def __init__(self, tag_size):
        super(Decoder, self).__init__(self)
        self.tag_size = tag_size
        w_init = tf.random_normal_initializer()
        # w_init = tf.constant_initializer(0.0)
        self.transition_params = tf.Variable(
            initial_value=w_init(
                shape=(tag_size, tag_size),
                dtype=tf.dtypes.float32),
            name='crf/transition_params'
        )

    def call(self, inputs, lengths):
        """
        parameters:
            inputs [B, L, T]
            lengths [B]
        returns: [B, L]
        """
        tags_id, _ = tfa.text.crf_decode(
            inputs, self.transition_params, lengths)
        return tags_id

    def compute_loss(self, inputs, lengths, tags):
        """
        parameters:
            inputs [B, L, T]
            lengths [B]
            tags [B, L, N]
        returns: loss
        """
        sequence_log_likelihood, _ = tfa.text.crf_log_likelihood(
            inputs=inputs,
            tag_indices=tags,
            sequence_lengths=lengths,
            transition_params=self.transition_params)
        loss = tf.reduce_mean(-sequence_log_likelihood)
        return loss