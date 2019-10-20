from heurispy.framework import genera_lista_ejecuciones_heuristicas, inicia_exploracion_heuristica
from heurispy.problema import Problema
from heurispy.heuristicas.recocido_simulado import RecocidoSimulado
from coloracion_grafo import *


if __name__ == '__main__':

    coloracion_grafo = Problema(dominio=crear_solucion,
                                funcion_objetivo=funcion_objetivo,
                                funcion_variacion_soluciones=variar_solucion)

    recSim = RecocidoSimulado(coloracion_grafo, alpha=0.9, max_iteraciones=10000)

    parametros_recSim = dict(temperatura=[1.0, 2.0], iteraciones_inyeccion_temperatura=[50, 100],
                             maximo_inyecciones_temperatura=[5, 10])

    lista_bloque_parametros_recocido = genera_lista_ejecuciones_heuristicas(parametros_recSim, repeticiones=10)

    inicia_exploracion_heuristica(recSim, lista_bloque_parametros_recocido, nucleos_cpu=4)

