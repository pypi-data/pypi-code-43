import typing
from itertools import product
from functools import lru_cache

import numpy as np
import pyspark

from .core import digitize, increase, AppendCov


__all__ = [
    "cov11", "cov21", "cov111", "cov211",
]


def cov11(
        df: pyspark.sql.DataFrame,
        key0: str,
        key1: typing.Optional[str] = None,
        ) -> typing.Callable[..., dict]:
    """
    Examples
    --------
    Typical use for TOF covariant with certain TOF region:

    >>> import pyspark.sql.functions as f
    >>> df: pyspark.sql.DataFrame
    >>> tof = cov11(
    ...     df.select(f.col("hits.t").alias("t")),
    ...     "t",
    ... )
    >>> tof(
    ...     fr0=1000, to0=6000, nbins0=2000,
    ...     fr1=5200, to1=5400,
    ... )["Cov[X,Y]"][..., 0]
    """
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
                {"arg": arg, "at": at - 1}
                for (arg,), at in zip(
                    np.argwhere(target["where"]),
                    target["digitized"][target["where"]],
                )
            ]

            target = digitize(
                row[key1],
                bins=np.linspace(fr1, to1, nbins1 + 1),
            )
            x1 = [
                {"arg": arg, "at": at - 1}
                for (arg,), at in zip(
                    np.argwhere(target["where"]),
                    target["digitized"][target["where"]],
                )
            ]

            yield (0, 0)

            for d in x0:
                yield (d["at"] + 1, 0)

            for d in x1:
                yield (0, d["at"] + 1)

            for d0, d1 in product(x0, x1):
                if len({d0["arg"], d1["arg"]}) != 2:
                    continue
                yield (d0["at"] + 1, d1["at"] + 1)

        reduced = (
            df
            .rdd
            .flatMap(f)
            .aggregate(
                np.zeros([nbins0 + 1, nbins1 + 1], dtype="int64"),
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


def cov21(
        df: pyspark.sql.DataFrame,
        key00: str,
        key01: str,
        key1: typing.Optional[str] = None,
        ) -> typing.Callable[..., dict]:
    """
    Examples
    --------
    Typical use for Fish covariant with certain TOF region:

    >>> import pyspark.sql.functions as f
    >>> df: pyspark.sql.DataFrame
    >>> fish = cov21(
    ...     df.select(f.col("hits.t").alias("t"),
    ...               f.col("hits.y").alias("y")),
    ...     "t", "y",
    ... )
    >>> fish(
    ...     fr00=1000, to00=6000, nbins00=2000,
    ...     fr01=-50, to01=50, nbins01=100,
    ...     fr1=5200, to1=5400,
    ... )["Cov[X,Y]"][..., 0]
    """
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
                {"arg": arg, "at": at - 1}
                for (arg,), at in zip(
                    np.argwhere(where),
                    np.stack([target00["digitized"],
                              target01["digitized"]], axis=-1)[where],
                )
            ]

            target = digitize(
                row[key1],
                bins=np.linspace(fr1, to1, nbins1 + 1),
            )
            x1 = [
                {"arg": arg, "at": at - 1}
                for (arg,), at in zip(
                    np.argwhere(target["where"]),
                    target["digitized"][target["where"]],
                )
            ]

            yield (0, 0, 0)

            for d in x0:
                yield (*(d["at"] + 1), 0)

            for d in x1:
                yield (0, 0, d["at"] + 1)

            for d0, d1 in product(x0, x1):
                if len({d0["arg"], d1["arg"]}) != 2:
                    continue
                yield (*(d0["at"] + 1), d1["at"] + 1)

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


def cov111(
        df: pyspark.sql.DataFrame,
        key0: str,
        key1: typing.Optional[str] = None,
        key2: typing.Optional[str] = None,
        ) -> typing.Callable[..., dict]:
    """
    Examples
    --------
    Typical use for PIPICO covariant with certain TOF region:

    >>> import pyspark.sql.functions as f
    >>> df: pyspark.sql.DataFrame
    >>> pipico = cov111(
    ...     df.select(f.col("hits.t").alias("t")),
    ...     "t",
    ... )
    >>> pipico(
    ...     fr0=1000, to0=6000, nbins0=500, nbins1=500,
    ...     fr2=5200, to2=5400,
    ... )["Cov[X,Y,Z]"][..., 0]
    """
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
                {"arg": arg, "at": at - 1}
                for (arg,), at in zip(
                    np.argwhere(target["where"]),
                    target["digitized"][target["where"]],
                )
            ]

            target = digitize(
                row[key1],
                bins=np.linspace(fr1, to1, nbins1 + 1),
            )
            x1 = [
                {"arg": arg, "at": at - 1}
                for (arg,), at in zip(
                    np.argwhere(target["where"]),
                    target["digitized"][target["where"]],
                )
            ]

            target = digitize(
                row[key2],
                bins=np.linspace(fr2, to2, nbins2 + 1),
            )
            x2 = [
                {"arg": arg, "at": at - 1}
                for (arg,), at in zip(
                    np.argwhere(target["where"]),
                    target["digitized"][target["where"]],
                )
            ]

            yield (0, 0, 0)

            for d in x0:
                yield (d["at"] + 1, 0, 0)

            for d in x1:
                yield (0, d["at"] + 1, 0)

            for d in x2:
                yield (0, 0, d["at"] + 1)

            for d0, d1 in product(x0, x1):
                if len({d0["arg"], d1["arg"]}) != 2:
                    continue
                yield (d0["at"] + 1, d1["at"] + 1, 0)

            for d0, d2 in product(x0, x2):
                if len({d0["arg"], d2["arg"]}) != 2:
                    continue
                yield (d0["at"] + 1, 0, d2["at"] + 1)

            for d1, d2 in product(x1, x2):
                if len({d1["arg"], d2["arg"]}) != 2:
                    continue
                yield (0, d1["at"] + 1, d2["at"] + 1)

            for d0, d1, d2 in product(x0, x1, x2):
                if len({d0["arg"], d1["arg"], d2["arg"]}) != 3:
                    continue
                yield (d0["at"] + 1, d1["at"] + 1, d2["at"] + 1)

        reduced = (
            df
            .rdd
            .flatMap(f)
            .aggregate(
                np.zeros([nbins0 + 1, nbins1 + 1, nbins2 + 1], dtype="int64"),
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


def cov211(
        df: pyspark.sql.DataFrame,
        key00: str,
        key01: str,
        key1: typing.Optional[str] = None,
        key2: typing.Optional[str] = None,
        ) -> typing.Callable[..., dict]:
    """
    Examples
    --------
    Typical use for Fish covariant with certain TOF region:

    >>> import pyspark.sql.functions as f
    >>> df: pyspark.sql.DataFrame
    >>> fish = cov211(
    ...     df.select(f.col("hits.t").alias("t"),
    ...               f.col("hits.y").alias("y")),
    ...     "t", "y",
    ... )
    >>> fish(
    ...     fr00=1000, to00=6000, nbins00=2000,
    ...     fr01=-50, to01=50, nbins01=100,
    ...     fr1=3800, to1=4000,
    ...     fr2=5200, to2=5400,
    ... )["Cov[X,Y,Z]"][..., 0, 0]
    """
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
                {"arg": arg, "at": at - 1}
                for (arg,), at in zip(
                    np.argwhere(where),
                    np.stack([target00["digitized"],
                              target01["digitized"]], axis=-1)[where],
                )
            ]

            target = digitize(
                row[key1],
                bins=np.linspace(fr1, to1, nbins1 + 1),
            )
            x1 = [
                {"arg": arg, "at": at - 1}
                for (arg,), at in zip(
                    np.argwhere(target["where"]),
                    target["digitized"][target["where"]],
                )
            ]

            target = digitize(
                row[key2],
                bins=np.linspace(fr2, to2, nbins2 + 1),
            )
            x2 = [
                {"arg": arg, "at": at - 1}
                for (arg,), at in zip(
                    np.argwhere(target["where"]),
                    target["digitized"][target["where"]],
                )
            ]

            yield (0, 0, 0, 0)

            for d in x0:
                yield (*(d["at"] + 1), 0, 0)

            for d in x1:
                yield (0, 0, d["at"] + 1, 0)

            for d in x2:
                yield (0, 0, 0, d["at"] + 1)

            for d0, d1 in product(x0, x1):
                if len({d0["arg"], d1["arg"]}) != 2:
                    continue
                yield (*(d0["at"] + 1), d1["at"] + 1, 0)

            for d0, d2 in product(x0, x2):
                if len({d0["arg"], d2["arg"]}) != 2:
                    continue
                yield (*(d0["at"] + 1), 0, d2["at"] + 1)

            for d1, d2 in product(x1, x2):
                if len({d1["arg"], d2["arg"]}) != 2:
                    continue
                yield (0, 0, d1["at"] + 1, d2["at"] + 1)

            for d0, d1, d2 in product(x0, x1, x2):
                if len({d0["arg"], d1["arg"], d2["arg"]}) != 3:
                    continue
                yield (*(d0["at"] + 1), d1["at"] + 1, d2["at"] + 1)

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
