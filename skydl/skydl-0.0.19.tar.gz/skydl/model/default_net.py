# -*- coding: utf-8 -*-
from skydl.model.super_net import SuperNet


class DefaultNet(SuperNet):

    def __init__(self, name=None, parser_args=None):
        super().__init__(name=name, parser_args=parser_args)

    def forward(self, *input, **kwargs):
        return super().forward(*input, **kwargs)

    def call_hidden_layers(self, _x, name="predict"):
        return super().call_hidden_layers(_x, name)

    def compile_loss_metrics_optimizer_predict(self, _x, _y, _learning_rate=0.001, devices=[]):
        pass

