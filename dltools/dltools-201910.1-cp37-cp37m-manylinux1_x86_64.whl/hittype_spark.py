from typing import List, Optional
from functools import partial
from itertools import chain
from cytoolz import identity, compose
from pyspark.sql import Column
from pyspark.sql.types import (
    StructType, StructField, MapType, StringType, ArrayType,
    IntegerType, DoubleType,
)
from pyspark.sql.functions import udf
from . import combine, as_minsqsum, filter_duphits

__all__ = [
    'SpkAnalyzedHit',
    'SpkHit',
    'SpkHits',
    'SpkCombinedHit',
    'SpkCombinedHits',
    'load_combiner',
]

SpkAnalyzedHit = StructType([
    StructField('pz', DoubleType(), nullable=False),
    StructField('px', DoubleType(), nullable=False),
    StructField('py', DoubleType(), nullable=False),
    StructField('ke', DoubleType(), nullable=False),
])

SpkHit = StructType([
    StructField('t', DoubleType(), nullable=False),
    StructField('x', DoubleType(), nullable=False),
    StructField('y', DoubleType(), nullable=False),
    StructField('as_', MapType(StringType(), SpkAnalyzedHit), nullable=False),
    StructField('flag', IntegerType(), nullable=True),
])

SpkHits = ArrayType(SpkHit)

SpkCombinedHit = StructType([
    StructField('comb', SpkHits, nullable=False),
    StructField('as_', MapType(StringType(), SpkAnalyzedHit), nullable=False),
    StructField('flag', IntegerType(), nullable=True),
])

SpkCombinedHits = ArrayType(SpkCombinedHit)


def load_combiner(r: int,
                  white_list: Optional[List[List[str]]] = None,
                  allow_various: bool = True,
                  allow_dup: bool = True) -> Column:
    if white_list is None:
        f = partial(combine, r=r)
    else:
        for arr in white_list:
            if len(arr) != r:
                raise ValueError(
                    "The length of 'white_list' element must be"
                    "the value of 'r', {}!".format(r)
                )
        f = partial(
            combine,
            r=r,
            white_list={i for i in chain.from_iterable(white_list)},
        )
    if allow_various:
        g = identity
    else:
        if white_list is None:
            g = as_minsqsum
        else:
            g = partial(
                as_minsqsum,
                white_list={",".join(arr) for arr in white_list},
            )
    if allow_dup:
        h = identity
    else:
        h = filter_duphits
    return udf(compose(h, g, f), SpkCombinedHits)
