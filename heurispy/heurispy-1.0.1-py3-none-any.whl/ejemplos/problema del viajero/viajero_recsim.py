from heurispy.problema import Problema
from heurispy.heuristicas.recocido_simulado import RecocidoSimulado
from heurispy.framework import genera_lista_ejecuciones_heuristicas, inicia_exploracion_heuristica
from problema_del_viajero import *

if __name__ == '__main__':

    problema_optimizacion = Problema(generar_solucion_nueva, funcion_objetivo, vecindad)

    recSim = RecocidoSimulado(problema_optimizacion, alpha=0.9, max_iteraciones=10000)

    parametros_recSim = dict(temperatura=[1.0, 2.0], iteraciones_inyeccion_temperatura=[100, 150],
                             maximo_inyecciones_temperatura=[5, 10])

    lista_bloque_parametros_simul = genera_lista_ejecuciones_heuristicas(parametros_recSim, 10)

    inicia_exploracion_heuristica(recSim, lista_bloque_parametros_simul)




