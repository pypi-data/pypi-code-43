import torch
import numpy as np
from typing import Union, List, Callable, Tuple
from .utils import generate_random_id, readable_number
from .metric import Metric, Epoch, SemSegAccuracy, Loss, EpochTimer

class Model:

    def __init__(self, network: torch.nn.Module, name: str = None, metrics: List[Metric] = None):

        # properties
        self.id: str = generate_random_id()
        self.name: str = name if name else self.network.__class__.__name__
        self.network: torch.nn.Module = network
        self.metrics = metrics if metrics else []

        self.network.to(device='cuda')

        # set default metrics
        self.metrics.append(Epoch())
        self.metrics.append(Loss())
        self.metrics.append(SemSegAccuracy())
        self.metrics.append(EpochTimer())

### Methods called by training strategies
    def training_fn(self, batch, batch_id: int, epoch: int)\
            -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Method should describe training process on one batch and return loss, y_pred and y_true
        :param batch:
        :param batch_id:
        :param epoch:
        :return: loss, y_pred, y_true
        """
        # must return loss to backprop
        raise NotImplementedError

    def backprop_fn(self, loss: torch.Tensor, optimizer: torch.optim.Optimizer) -> None:
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    def validation_fn(self, batch, batch_id: int, epoch: int)\
            -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """

        :param batch:
        :param batch_id:
        :param epoch:
        :return: loss, y_pred, y_true
        """
        raise NotImplementedError

    def testing_fn(self, batch: torch.Tensor, batch_id: int) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        raise NotImplementedError

### General methods
    def nparams(self, readable: bool = False, trainable: bool = True) -> Union[int, str]:
        if trainable:
            params = sum(p.numel() for p in self.network.parameters() if p.requires_grad)
        else:
            params = sum(p.numel() for p in self.network.parameters())

        if readable:
            return readable_number(params, unit='', decimal=3)
        else:
            return params

    def __repr__(self):
        summary = f'Model: {self.name}\n' \
                  f'\tTrainable parameters: {self.nparams(readable=True)}\n' \
                  f'\tMetrics: {", ".join(m.name for m in self.metrics)}'

        return summary

    def print_summary(self) -> None:
        print(repr(self))

    def progressbar_metrics(self, skip_metrics: List[str] = None) -> dict:
        if skip_metrics is None:
            skip_metrics = []

        metrics = {k.name: k.print() for k in self.metrics
                   if not isinstance(k.value, np.ndarray) and k.name not in skip_metrics and k.visible_progress}
        return metrics

### Events
    def on_start(self) -> None:
        for m in self.metrics:
            m.on_start()

    def on_finish(self) -> None:
        for m in self.metrics:
            m.on_finish()

    def on_epoch_start(self, epoch: int, model: 'Model') -> None:
        for m in self.metrics:
            m.on_epoch_start(epoch, model)

    def on_epoch_finish(self, epoch: int, model: 'Model') -> None:
        for m in self.metrics:
            m.on_epoch_finish(epoch, model)

    def on_batch_start(self, batch, batch_id: int, epoch: int) -> None:
        for m in self.metrics:
            m.on_batch_start(batch, batch_id, epoch)

    def on_batch_finish(self, batch, batch_id: int, epoch: int,
                        loss: torch.Tensor, y_pred: torch.Tensor, y_true: torch.Tensor) -> None:
        for m in self.metrics:
            m.on_batch_finish(batch, batch_id, epoch, loss, y_pred, y_true)

    def on_training_epoch_start(self, epoch: int, model: 'Model') -> None:
        for m in self.metrics:
            m.on_training_epoch_start(epoch, model)
        self.on_epoch_start(epoch, model)

    def on_training_epoch_finish(self, epoch: int, model: 'Model') -> None:
        for m in self.metrics:
            m.on_training_epoch_finish(epoch, model)
        self.on_epoch_finish(epoch, model)

    def on_validation_epoch_start(self, epoch: int, model: 'Model') -> None:
        for m in self.metrics:
            m.on_validation_epoch_start(epoch, model)
        self.on_epoch_start(epoch, model)

    def on_validation_epoch_finish(self, epoch: int, model: 'Model') -> None:
        for m in self.metrics:
            m.on_validation_epoch_finish(epoch, model)
        self.on_epoch_finish(epoch, model)

    def on_testing_start(self) -> None:
        for m in self.metrics:
            m.on_testing_start()
        self.on_epoch_start(-1, self)

    def on_testing_finish(self) -> None:
        for m in self.metrics:
            m.on_testing_finish()
        self.on_epoch_finish(-1, self)

    def on_training_batch_start(self, batch, batch_id: int, epoch: int) -> None:
        for m in self.metrics:
            m.on_training_batch_start(batch, batch_id, epoch)
        self.on_batch_start(batch, batch_id, epoch)

    def on_training_batch_finish(self, batch, batch_id: int, epoch: int,
                                 loss: torch.Tensor, y_pred: torch.Tensor, y_true: torch.Tensor) -> None:
        for m in self.metrics:
            m.on_training_batch_finish(batch, batch_id, epoch, loss, y_pred, y_true)
        self.on_batch_finish(batch, batch_id, epoch, loss, y_pred, y_true)

    def on_validation_batch_start(self, batch, batch_id: int, epoch: int) -> None:
        for m in self.metrics:
            m.on_validation_batch_start(batch, batch_id, epoch)
        self.on_batch_start(batch, batch_id, epoch)

    def on_validation_batch_finish(self, batch, batch_id: int, epoch: int,
                                   loss: torch.Tensor, y_pred: torch.Tensor, y_true: torch.Tensor) -> None:
        for m in self.metrics:
            m.on_validation_batch_finish(batch, batch_id, epoch, loss, y_pred, y_true)
        self.on_batch_finish(batch, batch_id, epoch, loss, y_pred, y_true)

    def on_testing_batch_start(self, batch, batch_id: int) -> None:
        for m in self.metrics:
            m.on_testing_batch_start(batch, batch_id)
        self.on_batch_start(batch, batch_id, -1)

    def on_testing_batch_finish(self, batch, batch_id: int,
                                loss: torch.Tensor, y_pred: torch.Tensor, y_true: torch.Tensor) -> None:
        for m in self.metrics:
            m.on_testing_batch_finish(batch, batch_id, loss, y_pred, y_true)
        self.on_batch_finish(batch, batch_id, -1, loss, y_pred, y_true)
