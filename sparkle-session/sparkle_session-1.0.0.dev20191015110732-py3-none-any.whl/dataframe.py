import inspect
from abc import ABC
from typing import Union, Tuple, Type

from pyspark.sql import DataFrame
# noinspection PyUnresolvedReferences
from pyspark.sql.functions import max as s_max

# noinspection PyPep8Naming
from pyspark.sql.types import DataType, StructField


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
        my_cols = self.col_set
        them_cols = other.col_set
        return my_cols == them_cols

    def max_value(self, col_name: str):
        return self.select(s_max(col_name).alias('max_val')).first().max_val

    @property
    def col_set(self):
        return set(self.columns)

    def requireColumn(self, *name: Union[str, Tuple[str, Type[DataType]]]):
        for n in name:
            if isinstance(n, str):
                assert n in self.columns, "Expecting column {} to exist in {}".format(n, self.columns)
            else:
                assert isinstance(n, Tuple), "Unexpected type {}".format(type(n))
                if inspect.isclass(n[1]):
                    t = n[1]()
                else:
                    t = n[1]
                name_type_found = any([f.name == n[0] and f.dataType == t for f in self.schema.fields])
                assert name_type_found, "Column '{}' of type {} not present in {}".format(n[0], n[1],
                                                                                          self.schema.fields)


DataFrame.isEmpty = SparkleDataFrame.isEmpty
DataFrame.any = SparkleDataFrame.any
DataFrame.all = SparkleDataFrame.all
DataFrame.sparkle_union = SparkleDataFrame.easyUnion
DataFrame.hasSameColumns = SparkleDataFrame.hasSameColumns
DataFrame.requireColumn = SparkleDataFrame.requireColumn


def sparkle_df(df) -> SparkleDataFrame:
    df.__class__ = SparkleDataFrame
    return df
