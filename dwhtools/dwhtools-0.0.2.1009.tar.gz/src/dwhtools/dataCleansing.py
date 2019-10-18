import pyspark
from pyspark.sql.dataframe import DataFrame
from datetime import datetime

#spark Session aufmachen
spark = pyspark.sql.SparkSession.builder.getOrCreate()


def replaceNulls(df:DataFrame, valueForNumbers:int = -99, valueForStrings:str = "-", valueForBool:bool = False) -> DataFrame:
  numberCols = []
  stringCols = []
  boolCols = []
  
  for col in df.dtypes:
    name = col[0]
    typ = col[1]
    if typ == "int" or typ[:7] == "decimal" or typ == "double" or typ == "bigint":
      numberCols.append(name)
    elif typ == "string":
      stringCols.append(name)
    elif typ == "boolean":
      boolCols.append(name)

      
  if len(numberCols) > 0:
    df = df.fillna(valueForNumbers, subset = numberCols)
  if len(stringCols) > 0:
    df = df.fillna(valueForStrings, subset = stringCols)
  if len(boolCols) > 0:
    df = df.fillna(valueForBool, subset = boolCols)
  return df
