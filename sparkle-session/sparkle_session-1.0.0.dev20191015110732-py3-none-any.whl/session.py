import inspect
import types

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.types import StructType
import collections

from sparkle_session.utils import _get_class_name


class SparkleSession(SparkSession):

    # noinspection PyPep8Naming
    def emptyDataFrame(self) -> DataFrame:
        schema = StructType([])
        return self.createDataFrame(self.sparkContext.emptyRDD(), schema)

    def log(self, name: str = None):
        if not name:
            name = _get_class_name(inspect.stack()[1][0])
        logging = self._jvm.org.apache.log4j.Logger.getLogger(name)

        def dbg(lgr, msg: str, format_args):
            # noinspection PyUnresolvedReferences
            """
                Laizy evaluation of debug code

                >>> log.dbg("Count of my df: {}", lambda: df.cache().count())
                :param lgr:
                :param msg: The log string with optional {}s in it
                :param format_args: a function that when called returns a list of the arguments for str.format()
                :return:
            """

            if lgr.isDebugEnabled():
                args = format_args()
                if isinstance(args, collections.Iterable):
                    lgr.debug(msg.format(*args))
                else:
                    lgr.debug(msg.format(args))

        logging.dbg = types.MethodType(dbg, logging)

        return logging


def session_sparkle(spark) -> SparkleSession:
    spark.__class__ = SparkleSession
    return spark
