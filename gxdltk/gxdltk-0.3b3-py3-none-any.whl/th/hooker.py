"""
General Hooker for forward and backward
"""
from gxdltk.th.header import *

__all__ = ["observer"]


def observer(module, it, output):
    """
    Forward hook for watch all var size
    using Name tensor in torch1.3
    :param module: torch.nn.Module
    :param it: any type
    :param output: any type, model output
    """
    print(f"Module \n {module}")
    if isinstance(it, tensor):
        print(f"Input shape {it.shape}")
    elif isinstance(it, tuple):
        for i in range(len(it)):
            print(f"Input {i} shape {it[i].shape}")

    if isinstance(output, tensor):
        print(f"Input shape {output.shape}")
    elif isinstance(output, tuple):
        for i in range(len(output)):
            print(f"Input {i} shape {output[i].shape}")
