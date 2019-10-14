from gxdltk.mx.header import *

__all__ = ['array','sim']

def array(data: list, ctx: mx.Context=mx.cpu()) -> NDArray:
    """
    Convert list data into ndarray
    :param data:
    :param ctx: context, default mx.cpu()
    :return:
    """
    return nd.array(data).as_in_context(ctx)

def sim(a : NDArray, b: NDArray)-> float:
    """
    calc vector sim in mxnet
    :param a: vec a
    :param b: vec b
    :return: similarity of a and b
    """
    res = nd.dot((a, b)) / (a.norm() * b.norm())
    return res
