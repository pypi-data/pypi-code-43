import pyspark


#sparkSession aufmachen
spark = pyspark.sql.SparkSession.builder.getOrCreate()


class sqlQuery:
  def __init__(self):
    self.text = ""
  
  def addRow(self, newText:str, indentTabs:int=0, makeRowBreak:bool=True):
    for i in range (1, indentTabs + 1):
      self.text += "\t"
    self.text += newText
    if makeRowBreak:
      self.text += "\n"

class scdColumn:
  def __init__(self, name:str, typ:str, scdTyp:int):
    
    allowedScdTypes = ["0", "1", "2", "SK", "BK", "ValidFrom", "ValidUntil", "isValid", "Timestamp", "Technical"]
    #scd typ 0, 1 und 2 sind wie die im BiDesigner
    if scdTyp not in allowedScdTypes:
      raise Exception("scdTyp " + str(scdTyp) + " is not valid!")
    self.name = name
    self.typ = typ
    self.scdTyp = scdTyp

class scdManager:
  def __init__(self):
    self.Columns = []
    self.Columns.append(scdColumn("MatchWithTarget", "Boolean", "Technical"))
    self.Columns.append(scdColumn("ScdOneChange", "Boolean", "Technical"))
    self.Columns.append(scdColumn("ScdTwoChange", "Boolean", "Technical"))
    #self.technischeSpalten = ["MatchWithTarget", "ScdOneChange", "ScdTwoChange"]

    #das folgende ist wichtig, um falsche Fehlermeldungen zu reduzieren
    self.scdTable = ""
    self.TimeRangeStartValue = ""
    self.dataSource = ""
    self.targetTable = ""
    self.TimeRangeEndValue = ""

  def addColumn(self, colName:str, dataType:str, scdType:str):
      myCol = scdColumn(colName, dataType, scdType)
      self.Columns.append(myCol)

  def getColumnsByScdTyp(self, scdTyp:str) -> scdColumn:
    resultList = []
    for col in self.Columns:
      if col.scdTyp == scdTyp:
        resultList.append(col)
    return resultList
  
  def buildDropTableStatement(self) -> str:
    query = sqlQuery()
    query.addRow("drop table if exists " + self.scdTable)
    return query.text
  
  def buildCreateTableStatement(self) -> str:
    timestampColumn = self.getColumnsByScdTyp("Timestamp")[0]

    query = sqlQuery()
    query.addRow("create table if not exists " + self.scdTable + " (")
    for col in self.Columns:
      if col.scdTyp in ["0", "1", "2", "BK", "ValidFrom", "Technical"]:
        query.addRow(col.name + " " + col.typ + ",", 1)
      
    query.addRow(timestampColumn.name + " " + timestampColumn.typ, 1)
    
    query.addRow(")")
    query.addRow("USING delta", makeRowBreak=False)
    return query.text
  
  def buildFillScdTableStatement(self) -> str:
    businessKeys = self.getColumnsByScdTyp("BK")

    scdOneColumns = self.getColumnsByScdTyp("1")
    scdTwoColumns = self.getColumnsByScdTyp("2")
    isValidCol = self.getColumnsByScdTyp("isValid")[0]
    timestampColumn = self.getColumnsByScdTyp("Timestamp")[0]
    
    if not businessKeys:
      raise Exception("We have no business Key!")
    
    query = sqlQuery()
    query.addRow("with sourceWithChanges as (")
    query.addRow("select not (isnull(target." + businessKeys[0].name + ")) as MatchWithTarget,", 1)
    
    #scd1 change ermitteln
    if scdOneColumns:
      query.addRow("(", 1)
      
      query.addRow("target." + scdOneColumns[0].name + " != source." + scdOneColumns[0].name , 2)
      for i in range(1, len(scdOneColumns)):
        query.addRow("OR" , 2)
        query.addRow("target." + scdOneColumns[i].name + " != source." + scdOneColumns[i].name , 2)
        
      
      query.addRow(") as ScdOneChange,", 1)
    else:
      query.addRow("False as ScdOneChange,", 1)
      
    #scd2 Change ermitteln
    if scdTwoColumns:
      query.addRow("(", 1)
      
      query.addRow("target." + scdTwoColumns[0].name + " != source." + scdTwoColumns[0].name , 2)
      for i in range(1, len(scdTwoColumns)):
        query.addRow("OR" , 2)
        query.addRow("target." + scdTwoColumns[i].name + " != source." + scdTwoColumns[i].name , 2)
        
      
      query.addRow(") as ScdTwoChange,", 1)
    else:
      query.addRow("False as ScdTwoChange,", 1)
    
    query.addRow("source.* from " + self.dataSource + " source", 1)
    
    #left join der bestehenden Tabelle
    query.addRow("left join (select * from " + self.targetTable + " where " + isValidCol.name + " = True) target", 1)
    query.addRow("on target." + businessKeys[0].name + " = source." + businessKeys[0].name, 1)
    for i in range(1, len(businessKeys)):
      query.addRow("and target." + businessKeys[i].name + " = source." + businessKeys[i].name, 1)
    query.addRow("),")
    
    #ValidFrom ermitteln
    query.addRow("sourceWithSK as (")
    query.addRow("select", 1)
    query.addRow("case when z.MatchWithTarget = True then", 2)
    query.addRow("z." + timestampColumn.name, 3)
    query.addRow("else", 2)
    query.addRow("from_utc_timestamp(" + self.TimeRangeStartValue + ", 'CET')", 3)
    query.addRow("end as ValidFrom,", 2)
    query.addRow("z.*", 2)
    query.addRow("from sourceWithChanges z", 2)
    query.addRow(")", 1)
    
    #in die scd-Tabelle inserten (nur über merge möglich, um die spaltennamen zu spezifizieren)    
    query.addRow("MERGE INTO " + self.scdTable + " as target")
    query.addRow("using (select * from sourceWithSK) as source", 1)
    query.addRow("ON False", 1)
    query.addRow("WHEN NOT MATCHED THEN", 1)
    query.addRow("insert (", 1)
    
    #Zielspaltennamen hinzufügen    
    for col in self.Columns:
      if col.scdTyp in ["0", "1", "2", "BK", "ValidFrom", "Technical"]:
        query.addRow(col.name + ",", 2)
    query.addRow(timestampColumn.name, 2)
    
    query.addRow(")", 2)
    query.addRow("VALUES", 2)
    query.addRow("(", 2)

    #Values hinzufügen
    for col in self.Columns:
      if col.scdTyp in ["0", "1", "2", "BK", "ValidFrom", "Technical"]:
        query.addRow("source." + col.name + ",", 2)
    query.addRow("source." + timestampColumn.name, 2)
    
    query.addRow(")", 1, makeRowBreak=False)
    return query.text
  
  def getBusinessKeyStringList(self) -> list:
    businessKeys = self.getColumnsByScdTyp("BK")
    if not businessKeys:
      raise Exception("There are no Business Keys!")
      
    returnList = []
    for businessKey in businessKeys:
      returnList.append(businessKey.name)
    return returnList
  
  def buildInsertMergeStatement(self) -> str:
    businessKeyNames = self.getBusinessKeyStringList()
    skColumn = self.getColumnsByScdTyp("SK")[0]
    isValidCol = self.getColumnsByScdTyp("isValid")[0]
    validUntilCol = self.getColumnsByScdTyp("ValidUntil")[0]
    query = sqlQuery()
    
    
    #an dieser Stelle wird der Surrogate Key ermittelt
    skQuery = "row_number() over (order by MatchWithTarget, ScdTwoChange desc, "+ ', '.join(businessKeyNames)+ ") + (select nvl(max(" + skColumn.name
    skQuery += "), 0) from " + self.targetTable + " where " + skColumn.name + " >= 0) as " + skColumn.name
    
    query.addRow("WITH mySource as (")
    query.addRow("select *,", 1)
    query.addRow(skQuery, 2)
    query.addRow("from " + self.scdTable, 1)
    query.addRow("where MatchWithTarget = False or ScdTwoChange = True", 1)
    query.addRow(")")
    query.addRow("MERGE INTO " + self.targetTable + " as target")
    query.addRow("USING (select * from mySource) as source")
    query.addRow("on False")
    query.addRow("WHEN NOT MATCHED THEN")
    query.addRow("INSERT(")
    
    #die zielspalten (also tabellenstruktur) hinzufügen
    for col in self.Columns:
      if col.scdTyp in ["SK", "0", "1", "2", "BK", "ValidFrom"]:
        query.addRow(col.name + ",", 1)
    query.addRow(validUntilCol.name + "," , 1)
    query.addRow(isValidCol.name, 1)
    
    query.addRow(")")
    query.addRow("values")
    query.addRow("(")
    
    #sourcespalten hinzufügen
    for col in self.Columns:
      if col.scdTyp in ["SK", "0", "1", "2", "BK", "ValidFrom"]:
        query.addRow("source." + col.name + ",", 1)
    query.addRow("from_utc_timestamp(" + self.TimeRangeEndValue + ", 'CET'),", 1)
    query.addRow("True", 1)
    query.addRow(")")
    
    return query.text

  def buildScdOneMergeStatement(self) -> str:
    query = sqlQuery()
    
    scdOneColumns = self.getColumnsByScdTyp("1")
    businessKeyNames = self.getBusinessKeyStringList()
    
    #aussteigen, falls keine scd1 columns vorhanden sind
    if not scdOneColumns:
      query.addRow("select 'There are no SCD1 Columns. . .'")
      return query.text
    
    query.addRow("with mySource as (select * from " + self.scdTable + " where MatchWithTarget = True and ScdOneChange = True)")
    query.addRow("")
    query.addRow("merge into " + self.targetTable + " as target")
    query.addRow("USING (select * from mySource) as source on")
    #hier müssen alle business Keys auftauchen
    for i in range(1, len(businessKeyNames)):
      query.addRow("source." + businessKeyNames[i] + " = target." + businessKeyNames[i] + " AND", 1)
    query.addRow("source." + businessKeyNames[0] + " = target." + businessKeyNames[0], 1)
    
    query.addRow("WHEN Matched THEN")
    query.addRow("update set", 1)
    #alle scd1 spalten einfügen
    for i in range(1, len(scdOneColumns)):
      query.addRow("target." + scdOneColumns[i].name + " = source." + scdOneColumns[i].name + ",", 2)
    query.addRow("target." + scdOneColumns[0].name + " = source." + scdOneColumns[0].name, 2)
    
      
    return query.text
  
  def buildScdTwoMergeStatement(self) -> str:
    query = sqlQuery()
    
    scdTwoColumns = self.getColumnsByScdTyp("2")
    businessKeyNames = self.getBusinessKeyStringList()
    isValidCol = self.getColumnsByScdTyp("isValid")[0]
    validUntilCol = self.getColumnsByScdTyp("ValidUntil")[0]
    validFromCol = self.getColumnsByScdTyp("ValidFrom")[0]
    
    #aussteigen, falls keine scd1 columns vorhanden sind
    if not scdTwoColumns:
      query.addRow("select 'There are no SCD2 Columns. . .'")
      return query.text
    
    query.addRow("with mySource as (select * from " + self.scdTable + " where MatchWithTarget = True and ScdTwoChange = True)")
    query.addRow("")
    query.addRow("merge into " + self.targetTable + " as target")
    query.addRow("USING (select * from mySource) as source on")
    #hier müssen alle business Keys auftauchen
    for i in range(0, len(businessKeyNames)):
      query.addRow("source." + businessKeyNames[i] + " = target." + businessKeyNames[i] + " AND", 1)
    query.addRow("target." + isValidCol.name + " = True", 1)
    
    query.addRow("WHEN Matched THEN")
    query.addRow("update set", 1)
    query.addRow("target." + isValidCol.name + " = False,",2)
    query.addRow("target." + validUntilCol.name + " = source." + validFromCol.name,2)
    
    return query.text