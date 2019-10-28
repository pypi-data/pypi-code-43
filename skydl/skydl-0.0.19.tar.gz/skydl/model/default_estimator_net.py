# -*- coding: utf-8 -*-
import tensorflow as tf
from skydl.model.super_net import SuperNet
from skydl.model.estimator_model_mixin import EstimatorModelMixin


class DefaultEstimatorNet(SuperNet, EstimatorModelMixin):
    """
    default keras net
    """
    def __init__(self, name=None, parser_args=None, layers=[], model_fn=None, params=None):
        # super()会默认调用第一个父类(SuperNet)的__init__()
        super().__init__(name=name, parser_args=parser_args)
        # 再显式调用其它的__init__(self)
        EstimatorModelMixin.__init__(self, layers, model_fn, params=params)

    def forward(self, *input, **kwargs):
        return super().forward(*input, **kwargs)

    def call(self, _x: tf.Tensor=None, training: bool=True) -> tf.Tensor:
        return self.forward(_x)

    def call_hidden_layers(self, _x: tf.Tensor=None, name="prediction"):
        return self.call_layers(_x, name)

    def compile_loss_metrics_optimizer_predict(self, _x, _y, _learning_rate=0.001, devices=[]):
        pass


