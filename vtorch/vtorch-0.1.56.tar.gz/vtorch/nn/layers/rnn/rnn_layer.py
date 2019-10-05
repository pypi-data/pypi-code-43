import torch.nn as nn
from vtorch.common.registrable import Registrable


class RNNLayer(nn.Module, Registrable):
    """
    RNN layer is a ``Module`` that is the same as default rnn pytorch layers,
    but registrable and has ``get_output_dim`` method
    """
    def get_output_dim(self) -> int:
        """
        Returns output dim based on input data
        """
        raise NotImplementedError
