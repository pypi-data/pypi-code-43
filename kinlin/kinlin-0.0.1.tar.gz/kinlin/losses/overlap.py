import torch
import torch.nn.functional as F
from torch import nn as nn
from ..core.utils import to_onehot

class TverskyLoss(nn.Module):
    def __init__(self, alpha: float = 0.5, beta: float = 0.5, classes: int = 13):
        super(TverskyLoss, self).__init__()
        self.alpha = alpha
        self.beta = beta
        self.n_classes = classes
        self.eps = 1e-7

    def forward(self, y_pred, y_true):

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

        return torch.sub(self.n_classes, tversky_index.sum())
