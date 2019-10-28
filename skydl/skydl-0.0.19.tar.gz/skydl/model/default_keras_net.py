# -*- coding: utf-8 -*-
import tensorflow as tf
from tensorflow import keras
from skydl.model.keras_model_mixin import KerasModelMixin
from skydl.model.super_net import SuperNet


class DefaultKerasNet(SuperNet, KerasModelMixin):
    """
    default keras net
    """
    @property
    def model_proxy(self)->keras.Model:
        """model_proxy maybe None or keras.Model"""
        return self._model_proxy

    def __init__(self, name=None, parser_args=None, keras_layers=[], keras_inputs=None, keras_outputs=None):
        # super()会默认调用第一个父类(SuperNet)的__init__()
        super().__init__(name=name, parser_args=parser_args)
        # 再显式调用其它的__init__(self)
        KerasModelMixin.__init__(self, keras_layers, keras_inputs=keras_inputs, keras_outputs=keras_outputs)
        # 构建keras.Model代理类接受keras_inputs, keras_outputs参数
        if keras_inputs is not None and keras_outputs is not None:
            self._model_proxy = keras.Model(inputs=keras_inputs, outputs=keras_outputs)

    def forward(self, *input, **kwargs):
        return super().forward(*input, **kwargs)

    def call(self, _x: tf.Tensor=None, training: bool=True) -> tf.Tensor:
        return self.forward(_x)

    def call_hidden_layers(self, _x: tf.Tensor=None, name="prediction"):
        if self._model_proxy is None:  # self is subclass of keras.Sequential
            return self.call_layers(_x, name)
        else:
            return self._model_proxy.call(_x)

    def compile_loss_metrics_optimizer_predict(self, _x, _y, _learning_rate=0.001, devices=[]):
        pass


