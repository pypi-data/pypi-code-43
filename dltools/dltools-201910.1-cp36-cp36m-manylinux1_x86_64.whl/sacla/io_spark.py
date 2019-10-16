from pyspark.sql import DataFrame, Column
from pyspark.sql.functions import col, udf
from .. import SpkHits, zip_to_hits
from . import Model, Models

__all__ = [
    'restructure',
    'load_analyzer',
]


def restructure(df: DataFrame) -> DataFrame:
    zipped = udf(zip_to_hits, SpkHits)
    c = col('SortedEvent.fDetektors')[0]['fDetektors_fHits']
    return df.select(
        col('SortedEvent.fEventID').alias("tag"),
        zipped(
            c['fTime'],
            c['fX_mm'],
            c['fY_mm'],
            c['fRekmeth'],
        ).alias('hits'),
    )


def load_analyzer(config: dict) -> Column:
    model = Models(
        {k: Model(**{**config, **m})
         for k, m in config.pop("models").items()},
    )
    return udf(model, SpkHits)
