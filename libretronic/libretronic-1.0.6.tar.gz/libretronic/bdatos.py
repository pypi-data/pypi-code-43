"""
Este es el módulo de Base de Datos
"""
import os
from libretronic import archivos

def consulta_de_archivo(servidor,base,usuario,rutaDeScript,nombreConsulta):
    """Esta función consulta desde un archivo.sql a un servidor específico"""
    print('Consultando '+nombreConsulta+'.sql')
    Cadena='psql -h '+servidor+' -U '+usuario+' -d '+base+' -A -F"|" -f '+'\"'+rutaDeScript+'\\'+nombreConsulta+'.sql" > "'+rutaDeScript+'\\'+nombreConsulta+'.csv"'      
    os.system(Cadena)        
    #archivos.csv_to_xlsx(rutaDeScript+'\\',nombreConsulta+'.csv',nombreConsulta)



def consulta_de_lista(servidor,base,usuario,rutaDeScript,listadeConsultas):
    """Esta función realiza consultas a partir de un archivo.dat
    que a su ves contiene  una lista de consultas
    """
    print("Barriendo ",listadeConsultas)
    
    #archivoConsulta=rutaDeScript+'\\'+listadeConsultas
    archivoConsulta=os.path.join(rutaDeScript,listadeConsultas)
    infile = open(archivoConsulta,'r')
    Consultas = infile.readlines()
    infile.close()
    for nombreConsulta in Consultas:
        nombreConsulta=nombreConsulta.rstrip('\n')
        consulta_de_archivo(servidor,base,usuario,rutaDeScript,nombreConsulta)         
