import random
import sys
import subprocess
import platform
import string
from typing import Union
from pathlib import Path
import numpy as np
import torch


def generate_random_id() -> str:
    # https://stackoverflow.com/questions/13484726/safe-enough-8-character-short-unique-random-string
    alphabet = string.ascii_lowercase + string.digits
    return ''.join(random.choices(alphabet, k=8))

def generate_random_seed() -> int:
    return random.randint(-sys.maxsize - 1, sys.maxsize)

def generate_fname(name: str, length_limit: int = 20) -> str:
    # https://stackoverflow.com/questions/295135/turn-a-string-into-a-valid-filename
    alphabet = string.ascii_lowercase + string.digits + '-_'
    return ''.join(c for c in name if c in alphabet)[:length_limit]

def set_seed(seed: int, cudnn_deterministic: bool = False) -> None:
    # https://pytorch.org/docs/master/notes/randomness.html
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)

    if cudnn_deterministic and torch.backends.cudnn.enabled:
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False

def fast_histogram(y_pred: torch.Tensor, y_true: torch.Tensor, num_classes: int) -> torch.Tensor:
    # https://github.com/kevinzakka/pytorch-goodies/blob/master/metrics.py

    mask = (y_true >= 0) & (y_true < num_classes)
    hist = torch.bincount(
        num_classes * y_true[mask] + y_pred[mask],
        minlength=num_classes ** 2,
    ).reshape(num_classes, num_classes).float()
    return hist

def open_folder(path: Union[Path, str]) -> None:
    if platform.system() == 'Windows':
        if isinstance(path, Path):
            subprocess.Popen(f'explorer "{str(path.absolute())}"')
        elif isinstance(path, str):
            subprocess.Popen(f'explorer "{path}"')
    else:
        raise NotImplementedError  # TODO

def open_file(path: Union[Path, str]) -> None:
    if platform.system() == 'Windows':
        if isinstance(path, Path):
            subprocess.Popen(f'explorer /select,"{str(path.absolute())}"')
        elif isinstance(path, str):
            subprocess.Popen(f'explorer /select,"{path}"')
    else:
        raise NotImplementedError  # TODO

def get_current_git_head() -> str:
    # https://stackoverflow.com/questions/14989858/get-the-current-git-hash-in-a-python-script
    return subprocess.check_output(['git', 'rev-parse', 'HEAD']).strip()

def has_nan(x: torch.Tensor) -> bool:
    return torch.isnan(x).any().item()

def to_onehot(tensor: torch.Tensor, num_classes: int) -> torch.Tensor:
    # (N, D, H, W) to (N, num_classes, D, H, W)
    onehot = torch.zeros(tensor.shape[0], num_classes, *tensor.shape[1:],
                         dtype=torch.int32,
                         device=tensor.device)
    return onehot.scatter_(1, tensor.unsqueeze(1), 1)

def readable_number(num: int, unit: str, decimal: int = 3) -> str:
    for mod in ['', 'K', 'M', 'B']:
        if num < 1000:
            break
        num /= 1000
    return f'{num:.{decimal}f} {mod}{unit}'

def readable_time(seconds: int) -> str:
    # https://github.com/pytorch/ignite/blob/master/ignite/_utils.py
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)

    if h > 0:
        return f'{h:.0f}h {m:.0f}m {s:.0f}s'
    elif m > 0:
        return f'{m:.0f}m {s:.1f}s'
    else:
        return f'{s:.1f}s'

