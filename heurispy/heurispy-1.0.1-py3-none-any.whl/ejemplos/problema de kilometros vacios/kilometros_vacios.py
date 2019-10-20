import pandas as pd
import random
import warnings
from datetime import timedelta
from time import time

warnings.simplefilter(action='ignore')

c_d = 1

c_t = 1

limites_km_por_dia = [0, 120, 960, 1920, 2880, 3841, 4801, 6000]

nombre_archivo = "ImplementacionFramework.xlsx"

unidades_original = pd.read_excel(nombre_archivo, sheet_name='Unidades')
unidades_id_unidad = unidades_original.copy()
unidades_id_unidad.set_index("id_unidad", inplace=True)

sucursales_original = pd.read_excel(nombre_archivo, sheet_name='Sucursales')

solicitud_servicios_original = pd.read_excel(nombre_archivo, sheet_name='SolicitudServicios')
solicitud_servicios_original = solicitud_servicios_original.sort_values("fecha_servicio", ascending=1)
solicitud_servicios_original.set_index("id_solicitud_servicio", inplace=True)

servicios_original = pd.read_excel(nombre_archivo, sheet_name='Servicios')
servicios_original.set_index(["id_solicitud_servicio", "id_tiposervicio"], inplace=True)

cotizador_original = pd.read_excel(nombre_archivo, sheet_name='Cotizador')
cotizador_original.set_index(["ciudad_origen", "ciudad_destino"], inplace=True)

unidades_movimiento = unidades_original[["id_unidad", "id_tipo_mudanza", "volumetria", "id_sucursal", "id_localidad"]]
unidades_movimiento["fecha_disponible"] = pd.Timestamp(2019, 9, 28).date()
unidades_movimiento.set_index("id_unidad", inplace=True)


def cacular_dias_viaje(kilometros_necesarios, id_solicitud_servicio):
    i = 0
    while kilometros_necesarios > limites_km_por_dia[i]:
        i = i + 1

    volumetria_servicio = calcular_volumetria_servicio(id_solicitud_servicio)
    if volumetria_servicio > 30:
        i = i + 1
    else:
        i = i + 0.5
    return i


def calcular_costo_viaje(origen, destino):
    if origen == destino:
        return 0
    else:
        costo = cotizador_original.loc[origen, destino]["kilometros_numerico"]
        return costo


def calcular_kilometros_viaje(origen, destino):
    kilometros = calcular_costo_viaje(origen, destino)
    return kilometros


def calcular_kilometros_viaje_total(origen_unidad, origen_servicio, destino_servicio):
    kilometros_totales = calcular_costo_viaje(origen_unidad, origen_servicio) + calcular_costo_viaje(origen_servicio, destino_servicio)
    return kilometros_totales


def calcular_volumetria_servicio(id_solicitud_servicio):
    servicios_original.sort_index()
    volumetria_servicio = servicios_original.loc[id_solicitud_servicio, 3]["volumetria"].sum()
    return volumetria_servicio


def calcular_total_volumetria_unidades(lista_unidades):
    total = 0
    for unidad in lista_unidades:
            volumetria = unidades_id_unidad.loc[unidad]["volumetria"]
            total = total + volumetria
    return total


def calcular_fecha_llegada(fecha, kilometros, id_solicitud_servicio):
    dias = cacular_dias_viaje(kilometros, id_solicitud_servicio)
    fecha = pd.Timestamp(fecha + timedelta(days=dias))
    return fecha


def asignar_nueva_fecha_a_unidad(fecha, unidad, dataframe_unidades):
    dataframe_unidades.at[unidad, 'fecha_disponible'] = fecha.date()


def asignar_nueva_localidad_a_unidad(localidad, unidad, dataframe_unidades):
    dataframe_unidades.at[unidad, "id_localidad"] = localidad


def confirmar_disponibilidad_unidad_a_servicio(id_unidad, id_solicitud_servicio):
    ciudad_unidad = unidades_id_unidad.loc[id_unidad]["id_localidad"]
    tipo_mudanza = unidades_id_unidad.loc[id_unidad]["tipo_mudanza"]
    ciudad_origen_servicio = solicitud_servicios_original.loc[id_solicitud_servicio]["id_localidad_origen"]

    if tipo_mudanza == 2:
        return True
    elif tipo_mudanza == 1 and ciudad_unidad == ciudad_origen_servicio:
        return True
    else:
        return False


def confirmar_volumetria_unidad_a_servicio(id_unidad, id_servicio):
    volumetria_unidad = unidades_id_unidad.loc[id_unidad]["volumetria"]
    volumetria_servicio = calcular_volumetria_servicio(id_servicio)
    if volumetria_unidad <= volumetria_servicio:
        return True
    else:
        return False


def obtener_unidades_disponibles_para_servicio(id_solicitud_servicio):

    unidades = unidades_original.copy()

    id_tipo_mudanza = solicitud_servicios_original.loc[id_solicitud_servicio]["id_tipo_mudanza"]

    if id_tipo_mudanza == 2:
        unidades.set_index("id_tipo_mudanza", inplace=True)
        unidades_disponibles = unidades.loc[2]
        unidades_disponibles.reset_index(inplace=True)
    else:
        ciudad_servicio = solicitud_servicios_original.loc[id_solicitud_servicio]["id_localidad_origen"]
        unidades.set_index("id_tipo_mudanza", inplace=True)

        unidades_tipo_uno = unidades.loc[1]
        unidades_tipo_dos = unidades.loc[2]

        unidades_tipo_uno_en_ciudad = unidades_tipo_uno["id_localidad"] == ciudad_servicio

        unidades_en_ciudad = unidades_tipo_uno[unidades_tipo_uno_en_ciudad]

        unidades_en_ciudad.reset_index(inplace=True)
        unidades_tipo_dos.reset_index(inplace=True)

        unidades_disponibles = pd.concat([unidades_en_ciudad, unidades_tipo_dos])

    return unidades_disponibles


def asignar_unidades_para_servicio(id_solicitud_servicio, lista_unidades_usadas):
    unidades_disponibles = obtener_unidades_disponibles_para_servicio(id_solicitud_servicio)
    unidades_disponibles.set_index("id_unidad", inplace=True)
    volumetria_servicio = calcular_volumetria_servicio(id_solicitud_servicio)

    num_aleatorio = random.choice(unidades_disponibles.index)

    if unidades_disponibles.loc[num_aleatorio]["volumetria"] < volumetria_servicio:
        suma_volumetria = unidades_disponibles.loc[num_aleatorio]["volumetria"]
        lista_unidades_servicio = [num_aleatorio]

        while suma_volumetria < volumetria_servicio:
            num_aleatorio_2 = random.choice(unidades_disponibles.index)
            while num_aleatorio_2 == num_aleatorio:
                num_aleatorio_2 = random.choice(unidades_disponibles.index)
            num_aleatorio = num_aleatorio_2
            suma_volumetria = suma_volumetria + unidades_disponibles.loc[num_aleatorio]["volumetria"]
            lista_unidades_servicio.append(num_aleatorio)
        lista_unidades_usadas.append(lista_unidades_servicio)

    else:
        lista_unidades_usadas.append([num_aleatorio])

    return lista_unidades_usadas


def cambiar_unidades_para_servicio(id_solicitud_servicio):
    unidades_disponibles = obtener_unidades_disponibles_para_servicio(id_solicitud_servicio)
    unidades_disponibles.set_index("id_unidad", inplace=True)
    volumetria_servicio = calcular_volumetria_servicio(id_solicitud_servicio)

    num_aleatorio = random.choice(unidades_disponibles.index)

    if unidades_disponibles.loc[num_aleatorio]["volumetria"] < volumetria_servicio:
        suma_volumetria = unidades_disponibles.loc[num_aleatorio]["volumetria"]
        lista_unidades_servicio = [num_aleatorio]

        while suma_volumetria < volumetria_servicio:
            num_aleatorio_2 = random.choice(unidades_disponibles.index)
            while num_aleatorio_2 == num_aleatorio:
                num_aleatorio_2 = random.choice(unidades_disponibles.index)
            num_aleatorio = num_aleatorio_2
            suma_volumetria = suma_volumetria + unidades_disponibles.loc[num_aleatorio]["volumetria"]
            lista_unidades_servicio.append(num_aleatorio)
        return lista_unidades_servicio
    else:
        return [num_aleatorio]


def generar_solucion_nueva():
    lista_solicitudes = solicitud_servicios_original.index.tolist()

    solucion_nueva = []

    for solicitud in lista_solicitudes:
        solucion_nueva = asignar_unidades_para_servicio(solicitud, solucion_nueva)

    return solucion_nueva


def funcion_objetivo(solucion_a_evaluar):
    lista_solicitudes = solicitud_servicios_original.index.tolist()
    unidades = unidades_movimiento.copy()

    km_vacios = 0
    costo_fechas = 0

    for i in range(len(lista_solicitudes)):

        solicitud = lista_solicitudes[i]
        unidad = solucion_a_evaluar[i]

        ciudad_origen = solicitud_servicios_original.loc[solicitud]["id_localidad_origen"]
        ciudad_destino = solicitud_servicios_original.loc[solicitud]["id_localidad_destino"]
        fecha_servicio_iniciado = solicitud_servicios_original.loc[solicitud]["fecha_servicio"]

        for elemento in unidad:
            ciudad_unidad = unidades.loc[elemento]["id_localidad"]
            fecha_unidad_disponible = unidades.loc[elemento]["fecha_disponible"]
            km_vacios = km_vacios + calcular_costo_viaje(ciudad_unidad, ciudad_origen)
            km_viaje = calcular_kilometros_viaje_total(ciudad_unidad, ciudad_origen, ciudad_destino)
            km_viaje_origen_solicitud = calcular_kilometros_viaje(ciudad_unidad, ciudad_origen)
            fecha_viaje_origen_solicitud = calcular_fecha_llegada(fecha_unidad_disponible, km_viaje_origen_solicitud, solicitud)
            fecha_total_viaje = calcular_fecha_llegada(fecha_unidad_disponible, km_viaje, solicitud)
            if fecha_viaje_origen_solicitud < fecha_servicio_iniciado:
                fecha_total_viaje = fecha_servicio_iniciado
            else:
                resta_fechas = (fecha_viaje_origen_solicitud - fecha_servicio_iniciado).days
                costo_fechas = costo_fechas + resta_fechas**2
            asignar_nueva_fecha_a_unidad(fecha_total_viaje, elemento, dataframe_unidades=unidades)
            asignar_nueva_localidad_a_unidad(ciudad_destino, elemento, dataframe_unidades=unidades)

    del unidades
    return c_d*km_vacios + c_t*costo_fechas


def variar_solucion(solucion_a_evaluar):
    solucion_nueva = solucion_a_evaluar.copy()
    num_aleatorio = random.randint(0, len(solucion_a_evaluar)-1)
    lista_solicitudes_servicios = solicitud_servicios_original.index.tolist()
    servicio_a_atender = lista_solicitudes_servicios[num_aleatorio]
    unidades_disponibles = cambiar_unidades_para_servicio(servicio_a_atender)
    solucion_nueva[num_aleatorio] = unidades_disponibles
    return solucion_nueva



