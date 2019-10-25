import torch
import torch.nn.functional as F


def mse(output, targ):
    return (output.squeeze(-1) - targ).pow(2).mean()

def accuracy(out, yb): return (torch.argmax(out, dim=1)==yb).float().mean()

def cross_entropy_flat(input, target):
    "ensures batch and sequence length dimensions are flattened"
    batch_size, seq_len = target.size()
    return F.cross_entropy(input.view(batch_size * seq_len, -1), target.view(batch_size * seq_len))

def accuracy_flat(input, target):
    "ensures batch and sequence length dimensions are flattened"
    batch_size, seq_len = target.size()
    return accuracy(input.view(batch_size * seq_len, -1), target.view(batch_size * seq_len))
