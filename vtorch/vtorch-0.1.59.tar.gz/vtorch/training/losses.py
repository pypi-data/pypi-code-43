import torch
from vtorch.common import Registrable


class Loss(Registrable):
    """
    Pytorch has a number of built-in activation functions.  We group those here under a common
    type, just to make it easier to configure and instantiate them ``from_params`` using
    ``Registrable``.
    """
    def forward(self, input, target):
        raise NotImplementedError


Registrable._registry[Loss] = {  # type: ignore
        "bce": torch.nn.BCELoss,
        "bce_with_logits": torch.nn.BCEWithLogitsLoss,
        "ce": torch.nn.CrossEntropyLoss
}
