import torch as th

def cuda(device: int) -> th.device:
    """

    Args:
        device: device id

    Returns:
        th.device
    """
    # TODO: multi - frameworks support
    if device >= 0 and th.cuda.is_available():
        return th.device(f"cuda:{device}")
    else:
        return th.device("cpu")
