#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : tql-cloudml.
# @File         : demo
# @Time         : 2019-06-21 15:00
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  :
from mlxtend.data import mnist
from tensorflow.python.keras.utils import np_utils
from tql.algo_dl.keras.utils import DataIter
from tensorflow.python.keras.datasets import mnist

# ConfigKeras(2019).set_seed()

from tql.algo_dl.keras.models import TextCNN

# 加载数据
(x_train, y_train), (x_test, y_test) = mnist.load_data()
x_train = x_train.reshape(x_train.shape[0], -1) / 255.0
y_train = np_utils.to_categorical(y_train, num_classes=10)


model = TextCNN(max_tokens=1000, maxlen=784, embedding_size=100, num_class=10)()
model.compile(loss='binary_crossentropy', optimizer='sgd', metrics=['accuracy'])
model.fit_generator(DataIter(x_train, y_train), epochs=5, validation_freq=0.3)
