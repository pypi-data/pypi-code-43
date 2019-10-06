import pytorch_transformers

from vtorch.common import Registrable


class Scheduler(Registrable):
    """
    Pytorch has a number of built-in activation functions.  We group those here under a common
    type, just to make it easier to configure and instantiate them ``from_params`` using
    ``Registrable``.
    """
    def lr_lambda(self, step):
        raise NotImplementedError


Registrable._registry[Scheduler] = {
    "constant": pytorch_transformers.ConstantLRSchedule,
    "w_linear": pytorch_transformers.WarmupLinearSchedule,
    "w_cosine": pytorch_transformers.WarmupCosineSchedule,
    "w_cosine_hard": pytorch_transformers.WarmupCosineWithHardRestartsSchedule,
}
