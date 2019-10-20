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

from .heuristica import Heuristica


class RecocidoSimulado(Heuristica):
    def __init__(self, problema_optimizacion, alpha=0.9, eps=0.01, max_iteraciones=1000000):
        super().__init__(problema_optimizacion,
                         lista_nombres_parametros=["temperatura", "iteraciones_inyeccion_temperatura",
                                                   "maximo_inyecciones_temperatura"])

        # implementación de prueba para el recocido simulado, para ver si funciona con la biblioteca pathos
        self.nombre ="RecocidoSimulado"
        self.alpha = alpha
        self.eps = eps

        def funcion_aceptacion(delta, t):
            import numpy
            return numpy.exp(-numpy.abs(delta) / t)

        self.funcion_aceptacion = funcion_aceptacion

        def busqueda_recocido(parametros):
            import random
            import pandas as pd

            if self.problema_optimizacion.solucion_inicial is None:
                self.problema_optimizacion.genera_solucion()

            if self.comprobar_parametros(parametros):

                dataframe_resultados = pd.DataFrame(columns=("iter", "f_sol", "temp"))

                f = self.funcion_objetivo
                cambia_solucion = self.cambia_solucion
                solucion_inicial = self.problema_optimizacion.solucion_inicial

                temperatura_inicial = parametros.get('temperatura')

                temperatura = parametros.get('temperatura')
                iteraciones_inyeccion_temperatura = parametros.get('iteraciones_inyeccion_temperatura')
                maximo_inyecciones_temperatura = parametros.get('maximo_inyecciones_temperatura')

                solucion_busqueda = solucion_inicial.copy()

                contador_repeticiones_temperatura = 0
                contador_iteraciones = 0
                iteracion_mejor_solucion = 0
                mejor_solucion = solucion_busqueda.copy()
                cantidad_inyecciones_temperatura = 0

                while temperatura > self.eps and cantidad_inyecciones_temperatura < maximo_inyecciones_temperatura and \
                        contador_iteraciones < max_iteraciones:

                    solucion_nueva = cambia_solucion(solucion_busqueda).copy()
                    delta = f(solucion_busqueda) - f(solucion_nueva)

                    if delta > 0:

                        solucion_busqueda = solucion_nueva.copy()

                        if f(solucion_busqueda) < f(mejor_solucion):
                            mejor_solucion = solucion_nueva.copy()
                            iteracion_mejor_solucion = contador_iteraciones

                        contador_repeticiones_temperatura = 0
                        temperatura = self.alpha * temperatura

                    else:

                        probabilidad = funcion_aceptacion(delta, temperatura)
                        numero_aleatorio = random.uniform(0, 1)

                        if numero_aleatorio < probabilidad:

                            solucion_busqueda = solucion_nueva.copy()
                            contador_repeticiones_temperatura = contador_repeticiones_temperatura + 1

                            if contador_repeticiones_temperatura == iteraciones_inyeccion_temperatura:
                                temperatura = temperatura_inicial
                                cantidad_inyecciones_temperatura = cantidad_inyecciones_temperatura + 1
                                contador_repeticiones_temperatura = 0

                        else:

                            contador_repeticiones_temperatura = contador_repeticiones_temperatura + 1

                            if contador_repeticiones_temperatura == iteraciones_inyeccion_temperatura:
                                temperatura = temperatura_inicial
                                cantidad_inyecciones_temperatura = cantidad_inyecciones_temperatura + 1
                                contador_repeticiones_temperatura = 0

                    contador_iteraciones = contador_iteraciones + 1
                    dataframe_resultados = dataframe_resultados.append(
                        dict(iter=contador_iteraciones, f_sol=f(mejor_solucion), temp=temperatura), ignore_index=True)

                if temperatura < self.eps:
                    condicion_parada = "Fin de temperatura"
                elif contador_repeticiones_temperatura >= maximo_inyecciones_temperatura:
                    condicion_parada = "No se ha encontrado mejor solución"
                else:
                    condicion_parada = "Máximo de iteraciones alcanzadas"

                contador_funciones = self.contador_llamadas_funcion_objetivo
                resultados_finales = dict(mejor_solucion=mejor_solucion,
                                          f_mejor_solucion=f(mejor_solucion),
                                          iteracion_mejor_solucion=iteracion_mejor_solucion,
                                          total_iteraciones=contador_iteraciones,
                                          total_llamados_funcion=contador_funciones,
                                          condición_de_parada=condicion_parada)
            return parametros, resultados_finales, dataframe_resultados

        self.funcion_busqueda = busqueda_recocido

        def genera_pdf_final(recolector_resultados, ruta, fecha_hora):
            import pathlib
            from heurispy.ayudantes import AyudanteEstadisticas, AyudanteGraficas, AyudantePDFs
            from heurispy.framework import crea_formato_tiempo

            ayudante_estadisticas = AyudanteEstadisticas(recolector_resultados)
            ayudante_graficas = AyudanteGraficas(recolector_resultados)

            for parametro in recolector_resultados.diccionario_mejores_f.keys():
                nombre_pdf_final = str(self.nombre + "-" + str(parametro) + "-" + str(fecha_hora)) + '.pdf'
                nombre_txt = str(self.nombre + "-" + str(parametro) + "-" + str(fecha_hora)) + '.txt'

                pdf = AyudantePDFs(parametro, ayudante_estadisticas, ayudante_graficas)

                tiempo_ejecucion = recolector_resultados.obtener_promedio_tiempo_ejecucion_parametro(parametro)

                pdf.texto(texto="Parametros: " + str(parametro), alineacion="C")
                pdf.texto(texto="Heurística: " + self.nombre)
                pdf.texto(texto="Temperatura: " + str(pdf.parametros[0]))
                pdf.texto(texto="Iteraciones para inyección de temperatura: " + str(pdf.parametros[1]))
                pdf.texto(texto="Máximo de inyecciones de temperatura: " + str(pdf.parametros[2]))
                pdf.texto(texto="Tiempo promedio de ejecución: "+crea_formato_tiempo(tiempo_ejecucion))
                pdf.texto(texto="Resultados de las mejores soluciones obtenidas", estilo='b')
                pdf.texto(texto="Mejor mínimo: ", funcion_estadistica=ayudante_estadisticas.solucion_minima)
                pdf.texto(texto="Mejor máximo: ", funcion_estadistica=ayudante_estadisticas.solucion_maxima)
                pdf.texto(texto="Promedio: ", funcion_estadistica=ayudante_estadisticas.calcula_media)
                pdf.texto(texto="Desviación estándar: ",
                          funcion_estadistica=ayudante_estadisticas.calcula_desv_estandar)
                pdf.texto(texto="Desviación mínima: ", funcion_estadistica=ayudante_estadisticas.calcula_desv_minima)
                pdf.texto(texto="Tabla de los mejores resultados: ", estilo='b')
                pdf.crear_tabla_mejores_resultados()
                pdf.finalizar_pdf_estadisticas(self.nombre + str(parametro))
                pdf.guardar_grafica(titulo_grafica="Recorridos de la función objetivo", nombre_parametro='f_sol',
                                    funcion_ayudante_grafico=ayudante_graficas.crear_grafica_parametro)
                pdf.guardar_grafica(titulo_grafica="Mejores soluciones por recorrido", nombre_parametro='f_sol',
                                    funcion_ayudante_grafico=ayudante_graficas.crear_grafica_mejores_f)
                pdf.guardar_grafica(titulo_grafica="Promedio de los recorridos de la función objetivo",
                                    nombre_parametro='f_sol',
                                    funcion_ayudante_grafico=ayudante_graficas.crear_grafica_promedio_parametro)
                pdf.guardar_grafica(titulo_grafica="Temperaturas alcanzadas", nombre_parametro='temp',
                                    funcion_ayudante_grafico=ayudante_graficas.crear_grafica_parametro)
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