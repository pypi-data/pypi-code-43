from heurispy.problema import Problema
from heurispy.heuristicas.busqueda_tabu import BusquedaTabu
from heurispy.framework import genera_lista_ejecuciones_heuristicas, inicia_exploracion_heuristica 

import os
from problema_kilometros_vacios_con_csv import *


if __name__ == '__main__':

    exists = os.path.isfile('datos_resultados.csv')

    if exists:
        os.remove("datos_resultados.csv")

    problema_kilometros = Problema(dominio=generar_solucion_nueva,
                                            funcion_objetivo=funcion_objetivo,
                                            funcion_variacion_soluciones=variar_solucion)

    tabuBus = BusquedaTabu(problema_kilometros, max_iteraciones=1000)

    parametros_tabuBus = dict(espacio_memoria=[100], max_busquedas_sin_mejora=[100])

    lista_bloque_parametros_taboo = .genera_lista_ejecuciones_heuristicas(parametros_tabuBus, repeticiones=1)

    inicia_exploracion_heuristica(tabuBus, lista_bloque_parametros_taboo, nucleos_cpu=1)
