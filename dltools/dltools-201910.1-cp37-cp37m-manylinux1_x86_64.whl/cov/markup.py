from functools import reduce
from operator import mul
import typing


__all__ = [
    "markup", "compute", "compute_err",
]


T = typing.TypeVar("T")


def markup(var: T, scale: float = 1) -> (T, dict):
    if scale == 1:
        return var
    else:
        return {"$multiply": [var, scale]}


def compute(oper: (T, dict)) -> T:
    if isinstance(oper, dict):
        var, scale = oper["$multiply"]
        return var * scale
    else:
        return oper


def compute_err(oper: (T, dict)) -> T:
    if isinstance(oper, dict):
        var, scale = oper["$multiply"]
        return var ** 0.5 * scale
    else:
        return oper ** 0.5
