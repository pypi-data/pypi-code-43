from heurispy.framework import genera_lista_ejecuciones_heuristicas, inicia_exploracion_heuristica
from heurispy.problema import Problema
from heurispy.heuristicas.busqueda_armonica import BusquedaArmonica
from coloracion_grafo import *


if __name__ == '__main__':

    coloracion_grafo = Problema(dominio=crear_solucion,
                                funcion_objetivo=funcion_objetivo,
                                funcion_variacion_soluciones=variar_solucion)

    heuristica = BusquedaArmonica(coloracion_grafo, max_iteraciones=1000)

    parametros_busArm = dict(espacio_memoria=[50], max_busqueda_sin_mejoras=[50],
                             radio_consideracion_memoria_armonica=[0.6], radio_ajuste_afinacion=[0.2])

    lista_bloque_parametros_armonica = genera_lista_ejecuciones_heuristicas(parametros_busArm, repeticiones=5)

    inicia_exploracion_heuristica(heuristica, lista_bloque_parametros_armonica, nucleos_cpu=4)
