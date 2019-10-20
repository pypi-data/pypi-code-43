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


class BusquedaArmonica(Heuristica):
    def __init__(self, problema_optimizacion, max_iteraciones=1000000):
        super().__init__(problema_optimizacion,
                         lista_nombres_parametros=["espacio_memoria", "max_busqueda_sin_mejoras",
                                                   "radio_consideracion_memoria_armonica", "radio_ajuste_afinacion"])
        self.nombre = "BusquedaArmonica"

        def genera_memoria_armonica(longitud_memoria):
            genera_nueva_solucion = self.problema_optimizacion.dominio
            f = self.funcion_objetivo
            memoria_armonica = []
            f_memoria_armonica = []
            for i in range(longitud_memoria):
                solucion = genera_nueva_solucion()
                memoria_armonica.append(solucion)
                f_memoria_armonica.append(f(solucion))

            return memoria_armonica, f_memoria_armonica

        self.genera_memoria_armonica = genera_memoria_armonica

        def crea_nueva_solucion_armonica(memoria_armonica):
            import random

            solucion_nueva = []

            longitud_solucion = len(memoria_armonica[0])
            #print("LONGITUD_SOLUCION:", longitud_solucion)
            soluciones_elegidas_memoria = random.sample(memoria_armonica, k=longitud_solucion)

            for i in range(longitud_solucion):
                solucion_a_obtener_dato = soluciones_elegidas_memoria[i]
                solucion_nueva.append(solucion_a_obtener_dato[i])

            return solucion_nueva

        self.crea_nueva_solucion_armonica = crea_nueva_solucion_armonica

        def modifica_memoria_armonica(memoria_armonica, f_memoria_armonica, solucion, busqueda_sin_mejora,
                                      contador_iteraciones):
            f = self.funcion_objetivo
            indice_peor_solucion = f_memoria_armonica.index(max(f_memoria_armonica))
            f_peor_solucion = f_memoria_armonica[indice_peor_solucion]
            f_solucion = f(solucion)

            #print("Peor solucion en memoria:", f_peor_solucion)
            #print("Valor de sol. nueva:", f_solucion)

            if f_solucion < f_peor_solucion:
                #print("Modifico memoria armonica.")
                del memoria_armonica[indice_peor_solucion]
                del f_memoria_armonica[indice_peor_solucion]
                memoria_armonica.append(solucion)
                f_memoria_armonica.append(f_solucion)
                busqueda_sin_mejora = 0
                iteracion_mejor_sol = contador_iteraciones
            else:
                busqueda_sin_mejora = busqueda_sin_mejora + 1
                iteracion_mejor_sol = None
            return memoria_armonica, f_memoria_armonica, busqueda_sin_mejora, iteracion_mejor_sol

        self.modifica_memoria_armonica = modifica_memoria_armonica

        def obten_nueva_solucion(memoria_armonica, rcma, raa):
            import random
            cambia_solucion = self.problema_optimizacion.cambia_solucion
            genera_solucion = self.problema_optimizacion.dominio
            probabilidad_rcma = random.random()
            probabilidad_raa = random.random()
            if probabilidad_rcma > rcma:
                solucion_nueva = genera_solucion()
                #print("1:", solucion_nueva)
            else:
                solucion_nueva = crea_nueva_solucion_armonica(memoria_armonica)
                #print("2:", solucion_nueva)
            if probabilidad_raa > raa:
                solucion_nueva = cambia_solucion(solucion_nueva)
            return solucion_nueva

        self.obten_nueva_solucion = obten_nueva_solucion

        def obten_solucion_minima(memoria_armonica, f_memoria_armonica):
            #f = self.problema_optimizacion.funcion_objetivo
            indice_menor_valor = f_memoria_armonica.index(min(f_memoria_armonica))
            menor_valor = memoria_armonica[indice_menor_valor]
            #print("VALOR MÏNIMO:", f(menor_valor))
            return menor_valor

        self.obten_solucion_minima = obten_solucion_minima

        def busqueda_armonica(parametros):
            import pandas as pd

            if self.comprobar_parametros(parametros):
                dataframe_resultados = pd.DataFrame(columns=("iter", "f_sol"))

                f = self.funcion_objetivo
                genera_memoria_arm = self.genera_memoria_armonica
                modifica_memoria_arm = self.modifica_memoria_armonica
                obten_nueva_sol = self.obten_nueva_solucion

                rcma_actual = parametros.get('radio_consideracion_memoria_armonica')
                raa_actual = parametros.get('radio_ajuste_afinacion')
                espacio_memoria = parametros.get('espacio_memoria')
                max_busqueda_sin_mejoras = parametros.get('max_busqueda_sin_mejoras')

                memoria_armonica_actual, f_memoria_armonica_actual = genera_memoria_arm(espacio_memoria)

                busquedas_sin_mejora = 0
                contador_iteraciones = 0
                iteracion_mejor_sol = 0

                while busquedas_sin_mejora < max_busqueda_sin_mejoras and contador_iteraciones < max_iteraciones:
                    nueva_solucion = obten_nueva_sol(memoria_armonica_actual, rcma_actual, raa_actual)
                    memoria_armonica_actual, f_memoria_armonica_actual, busquedas_sin_mejora, valor_iter =\
                        modifica_memoria_arm(memoria_armonica_actual, f_memoria_armonica_actual, nueva_solucion,
                                             busquedas_sin_mejora, contador_iteraciones)
                    if valor_iter is not None:
                        iteracion_mejor_sol = valor_iter
                    contador_iteraciones = contador_iteraciones + 1
                    dataframe_resultados = dataframe_resultados.append(
                        dict(iter=contador_iteraciones, f_sol=f(obten_solucion_minima(memoria_armonica_actual,
                                                                                    f_memoria_armonica_actual)))
                        , ignore_index=True)
                if busquedas_sin_mejora == max_busqueda_sin_mejoras:
                    condicion_parada = "No se encontraton mejores soluciones"
                else:
                    condicion_parada = "Máximo de iteraciones alcanzadas"
                mejor_solucion = obten_solucion_minima(memoria_armonica_actual, f_memoria_armonica_actual)
                resultados_finales = dict(mejor_solucion=mejor_solucion,
                                          f_mejor_solucion=f(mejor_solucion),
                                          iteracion_mejor_solucion=iteracion_mejor_sol,
                                          total_iteraciones=contador_iteraciones,
                                          total_llamados_funcion=self.contador_llamadas_funcion_objetivo,
                                          condicion_de_parada=condicion_parada)
                return parametros, resultados_finales, dataframe_resultados

        self.funcion_busqueda = busqueda_armonica

        def genera_pdf_final(recolector_resultados, ruta, fecha_hora):
            import pathlib
            from heurispy.framework import crea_formato_tiempo
            from heurispy.ayudantes import AyudanteEstadisticas, AyudanteGraficas, AyudantePDFs

            ayudante_estadisticas = AyudanteEstadisticas(recolector_resultados)
            ayudante_graficas = AyudanteGraficas(recolector_resultados)

            for parametro in recolector_resultados.diccionario_mejores_f.keys():

                nombre_pdf_final = str(self.nombre + "-" + str(parametro) + "-" + str(fecha_hora)) + '.pdf'
                nombre_txt = str(self.nombre + "-" + str(parametro) + "-" + str(fecha_hora)) + '.txt'

                tiempo_ejecucion = recolector_resultados.obtener_promedio_tiempo_ejecucion_parametro(parametro)

                pdf = AyudantePDFs(parametro, ayudante_estadisticas, ayudante_graficas)

                pdf.texto(texto="Parametros: "+str(parametro), alineacion="C")
                pdf.texto(texto="Heurística: "+self.nombre)
                pdf.texto(texto="Espacio en memoria (cantidad de soluciones): "+str(pdf.parametros[0]))
                pdf.texto(texto="Máximo de búsquedas sin mejora: "+str(pdf.parametros[1]))
                pdf.texto(texto="Radio de consideración para memoria armónica: "+str(pdf.parametros[2]))
                pdf.texto(texto="Radio de ajuste de afinación: "+str(pdf.parametros[3]))
                pdf.texto(texto="Tiempo promedio de ejecución: "+crea_formato_tiempo(tiempo_ejecucion))
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
                                         "calcula_desv_minima", ]








