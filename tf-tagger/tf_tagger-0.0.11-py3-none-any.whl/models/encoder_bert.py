# -*- coding: utf-8 -*-
import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

import numpy as np
import tensorflow as tf
from bert import BertModelLayer
from bert import params_from_pretrained_ckpt
from bert import load_stock_weights


class EncoderBert(tf.keras.Model):

    def __init__(self, max_length=4096, model_dir=None):
        super(EncoderBert, self).__init__(self)

        bert_params = params_from_pretrained_ckpt(model_dir)
        # bert_params.num_layers = 4
        l_bert = BertModelLayer.from_params(bert_params, name="bert")

        l_input_ids = tf.keras.layers.Input(shape=(max_length,), dtype='int32')
        l_token_type_ids = tf.keras.layers.Input(shape=(max_length,), dtype='int32')

        # using the default token_type/segment id 0
        output = l_bert(l_input_ids)
        model = tf.keras.Model(inputs=l_input_ids, outputs=output)
        model.build(input_shape=(None, max_length))
        model.trainable = False
        self.model = model

        if model_dir is not None:
            bert_ckpt_file = os.path.join(model_dir, "bert_model.ckpt")
            load_stock_weights(l_bert, bert_ckpt_file)

    def call(self, inputs, mask=None):
        return self.model(inputs)


if __name__ == "__main__":
    from ..utils.tokenizer import Tokenizer
    tokenizer = Tokenizer('./chinese_L-12_H-768_A-12/vocab.txt')
    ids = tokenizer.transform([['我', '爱', '你']])
    en = EncoderBert(model_dir='./chinese_L-12_H-768_A-12')
    r = en(ids)
    print(r)
