"""
Test in gxdltk
"""
import torch
from gxdltk.th.tensor import tensors
from gxdltk.th.utils import *

if __name__ == '__main__':
    a = [i for i in range(10)]
    y = [[i, i, i] for i in range(10)]
    z = [[i, 2*i, 3*i] for i in range(10)]
    idx_loader  = batch_idx_provider(a, batch_size=5)
    loader = batch_provider(y,z)
    for index, (y, z) in enumerate(loader):
        print(f"index {index}")
        print(f"y {y}")
        print(f"z {z}")
