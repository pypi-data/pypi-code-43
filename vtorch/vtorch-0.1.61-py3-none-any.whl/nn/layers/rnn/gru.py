from .rnn_layer import RNNLayer
import torch.nn as nn
from overrides import overrides


@RNNLayer.register("gru")
class GRU(RNNLayer, nn.GRU):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @overrides
    def get_output_dim(self) -> int:
        return self.hidden_size * (int(self.bidirectional) + 1)
