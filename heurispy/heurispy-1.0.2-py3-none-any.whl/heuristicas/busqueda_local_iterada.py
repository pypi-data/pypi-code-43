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

from heurispy.heuristicas.heuristica import Heuristica


class BusquedaLocalIterada(Heuristica):
    def __init__(self, problema_optimizacion, max_iteraciones=1000000):
        super().__init__(problema_optimizacion,
                         lista_nombres_parametros=["busqueda_local_sin_minimo_global", "rango_perturbacion",
                                                   "busqueda_iterada_sin_mejora"])
        self.nombre = "BusquedaLocalIterada"

        def busqueda_local(solucion_inicial, iteraciones_minimo_local, iteraciones_maximas=100):

            f = self.funcion_objetivo
            cambia_solucion = self.problema_optimizacion.cambia_solucion

            busquedas_sin_mejora = 0
            contador_iteraciones = 0

            mejor_solucion = solucion_inicial.copy()
            nueva_solucion = cambia_solucion(mejor_solucion)

            while busquedas_sin_mejora < iteraciones_minimo_local and contador_iteraciones < iteraciones_maximas:
                bandera_nuevo_min = False
                while busquedas_sin_mejora < iteraciones_minimo_local and bandera_nuevo_min is False:
                    f_nueva_solucion = f(nueva_solucion)
                    f_mejor_solucion = f(mejor_solucion)
                    if f_nueva_solucion < f_mejor_solucion:
                        mejor_solucion = nueva_solucion.copy()
                        #print("Sol nueva: ", mejor_solucion)
                        bandera_nuevo_min = True
                        busquedas_sin_mejora = 0
                        nueva_solucion = cambia_solucion(mejor_solucion)
                    else:
                        nueva_solucion = cambia_solucion(mejor_solucion)
                        busquedas_sin_mejora = busquedas_sin_mejora + 1
                    contador_iteraciones = contador_iteraciones + 1

            return mejor_solucion, contador_iteraciones

        def perturbar_solucion(solucion, numero_cambios):
            cambia_solucion = self.problema_optimizacion.cambia_solucion
            nueva_solucion = solucion.copy()
            #print("Vieja:", nueva_solucion)
            for i in range(numero_cambios):
                nueva_solucion = cambia_solucion(nueva_solucion)
            #print("Nueva", nueva_solucion)
            return nueva_solucion

        def busqueda_local_iterada(parametros):
            import pandas as pd

            if self.problema_optimizacion.solucion_inicial is None:
                self.problema_optimizacion.genera_solucion()

            if self.comprobar_parametros(parametros):

                dataframe_resultados = pd.DataFrame(columns=("iter", "f_sol", "temp"))

                f = self.funcion_objetivo
                solucion_inicial = self.problema_optimizacion.solucion_inicial

                busqueda_local_sin_minimo_global = parametros.get("busqueda_local_sin_minimo_global")
                rango_perturbacion = parametros.get("rango_perturbacion")
                busqueda_iterada_sin_mejora = parametros.get("busqueda_iterada_sin_mejora")

                mejor_solucion = solucion_inicial.copy()
                solucion_actual = solucion_inicial.copy()

                contador_iteraciones = 0
                contador_bus_iterada_sin_mejora = 0
                iteracion_mejor_solucion = 0

                while contador_bus_iterada_sin_mejora < busqueda_iterada_sin_mejora \
                        and contador_iteraciones < max_iteraciones:
                    solucion_actual = perturbar_solucion(solucion_actual, rango_perturbacion)
                    solucion_actual, contador_iteraciones_bus_local = busqueda_local(solucion_actual, busqueda_local_sin_minimo_global)
                    contador_iteraciones = contador_iteraciones + contador_iteraciones_bus_local
                    f_sol_actual = f(solucion_actual)
                    f_mejor_solucion = f(mejor_solucion)
                    if f_sol_actual < f_mejor_solucion:
                        #print("Reemplazo mejor solucion")
                        mejor_solucion = solucion_actual.copy()
                        solucion_actual = mejor_solucion.copy()
                        iteracion_mejor_solucion = contador_iteraciones
                        contador_bus_iterada_sin_mejora = 0
                    else:
                        contador_bus_iterada_sin_mejora = contador_bus_iterada_sin_mejora + 1
                    contador_iteraciones = contador_iteraciones + 1
                    dataframe_resultados = dataframe_resultados.append(dict(iter=contador_iteraciones,
                                                                            f_sol=f_mejor_solucion), ignore_index=True)

                if contador_bus_iterada_sin_mejora == busqueda_iterada_sin_mejora:
                    condicion_parada = "Se encontró mínimo local"
                else:
                    condicion_parada = "Máximo de iteraciones alcanzadas"

                resultados_finales = dict(mejor_solucion=mejor_solucion,
                                          f_mejor_solucion=f_mejor_solucion,
                                          iteracion_mejor_solucion=iteracion_mejor_solucion,
                                          total_iteraciones=contador_iteraciones,
                                          total_llamados_funcion=self.contador_llamadas_funcion_objetivo,
                                          condicion_de_parada=condicion_parada)
                return parametros, resultados_finales, dataframe_resultados

        self.funcion_busqueda = busqueda_local_iterada

        def genera_pdf_final(recolector_resultados, ruta, fecha_hora):
            import pathlib
            from heurispy.ayudantes import AyudanteEstadisticas, AyudanteGraficas, AyudantePDFs
            from heurispy.framework import crea_formato_tiempo

            ayudante_estadisticas = AyudanteEstadisticas(recolector_resultados)
            ayudante_graficas = AyudanteGraficas(recolector_resultados)

            for parametro in recolector_resultados.diccionario_mejores_f.keys():

                nombre_pdf_final = str(self.nombre + "-" + str(parametro) + "-" + str(fecha_hora)) + '.pdf'
                nombre_txt = str(self.nombre + "-" + str(parametro) + "-" + str(fecha_hora)) + '.txt'

                tiempo_ejecucion = recolector_resultados.obtener_promedio_tiempo_ejecucion_parametro(parametro)

                pdf = AyudantePDFs(parametro, ayudante_estadisticas, ayudante_graficas)

                pdf.texto(texto="Parametros: "+str(parametro), alineacion="C")
                pdf.texto(texto="Heurística: "+self.nombre)
                pdf.texto(texto="Búsqueda local sin mínimo: "+str(pdf.parametros[0]))
                pdf.texto(texto="Rango de perturbación: "+str(pdf.parametros[1]))
                pdf.texto(texto="Búsqueda iterada sin mejora: "+str(pdf.parametros[2]))
                pdf.texto(texto="Tiempo promedio de ejecución: " + crea_formato_tiempo(tiempo_ejecucion))
                pdf.texto(texto="Resultados de las mejores soluciones obtenidas", estilo='b')
                pdf.texto(texto="Mejor mínimo: ", funcion_estadistica=ayudante_estadisticas.solucion_minima)
                pdf.texto(texto="Mejor máximo: ", funcion_estadistica=ayudante_estadisticas.solucion_maxima)
                pdf.texto(texto="Promedio: ", funcion_estadistica=ayudante_estadisticas.calcula_media)
                pdf.texto(texto="Desviación estándar: ", funcion_estadistica=ayudante_estadisticas.calcula_desv_estandar)
                pdf.texto(texto="Desviación mínima: ", funcion_estadistica=ayudante_estadisticas.calcula_desv_minima)
                pdf.texto(texto="Tabla de los mejores resultados: ", estilo='b')
                pdf.crear_tabla_mejores_resultados()
                pdf.finalizar_pdf_estadisticas(self.nombre+str(parametro))
                pdf.guardar_grafica(titulo_grafica="Recorridos de la función objetivo", nombre_parametro='f_sol',
                                    funcion_ayudante_grafico=ayudante_graficas.crear_grafica_parametro)
                pdf.guardar_grafica(titulo_grafica="Mejores soluciones por recorrido", nombre_parametro='f_sol',
                                    funcion_ayudante_grafico=ayudante_graficas.crear_grafica_mejores_f)
                pdf.guardar_grafica(titulo_grafica="Promedio de los recorridos de la función objetivo",
                                    nombre_parametro='f_sol',
                                    funcion_ayudante_grafico=ayudante_graficas.crear_grafica_promedio_parametro)
                pdf.finalizar_pdf_graficas()
                pdf.generar_pdf_final(nombre_pdf_final)
                pdf.generar_txt_funciones(nombre_txt)

                ruta_pdf = pathlib.Path(nombre_pdf_final)
                ruta_txt = pathlib.Path(nombre_txt)

                ruta_pdf.replace(ruta / nombre_pdf_final)
                ruta_txt.replace(ruta / nombre_txt)

        self.genera_pdf_final = genera_pdf_final

        self.funciones_utilizadas_pdf = ["solucion_minima", "solucion_maxima", "calcula_media", "calcula_desv_estandar",
                                         "calcula_desv_minima"]
