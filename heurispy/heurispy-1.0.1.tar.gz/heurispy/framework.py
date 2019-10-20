"""
 Copyright 2019, LANIA, A.C.

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

from pathos.helpers import cpu_count

class RecopiladorInformacion:
    def __init__(self):
        self.nombre_heuristica = None
        self.lista_parametros = None
        self.lista_nombres_parametros_dataframe = None
        self.fecha_hora = None
        self.funciones_utilizadas_pdf = None

    def transformar_archivo_json(self, ruta):
        import json

        diccionario = {'nombre_heuristica': self.nombre_heuristica, 'lista_parametros': self.lista_parametros,
                       'lista_nombres_parametros_dataframes': list(set(self.lista_nombres_parametros_dataframe)),
                       'fecha_hora': self.fecha_hora, 'funciones_utilizadas_pdf': self.funciones_utilizadas_pdf}
        ruta_archivo_json = "Ejecucion-" + str(self.nombre_heuristica) + "-" + str(self.fecha_hora) + ".txt"
        nueva_ruta_json = ruta / ruta_archivo_json
        with open(nueva_ruta_json, 'w') as outfile:
            json.dump(diccionario, outfile, indent=4)


#todo: Crear los métodos para verificar que el p.o.d. del usuario está bien planteado, y construir un p.o.d. genérico.


def cart_prod(dicts):
    import itertools
    return list(dict(zip(dicts, x)) for x in itertools.product(*dicts.values()))


def genera_lista_ejecuciones_heuristicas(dicts, repeticiones=1):
    import itertools
    lista_producto_cartesiano = cart_prod(dicts)
    return [x for item in lista_producto_cartesiano for x in itertools.repeat(item, repeticiones)]


def genera_carpeta_resultados(nombre, fecha_hora):
    import pathlib
    import os

    ruta = pathlib.Path('Resultados')

    try:
        os.mkdir(ruta)
    except:
        print("Ruta ", ruta ,"ya existente.")

    ruta = pathlib.Path('Resultados', nombre)

    try:
        os.mkdir(ruta)
    except:
        print("Ruta ", ruta ,"ya existente.")

    ruta = pathlib.Path('Resultados', nombre, fecha_hora)

    try:
        os.mkdir(ruta)
    except:
        print("Ruta ", ruta ,"ya existente.")

    return ruta


def genera_carpeta_datos(nombre, fecha_hora):
    import pathlib
    import os

    ruta = pathlib.Path('Datos')

    try:
        os.mkdir(ruta)
    except:
        print("Carpeta \"Datos\" ya existente.")

    ruta = pathlib.Path('Datos', nombre)

    try:
        os.mkdir(ruta)
    except:
        print("Carpeta \"", nombre,"\" ya existente.")

    ruta = pathlib.Path('Datos', nombre, fecha_hora)

    try:
        os.mkdir(ruta)
    except:
        print("Carpeta \"", fecha_hora,"\" ya existente.")

    return ruta


def genera_carpeta_ejecuciones(nombre, fecha_hora):
    import pathlib
    import os

    ruta = pathlib.Path('Ejecuciones')

    try:
        os.mkdir(ruta)
    except:
        print("Carpeta \"Ejecuciones\" ya existente.")

    ruta = pathlib.Path('Ejecuciones', nombre)

    try:
        os.mkdir(ruta)
    except:
        print("Carpeta \"", nombre,"\" ya existente.")

    return ruta


def crea_formato_tiempo(segundos_total):
    segundos_total = int(segundos_total)
    if segundos_total < 60:
        minutos, segundos = divmod(segundos_total, 60)
        if segundos_total < 10:
            cadena = "0"+str(segundos)+" seg"
        else:
            cadena = str(segundos)+" seg"
    elif segundos_total < 3600:
        minutos, segundos = divmod(segundos_total, 60)
        if minutos < 10:
            cadena = "0"+str(minutos)
        else:
            cadena = str(minutos)
        if segundos < 10:
            cadena = cadena+":0"+str(segundos)+" min"
        else:
            cadena = cadena+":"+str(segundos)+" min"
    elif segundos_total < 86400:
        minutos, segundos = divmod(segundos_total, 60)
        horas, minutos = divmod(minutos, 60)
        cadena = str(horas)+":"
        if minutos < 10:
            cadena = cadena+"0"+str(minutos)
        else:
            cadena = cadena+str(minutos)
        if segundos < 10:
            cadena = cadena+":0"+str(segundos)+" hrs"
        else:
            cadena = cadena+":"+str(segundos)+" hrs"
    return cadena


def inicia_exploracion_heuristica(heuristica, parametros_heuristica, nucleos_cpu=cpu_count(),
                                  modo_consola="parlante"):
    import pathos
    from .recolector_resultados import RecolectorResultados
    from tqdm import tqdm
    from datetime import datetime

    recopilador_informacion = RecopiladorInformacion()
    recopilador_informacion.nombre_heuristica = heuristica.nombre
    recopilador_informacion.lista_parametros = parametros_heuristica
    recopilador_informacion.funciones_utilizadas_pdf = heuristica.funciones_utilizadas_pdf

    heuristica.comprobar_parametros(parametros_heuristica[0])
    if modo_consola is not "silencioso":
        print("Preparando trabajo en paralelo...\n")
    pathos.multiprocessing.freeze_support()
    servidor = pathos.pools.ProcessPool(nucleos_cpu)
    if modo_consola is not "silencioso":
        print("Servidor con", servidor.ncpus, "procesadores listo.\n")
    resultados_heuristica = list(tqdm(servidor.imap(heuristica.iniciar_busqueda, parametros_heuristica),
                                      total=len(parametros_heuristica)))
    print("------------------------------------------------------------------------")
    if modo_consola is not "silencioso":
        print("Exploración heurística terminada.\n")
        print("Procesando resultados...\n")
    recolector_resultados = RecolectorResultados(resultados_heuristica)
    fecha_hora = datetime.now().strftime('%Y-%m-%d---%H-%M')
    recopilador_informacion.fecha_hora = fecha_hora
    recopilador_informacion.lista_nombres_parametros_dataframe = recolector_resultados.\
        obtener_nombre_parametros_dataframe()
    ruta_carpeta_ejecuciones = genera_carpeta_ejecuciones(heuristica.nombre, fecha_hora)
    recopilador_informacion.transformar_archivo_json(ruta_carpeta_ejecuciones)
    if modo_consola is not "silencioso":
        print("Resultados recolectados.\n")
    ruta_carpeta_resultados = genera_carpeta_resultados(heuristica.nombre, fecha_hora)
    ruta_carpeta_datos = genera_carpeta_datos(heuristica.nombre, fecha_hora)
    lista_rutas = [ruta_carpeta_ejecuciones, ruta_carpeta_resultados, ruta_carpeta_datos]
    if modo_consola is not "silencioso":
        print("\nRutas generadas: ")
        for ruta in lista_rutas:
            print(ruta)
    recolector_resultados.generar_datos_todos_resultados(ruta_carpeta_datos, heuristica.nombre, fecha_hora)
    recolector_resultados.generar_csv_resultados_procesados(ruta_carpeta_datos, heuristica.nombre, fecha_hora)
    heuristica.genera_pdf_final(recolector_resultados, ruta_carpeta_resultados, fecha_hora)
    if modo_consola is not "silencioso":
        print("Resultados guardados en", ruta_carpeta_resultados)
        print("Datos extra guardados en", ruta_carpeta_datos, "y", ruta_carpeta_ejecuciones, "\n")

