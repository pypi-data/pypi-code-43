from datetime import date, timedelta
from pyspark.sql.types import *
from pyspark.sql.functions import *
from math import ceil
from pyspark.sql.dataframe import DataFrame


#spark Session aufmachen
spark = pyspark.sql.SparkSession.builder.getOrCreate()


def getDateDF(spark, startDate:date, endDate:date) -> DataFrame:
  
  #abstand der daten ausrechnen
  lag = (endDate-startDate).days
  print("Abstand in Tagen: " + str(lag))
  if lag <= 0:
    raise Exception("The input dates do not make sense...")
  
  #Dates in eine Liste schreiben
  listOfDates = []
  for x in range(0, lag + 1):
    listOfDates.append([startDate + timedelta(days=x)])
  
  #Dataframe erstellen
  schema = StructType([StructField("Date", DateType(), True)])
  dfDates = spark.createDataFrame(listOfDates, schema)
  
  return dfDates


def getDateTable(startDate:date, endDate:date) -> DataFrame:
  def getMonthName(monthNumber:int) -> str:
    dicMonths = {
      1:"January",
      2:"February",
      3:"March",
      4:"April",
      5:"May",
      6:"June",
      7:"July",
      8:"August",
      9:"September",
      10:"October",
      11:"November",
      12:"December"
    }
    return dicMonths[monthNumber]
  def getHalfYear(myDate:date) -> int:
    monat = myDate.month
    rounded = ceil(monat/6)
    return rounded
  #udfs registrieren
  # registerMyUDFs(spark)
  getMonthName = spark.udf.register("getMonthName", getMonthName, StringType())
  getHalfYear = spark.udf.register("getHalfYear", getHalfYear, IntegerType())
  #Daten in einen Dataframe lesen
  df = getDateDF(spark, startDate, endDate)

  #spalten hinzufügen
  df = df.withColumn("Year", year(df["Date"]))
  df = df.withColumn("MonthNumber", month(df["Date"]))
  df = df.withColumn("MonthId", df["Year"]*100 + df["MonthNumber"])
  # df = df.withColumn("MonthName", getMonthName(df["MonthNumber"]))
  df = df.withColumn("DateSID", df["MonthId"]*100 + dayofmonth(df["Date"]))
  df = df.withColumn("QuarterNumber", quarter(df["Date"]))
  df = df.withColumn("QuarterId", df["Year"] * 100 + df["QuarterNumber"])
  df = df.withColumn("QuarterName", concat(df["QuarterNumber"].cast(StringType()), lit(". Quarter")))
  df = df.withColumn("HalfYearNumber", getHalfYear(df["Date"]))
  df = df.withColumn("HalfYearId", df["Year"] * 100 + df["HalfYearNumber"])
  df = df.withColumn("HalfYearName", concat(df["HalfYearNumber"].cast(StringType()), lit(". Halfyear")))
  return df