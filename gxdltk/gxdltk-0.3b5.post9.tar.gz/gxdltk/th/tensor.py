from gxdltk.th.header import *

__all__ = ["sim", "tensors"]
def sim(a: tensor, b: tensor) -> float:
    """
    calc vector sim
    :param a: 1 by D tensor (vector)
    :param b: 1 by D tensor (vector)
    :return:
    """
    assert a.shape == b.shape, f"Shape of a and b must be equal, expect b " \
                               f"shape {a.shape} but got {b.shape}"
    assert len(a.shape) == 1, "a and b must be a 1D tensor"
    res = th.dot(a, b) / (a.norm() * b.norm())
    return res.item()


def tensors(data: list, device: th.device) -> list:
    """
    Providing multiple tensors and using tensors() to convert them into
    th.tensors
    Args:
        data: list of list
        device: th.device type

    Returns:
        list of tensors
    """
    # TODO: deal with dtype
    res = [i for i in data]
    for i in data:
        i_tenor = th.tensor(i).to(device)
        res[data.index(i)] = i_tenor
    return res
