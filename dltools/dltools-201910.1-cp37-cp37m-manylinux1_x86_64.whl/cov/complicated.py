import typing
from itertools import product
from functools import lru_cache

import numpy as np
import pyspark
from pyspark.sql import functions as f
from pyspark.sql.types import ArrayType, StructField, StructType

from dltools import SpkHit
from .core import (
    SpkPersist, SpkRepart, SpkMapPartThanSum, SpkCrossJoin,
    AppendCCov,
)
from .markup import markup


__all__ = [
    "cov2d_complicated", "cov3d_complicated",
]


def cov2d_complicated(
        df: pyspark.sql.DataFrame,
        ishit0: typing.Callable[[pyspark.sql.Row], bool],
        ishit1: typing.Optional[typing.Callable[[pyspark.sql.Row], bool]] = None,
        key: str = "hits",
        npart: typing.Optional[int] = None,
        persist: typing.Optional[str] = "MEMORY_AND_DISK",
        opt1: typing.Optional[dict] = None,
        opt2: typing.Optional[dict] = None,
        ) -> typing.Callable[..., dict]:
    if ishit1 is None:
        ishit1 = ishit0

    if opt1 is None:
        opt1 = {}

    if opt2 is None:
        opt2 = {}

    @f.udf(StructType([
        StructField("X", ArrayType(StructType([
            StructField("hit0", SpkHit),
        ]))),
        StructField("Y", ArrayType(StructType([
            StructField("hit1", SpkHit),
        ]))),
        StructField("XY", ArrayType(StructType([
            StructField("hit0", SpkHit),
            StructField("hit1", SpkHit),
        ]))),
    ]))
    def combine(
            hits: (pyspark.sql.Column, typing.List[pyspark.sql.Row]),
            ) -> (pyspark.sql.Column, dict):
        x0 = [
            {"arg": arg, "hit": hit}
            for arg, hit in enumerate(hits)
            if ishit0(hit)
        ]
        x1 = [
            {"arg": arg, "hit": hit}
            for arg, hit in enumerate(hits)
            if ishit1(hit)
        ]
        return {
            "X": [
                {"hit0": d["hit"]}
                for d in x0
            ],
            "Y": [
                {"hit1": d["hit"]}
                for d in x1
            ],
            "XY": [
                {"hit0": d0["hit"], "hit1": d1["hit"]}
                for d0, d1 in product(x0, x1)
                if len({d0["arg"], d1["arg"]}) == 2
            ],
        }

    combined = (
        df
        .select(combine(key).alias("h"))
        | SpkRepart(npart)
        | SpkPersist(persist)
    )

    @lru_cache()
    def analyzer(
            hist: typing.Callable[
                [typing.List[pyspark.sql.Row]],
                typing.List[np.ndarray],
            ],
            ) -> dict:
        return {
            "N": df.count(),
            "Sum[X]Sum[Y]": markup(
                combined
                | SpkCrossJoin("X", "Y", **opt2)
                | SpkMapPartThanSum(hist),
                (1 / opt2["fraction"] if "fraction" in opt2 else 1) ** 2,
            ),
            "Sum[XY]": markup(
                combined
                | SpkCrossJoin("XY", **opt1)
                | SpkMapPartThanSum(hist),
                (1 / opt1["fraction"] if "fraction" in opt1 else 1),
            ),
        } | AppendCCov("X", "Y")
    return analyzer


def cov3d_complicated(
        df: pyspark.sql.DataFrame,
        ishit0: typing.Callable[[pyspark.sql.Row], bool],
        ishit1: typing.Optional[typing.Callable[[pyspark.sql.Row], bool]] = None,
        ishit2: typing.Optional[typing.Callable[[pyspark.sql.Row], bool]] = None,
        key: str = "hits",
        npart: typing.Optional[int] = None,
        persist: typing.Optional[str] = "MEMORY_AND_DISK",
        opt1: typing.Optional[dict] = None,
        opt2: typing.Optional[dict] = None,
        opt3: typing.Optional[dict] = None,
        ) -> typing.Callable[..., dict]:
    if ishit1 is None:
        ishit1 = ishit0

    if ishit2 is None:
        ishit2 = ishit1

    if opt1 is None:
        opt1 = {}

    if opt2 is None:
        opt2 = {}

    if opt3 is None:
        opt3 = {}

    @f.udf(StructType([
        StructField("X", ArrayType(StructType([
            StructField("hit0", SpkHit),
        ]))),
        StructField("Y", ArrayType(StructType([
            StructField("hit1", SpkHit),
        ]))),
        StructField("Z", ArrayType(StructType([
            StructField("hit2", SpkHit),
        ]))),
        StructField("XY", ArrayType(StructType([
            StructField("hit0", SpkHit),
            StructField("hit1", SpkHit),
        ]))),
        StructField("XZ", ArrayType(StructType([
            StructField("hit0", SpkHit),
            StructField("hit2", SpkHit),
        ]))),
        StructField("YZ", ArrayType(StructType([
            StructField("hit1", SpkHit),
            StructField("hit2", SpkHit),
        ]))),
        StructField("XYZ", ArrayType(StructType([
            StructField("hit0", SpkHit),
            StructField("hit1", SpkHit),
            StructField("hit2", SpkHit),
        ]))),
    ]))
    def combine(
            hits: (pyspark.sql.Column, typing.List[pyspark.sql.Row]),
            ) -> (pyspark.sql.Column, dict):
        x0 = [
            {"arg": arg, "hit": hit}
            for arg, hit in enumerate(hits)
            if ishit0(hit)
        ]
        x1 = [
            {"arg": arg, "hit": hit}
            for arg, hit in enumerate(hits)
            if ishit1(hit)
        ]
        x2 = [
            {"arg": arg, "hit": hit}
            for arg, hit in enumerate(hits)
            if ishit2(hit)
        ]
        return {
            "X": [
                {"hit0": d["hit"]}
                for d in x0
            ],
            "Y": [
                {"hit1": d["hit"]}
                for d in x1
            ],
            "Z": [
                {"hit2": d["hit"]}
                for d in x2
            ],
            "XY": [
                {"hit0": d0["hit"], "hit1": d1["hit"]}
                for d0, d1 in product(x0, x1)
                if len({d0["arg"], d1["arg"]}) == 2
            ],
            "XZ": [
                {"hit0": d0["hit"], "hit2": d2["hit"]}
                for d0, d2 in product(x0, x2)
                if len({d0["arg"], d2["arg"]}) == 2
            ],
            "YZ": [
                {"hit1": d1["hit"], "hit2": d2["hit"]}
                for d1, d2 in product(x1, x2)
                if len({d1["arg"], d2["arg"]}) == 2
            ],
            "XYZ": [
                {"hit0": d0["hit"], "hit1": d1["hit"], "hit2": d2["hit"]}
                for d0, d1, d2 in product(x0, x1, x2)
                if len({d0["arg"], d1["arg"], d2["arg"]}) == 3
            ],
        }

    combined = (
        df
        .select(combine(key).alias("h"))
        | SpkRepart(npart)
        | SpkPersist(persist)
    )

    @lru_cache()
    def analyzer(
            hist: typing.Callable[
                [typing.List[pyspark.sql.Row]],
                typing.List[np.ndarray],
            ],
            ) -> dict:
        return {
            "N": df.count(),
            "Sum[X]Sum[Y]Sum[Z]": markup(
                combined
                | SpkCrossJoin("X", "Y", "Z", **opt3)
                | SpkMapPartThanSum(hist),
                (1 / opt3["fraction"] if "fraction" in opt3 else 1) ** 3,
            ),
            "Sum[XY]Sum[Z]": markup(
                combined
                | SpkCrossJoin("XY", "Z", **opt2)
                | SpkMapPartThanSum(hist),
                (1 / opt2["fraction"] if "fraction" in opt2 else 1) ** 2,
            ),
            "Sum[XZ]Sum[Y]": markup(
                combined
                | SpkCrossJoin("XZ", "Y", **opt2)
                | SpkMapPartThanSum(hist),
                (1 / opt2["fraction"] if "fraction" in opt2 else 1) ** 2,
            ),
            "Sum[YZ]Sum[X]": markup(
                combined
                | SpkCrossJoin("YZ", "X", **opt2)
                | SpkMapPartThanSum(hist),
                (1 / opt2["fraction"] if "fraction" in opt2 else 1) ** 2,
            ),
            "Sum[XYZ]": markup(
                combined
                | SpkCrossJoin("XYZ", **opt1)
                | SpkMapPartThanSum(hist),
                (1 / opt1["fraction"] if "fraction" in opt1 else 1),
            ),
        } | AppendCCov("X", "Y", "Z")
    return analyzer
