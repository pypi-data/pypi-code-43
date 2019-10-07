import torch
import torch.nn.functional as F


def mse(output, targ):
    return (output.squeeze(-1) - targ).pow(2).mean()

def accuracy(out, yb): return (torch.argmax(out, dim=1)==yb).float().mean()

def cross_entropy_flat(input, target):
    "ensures batch and sequence length dimensions are flattened"
    bs, sl = target.size()
    return F.cross_entropy(input.view(bs * sl, -1), target.view(bs * sl))

def accuracy_flat(input, target):
    "ensures batch and sequence length dimensions are flattened"
    bs, sl = target.size()
    return accuracy(input.view(bs * sl, -1), target.view(bs * sl))


