import torch
import transformers

from typing import List, Generator, Tuple

from vtorch.common import Registrable


def prepare_parameters_group(named_model_parameters: Generator[Tuple[str, torch.nn.Parameter], None, None],
                             no_decay_layers: List[str], weight_decay: float):
    return [
        {'params': [p for n, p in named_model_parameters if not any(nd in n for nd in no_decay_layers)],
         'weight_decay': weight_decay},
        {'params': [p for n, p in named_model_parameters if any(nd in n for nd in no_decay_layers)],
         'weight_decay': 0.0}
        ]


class Optimizer(Registrable):
    """
    Pytorch has a number of built-in activation functions.  We group those here under a common
    type, just to make it easier to configure and instantiate them ``from_params`` using
    ``Registrable``.
    """
    def step(self, closure=None):
        raise NotImplementedError


Registrable._registry[Optimizer] = {  # type: ignore
        "sgd": torch.optim.SGD,
        "adam": torch.optim.Adam,
        "adamW": transformers.AdamW
}
