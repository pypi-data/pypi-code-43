import inspect
from typing import Union, List

from pyspark.sql.types import StructType, DataType, StructField


def _field_is(field: StructField, tipe: Union[str, Union[DataType, type]]) -> bool:
    if isinstance(tipe, str):
        return tipe.lower() == field.dataType.typeName() or tipe.lower() == field.dataType.simpleString()
    else:
        if inspect.isclass(tipe):
            return isinstance(field.dataType, tipe)
        else:
            return field.dataType.simpleString() == tipe.simpleString()


class SparkleStructType(StructType):

    # noinspection PyPep8Naming
    def colsOffType(self, tipe: Union[str, Union[DataType, type]]):
        return [f.name for f in self.offType(tipe)]

    # noinspection PyPep8Naming
    def offType(self, tipe: Union[str, DataType]) -> List[StructField]:
        return [f for f in self.fields if _field_is(f, tipe)]


def sparkle_struct_type(s):
    s.__class__ = SparkleStructType
    return s


StructType.colsOffType = SparkleStructType.colsOffType
StructType.offType = SparkleStructType.offType
