from typing import List, Any, Union
import torch
from enum import Enum
import torch.nn.functional as f
import time
from .utils import readable_time
import numpy as np

### Base classes
class Metric:
    def __init__(self):
        self.name = self.__class__.__name__
        self.value = None
        self.visible_progress = True

        self.setup()

    def setup(self) -> None:
        pass

    def set(self, value) -> None:
        self.value = value

    def print(self) -> str:
        try:
            return f'{self.value:.3f}'
        except TypeError:
            return ''

    def on_start(self) -> None:
        pass

    def on_finish(self) -> None:
        pass

    def on_epoch_start(self, epoch: int, model: 'Model') -> None:
        pass

    def on_epoch_finish(self, epoch: int, model: 'Model') -> None:
        pass

    def on_batch_start(self, batch, batch_id: int, epoch: int) -> None:
        pass

    def on_batch_finish(self, batch, batch_id: int, epoch: int,
                        loss: torch.Tensor, y_pred: torch.Tensor, y_true: torch.Tensor) -> None:
        pass

    def on_training_epoch_start(self, epoch: int, model: 'Model') -> None:
        pass

    def on_training_epoch_finish(self, epoch: int, model: 'Model') -> None:
        pass

    def on_validation_epoch_start(self, epoch: int, model: 'Model') -> None:
        pass

    def on_validation_epoch_finish(self, epoch: int, model: 'Model') -> None:
        pass

    def on_testing_start(self) -> None:
        pass

    def on_testing_finish(self) -> None:
        pass

    def on_training_batch_start(self, batch, batch_id: int, epoch: int) -> None:
        pass

    def on_training_batch_finish(self, batch, batch_id: int, epoch: int,
                                 loss: torch.Tensor, y_pred: torch.Tensor, y_true: torch.Tensor) -> None:
        pass

    def on_validation_batch_start(self, batch, batch_id: int, epoch: int) -> None:
        pass

    def on_validation_batch_finish(self, batch, batch_id: int, epoch: int,
                                   loss: torch.Tensor, y_pred: torch.Tensor, y_true: torch.Tensor) -> None:
        pass

    def on_testing_batch_start(self, batch, batch_id: int) -> None:
        pass

    def on_testing_batch_finish(self, batch, batch_id: int,
                                loss: torch.Tensor, y_pred: torch.Tensor, y_true: torch.Tensor) -> None:
        pass

class RunningEpochMetric(Metric):
    def __init__(self):
        super(RunningEpochMetric, self).__init__()

    def on_epoch_start(self, epoch: int, model: 'Model') -> None:
        self.value = None

    def set(self, value) -> None:
        if self.value is None:
            self.value = value
        else:
            self.value = (self.value + value) / 2

### General metrics
class Epoch(Metric):
    def setup(self) -> None:
        super(Epoch, self).setup()
        self.value: int = 0
        self.visible_progress = False

    def on_training_epoch_finish(self, epoch: int, model: 'Model') -> None:
        super(Epoch, self).on_training_epoch_finish(epoch, model)
        self.set(self.value + 1)

class SemSegAccuracy(RunningEpochMetric):
    def on_epoch_start(self, epoch: int, model: 'Model') -> None:
        super(SemSegAccuracy, self).on_epoch_start(epoch, model)
        self.value: float = 0.0

    def on_batch_finish(self, batch, batch_id: int, epoch: int,
                        loss: torch.Tensor, y_pred: torch.Tensor, y_true: torch.Tensor) -> None:
        super(SemSegAccuracy, self).on_batch_finish(batch, batch_id, epoch, loss, y_pred, y_true)

        # convert to sem. seg. map
        y_pred_prob = f.softmax(y_pred, dim=1)
        y_pred_prob = torch.argmax(y_pred_prob, 1)
        accuracy = y_pred_prob.eq(y_true).sum().item() / y_true.nelement()
        del y_pred_prob
        self.set(accuracy)

class Loss(RunningEpochMetric):
    def on_epoch_start(self, epoch: int, model: 'Model') -> None:
        super(Loss, self).on_epoch_start(epoch, model)
        self.value: float = 0.0

    def on_batch_finish(self, batch, batch_id: int, epoch: int,
                        loss: torch.Tensor, y_pred: torch.Tensor, y_true: torch.Tensor) -> None:
        super(Loss, self).on_batch_finish(batch, batch_id, epoch, loss, y_pred, y_true)
        self.set(loss.item())

class EpochTimer(Metric):
    def setup(self) -> None:
        super(EpochTimer, self).setup()
        self.visible_progress = False

    def on_epoch_start(self, epoch: int, model: 'Model') -> None:
        super(EpochTimer, self).on_epoch_start(epoch, model)
        self.value = time.time()

    def on_epoch_finish(self, epoch: int, model: 'Model') -> None:
        super(EpochTimer, self).on_epoch_finish(epoch, model)
        self.value = time.time() - self.value

    def print(self) -> str:
        return readable_time(time.time() - self.value)
