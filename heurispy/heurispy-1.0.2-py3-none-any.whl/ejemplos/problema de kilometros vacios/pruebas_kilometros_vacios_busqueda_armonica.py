from heurispy.framework import genera_lista_ejecuciones_heuristicas, inicia_exploracion_heuristica
from heurispy.heuristicas.busqueda_armonica import BusquedaArmonica
from heurispy.problema import Problema
from kilometros_vacios import *


if __name__ == '__main__':

    problema_kilometros = Problema(dominio=generar_solucion_nueva,
                                            funcion_objetivo=funcion_objetivo,
                                            funcion_variacion_soluciones=variar_solucion)

    tabuBus = BusquedaArmonica(problema_kilometros, max_iteraciones=10000)

    parametros_busArm = dict(espacio_memoria=[50, 100], max_busqueda_sin_mejoras=[50, 100],
                             radio_consideracion_memoria_armonica=[0.75, 0.9], radio_ajuste_afinacion=[0.1, 0.2])

    lista_bloque_parametros_armonica = genera_lista_ejecuciones_heuristicas(parametros_busArm, repeticiones=10)

    inicia_exploracion_heuristica(tabuBus, lista_bloque_parametros_armonica)
