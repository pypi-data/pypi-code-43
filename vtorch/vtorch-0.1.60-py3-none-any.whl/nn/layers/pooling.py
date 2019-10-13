import torch
from torch import nn


class MaxPool(nn.Module):
    def __init__(self):
        super().__init__()
        self.register_buffer('zero_const', torch.tensor([0.]))
        self.register_buffer('big_const', torch.tensor([1000.]))

    def forward(self, x, batch_first=False):
        mask = torch.where(x != 0, self.zero_const, self.big_const)
        x = x - mask
        y = x.max(dim=int(batch_first))
        y = y[0] if isinstance(y, tuple) else y
        return y


class MeanPool(nn.Module):
    def __init__(self):
        super().__init__()
        self.register_buffer('zero_const', torch.tensor([0.]))
        self.register_buffer('one_const', torch.tensor([1.]))

    def forward(self, x, batch_first=False):
        mask = torch.where(x != 0, self.one_const, self.zero_const)
        x = x * mask
        n_ = mask[:, :, 0].sum(dim=int(batch_first))[:, None]
        y = x.sum(dim=int(batch_first))
        y = y[0] if isinstance(y, tuple) else y
        y = y / n_
        return y
