from heurispy.framework import genera_lista_ejecuciones_heuristicas, inicia_exploracion_heuristica
from heurispy.heuristicas.busqueda_tabu import BusquedaTabu
from heurispy.problema import Problema
from kilometros_vacios import *

from problema_kilometros_vacios import *


if __name__ == '__main__':

    problema_kilometros = Problema(dominio=generar_solucion_nueva,
                                            funcion_objetivo=funcion_objetivo,
                                            funcion_variacion_soluciones=variar_solucion)

    tabuBus = BusquedaTabu(problema_kilometros, max_iteraciones=10000)

    parametros_tabuBus = dict(espacio_memoria=[50, 100, 150], max_busquedas_sin_mejora=[50, 100])

    lista_bloque_parametros_taboo = genera_lista_ejecuciones_heuristicas(parametros_tabuBus, repeticiones=10)

    inicia_exploracion_heuristica(tabuBus, lista_bloque_parametros_taboo)


