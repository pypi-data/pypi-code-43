import typing
from itertools import product
from functools import lru_cache

import numpy as np
import pyspark

from .core import digitize, increase, AppendCov, ReferTo


__all__ = [
    "cov11_simple", "cov111_simple",
]


def cov11_simple(
        df: pyspark.sql.DataFrame,
        key: str,
        ) -> typing.Callable[..., dict]:
    """
    Examples
    --------
    Typical use for PIPICO:

    >>> import pyspark.sql.functions as f
    >>> df: pyspark.sql.DataFrame
    >>> pipico = cov11_simple(
    ...     df.select(f.col("hits.t").alias("t")),
    ...     "t",
    ... )
    >>> pipico(fr=1000, to=6000, nbins=500)["Cov[X,Y]"]
    """

    @lru_cache()
    def analyzer(fr: float, to: float, nbins: int) -> dict:

        def f(row: pyspark.sql.Row) -> typing.Iterator[tuple]:
            target = digitize(
                row[key],
                bins=np.linspace(fr, to, nbins + 1),
            )
            x = [
                {"arg": arg, "at": at - 1}
                for (arg,), at in zip(
                    np.argwhere(target["where"]),
                    target["digitized"][target["where"]],
                )
            ]

            yield (0, 0)

            for d in x:
                yield (d["at"] + 1, 0)

            for d0, d1 in product(x, x):
                if len({d0["arg"], d1["arg"]}) != 2:
                    continue
                yield (d0["at"] + 1, d1["at"] + 1)

        reduced = (
            df
            .rdd
            .flatMap(f)
            .aggregate(
                np.zeros(2 * [nbins + 1], dtype="int64"),
                increase,
                np.add,
            )
        )
        return {
            "N": reduced[0, 0],
            "Sum[X]": reduced[1:, 0],
            "Sum[XY]": reduced[1:, 1:],
        } | ReferTo("Sum[X]", "Sum[Y]") | AppendCov("X", "Y")
    return analyzer


def cov111_simple(
        df: pyspark.sql.DataFrame,
        key: str,
        ) -> typing.Callable[..., dict]:
    """
    Examples
    --------
    Typical use for 3PICO:

    >>> import pyspark.sql.functions as f
    >>> df: pyspark.sql.DataFrame
    >>> threepico = cov111_simple(
    ...     df.select(f.col("hits.t").alias("t")),
    ...     "t",
    ... )
    >>> threepico(fr=2000, to=6000, nbins=200)["Cov[X,Y,Z]"]
    """

    @lru_cache()
    def analyzer(fr: float, to: float, nbins: int) -> dict:

        def f(row: pyspark.sql.Row) -> typing.Iterator[tuple]:
            target = digitize(
                row[key],
                bins=np.linspace(fr, to, nbins + 1),
            )
            x = [
                {"arg": arg, "at": at - 1}
                for (arg,), at in zip(
                    np.argwhere(target["where"]),
                    target["digitized"][target["where"]],
                )
            ]

            yield (0, 0, 0)

            for d in x:
                yield (d["at"] + 1, 0, 0)

            for d0, d1 in product(x, repeat=2):
                if len({d0["arg"], d1["arg"]}) != 2:
                    continue
                yield (d0["at"] + 1, d1["at"] + 1, 0)

            for d0, d1, d2 in product(x, repeat=3):
                if len({d0["arg"], d1["arg"], d2["arg"]}) != 3:
                    continue
                yield (d0["at"] + 1, d1["at"] + 1, d2["at"] + 1)

        reduced = (
            df
            .rdd
            .flatMap(f)
            .aggregate(
                np.zeros(3 * [nbins + 1], dtype="int64"),
                increase,
                np.add,
            )
        )
        return (
            {
                "N": reduced[0, 0, 0],
                "Sum[X]": reduced[1:, 0, 0],
                "Sum[XY]": reduced[1:, 1:, 0],
                "Sum[XYZ]": reduced[1:, 1:, 1:],
            } | ReferTo("Sum[X]", "Sum[Y]", "Sum[Z]")
            | ReferTo("Sum[XY]", "Sum[XZ]", "Sum[YZ]")
            | AppendCov("X", "Y") | ReferTo("Cov[X,Y]", "Cov[X,Z]", "Cov[Y,Z]")
            | AppendCov("X", "Y", "Z")
        )
    return analyzer
