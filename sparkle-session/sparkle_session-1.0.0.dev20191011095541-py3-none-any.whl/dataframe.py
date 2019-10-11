from abc import ABC

from pyspark.sql import DataFrame


# noinspection PyPep8Naming
class SparkleDataFrame(ABC, DataFrame):
    def any(self, condition) -> bool:
        return self.filter(condition).first() is not None

    def all(self, condition) -> bool:
        return self.filter(condition).count() == self.count()

    def easyUnion(self, df: 'SparkleDataFrame', trim_colums=False, expand_columns=False):
        if self.hasSameColumns(df):
            return self.union(df.select(*self.columns))
        else:
            raise NotImplementedError("Only supporting same columns for now")

    def isEmpty(self):
        return self.rdd.isEmpty()

    def hasSameColumns(self, other: DataFrame):
        my_cols = set(self.columns)
        them_cols = set(other.columns)
        return my_cols == them_cols


DataFrame.isEmpty = SparkleDataFrame.isEmpty
DataFrame.any = SparkleDataFrame.any
DataFrame.all = SparkleDataFrame.all
DataFrame.sparkle_union = SparkleDataFrame.easyUnion
DataFrame.hasSameColumns = SparkleDataFrame.hasSameColumns


def sparkle_df(df) -> SparkleDataFrame:
    df.__class__ = SparkleDataFrame
    return df
