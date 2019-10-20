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

import json
from pathlib import Path
import itertools
import pandas as pd


class EjecucionPruebas:
    def __init__(self, cadena_archivo):
        diccionario_exploracion_heuristica = leer_json(cadena_archivo)
        self.nombre_heuristica = diccionario_exploracion_heuristica['nombre_heuristica']
        self.parametros_corrida_exploracion_heuristica = diccionario_exploracion_heuristica['lista_parametros']
        self.lista_nombres_parametros_dataframes = \
            diccionario_exploracion_heuristica['lista_nombres_parametros_dataframes']
        self.fecha_hora = diccionario_exploracion_heuristica['fecha_hora']
        self.funciones_utilizadas_pdf = diccionario_exploracion_heuristica['funciones_utilizadas_pdf']

    def __str__(self):
        cadena = str(self.nombre_heuristica) + str(self.parametros_corrida_exploracion_heuristica) +\
                 str(self.lista_nombres_parametros_dataframes) + str(self.fecha_hora) + \
                 str(self.funciones_utilizadas_pdf)
        return cadena


def leer_json(ruta_json):
    try:
        with open(ruta_json, encoding='utf-8') as archivo_datos:
            archivo_json = json.loads(archivo_datos.read())
    except FileNotFoundError as fnfe:
        archivo_json = None
        print(fnfe)
    return archivo_json


def comprobar_directorio(ruta_actual, ac, tot):
    tot = tot + 1
    if ruta_actual.is_dir():
        ac = ac + 1
    else:
        print("La ruta", ruta_actual, "no existe.")
    return ac, tot


def comprobar_archivo(ruta_actual, ac, tot):
    tot = tot + 1
    if ruta_actual.exists():
        ac = ac + 1
    else:
        print("La ruta", ruta_actual, "no existe.")
    return ac, tot


def obtener_corridas_parametros_repetidos(lista_diccionarios_parametros_corridas):
    lista_valores = []
    for diccionario in lista_diccionarios_parametros_corridas:
        lista_valores.append(list(diccionario.values()))
    lista_valores.sort()
    lista_final = list(lista_valores for lista_valores, _ in itertools.groupby(lista_valores))
    return lista_final

def comprobar_archivos_resultados_finales(ruta_carpeta, ejecucion_pruebas, lista_parametros_bloque, ac, tot):
    fecha_hora = ejecucion_pruebas.fecha_hora
    nombre_heuristica = ejecucion_pruebas.nombre_heuristica

    for parametro in lista_parametros_bloque:
        nombre_archivo = str(nombre_heuristica) + "-" + str(parametro) + "-" + str(fecha_hora) + ".pdf"
        ruta_nueva = ruta_carpeta / nombre_archivo
        ac, tot = comprobar_archivo(ruta_nueva, ac, tot)

    return ac, tot

def verifica_pdf_resultados(ruta_carpeta, ejecucion_pruebas, lista_parametros_bloque, ac, tot):
    fecha_hora = ejecucion_pruebas.fecha_hora
    nombre_heuristica = ejecucion_pruebas.nombre_heuristica
    funciones_utilizadas_pdf = ejecucion_pruebas.funciones_utilizadas_pdf

    for parametro in lista_parametros_bloque:
        nombre_archivo = str(nombre_heuristica) + "-" + str(parametro) + "-" + str(fecha_hora) + ".txt"
        ruta_nueva = ruta_carpeta / nombre_archivo
        with open(ruta_nueva) as file:
            funciones = [line.rstrip('\n') for line in file]
            for i in range(len(funciones)):
                tot = tot + 1
                if funciones[i] == funciones_utilizadas_pdf[i]:
                    ac = ac + 1
    return ac, tot

def obtener_lista_corridas_parametros(lista_diccionarios_parametros_corridas):
    lista_valores = []
    for diccionario in lista_diccionarios_parametros_corridas:
        lista_valores.append(list(diccionario.values()))
    lista_valores.sort()
    lista_repetidos = [len(list(group)) for key, group in itertools.groupby(lista_valores)]
    lista_final = list(lista_valores for lista_valores, _ in itertools.groupby(lista_valores))
    return lista_final, lista_repetidos


def comprobar_archivos_datos(ruta_nueva, ejecucion_pruebas, lista_parametros_bloque, lista_repetidos, ac, tot):
    lista_nombres_parametros_dataframes = ejecucion_pruebas.lista_nombres_parametros_dataframes
    fecha_hora = ejecucion_pruebas.fecha_hora
    nombre_heuristica = ejecucion_pruebas.nombre_heuristica

    for posicion_lista in range(len(lista_parametros_bloque)):
        parametro = lista_parametros_bloque[posicion_lista]
        repeticiones_repetidos = lista_repetidos[posicion_lista]
        i = 0

        """Se revisan primero los csv que contienen los dataframes procesados."""

        for nombre_parametro in lista_nombres_parametros_dataframes:
            nombre_archivo_csv_procesado = str(nombre_heuristica) + "-" + str(parametro) + "-" + str(nombre_parametro) \
                                           + "-" + str(fecha_hora) + ".csv"
            ruta_archivo = ruta_nueva / nombre_archivo_csv_procesado
            ac, tot = comprobar_archivo(ruta_archivo, ac, tot)

        while i < repeticiones_repetidos:
            nombre_archivo_txt = str(nombre_heuristica) + "-" + str(parametro) + "-" + str(i) + "-" + str(fecha_hora) +\
                                 ".txt"
            nombre_archivo_csv = str(nombre_heuristica) + "-" + str(parametro) + "-" + str(i) + "-" + str(fecha_hora) +\
                                 ".csv"

            ruta_txt = ruta_nueva / nombre_archivo_txt
            ruta_csv = ruta_nueva / nombre_archivo_csv

            ac, tot = comprobar_archivo(ruta_csv, ac, tot)
            try:
                datos_csv = pd.read_csv(ruta_csv)
            except:
                datos_csv = None

            ac, tot = comprobar_archivo(ruta_txt, ac, tot)

            try:
                datos_txt = leer_json(ruta_txt)
            except:
                datos_txt = None

            ac, tot = verifica_total_iteraciones(datos_csv, datos_txt, ac, tot)
            ac, tot = verifica_mejor_solucion(datos_csv, datos_txt, ac, tot)

            i = i + 1

    return ac, tot


def verifica_total_iteraciones(datos_csv, datos_txt, ac, tot):

    tot = tot + 1

    if datos_csv is not None and datos_txt is not None:
        if datos_txt['total_iteraciones'] == len(datos_csv.index):
            ac = ac + 1

    return ac, tot


def verifica_mejor_solucion(datos_csv, datos_txt, ac, tot):

    tot = tot + 1

    if datos_csv is not None and datos_txt is not None:
        indice_mejor_solucion = datos_txt['iteracion_mejor_solucion']
        mejor_solucion = datos_txt['f_mejor_solucion']

        if mejor_solucion == datos_csv.loc[datos_csv.index[indice_mejor_solucion], 'f_sol']:
            ac = ac + 1

    return ac, tot


def ejecuta_pruebas(cadena_archivo):

    ejecucion_pruebas = EjecucionPruebas(cadena_archivo)

    fecha_hora = ejecucion_pruebas.fecha_hora
    nombre_heuristica = ejecucion_pruebas.nombre_heuristica
    parametros_corrida_exploracion_heuristica = ejecucion_pruebas.parametros_corrida_exploracion_heuristica

    # checar que archivo de resultados existe:

    aciertos = 0
    total = 0

    ruta = Path('Resultados', nombre_heuristica)

    aciertos, total = comprobar_directorio(ruta, aciertos, total)

    ruta = ruta / fecha_hora

    aciertos, total = comprobar_directorio(ruta, aciertos, total)

    parametros_corrida = obtener_corridas_parametros_repetidos(parametros_corrida_exploracion_heuristica)

    aciertos, total = comprobar_archivos_resultados_finales(ruta, ejecucion_pruebas, parametros_corrida, aciertos,
                                                            total)

    aciertos, total = verifica_pdf_resultados(ruta, ejecucion_pruebas, parametros_corrida, aciertos, total)

    ruta = Path('Datos', nombre_heuristica)

    aciertos, total = comprobar_directorio(ruta, aciertos, total)

    ruta = ruta / fecha_hora

    aciertos, total = comprobar_directorio(ruta, aciertos, total)

    parametros_corrida, repeticiones = obtener_lista_corridas_parametros(parametros_corrida_exploracion_heuristica)

    aciertos, total = comprobar_archivos_datos(ruta, ejecucion_pruebas, parametros_corrida, repeticiones, aciertos,
                                               total)

    print("Aciertos:", aciertos)

    print("Total:", total)


archivo = "Ejecuciones\\RecocidoSimulado\\Ejecucion-RecocidoSimulado-2019-06-30---01-07.txt"

ejecuta_pruebas(archivo)
