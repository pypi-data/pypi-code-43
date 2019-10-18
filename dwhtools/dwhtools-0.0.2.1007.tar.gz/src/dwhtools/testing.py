import pyspark
from pyspark.sql import Row
from pyspark.sql.dataframe import DataFrame
from pyspark.sql.types import *

from datetime import datetime, date
from decimal import Decimal


#sparkSession aufmachen
spark = pyspark.sql.SparkSession.builder.getOrCreate()


def getTestData() -> DataFrame:
  row1 = Row(MenschName = "Herbert", Stadt = None, Abteilung = "Purchase", PersonalNummer = 1)
  row2 = Row(MenschName = "Gundula", Stadt = "Düsseldorf", Abteilung = "HR", PersonalNummer = None)
  row3 = Row(MenschName = "Petra", Stadt = "Berlin", Abteilung = "Finance", PersonalNummer = 3)
  row4 = Row(MenschName = "Serafina", Stadt = "Berlin", Abteilung = "Finance", PersonalNummer = 4)

  departmentsWithEmployees_Seq = [row1, row2, row3, row4]
  dframe = spark.createDataFrame(departmentsWithEmployees_Seq)
  return dframe


def getTestDataWithAllDataTypes() -> DataFrame:

  rowList = []
  rowList.append(Row(1, "Herbert", 22, Decimal(3.5), None, 1.12345, 3, -123, 12345, bytearray("hallo", "utf-8"), True, datetime(2019, 2, 3, 14, 3, 5), date(1900, 2, 3), [1, 2], {1:"Hey"}, None))
  rowList.append(Row(2, "Gundula", None, Decimal(4.0), -1.123, 4.1231, -1, None, -512311, None, False, None, date(2500, 12, 3), [0, None], {1:"Hey", 5:"Hallo"}, [1, "hey"]))
  rowList.append(Row(3, None, 35, Decimal(1.5), 2.124, 1.0, None, 1412, None, bytearray("hi 123 !! :)", "utf-8"), None, datetime(2019, 10, 31, 9, 1, 4), None, [-3, 999], None, [3, "yes"]))
  rowList.append(Row(4, "Serafina", 32, None, -2.123435, None, 1, 1234, 3, bytearray("big data", "utf-16"), True, datetime(1900, 2, 3, 1, 2, 3), date(1900, 2, 3), None, {3:None}, [-5, "string"]))

  fieldList = []
  fieldList.append(StructField("RowId", IntegerType()))
  fieldList.append(StructField("String", StringType()))
  fieldList.append(StructField("Integer", IntegerType()))
  fieldList.append(StructField("Decimal", DecimalType(10, 5)))
  fieldList.append(StructField("Float", FloatType()))
  fieldList.append(StructField("Double", DoubleType()))
  fieldList.append(StructField("Byte", ByteType()))
  fieldList.append(StructField("Short", ShortType()))
  fieldList.append(StructField("Long", LongType()))
  fieldList.append(StructField("Binary", BinaryType()))
  fieldList.append(StructField("Boolean", BooleanType()))
  fieldList.append(StructField("Timestamp", TimestampType()))
  fieldList.append(StructField("Date", DateType()))
  fieldList.append(StructField("Array", ArrayType(IntegerType())))
  fieldList.append(StructField("Map", MapType(IntegerType(), StringType())))
  fieldList.append(StructField("StructType", StructType([StructField("Feld1", IntegerType()), StructField("Feld2", StringType())])))
  schema = StructType(fieldList)
  
  df = spark.createDataFrame(rowList, schema)
  return df