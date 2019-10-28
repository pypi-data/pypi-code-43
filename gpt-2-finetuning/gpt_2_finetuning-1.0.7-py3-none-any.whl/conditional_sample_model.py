#!/usr/bin/env python3

import json
import os
import numpy as np
import tensorflow as tf

from .model import default_hparams
from .sample import sample_sequence
from .encoder import get_encoder_from_path

class ConditionalSampleModel:
    def __init__(self, checkpoint_dir, sample_length, 
                 batch_size=1, temperature=1, top_k=40, top_p=0.0):
        self.graph = tf.Graph()
        self.sess = tf.Session(graph=self.graph())
        self.encoder = get_encoder_from_path(checkpoint_dir)
        self.batch_size = batch_size
        self.temperature = temperature
        self.top_k = top_k
        self.top_p = top_p

        self.hparams = default_hparams()
        with open(os.path.join(checkpoint_dir, 'hparams.json')) as f:
            self.hparams.override_from_dict(json.load(f))

        self.sample_length = sample_length
        if self.sample_length is None:
            self.sample_length = self.hparams.n_ctx // 2
        elif self.sample_length > self.hparams.n_ctx:
            raise ValueError("Can't get samples longer than window size: %s" % self.hparams.n_ctx)

        self.input_tokens, self.output = self.graph()

        self.saver = tf.train.Saver()
        ckpt = tf.train.latest_checkpoint(checkpoint_dir)
        self.saver.restore(self.sess, ckpt)

    def graph(self, seed=None):
        with self.graph.as_default():
            input_tokens = tf.placeholder(tf.int32, [self.batch_size, None])
            np.random.seed(seed)
            tf.set_random_seed(seed)
            output = sample_sequence(
                hparams=self.hparams, 
                length=self.sample_length,
                context=input_tokens,
                batch_size=self.batch_size,
                temperature=self.temperature, top_k=self.top_k, top_p=self.top_p
            )

        return input_tokens, output

    def run(self, raw_text, nsamples=1):
        assert nsamples % self.batch_size == 0

        all_samples = []

        input_tokens = self.encoder.encode(raw_text)
        for _ in range(nsamples // self.batch_size):
            out = self.sess.run(output, feed_dict={
                context: [context_tokens for _ in range(self.batch_size)]
            })[:, len(context_tokens):]
            for i in range(self.batch_size):
                all_samples.append(enc.decode(out[i]))
        
        return all_samples
