# -*- coding: utf-8 -*-
from skydl.model.default_net import DefaultNet
from skydl.model.super_model import SuperModel
from tensorflow.python import keras


class DefaultModel(SuperModel):

    def adjust_parse_args_value(self):
        super().adjust_parse_args_value()

    def build_network(self):
        return DefaultNet(self.name if self.name else self.__class__.__name__, self.parser_args)

    def load_data(self, *args, **kwargs):
        dict_load_data = super().load_data()
        fashion_mnist = keras.datasets.fashion_mnist
        (train_images, train_labels), (test_images, test_labels) = fashion_mnist.load_data()
        class_names = ['T-shirt/top', 'Trouser', 'Pullover', 'Dress', 'Coat',
                       'Sandal', 'Shirt', 'Sneaker', 'Bag', 'Ankle boot']
        train_images = train_images / 255.0
        test_images = test_images / 255.0
        dict_load_data["train_data"] = train_images
        dict_load_data["test_data"] = test_images
        return dict_load_data

    def fit(self, *args, **kwargs):
        """
        模型训练的启动入口
        子类需要重写该方法
        Training settings: 设置一些参数，每个都有默认值，输入 $python3 main.py -h 可以获得相关帮助
        $python3 main.py -batch_size=32 -log_interval=20
        :return:
        """
        return self

    def evaluate(self, *args, **kwargs):
        return self

    def serving(self, *args, **kwargs):
        return self

    def predict(self, *args, **kwargs):
        """python版的预测接口，返回预测结果"""
        return None





