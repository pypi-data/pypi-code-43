from typing import List, Any, Union
import torch
import torch.nn.functional as F
from kinlin.core import Metric, RunningEpochMetric
from kinlin.core.utils import to_onehot
import numpy as np

### Classwise metrics

# Tversky index: https://en.wikipedia.org/wiki/Tversky_index
# a = b = 0.5 = dice coefficient
# a = b = 1 = jaccard index / tanimoto coefficient
class ClasswiseTverskyIndex(RunningEpochMetric):
    def __init__(self, n_classes: int, alpha: float = 0.5, beta: float = 0.5, eps: float = 1e-7):
        super(ClasswiseTverskyIndex, self).__init__()
        self.n_classes = n_classes
        self.alpha = alpha
        self.beta = beta
        self.eps = eps

    def print(self) -> str:
        return f'[{",".join(f"{k:.3f}" for k in self.value)}]'

    def on_batch_finish(self, batch, batch_id: int, epoch: int, loss: torch.Tensor, y_pred: torch.Tensor, y_true: torch.Tensor) -> None:
        super(ClasswiseTverskyIndex, self).on_batch_finish(batch, batch_id, epoch, loss, y_pred, y_true)

        y_true_onehot = to_onehot(y_true, self.n_classes).float()
        prob = F.softmax(y_pred, dim=1)

        dims = (0, 2, 3, 4)
        intersection = torch.sum(prob * y_true_onehot, dims)
        fps = torch.sum(prob * torch.sub(1, y_true_onehot), dims)
        fns = torch.sum(torch.sub(1, prob) * y_true_onehot, dims)

        del y_true_onehot, prob

        num = intersection
        den = intersection + (self.alpha * fps) + (self.beta * fns)
        tversky_index = (num / (den + self.eps))

        self.set(tversky_index.cpu().numpy())

class ClasswiseDiceCoefficient(ClasswiseTverskyIndex):
    def __init__(self, n_classes: int):
        super(ClasswiseDiceCoefficient, self).__init__(n_classes, alpha=0.5, beta=0.5)

class ClasswiseJaccardIndex(ClasswiseTverskyIndex):
    def __init__(self, n_classes: int):
        super(ClasswiseJaccardIndex, self).__init__(n_classes, alpha=1.0, beta=1.0)

class ClasswiseTanimotoCoefficient(ClasswiseJaccardIndex):
    # alias for Jaccard index
    pass


### Averaged metrics
class TverskyIndex(ClasswiseTverskyIndex):
    def on_batch_finish(self, batch, batch_id: int, epoch: int, loss: torch.Tensor, y_pred: torch.Tensor, y_true: torch.Tensor) -> None:
        super(TverskyIndex, self).on_batch_finish(batch, batch_id, epoch, loss, y_pred, y_true)
        self.value = self.value.mean()

    def print(self) -> str:
        return f'{self.value:.3f}'

class DiceCoefficient(TverskyIndex):
    def __init__(self, n_classes: int):
        super(DiceCoefficient, self).__init__(n_classes, alpha=0.5, beta=0.5)

class JaccardIndex(TverskyIndex):
    def __init__(self, n_classes: int):
        super(JaccardIndex, self).__init__(n_classes, alpha=1.0, beta=1.0)

class TanimotoCoefficient(JaccardIndex):
    # alias for Jaccard index
    pass
