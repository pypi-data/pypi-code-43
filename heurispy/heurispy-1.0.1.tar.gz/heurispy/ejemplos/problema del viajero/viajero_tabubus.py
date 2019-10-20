from heurispy.problema import Problema
from heurispy.heuristicas.busqueda_tabu import BusquedaTabu
from heurispy.framework import genera_lista_ejecuciones_heuristicas, inicia_exploracion_heuristica
from problema_del_viajero import *

if __name__ == '__main__':

    problema_optimizacion = Problema(generar_solucion_nueva, funcion_objetivo, vecindad)

    tabuBus = BusquedaTabu(problema_optimizacion, max_iteraciones=10000)

    parametros_tabuBus = dict(espacio_memoria=[50, 100], max_busquedas_sin_mejora=[100])

    lista_bloque_parametros_taboo = genera_lista_ejecuciones_heuristicas(parametros_tabuBus, 10)

    inicia_exploracion_heuristica(tabuBus, lista_bloque_parametros_taboo)



