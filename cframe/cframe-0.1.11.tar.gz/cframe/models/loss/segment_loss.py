import torch.nn as nn
from .base_loss import lovasz_losses as L

class SymmetricLovaszLoss(nn.Module):
    def __init__(self, weight=None, size_average=True):
        super(SymmetricLovaszLoss, self).__init__()
    def forward(self, logits, targets):
        return ((L.lovasz_hinge(logits, targets, per_image=True)) \
                + (L.lovasz_hinge(-logits, 1-targets, per_image=True))) / 2