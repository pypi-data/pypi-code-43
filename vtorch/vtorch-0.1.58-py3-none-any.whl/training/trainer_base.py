"""
A :class:`~vtorch.training.trainer.Trainer` is responsible for training a
:class:`~vtorch.models.model.Model`.
Typically you might create a configuration file specifying the model and
training parameters and then use :mod:`~vtorch.commands.train`
rather than instantiating a ``Trainer`` yourself.
"""

import logging
from typing import Dict, List, Union, Any

from vtorch.common import Registrable
from vtorch.common.checks import ConfigurationError, check_for_gpu
from vtorch.models.model import Model

logger = logging.getLogger(__name__)


class TrainerBase(Registrable):
    """
    The base class for an AllenNLP trainer. It can do pretty much
    anything you want. Your subclass should implement ``train``
    and also probably ``from_params``.
    """
    default_implementation = "default"

    def __init__(self,
                 serialization_dir: str,
                 cuda_device: Union[int, List] = -1) -> None:
        check_for_gpu(cuda_device)

        self._serialization_dir = serialization_dir

        # Configure GPUs:
        if not isinstance(cuda_device, int) and not isinstance(cuda_device, list):
            raise ConfigurationError("Expected an int or list for cuda_device, got {}".format(cuda_device))

        if isinstance(cuda_device, list):
            self._multiple_gpu = True
            self._cuda_devices = cuda_device
        else:
            self._multiple_gpu = False
            self._cuda_devices = [cuda_device]

    def _move_to_gpu(self, model: Model) -> Model:
        if self._cuda_devices[0] != -1:
            return model.cuda(self._cuda_devices[0])
        else:
            return model

    def train(self) -> Dict[str, Any]:
        """
        Train a model and return the results.
        """
        raise NotImplementedError
