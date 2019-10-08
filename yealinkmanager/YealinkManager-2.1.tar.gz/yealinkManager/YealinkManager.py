import sys, csv, requests
from yealinkManager.ConstantsYealinkManager import ConstantsYealinkManager as C

class YealinkManager:
  def isListReadable(self, filename:str):
    try:
      with open(filename, newline='\n') as csvfile:
        csv.reader(csvfile, delimiter=',', quotechar='|')
        return True
    except Exception:
      return False

  # Legge la lista ed esegue i comandi specificati
  def executeList(self, filename:str):
    with open(filename, newline='\n') as csvfile:
     spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
     for row in spamreader:

        if (self.__is2Skip(row)): 
          continue
        dt = self.__getDataFrom(row)

        try:
          res = requests.get(
            f"http://{dt[C.CREDENTIAL]}@{dt[C.IP]}"
            f"/cgi-bin/ConfigManApp.com?key={dt[C.ACTION]}"
          )
          self.__log(f" {dt[C.IP]} ({dt[C.OPERATIVECOMMENT]}) ->  {res}")
        except Exception:
          self.__log(f" {dt[C.IP]} ({dt[C.OPERATIVECOMMENT]}) ->  FAIL")

  # Verifica se la riga è da saltare o meno
  @staticmethod
  def __is2Skip(row):
    return (  
      not row 
      or len(row) == 0 
      or row[0][0] == '#'
    )

  # Prepara un oggetto con i dati estratti dalla posizione
  @staticmethod
  def __getDataFrom(row):
    return {
      C.IP : row[0],
      C.ACTION : row[1],
      C.CREDENTIAL : row[2],
      C.OPERATIVECOMMENT : row[3] if len(row) > 3 else '' ,
    }

  @staticmethod
  def __log(msg):
    print(msg)

# Funzione di ingresso per lo script
def entryPoint():
  # No path specificato
  if (len(sys.argv) == 1 or sys.argv[1] == '\n'): 
    print(C.NOPATH)
    print(C.HELPMESSAGE)
    print(C.NOPATH)
    exit(1)

  # Lista non leggibile dal reader CSV
  if (not YealinkManager().isListReadable(sys.argv[1])):
    print(C.INVALIDCSV)
    print(C.HELPMESSAGELIST)
    print(C.INVALIDCSV)
    exit(1)    

  YealinkManager().executeList(sys.argv[1])

if __name__  == '__main__': entryPoint()
