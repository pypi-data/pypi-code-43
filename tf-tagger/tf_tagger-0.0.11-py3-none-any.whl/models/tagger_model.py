# -*- coding: utf-8 -*-
import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

import numpy as np
import tensorflow as tf

from .embed import Embed
from .encoder import Encoder
from .decoder import Decoder
from .encoder_bert import EncoderBert

class TaggerModel(tf.keras.Model):
    def __init__(self,
                 embedding_size,
                 hidden_size,
                 vocab_size,
                 tag_size,
                 dropout,
                 layer_size,
                 bidirectional,
                 bert=False,
                 bert_model_dir=None,
                 bert_max_length=4096):
        super(TaggerModel, self).__init__(self)
        self.bert = bert
        if bert:
            self.emb = EncoderBert(
                max_length=bert_max_length,
                model_dir=bert_model_dir
            )
        else:
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


if __name__ == "__main__":
    tm = TaggerModel(
        embedding_size=None,
        hidden_size=768,
        vocab_size=None,
        tag_size=10,
        dropout=.0,
        layer_size=None,
        bidirectional=None,
        bert=True,
        bert_model_dir='./chinese_L-12_H-768_A-12',
        bert_max_length=4096)
    from ..utils.tokenizer import Tokenizer
    tokenizer = Tokenizer('./chinese_L-12_H-768_A-12/vocab.txt')
    ids = tokenizer.transform([['我', '爱', '你']])
    r = tm(ids)
    print(r)