# -*- coding: utf-8 -*-
import torch.nn as nn


class TorchModelMixin(nn.Module):

    @property
    def logits(self):
        return self._logits

    def __init__(self):
        self._logits = None
        super().__init__()

    def forward(self, *input):
        self._logits = super().forward(input)
        return self._logits

