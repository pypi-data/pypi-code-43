# -*- coding: utf-8 -*-
from skydl.model.torch_model_mixin import TorchModelMixin
from skydl.model.super_net import SuperNet


class SuperTorchNet(SuperNet, TorchModelMixin):
    """pytorch net"""
    def __init__(self, name=None, parser_args=None):
        super().__init__(name=name, parser_args=parser_args)
        # 再显式调用其它的__init__(self)
        TorchModelMixin.__init__(self)

    def forward(self, *input, **kwargs):
        return super().forward(*input, **kwargs)

    def call_hidden_layers(self, _x, name="predict"):
        name = 'predict' if name is None else name
        predict = None
        return predict

    def compile_loss_metrics_optimizer_predict(self, _x, _y, _learning_rate=0.001, devices=[]):
        pass


