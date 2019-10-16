import typing
from functools import reduce

import pyspark
import pyspark.sql.functions as f
from numba import jit
import numpy as np

from .markup import compute, compute_err


__all__ = [
    "digitize", "increase",
    "SpkPersist", "SpkRepart", "SpkMapPartThanSum", "SpkCrossJoin",
    "ReferTo", "AppendCov", "AppendCCov",
]


def digitize(
        arr: (typing.List[float], np.ndarray),
        bins: (typing.List[float], np.ndarray),
        ) -> dict:
    n, m = len(arr), len(bins)
    digitized = np.digitize(arr, bins=bins)
    where = (0 < digitized) & (digitized < m)
    return {
        "digitized": digitized,
        "where": where,
    }


@jit(nopython=True, nogil=True)
def increase(counter: np.ndarray, at: tuple) -> np.ndarray:
    counter[at] += 1
    return counter


class SpkPersist:
    def __init__(self, where: typing.Optional[str] = "MEMORY_AND_DISK"):
        options = {
            "DISK_ONLY": pyspark.StorageLevel.DISK_ONLY,
            "DISK_ONLY_2": pyspark.StorageLevel.DISK_ONLY_2,
            "MEMORY_ONLY": pyspark.StorageLevel.MEMORY_ONLY,
            "MEMORY_ONLY_2": pyspark.StorageLevel.MEMORY_ONLY_2,
            "MEMORY_AND_DISK": pyspark.StorageLevel.MEMORY_AND_DISK,
            "MEMORY_AND_DISK_2": pyspark.StorageLevel.MEMORY_AND_DISK_2,
            "OFF_HEAP": pyspark.StorageLevel.OFF_HEAP,
        }

        if not (where is None or where in options):
            raise ValueError(
                f'Argument "on" (passed as "{where}") has to be '
                f'None or one of {", ".join(options)}!',
            )
        self.__where = None if where is None else options[where]

    def __call__(self, df: pyspark.sql.DataFrame) -> pyspark.sql.DataFrame:
        if self.__where is None:
            return df
        return df.persist(self.__where)

    def __ror__(self, other: pyspark.sql.DataFrame) -> pyspark.sql.DataFrame:
        return self(other)


class SpkRepart:
    def __init__(self, npart: typing.Optional[int] = None):
        self.__npart = npart

    def __call__(self, df: pyspark.sql.DataFrame) -> pyspark.sql.DataFrame:
        npart = self.__npart
        if npart is None:
            return df
        return df.repartition(npart)

    def __ror__(self, other: pyspark.sql.DataFrame) -> pyspark.sql.DataFrame:
        return self(other)


class SpkCrossJoin:
    def __init__(
            self,
            *columns: str,
            fraction: typing.Optional[float] = None,
            npart: typing.Optional[int] = None,
            ):
        if len(columns) == 0:
            raise ValueError('Argument "columns" must have at least one element!')

        self.__columns = columns
        self.__fraction = None if fraction is None else float(fraction)
        self.__npart = npart

    def __sampled(self, df: pyspark.sql.DataFrame) -> pyspark.sql.DataFrame:
        if self.__fraction is None:
            return df
        return df.sample(False, self.__fraction)

    def __selected(self,
            df: pyspark.sql.DataFrame,
            ) -> typing.Iterable[pyspark.sql.DataFrame]:
        for c in self.__columns:
            yield (
                self
                .__sampled(df)
                .select(f.explode(f"h.{c}").alias("h"))
                .select("h.*")
            )

    def __call__(self, df: pyspark.sql.DataFrame) -> pyspark.sql.DataFrame:
        ret = reduce(pyspark.sql.DataFrame.crossJoin, self.__selected(df))
        if self.__npart is None:
            return ret
        return ret.coalesce(self.__npart)

    def __ror__(self, other: pyspark.sql.DataFrame) -> pyspark.sql.DataFrame:
        return self(other)


Return = typing.TypeVar("Return")


class SpkMapPartThanSum(typing.Generic[Return]):
    def __init__(self, f: typing.Callable[[typing.List[pyspark.sql.Row]], Return]):
        self.__f = f

    def __call__(self, df: pyspark.sql.DataFrame) -> Return:
        return df.rdd.mapPartitions(self.__f).sum()

    def __ror__(self, other: pyspark.sql.DataFrame) -> Return:
        return self(other)


class ReferTo:
    def __init__(self, ref: str, *keys: str):
        self.__ref, self.__keys = ref, keys

    def __call__(self, d: dict) -> dict:
        ref, keys = self.__ref, self.__keys
        return {
            **{k: d[ref] for k in keys},
            **d,
        }

    def __ror__(self, other: dict) -> dict:
        return self(other)


class AppendCov:
    def __init__(self, *keys: str):
        if not 1 < len(keys) < 4:
            raise ValueError(f"Too less or many keys: {', '.join(keys)}!")

        self.__keys = keys

    def __call__(self, d: dict) -> dict:
        keys = self.__keys

        if len(keys) == 2:
            i, j = keys
            return {
                f"Cov[{i},{j}]": (
                    d[f"Sum[{i}{j}]"] / d["N"]
                    - np.einsum("i...,j->i...j",
                                d[f"Sum[{i}]"],
                                d[f"Sum[{j}]"]) / d["N"] ** 2
                ),
                f"Err[Cov[{i},{j}]]": (
                    (d[f"Sum[{i}{j}]"] ** 0.5 / d["N"]) ** 2
                    + (np.einsum("i...,j->i...j",
                                 d[f"Sum[{i}]"],
                                 d[f"Sum[{j}]"]) ** 0.5 / d["N"] ** 2) ** 2
                ) ** 0.5,
                **d,
            }

        if len(keys) == 3:
            i, j, k = keys
            return {
                f"Cov[{i},{j},{k}]": (
                    d[f"Sum[{i}{j}{k}]"] / d["N"]
                    - np.einsum("i...j,k->i...jk",
                                d[f"Sum[{i}{j}]"],
                                d[f"Sum[{k}]"]) / d["N"] ** 2
                    - np.einsum("i...,jk->i...jk",
                                d[f"Sum[{i}]"],
                                d[f"Cov[{j},{k}]"]) / d["N"]
                    - np.einsum("j...,ik->ij...k",
                                d[f"Sum[{j}]"],
                                d[f"Cov[{i},{k}]"]) / d["N"]
                ),
                f"Err[Cov[{i},{j},{k}]]": (
                    (d[f"Sum[{i}{j}{k}]"] ** 0.5 / d["N"]) ** 2
                    + (np.einsum("i...j,k->i...jk",
                                 d[f"Sum[{i}{j}]"],
                                 d[f"Sum[{k}]"]) ** 0.5 / d["N"] ** 2) ** 2
                    + (np.einsum("i...,jk->i...jk",
                                 d[f"Sum[{i}]"],
                                 d[f"Cov[{j},{k}]"]) ** 0.5 / d["N"]) ** 2
                    + (np.einsum("j...,ik->ij...k",
                                 d[f"Sum[{j}]"],
                                 d[f"Cov[{i},{k}]"]) ** 0.5 / d["N"]) ** 2
                ) ** 0.5,
                **d,
            }

    def __ror__(self, other: dict) -> dict:
        return self(other)


class AppendCCov:
    def __init__(self, *keys: str):
        if not 1 < len(keys) < 4:
            raise ValueError(f"Too less or many keys: {', '.join(keys)}!")

        self.__keys = keys

    def __call__(self, d: dict) -> dict:
        keys = self.__keys

        if len(keys) == 2:
            i, j = keys
            return {
                f"Cov[{i},{j}]": (
                    compute(d[f"Sum[{i}{j}]"]) / d["N"]
                    - compute(d[f"Sum[{i}]Sum[{j}]"]) / d["N"] ** 2
                ),
                f"Err[Cov[{i},{j}]]": (
                    (compute_err(d[f"Sum[{i}{j}]"]) / d["N"]) ** 2
                    + (compute_err(d[f"Sum[{i}]Sum[{j}]"]) / d["N"] ** 2) ** 2
                ) ** 0.5,
                **d,
            }

        if len(keys) == 3:
            i, j, k = keys
            return {
                f"Cov[{i},{j},{k}]": (
                    compute(d[f"Sum[{i}{j}{k}]"]) / d["N"]
                    - compute(d[f"Sum[{i}{j}]Sum[{k}]"]) / d["N"] ** 2
                    - compute(d[f"Sum[{i}{k}]Sum[{j}]"]) / d["N"] ** 2
                    - compute(d[f"Sum[{j}{k}]Sum[{i}]"]) / d["N"] ** 2
                    + 2 * compute(d[f"Sum[{i}]Sum[{j}]Sum[{k}]"]) / d["N"] ** 3
                ),
                f"Err[Cov[{i},{j},{k}]]": (
                    (compute_err(d[f"Sum[{i}{j}{k}]"]) / d["N"]) ** 2
                    + (compute_err(d[f"Sum[{i}{j}]Sum[{k}]"]) / d["N"] ** 2) ** 2
                    + (compute_err(d[f"Sum[{i}{k}]Sum[{j}]"]) / d["N"] ** 2) ** 2
                    + (compute_err(d[f"Sum[{j}{k}]Sum[{i}]"]) / d["N"] ** 2) ** 2
                    + (2 * compute_err(d[f"Sum[{i}]Sum[{j}]Sum[{k}]"]) / d["N"] ** 3) ** 2
                ) ** 0.5,
                **d,
            }

    def __ror__(self, other: dict) -> dict:
        return self(other)
