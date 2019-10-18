#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : tql-cloudml.
# @File         : bert_keras
# @Time         : 2019-06-20 19:59
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  :

try:
    from utils import ifelse
except Exception as e:
    from ..utils import ifelse

import os

os.environ['TF_KERAS'] = '1'
import pandas as pd
from sklearn.model_selection import train_test_split
# from tql.algo_dl.keras.utils import _DataGenerator as DataGenerator
from tql.algo_dl.keras.utils import DataIter

from keras_bert import load_trained_model_from_checkpoint, Tokenizer, load_vocabulary


from tensorflow.python.keras.layers import *
from tensorflow.python.keras.models import Model
from tensorflow.python.keras.optimizers import Adam
from tensorflow.python.keras.preprocessing.sequence import pad_sequences



bert_dir = ifelse('/Users/yuanjie/Desktop/Data/chinese_L-12_H-768_A-12', '/fds/data/wv/chinese_L-12_H-768_A-12')
data_path = ifelse('./sentiment.tsv.zip', '/fds/data/sentiment.tsv.zip')


config_path = bert_dir + '/bert_config.json'
checkpoint_path = bert_dir + '/bert_model.ckpt'
dict_path = bert_dir + '/vocab.txt'
token_dict = load_vocabulary(dict_path)
bert_model = load_trained_model_from_checkpoint(config_path, checkpoint_path)

for l in bert_model.layers:
    l.trainable = True


# 重写Token
class OurTokenizer(Tokenizer):
    def _tokenize(self, text):
        R = []
        for c in text:
            if c in self._token_dict:
                R.append(c)
            elif self._is_space(c):
                R.append('[unused1]')  # space类用未经训练的[unused1]表示
            else:
                R.append('[UNK]')  # 剩余的字符是[UNK]
        return R


tokenizer = OurTokenizer(token_dict)



x1_in = Input(shape=(None,))
x2_in = Input(shape=(None,))

x = bert_model([x1_in, x2_in])
x = Lambda(lambda x: x[:, 0])(x)
p = Dense(1, activation='sigmoid')(x)

model = Model([x1_in, x2_in], p)
model.compile(
    loss='binary_crossentropy',
    optimizer=Adam(1e-5),  # 用足够小的学习率
    metrics=['accuracy']
)
model.summary()

######################################################

def mapper(X, y):
    X = list(map(lambda x: pad_sequences(x, 256), zip(*map(tokenizer.encode, X))))
    return X, y


######################################################

df = pd.read_csv(data_path, '\t')
X = df.text.astype(str)
y = df.label.values.reshape(-1, 1)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42)

# dg_train = DataGenerator(X_train, y_train, 32, mapper)
# dg_valid = DataGenerator(X_test, y_test, 32, mapper)

dg_train = DataIter(X_train, y_train, 32, mapper)
dg_valid = DataIter(X_test, y_test, 32, mapper)

model.fit_generator(dg_train,
                    epochs=10,
                    validation_data=dg_valid)
