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
import numpy as np


class NumpyEncoder(json.JSONEncoder):
    """ Special json encoder for numpy types """
    def default(self, obj):
        if isinstance(obj, (np.int_, np.intc, np.intp, np.int8, np.int16, np.int32, np.int64, np.uint8, np.uint16,
                            np.uint32, np.uint64)):
            return int(obj)
        elif isinstance(obj, (np.float_, np.float16, np.float32, np.float64)):
            return float(obj)
        elif isinstance(obj, (np.ndarray,)): #### This is the fix
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


class RecolectorResultados:

    def __init__(self, resultados_experimento):
        self.diccionario_resultados = dict()
        self.diccionario_dataframes = dict()
        self.diccionario_mejores_f = dict()
        self.diccionario_indices_mejores_f = dict()
        self.diccionario_contadores_llamados_f = dict()
        self.diccionario_total_iteraciones = dict()

        for i in range(len(resultados_experimento)):
            resultados_experimento[i] = list(resultados_experimento[i])

        for lista_resultados in resultados_experimento:

            parametros_experimento = str(list(lista_resultados[0].values()))

            del(lista_resultados[0])

            if parametros_experimento in self.diccionario_resultados:
                self.diccionario_resultados[parametros_experimento].append(lista_resultados)
            else:
                self.diccionario_resultados[parametros_experimento] = [lista_resultados]

        self.__procesar_resultados__()

    def __procesar_resultados__(self):
        import pandas as pd
        for parametros_experimento, resultados_experimento in self.diccionario_resultados.items():
            diccionario_dataframe_un_parametro = dict()
            dataframe_prueba = resultados_experimento[0][1]
            lista_mejores_resultados = []
            lista_indices_mejores_resultados = []
            lista_contadores_f = []
            lista_total_iteraciones = []
            for columna in dataframe_prueba.columns.tolist():
                diccionario_dataframe_un_parametro[columna] = pd.DataFrame()
            for resultado in resultados_experimento:
                diccionario_resultados_finales = resultado[0]
                lista_mejores_resultados.append(diccionario_resultados_finales['f_mejor_solucion'])
                lista_indices_mejores_resultados.append(diccionario_resultados_finales['iteracion_mejor_solucion'])
                lista_contadores_f.append(diccionario_resultados_finales['total_llamados_funcion'])
                lista_total_iteraciones.append(diccionario_resultados_finales['total_iteraciones'])
                dataframe_resultado = resultado[1]
                for columna in dataframe_resultado.columns.tolist():
                    diccionario_dataframe_un_parametro[columna] = \
                        diccionario_dataframe_un_parametro[columna].append(dataframe_resultado[columna])
            self.diccionario_mejores_f[parametros_experimento] = lista_mejores_resultados
            self.diccionario_indices_mejores_f[parametros_experimento] = lista_indices_mejores_resultados
            self.diccionario_dataframes[parametros_experimento] = diccionario_dataframe_un_parametro
            self.diccionario_contadores_llamados_f[parametros_experimento] = lista_contadores_f
            self.diccionario_total_iteraciones[parametros_experimento] = lista_total_iteraciones

    def __str__(self):

        string = "Cantidad de bloque de parámetros: " + str(len(self.diccionario_resultados))

        for bloque, resultado in self.diccionario_resultados.items():
            string = string + "\nBloque: "+str(bloque) + "\n --------------------------------------------------- \n"\
                     + str(resultado)+"\n"

        for bloque, resultado in self.diccionario_dataframes.items():
            string = string + "\nBloque: " + str(bloque) + "\n --------------------------------------------------- \n" \
                     + str(resultado) + "\n"

        return string

    def generar_datos_todos_resultados(self, ruta, nombre_heuristica, fecha_hora):

        import json

        for parametro, resultados in self.diccionario_resultados.items():
            for i in range(len(resultados)):

                ruta_archivo_csv = str(nombre_heuristica) + "-" + str(parametro) + "-" + str(i) + "-" + str(fecha_hora) \
                                   + ".csv"
                ruta_archivo_json = str(nombre_heuristica) + "-" + str(parametro) + "-" + str(i) + "-" + str(fecha_hora)\
                                    + ".txt"

                nueva_ruta_csv = ruta / ruta_archivo_csv
                nueva_ruta_json = ruta / ruta_archivo_json

                resultados_dataframe = resultados[i][1]
                resultados_dataframe.to_csv(nueva_ruta_csv)
                resultados_json = resultados[i][0]
                with open(nueva_ruta_json, 'w') as outfile:
                    json.dump(resultados_json, outfile, cls=NumpyEncoder, indent=4)

    def generar_csv_resultados_procesados(self, ruta, nombre_heuristica, fecha_hora):

        for parametro, resultados in self.diccionario_dataframes.items():

            for nombre_parametro, dataframe in resultados.items():

                ruta_archivo = str(nombre_heuristica) + "-" + str(parametro) + "-" + str(nombre_parametro) +\
                               "-" + str(fecha_hora) + ".csv"
                nueva_ruta = ruta / ruta_archivo
                dataframe.to_csv(nueva_ruta)

    def obtener_nombre_parametros_dataframe(self):

        lista_nombre_parametros_dataframe = []

        for parametro, resultados in self.diccionario_dataframes.items():
            for nombre_parametro, dataframe in resultados.items():
                lista_nombre_parametros_dataframe.append(str(nombre_parametro))

        return lista_nombre_parametros_dataframe

    def obtener_promedio_tiempo_ejecucion_parametro(self, parametro):
        tiempo = 0
        for lista in self.diccionario_resultados[parametro]:
            diccionario_resultados = lista[0]
            tiempo = tiempo + diccionario_resultados['tiempo_ejecucion']
        promedio_tiempo_ejecucion = tiempo / len(self.diccionario_resultados)
        return promedio_tiempo_ejecucion
















