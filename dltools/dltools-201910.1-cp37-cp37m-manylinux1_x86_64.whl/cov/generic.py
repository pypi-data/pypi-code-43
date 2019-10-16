import typing
from itertools import product
from functools import lru_cache

import numpy as np
import pyspark

from .core import digitize, increase, AppendCov


__all__ = [
    "cov1x1", "cov2x1", "cov1x1x1", "cov2x1x1",
]


def cov1x1(
        df: pyspark.sql.DataFrame,
        key0: str,
        key1: typing.Optional[str] = None,
        ) -> typing.Callable[..., dict]:
    if key1 is None:
        key1 = key0

    @lru_cache()
    def analyzer(
            fr0: float, to0: float, nbins0: int,
            fr1: typing.Optional[float] = None,
            to1: typing.Optional[float] = None,
            nbins1: int = 1,
            ) -> dict:
        if fr1 is None:
            fr1 = fr0

        if to1 is None:
            to1 = to0

        def f(row: pyspark.sql.Row) -> typing.Iterator[tuple]:
            target = digitize(
                row[key0],
                bins=np.linspace(fr0, to0, nbins0 + 1),
            )
            x0 = [
                at - 1
                for at in target["digitized"][target["where"]]
            ]

            target = digitize(
                row[key1],
                bins=np.linspace(fr1, to1, nbins1 + 1),
            )
            x1 = [
                at - 1
                for at in target["digitized"][target["where"]]
            ]

            yield (0, 0)

            for at in x0:
                yield (at + 1, 0)

            for at in x1:
                yield (0, at + 1)

            for at0, at1 in product(x0, x1):
                yield (at0 + 1, at1 + 1)

        reduced = (
            df
            .rdd
            .flatMap(f)
            .aggregate(
                np.zeros([nbins0 + 1,
                          nbins1 + 1], dtype="int64"),
                increase,
                np.add,
            )
        )
        return {
            "N": reduced[0, 0],
            "Sum[X]": reduced[1:, 0],
            "Sum[Y]": reduced[0, 1:],
            "Sum[XY]": reduced[1:, 1:],
        } | AppendCov("X", "Y")
    return analyzer


def cov2x1(
        df: pyspark.sql.DataFrame,
        key00: str,
        key01: str,
        key1: typing.Optional[str] = None,
) -> typing.Callable[..., dict]:
    if key1 is None:
        key1 = key00

    @lru_cache()
    def analyzer(
            fr00: float, to00: float, nbins00: int,
            fr01: float, to01: float, nbins01: int,
            fr1: typing.Optional[float] = None,
            to1: typing.Optional[float] = None,
            nbins1: int = 1,
    ) -> dict:
        if fr1 is None:
            fr1 = fr00

        if to1 is None:
            to1 = to00

        def f(row: pyspark.sql.Row) -> typing.Iterator[tuple]:
            target00 = digitize(
                row[key00],
                bins=np.linspace(fr00, to00, nbins00 + 1),
            )
            target01 = digitize(
                row[key01],
                bins=np.linspace(fr01, to01, nbins01 + 1),
            )
            where = target00["where"] & target01["where"]
            x0 = [
                at - 1
                for at in np.stack([target00["digitized"],
                                    target01["digitized"]], axis=-1)[where]
            ]

            target = digitize(
                row[key1],
                bins=np.linspace(fr1, to1, nbins1 + 1),
            )
            x1 = [
                at - 1
                for at in target["digitized"][target["where"]]
            ]

            yield (0, 0, 0)

            for at in x0:
                yield (*(at + 1), 0)

            for at in x1:
                yield (0, 0, at + 1)

            for at0, at1 in product(x0, x1):
                yield (*(at0 + 1), at1 + 1)

        reduced = (
            df
            .rdd
            .flatMap(f)
            .aggregate(
                np.zeros([nbins00 + 1,
                          nbins01 + 1,
                          nbins1 + 1], dtype="int64"),
                increase,
                np.add,
            )
        )
        return {
                   "N": reduced[0, 0, 0],
                   "Sum[X]": reduced[1:, 1:, 0],
                   "Sum[Y]": reduced[0, 0, 1:],
                   "Sum[XY]": reduced[1:, 1:, 1:],
               } | AppendCov("X", "Y")

    return analyzer


def cov1x1x1(
        df: pyspark.sql.DataFrame,
        key0: str,
        key1: typing.Optional[str] = None,
        key2: typing.Optional[str] = None,
        ) -> typing.Callable[..., dict]:
    if key1 is None:
        key1 = key0

    if key2 is None:
        key2 = key1

    @lru_cache()
    def analyzer(
            fr0: float, to0: float, nbins0: int,
            fr1: typing.Optional[float] = None,
            to1: typing.Optional[float] = None,
            nbins1: int = 1,
            fr2: typing.Optional[float] = None,
            to2: typing.Optional[float] = None,
            nbins2: int = 1,
            ) -> dict:
        if fr1 is None:
            fr1 = fr0

        if to1 is None:
            to1 = to0

        if fr2 is None:
            fr2 = fr1

        if to2 is None:
            to2 = to1

        def f(row: pyspark.sql.Row) -> typing.Iterator[tuple]:
            target = digitize(
                row[key0],
                bins=np.linspace(fr0, to0, nbins0 + 1),
            )
            x0 = [
                at - 1
                for at in target["digitized"][target["where"]]
            ]

            target = digitize(
                row[key1],
                bins=np.linspace(fr1, to1, nbins1 + 1),
            )
            x1 = [
                at - 1
                for at in target["digitized"][target["where"]]
            ]

            target = digitize(
                row[key2],
                bins=np.linspace(fr2, to2, nbins2 + 1),
            )
            x2 = [
                at - 1
                for at in target["digitized"][target["where"]]
            ]

            yield (0, 0, 0)

            for at in x0:
                yield (at + 1, 0, 0)

            for at in x1:
                yield (0, at + 1, 0)

            for at in x2:
                yield (0, 0, at + 1)

            for at0, at1 in product(x0, x1):
                yield (at0 + 1, at1 + 1, 0)

            for at0, at2 in product(x0, x2):
                yield (at0 + 1, 0, at2 + 1)

            for at1, at2 in product(x1, x2):
                yield (0, at1 + 1, at2 + 1)

            for at0, at1, at2 in product(x0, x1, x2):
                yield (at0 + 1, at1 + 1, at2 + 1)

        reduced = (
            df
            .rdd
            .flatMap(f)
            .aggregate(
                np.zeros([nbins0 + 1,
                          nbins1 + 1,
                          nbins2 + 1], dtype="int64"),
                increase,
                np.add,
            )
        )
        return (
            {
                "N": reduced[0, 0, 0],
                "Sum[X]": reduced[1:, 0, 0],
                "Sum[Y]": reduced[0, 1:, 0],
                "Sum[Z]": reduced[0, 0, 1:],
                "Sum[XY]": reduced[1:, 1:, 0],
                "Sum[XZ]": reduced[1:, 0, 1:],
                "Sum[YZ]": reduced[0, 1:, 1:],
                "Sum[XYZ]": reduced[1:, 1:, 1:],
            } | AppendCov("X", "Y") | AppendCov("X", "Z") | AppendCov("Y", "Z")
            | AppendCov("X", "Y", "Z")
        )
    return analyzer


def cov2x1x1(
        df: pyspark.sql.DataFrame,
        key00: str,
        key01: str,
        key1: typing.Optional[str] = None,
        key2: typing.Optional[str] = None,
        ) -> typing.Callable[..., dict]:
    if key1 is None:
        key1 = key00

    if key2 is None:
        key2 = key1

    @lru_cache()
    def analyzer(
            fr00: float, to00: float, nbins00: int,
            fr01: float, to01: float, nbins01: int,
            fr1: typing.Optional[float] = None,
            to1: typing.Optional[float] = None,
            nbins1: int = 1,
            fr2: typing.Optional[float] = None,
            to2: typing.Optional[float] = None,
            nbins2: int = 1,
            ) -> dict:
        if fr1 is None:
            fr1 = fr00

        if to1 is None:
            to1 = to00

        if fr2 is None:
            fr2 = fr1

        if to2 is None:
            to2 = to1

        def f(row: pyspark.sql.Row) -> typing.Iterator[tuple]:
            target00 = digitize(
                row[key00],
                bins=np.linspace(fr00, to00, nbins00 + 1),
            )
            target01 = digitize(
                row[key01],
                bins=np.linspace(fr01, to01, nbins01 + 1),
            )
            where = target00["where"] & target01["where"]
            x0 = [
                at - 1
                for at in np.stack([target00["digitized"],
                                    target01["digitized"]], axis=-1)[where]
            ]

            target = digitize(
                row[key1],
                bins=np.linspace(fr1, to1, nbins1 + 1),
            )
            x1 = [
                at - 1
                for at in target["digitized"][target["where"]]
            ]

            target = digitize(
                row[key2],
                bins=np.linspace(fr2, to2, nbins2 + 1),
            )
            x2 = [
                at - 1
                for at in target["digitized"][target["where"]]
            ]

            yield (0, 0, 0, 0)

            for at in x0:
                yield (*(at + 1), 0, 0)

            for at in x1:
                yield (0, 0, at + 1, 0)

            for at in x2:
                yield (0, 0, 0, at + 1)

            for at0, at1 in product(x0, x1):
                yield (*(at0 + 1), at1 + 1, 0)

            for at0, at2 in product(x0, x2):
                yield (*(at0 + 1), 0, at2 + 1)

            for at1, at2 in product(x1, x2):
                yield (0, 0, at1 + 1, at2 + 1)

            for at0, at1, at2 in product(x0, x1, x2):
                yield (*(at0 + 1), at1 + 1, at2 + 1)

        reduced = (
            df
            .rdd
            .flatMap(f)
            .aggregate(
                np.zeros([nbins00 + 1,
                          nbins01 + 1,
                          nbins1 + 1,
                          nbins2 + 1], dtype="int64"),
                increase,
                np.add,
            )
        )
        return (
            {
                "N": reduced[0, 0, 0, 0],
                "Sum[X]": reduced[1:, 1:, 0, 0],
                "Sum[Y]": reduced[0, 0, 1:, 0],
                "Sum[Z]": reduced[0, 0, 0, 1:],
                "Sum[XY]": reduced[1:, 1:, 1:, 0],
                "Sum[XZ]": reduced[1:, 1:, 0, 1:],
                "Sum[YZ]": reduced[0, 0, 1:, 1:],
                "Sum[XYZ]": reduced[1:, 1:, 1:, 1:],
            } | AppendCov("X", "Y") | AppendCov("X", "Z") | AppendCov("Y", "Z")
            | AppendCov("X", "Y", "Z")
        )
    return analyzer
