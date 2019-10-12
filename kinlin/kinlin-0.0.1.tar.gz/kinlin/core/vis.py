import random
import sys
import string
import subprocess
import platform
from typing import Union, List
from pathlib import Path
import numpy as np
import torch
import matplotlib.pyplot as plt


def plot_tensor_5d(data: torch.Tensor, name: str = None, depth_slice: int = None,
                   format: str = 'bcdhw', mode: str = 'column'):
    # assumes B, C, D, H, W

    # TODO oooooooooo
    if format.lower() != 'bcdhw':
        raise NotImplementedError('Only "bcdhw" format is implemented for now')
    if mode.lower() != 'column':
        raise NotImplementedError('Only "column" mode is implemented for now')

    b, c, d, h, w = data.shape
    fig, ax = plt.subplots(nrows=b, ncols=1, sharex=False, sharey=False)

    if name:
        ax[0].set_title(name)

    # if depth_slice is not specified, use middle slice
    if not depth_slice:
        depth_slice = d // 2

    for i in range(b):
        ax[i].imshow(data[i][:, depth_slice, :, :].detach().cpu())

    raise NotImplementedError
    # TODO check if image is shown
