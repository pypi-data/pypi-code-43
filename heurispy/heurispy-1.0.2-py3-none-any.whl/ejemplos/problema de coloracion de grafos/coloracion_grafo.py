cantidad_vertices = 10

c_1 = 1
c_2 = 1

adyacencias_vertices = {"0": [1, 4, 6],
                        "1": [0, 2, 7],
                        "2": [1, 3, 8],
                        "3": [2, 4, 9],
                        "4": [0, 3, 5],
                        "5": [4, 7, 8],
                        "6": [0, 8, 9],
                        "7": [1, 5, 9],
                        "8": [2, 5, 6],
                        "9": [3, 6, 7]}


def obtener_colores_adyacentes(solucion, vertice):
    vertices = adyacencias_vertices[str(vertice)]
    colores = []
    for vertice_adyacente in vertices:
        colores.append(solucion[vertice_adyacente])
    return colores


def costo_colores_diferentes(solucion):
    colores_distintos = set(solucion)
    return len(colores_distintos)


def costo_colores_adyacentes(solucion):
    valor_final = 0
    longitud_solucion = len(solucion)
    for indice in range(longitud_solucion):
        color = solucion[indice]
        colores_adyacentes = obtener_colores_adyacentes(solucion, indice)
        repeticiones = colores_adyacentes.count(color)
        valor_final = valor_final + repeticiones
    return valor_final


def crear_solucion():
    import random
    nueva_solucion = []
    for indice in range(cantidad_vertices):
        nueva_solucion.append(random.randint(0, cantidad_vertices-1))
    return nueva_solucion


def variar_solucion(solucion):
    import random
    nueva_solucion = solucion.copy()
    longitud_solucion = len(nueva_solucion)
    indice_a_cambiar = random.randint(0, longitud_solucion-1)
    colores = list(range(cantidad_vertices))
    colores_adyacentes = obtener_colores_adyacentes(nueva_solucion, indice_a_cambiar)
    colores_disponibles = [color for color in colores if color not in colores_adyacentes]
    nueva_solucion[indice_a_cambiar] = random.choice(colores_disponibles)
    return nueva_solucion


def funcion_objetivo(solucion):
    costo_colores = costo_colores_diferentes(solucion)
    costo_adyacencia = costo_colores_adyacentes(solucion)
    return c_1 * costo_colores + c_2 * costo_adyacencia

