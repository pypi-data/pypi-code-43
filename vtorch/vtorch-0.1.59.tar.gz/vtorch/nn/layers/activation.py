from torch import nn


class Activation(nn.Module):
    def __init__(self, activation_type: str = None):
        super().__init__()
        self.activation_layer = self._get_activation_layer(activation_type)

    def forward(self, input_data):
        if self.activation_layer is not None:
            return self.activation_layer(input_data)
        return input_data

    @staticmethod
    def _get_activation_layer(activation_type: str) -> nn.Module:
        if activation_type is None:
            return None
        elif activation_type == "sigmoid":
            return nn.Sigmoid()
        elif activation_type == "softmax":
            return nn.Softmax(dim=1)
        else:
            raise NotImplementedError
