
import paramiko
import csv
import sys
from openpyxl import Workbook

def archivo2folios(ruta,archivo,salida):   
    archivo_salida = salida
    with open(ruta+'\\'+archivo,'r') as inp,open(ruta+'\\'+archivo_salida,'w') as out:        
        datos = inp.readlines()
        i = 1
        for linea in datos:
            if (i != 1) and (i != len(datos) and any(linea)):
                if i != len(datos)-1:
                    out.write(linea)
                else:
                    out.write(linea.strip())
            i+=1
    inp.close()
    out.close()
    return archivo_salida


def subirArchivo(hostname,username,password,file,rutal,rutar):
    local = rutal+"/"+file
    remoto = rutar+file
    port = 22
    try:
        t = paramiko.Transport((hostname, port))
        t.connect(username=username, password=password)
        sftp = paramiko.SFTPClient.from_transport(t)
        sftp.put(local,remoto)

    finally:
        t.close()

def bajarArchivo(hostname,username,password,file,rutal,rutar):
    local = rutal+"/"+file
    remoto = rutar+file
    port = 22
    try:
        t = paramiko.Transport((hostname, port))
        t.connect(username=username, password=password)
        sftp = paramiko.SFTPClient.from_transport(t)
        sftp.get(remoto,local)

    finally:
        t.close()        


def csv_to_xlsx(ruta,archivo,salida):
    if not archivo.endswith(".csv"):
        sys.stderr.write("Error: File does not have the ending \".csv\".\n")
        sys.exit(2)
    entrada = ruta+archivo
    salida = ruta+salida
 
    wb = Workbook()
    worksheet = wb.active
    for row in csv.reader(open(entrada,'rt',encoding='iso8859_3'), delimiter="|"):
        worksheet.append([convert_to_number(cell) for cell in row])
    wb.save(salida+".xlsx")

def convert_to_number(cell):
    if cell.isnumeric():
        return int(cell)
    try:
        return float(cell)
    except ValueError:
        return cell       