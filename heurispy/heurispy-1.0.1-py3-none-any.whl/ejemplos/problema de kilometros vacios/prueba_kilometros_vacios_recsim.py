from heurispy.framework import genera_lista_ejecuciones_heuristicas, inicia_exploracion_heuristica
from heurispy.heuristicas.recocido_simulado import RecocidoSimulado
from heurispy.problema import Problema
from kilometros_vacios import *


if __name__ == '__main__':

    problema_kilometros = Problema(dominio=generar_solucion_nueva,
                                   funcion_objetivo=funcion_objetivo,
                                   funcion_variacion_soluciones=variar_solucion)

    recSim = RecocidoSimulado(problema_kilometros, alpha=0.9, max_iteraciones=10000)

    parametros_recSim = dict(temperatura=[1.0, 2.0], iteraciones_inyeccion_temperatura=[100, 150, 200],
                             maximo_inyecciones_temperatura=[5])

    lista_bloque_parametros_armonica = genera_lista_ejecuciones_heuristicas(parametros_recSim, repeticiones=10)

    inicia_exploracion_heuristica(recSim, lista_bloque_parametros_armonica)

