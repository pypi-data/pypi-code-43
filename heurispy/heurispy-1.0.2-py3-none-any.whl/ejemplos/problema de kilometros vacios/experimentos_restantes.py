from heurispy.framework import genera_lista_ejecuciones_heuristicas, inicia_exploracion_heuristica
from heurispy.heuristicas.recocido_simulado import RecocidoSimulado
from heurispy.heuristicas.busqueda_local_iterada import BusquedaLocalIterada
from heurispy.heuristicas.busqueda_armonica import BusquedaArmonica
from heurispy.problema import Problema
from kilometros_vacios import *


if __name__ == '__main__':

    problema_kilometros = Problema(dominio=generar_solucion_nueva,
                                   funcion_objetivo=funcion_objetivo,
                                   funcion_variacion_soluciones=variar_solucion)

    recSim = RecocidoSimulado(problema_kilometros, alpha=0.9, max_iteraciones=10000)


    parametros_recSim = dict(temperatura=[2.0], iteraciones_inyeccion_temperatura=[150, 200],
                             maximo_inyecciones_temperatura=[5])

    lista_bloque_parametros_armonica = genera_lista_ejecuciones_heuristicas(parametros_recSim, repeticiones=10)

    inicia_exploracion_heuristica(recSim, lista_bloque_parametros_armonica)

    localIter = BusquedaLocalIterada(problema_kilometros, max_iteraciones=10000)

    parametros_locGui = dict(busqueda_local_sin_minimo_global=[100], rango_perturbacion=[6],
                             busqueda_iterada_sin_mejora=[50])

    lista_bloque_parametros_guiada = genera_lista_ejecuciones_heuristicas(parametros_locGui, repeticiones=10)

    inicia_exploracion_heuristica(localIter, lista_bloque_parametros_guiada)

    busArm = BusquedaArmonica(problema_kilometros, max_iteraciones=10000)

    parametros_busArm = dict(espacio_memoria=[50, 100], max_busqueda_sin_mejoras=[100],
                             radio_consideracion_memoria_armonica=[0.8], radio_ajuste_afinacion=[0.2])

    lista_bloque_parametros_armonica = genera_lista_ejecuciones_heuristicas(parametros_busArm, repeticiones=10)

    inicia_exploracion_heuristica(busArm, lista_bloque_parametros_armonica)
