from math import nan
from typing import Callable, Mapping, List
from pyspark.sql import Column, Row
from pyspark.sql.functions import udf
from .. import SpkHits

__all__ = [
    'load_analyzer',
]


dummy = {'px': nan, 'py': nan, 'pz': nan, 'ke': nan}


def init_model(fr: float, to: float) -> Callable[[Row], bool]:
    def f(hit: Row) -> bool:
        return fr < hit['t'] < to
    return f


def init_models(
        models: Mapping[str, Callable[[Row], bool]],
        ) -> Column:
    @udf(returnType=SpkHits)
    def col(hits: List[Row]) -> List[Row]:
        it = models.items()
        for hit in hits:
            for k, f in it:
                if f(hit):
                    hit['as_'][k] = dummy
        return hits
    return col


def load_analyzer(config: dict) -> Column:
    return init_models(
        {k: init_model(**{**config, **m})
         for k, m in config.pop('models').items()},
    )
