"""
Test in gxdltk
"""
import torch
from gxdltk.th.tensor import tensors

if __name__ == '__main__':
    a = [1,2,3]
    b = [2,3,4]
    a_t, b_t = tensors([a,b],device=torch.device("cpu"))
    print(a_t, b_t)
