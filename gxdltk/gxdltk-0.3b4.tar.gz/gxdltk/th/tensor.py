from gxdltk.th.header import *
def sim(a: tensor, b: tensor) -> float:
    """
    calc vector sim
    :param a:
    :param b:
    :return:
    """
    res = th.dot(a, b) / (a.norm() * b.norm())
    return res.item()
