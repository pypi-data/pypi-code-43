from datetime import date, timedelta
from pyspark.sql.types import *
from pyspark.sql.functions import *
from math import ceil
from pyspark.sql.dataframe import DataFrame
import pyspark

#spark Session aufmachen
spark = pyspark.sql.SparkSession.builder.getOrCreate()


def getDateDF(spark, startYear:int, endYear:int) -> DataFrame:
  
  startDate = date(startYear, 1, 1)
  endDate = date(endYear, 12, 31)

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
  
  def getIsoCalendarWeek(myDate:date) -> int:
    myWeek = myDate.isocalendar()[1]
    return myWeek
  
  def getWeekday(myDate:date) -> int:
    weekDay = myDate.strftime('%w')
    return int(weekDay)
  
  def getWeekdayName(weekday:int) -> str:
    german_weekdayNames = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
    english_weekdayNames = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return english_weekdayNames[weekday]
  
  def getConcatWithHyphen(firstPart, secondPart) -> str:
    return str(firstPart) + "-" + str(secondPart)

  #udfs registrieren
  getMonthName = spark.udf.register("getMonthName", getMonthName, StringType())
  getHalfYear = spark.udf.register("getHalfYear", getHalfYear, IntegerType())
  getIsoCalendarWeek = spark.udf.register("getIsoCalendarWeek", getIsoCalendarWeek, IntegerType())
  getWeekday =  spark.udf.register("getWeekday", getWeekday, IntegerType())
  getWeekdayName =  spark.udf.register("getWeekdayName", getWeekdayName, StringType())
  getConcatWithHyphen =  spark.udf.register("getConcatWithHyphen", getConcatWithHyphen, StringType())
  
  
  #Simple Datumsspalte in einen Dataframe lesen
  df = getDateDF(spark, startDate, endDate)

  #spalten hinzufügen
  df = df.withColumn("Year", year(df["Date"]))
  df = df.withColumn("MonthNumber", month(col("Date")))
  df = df.withColumn("MonthId", df["Year"]*100 + df["MonthNumber"])
  df = df.withColumn("MonthName", getMonthName(df["MonthNumber"]))
  df = df.withColumn("DateSID", df["MonthId"]*100 + dayofmonth(df["Date"]))
  df = df.withColumn("QuarterNumber", quarter(df["Date"]))
  df = df.withColumn("QuarterId", df["Year"] * 100 + df["QuarterNumber"])
  df = df.withColumn("QuarterName", concat(df["QuarterNumber"].cast(StringType()), lit(". Quarter")))
  df = df.withColumn("HalfYearNumber", getHalfYear(df["Date"]))
  df = df.withColumn("HalfYearId", df["Year"] * 100 + df["HalfYearNumber"])
  df = df.withColumn("HalfYearName", concat(df["HalfYearNumber"].cast(StringType()), lit(". Halfyear")))
  df = df.withColumn("IsoCalendarWeek", getIsoCalendarWeek(col("Date")))
  df = df.withColumn("IsoCalendarWeekYear", col("Year"))
  df = df.withColumn("IsoCalendarWeekId", col("IsoCalendarWeekYear") * 100 + col("IsoCalendarWeek"))
  df = df.withColumn("MonthDay", dayofmonth(col("Date")))
  df = df.withColumn("Weekday", getWeekday(col("Date")))
  df = df.withColumn("WeekdayName", getWeekdayName(col("Weekday")))
  df = df.withColumn("YearMonth", getConcatWithHyphen(col("Year"), col("MonthNumber")))
  df = df.withColumn("YearWeek", getConcatWithHyphen(col("Year"), col("IsoCalendarWeek")))
  
  #Reihenfolge anpassen
  df = df.select("DateSID", "Date", "Year", "YearMonth", "YearWeek", "HalfYearId", "HalfYearNumber", "HalfYearName", "QuarterId", "QuarterNumber", "QuarterName", "MonthId", "MonthNumber", "MonthDay", "MonthName", "IsoCalendarWeekId", "IsoCalendarWeekYear", "IsoCalendarWeek", "Weekday", "WeekdayName")


  return df