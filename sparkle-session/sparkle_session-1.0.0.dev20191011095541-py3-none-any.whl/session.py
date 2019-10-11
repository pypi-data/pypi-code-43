import inspect

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.types import StructType


def _get_class_name(fr):
    c = _get_class_from_frame(fr)
    if c:
        return c.__name__
    else:
        return None


def _get_class_from_frame(fr):
    args, _, _, value_dict = inspect.getargvalues(fr)
    # we check the first parameter for the frame function is
    # named 'self'
    if len(args) and args[0] == 'self':
        # in that case, 'self' will be referenced in value_dict
        instance = value_dict.get('self', None)
        if instance:
            # return its class
            return getattr(instance, '__class__', None)
    # return None otherwise
    return None


# noinspection PyPep8Naming
class SparkleSession(SparkSession):

    def emptyDataFrame(self) -> DataFrame:
        schema = StructType([])
        return self.createDataFrame(self.sparkContext.emptyRDD(), schema)

    def log(self, name: str = None):
        if not name:
            name = _get_class_name(inspect.stack()[1][0])
        mylogger = self._jvm.org.apache.log4j.Logger.getLogger(name)
        return mylogger


SparkSession.emptyDataFrame = SparkleSession.emptyDataFrame
SparkSession.log = SparkleSession.log


def session_sparkle(spark) -> SparkleSession:
    return spark
