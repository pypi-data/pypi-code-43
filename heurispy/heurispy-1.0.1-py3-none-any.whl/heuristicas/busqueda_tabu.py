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


class BusquedaTabu(Heuristica):
    def __init__(self, problema_optimizacion, max_iteraciones=1000000):
        super().__init__(problema_optimizacion,
                         lista_nombres_parametros=["espacio_memoria", "max_busquedas_sin_mejora"])
        self.nombre = "BusquedaTabu"

        def modifica_lista_tabu(lista_tabu, solucion, limite):
            longitud_lista = len(lista_tabu)
            f = self.problema_optimizacion.funcion_objetivo
            f_lista_tabu = []
            for solucion_en_lista in lista_tabu:
                f_lista_tabu.append(f(solucion_en_lista))
            if longitud_lista == limite:
                del lista_tabu[max(f_lista_tabu)]
                lista_tabu.append(solucion)
            else:
                lista_tabu.append(solucion)

        self.modifica_lista_tabu = modifica_lista_tabu

        def comprueba_solucion(lista_tabu, solucion):
            comprobacion = False
            i = 0
            while comprobacion is False and i < len(lista_tabu):
                comprobacion = solucion == lista_tabu[i]
                i = i + 1
            return comprobacion

        self.comprueba_solucion = comprueba_solucion

        def regresa_solucion_min(lista_tabu):
            if len(lista_tabu) != 1:
                f = self.problema_optimizacion.funcion_objetivo
                f_lista_tabu = list()
                for elemento in lista_tabu:
                    f_lista_tabu.append(f(elemento))
                indice_peor_valor = f_lista_tabu.index(min(f_lista_tabu))
                return lista_tabu[indice_peor_valor]
            else:
                return lista_tabu[0]

        self.obtener_mejor_solucion = regresa_solucion_min

        def busqueda_tabu(parametros):
            import pandas as pd

            if self.problema_optimizacion.solucion_inicial is None:
                self.problema_optimizacion.genera_solucion()

            if self.comprobar_parametros(parametros):
                dataframe_resultados = pd.DataFrame(columns=("iter", "f_sol"))

                f = self.funcion_objetivo
                cambia_solucion = self.problema_optimizacion.cambia_solucion
                solucion_inicial = self.problema_optimizacion.solucion_inicial

                obtener_mejor_sol = self.obtener_mejor_solucion
                modifica_lista = self.modifica_lista_tabu
                comprueba_sol = self.comprueba_solucion

                limite_lista_tabu = parametros.get('espacio_memoria')
                max_busquedas_sin_mejora = parametros.get('max_busquedas_sin_mejora')

                lista_tabu = list()
                lista_tabu.append(solucion_inicial)

                busquedas_sin_mejora = 0
                contador_iteraciones = 0

                solucion_busqueda = solucion_inicial.copy()

                while busquedas_sin_mejora < max_busquedas_sin_mejora and contador_iteraciones < max_iteraciones:
                    nueva_solucion = cambia_solucion(solucion_busqueda)
                    while comprueba_sol(lista_tabu, nueva_solucion) is True:
                        nueva_solucion = cambia_solucion(solucion_busqueda)
                    valor_solucion = f(nueva_solucion)
                    if valor_solucion < f(obtener_mejor_sol(lista_tabu)):
                        modifica_lista(lista_tabu, nueva_solucion, limite_lista_tabu)
                        solucion_busqueda = obtener_mejor_sol(lista_tabu)
                        iteracion_mejor_solucion = contador_iteraciones
                        busquedas_sin_mejora = 0
                    else:
                        busquedas_sin_mejora = busquedas_sin_mejora + 1
                    contador_iteraciones = contador_iteraciones + 1
                    dataframe_resultados = dataframe_resultados.append(
                        dict(iter=contador_iteraciones, f_sol=f(solucion_busqueda)), ignore_index=True)

                if busquedas_sin_mejora == max_busquedas_sin_mejora:
                    condicion_parada = "No se encontraton mejores soluciones"
                else:
                    condicion_parada = "Máximo de iteraciones alcanzadas"
                mejor_solucion = self.obtener_mejor_solucion(lista_tabu)

                resultados_finales = dict(mejor_solucion=mejor_solucion,
                                          f_mejor_solucion=f(mejor_solucion),
                                          iteracion_mejor_solucion=iteracion_mejor_solucion,
                                          total_iteraciones=contador_iteraciones,
                                          total_llamados_funcion=self.contador_llamadas_funcion_objetivo,
                                          condicion_de_parada=condicion_parada)
                return parametros, resultados_finales, dataframe_resultados

        self.funcion_busqueda = busqueda_tabu

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
                pdf.texto(texto="Máximo de búsuqedas sin mejora: "+str(pdf.parametros[0]))
                pdf.texto(texto="Espacio en memoria: "+str(pdf.parametros[1]))
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










