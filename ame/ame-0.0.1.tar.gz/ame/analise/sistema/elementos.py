from typing import Optional

import numpy as np

from ame.analise.elemento_numerado import ElementoNumerado
from ame.analise.sistema.cargas import CargaDistribuida
from ame.analise.sistema.material import Material
from ame.analise.sistema.no import No
from ame.analise.sistema.secao import Secao
from ame.constantes import TIPOS_ELEMENTOS, SISTEMAS_COORDENADAS


class ElementoBarra(ElementoNumerado):
    """Classe abstrata que define as propriedades genéricas de um elemento."""

    def __init__(self, identificacao: int, no_inicial: No, no_final: No, material: Material, secao: Secao,
                 carga: CargaDistribuida):
        """Construtor

        Args:
            identificacao: Identificação.
            no_inicial: Nó inicial.
            no_final: Nó final.
            material: Material.
            secao: Seção transversal.
            carga: Carga distribuída no elemento.
        """
        super().__init__(identificacao)
        if carga is None:
            self._carga = None
        else:
            self.carga = carga

        self.no_inicial = no_inicial
        self.no_final = no_final
        self.material = material
        self.secao = secao

    def __eq__(self, other):
        """Condição de igualdade entre as instâncias.

        Args:
            other(ElementoBarra): Instância de referência.
        """
        return bool(self.identificacao == other.identificacao and self.no_inicial == other.no_inicial and
                    self.no_final == other.no_final and self.material == other.material and
                    self.secao == other.secao and self.carga == other.carga)

    def __repr__(self):
        return f'ELEMENTO {self.identificacao}:\n' \
               f'----\n' \
               f'No inicial: {self.no_inicial.identificacao} (x={self.no_inicial.x:.2f}, ' \
               f'y={self.no_final.y:.2f})\n' \
               f'No final: {self.no_final.identificacao} (x={self.no_final.x:.2f}, ' \
               f'y={self.no_final.y:.2f})\n' \
               f'Comprimento: {self.comprimento():.2f}\n' \
               f'Material: {self.material.identificacao}\n' \
               f'Seção transversal: {self.secao.identificacao}\n'
        # region Properties

    @property
    def carga(self) -> Optional[CargaDistribuida]:
        """Retorna a carga distribuída no elemento.

        Retorna None se não houver carga distribuída na barra.

        Raises:
            TypeError:
                Se o tipo de dado não for Carga.
        """
        return self._carga

    @carga.setter
    def carga(self, value):
        if not isinstance(value, CargaDistribuida):
            raise TypeError(f'O tipo de dado "{type(value)}" não é válido para representar os carregamentos '
                            f'distribuídos no elemento!')
        else:
            self._carga = value

    @property
    def no_inicial(self) -> No:
        """Retorna o nó do início da barra.

        Raises:
            TypeError:
                Se o tipo de dado não for No.
        """
        return self._no_inicial

    @no_inicial.setter
    def no_inicial(self, value):
        if not isinstance(value, No):
            raise TypeError(f'O tipo de dado "{type(value)}" não é válido para descrever o nó inicial da barra!')
        else:
            self._no_inicial = value

    @property
    def no_final(self) -> No:
        """Retorna o nó do final da barra.

        Raises:
            TypeError:
                Se o tipo de dado não for No.
        """
        return self._no_final

    @no_final.setter
    def no_final(self, value):
        if not isinstance(value, No):
            raise TypeError(f'O tipo de dado "{type(value)}" não é válido para descrever o nó final da barra!')
        else:
            self._no_final = value

    @property
    def material(self) -> Material:
        """Retorna o material que compõe a barra.

        Raises:
            TypeError:
                Se o tipo de dado não for Material.
        """
        return self._material

    @material.setter
    def material(self, value):
        if not isinstance(value, Material):
            raise TypeError(f'O tipo de dado "{type(value)}" não é válido para representar o material da barra!')
        else:
            self._material = value

    @property
    def secao(self) -> Secao:
        """Retorna a seção transversal que compõe a barra.

        Raises:
            TypeError:
                Se o tipo de dado não for Secao.
        """
        return self._secao

    @secao.setter
    def secao(self, value):
        if not isinstance(value, Secao):
            raise TypeError(f'O tipo de dado "{type(value)}" não é válido para representar a seção da barra!')
        else:
            self._secao = value

    # endregion

    @staticmethod
    def espelhar_matriz_triangular(matriz: np.ndarray) -> np.ndarray:
        """Retorna uma matriz diagonal a partir de uma matriz triagular.

        Args:
            matriz: Matriz triangular (superior ou inferior).
        """
        # Verificações
        if np.allclose(matriz, np.triu(matriz)):
            tipo_matriz = 'superior'
        elif np.allclose(matriz, np.tril(matriz)):
            tipo_matriz = 'inferior'
        else:
            raise AttributeError(f'A matriz a ser espelhada deve ser triangular superior ou inferior!')

        # Espelhamento
        if tipo_matriz == 'inferior':
            return matriz + np.tril(matriz, -1).T
        else:
            return matriz + np.triu(matriz, 1).T

    def graus_liberdade(self) -> list:
        """Retorna uma lista com os graus de liberdade do elemento.

        Raises:
            ValueError:
                Se o tipo de elemento utilizado ainda não estiver cadastrado na função de cálculo do graus
                de liberdade dos elementos.
        """
        tpe = TIPOS_ELEMENTOS

        if type(self) is PP2:
            return self.no_inicial.graus_liberdade(tpe[0]) + self.no_final.graus_liberdade(tpe[0])
        else:
            raise ValueError(f'O tipo de elemento "{type(self)}" não está cadastrado!')

    def graus_liberdade_livres(self) -> list:
        """Retorna um vetor com os graus de liberdade livres do elemento."""
        return [i for i in self.graus_liberdade() if i not in self.graus_liberdade_impedidos()]

    def graus_liberdade_impedidos(self) -> list:
        """Retorna um vetor com os graus de liberdade impedidos do elemento."""
        pass

    def total_graus_liberdade(self) -> int:
        """Retorna a quantidade de graus de liberdade do elemento."""
        return len(self.graus_liberdade())

    def matriz_rigidez_local(self) -> np.ndarray:
        """Matriz de rigidez do elemento no sistema local."""
        pass

    def matriz_rotacao(self) -> np.ndarray:
        """Retorna a matriz de rotação do elemento."""
        pass

    def matriz_rigidez_global(self) -> np.ndarray:
        """Retorna a matriz de rigidez no sistema global."""
        k = self.matriz_rigidez_local()
        r = self.matriz_rotacao()

        return r.T.dot(k).dot(r)

    def forcas_aplicadas_nos_global(self) -> np.ndarray:
        """Retorna um vetor de forças aplicadas nos nós do elemento no sistema global."""
        return np.array([[self.no_inicial.carga.fx],
                         [self.no_inicial.carga.fy],
                         [self.no_inicial.carga.mz],
                         [self.no_final.carga.fx],
                         [self.no_final.carga.fy],
                         [self.no_final.carga.mz]])

    def forcas_equivalentes_nos_local(self) -> np.ndarray:
        """Retorna um vetor de forças equivalentes no sistema local."""
        pass

    def forcas_equivalentes_nos_global(self) -> np.ndarray:
        f = self.forcas_equivalentes_nos_local()
        r = self.matriz_rotacao()

        return r.T.dot(f)

    def comprimento(self) -> float:
        """Retorna o comprimento do elemento"""
        return self.no_inicial.distancia(self.no_final)

    def seno_angulo_inclinacao(self) -> float:
        """Retorna o valor do seno do ângulo formado pela inclinação do elemento."""
        return self.no_inicial.distancia_y(self.no_final) / self.comprimento()

    def cosseno_angulo_inclinacao(self) -> float:
        """Retorna o valor do cosseno do ângulo formado pela inclinação do elemento."""
        return self.no_inicial.distancia_x(self.no_final) / self.comprimento()

    def deslocamentos(self, deslocamento_estrutura: np.ndarray) -> np.ndarray:
        """Retorna os deslocamentos dos graus de liberdade do elemento."""
        gle = self.graus_liberdade()
        delem = np.array([deslocamento_estrutura[i - 1] for i in gle])
        return delem.reshape(-1, 1)

    def esforcos(self, deslocamento_estrutura: np.ndarray, n: int = 20) -> np.ndarray:
        """Retorna uma matriz contendo a posição da seção na primeira coluna seguida de seus respectivos
        esforços normal, de momento e cortante.

        Args:
            n: Número de seções em que o elemento será dividido.
            deslocamento_estrutura: Vetor de deslocamentos da estrutura.
        """
        # Força no elemento.
        mat_rot = self.matriz_rotacao()
        uel = mat_rot.dot(self.deslocamentos(deslocamento_estrutura))
        fel = self.matriz_rigidez_local().dot(uel) - self.forcas_equivalentes_nos_local().reshape(-1, 1)

        esforcos = []

        # Decomposição dos esforços.
        cos = self.cosseno_angulo_inclinacao()
        sen = self.seno_angulo_inclinacao()

        if self.carga.sistema_coord == SISTEMAS_COORDENADAS[0]:
            qx = self.carga.qx
            qy = self.carga.qy
        else:
            qx = self.carga.qx * cos + self.carga.qy * sen
            qy = -self.carga.qx * sen + self.carga.qy * cos

        # Cálculo dos esforços.
        for x in np.linspace(0, self.comprimento(), n):
            normal = -fel[0][0] - qx * x
            fletor = -fel[2][0] + fel[1][0] * x + (qy * x ** 2) / 2
            cortante = fel[1][0] + qy * x

            esforcos.append([x, normal, fletor, cortante])

        return np.array(esforcos)


class PP2(ElementoBarra):
    def __init__(self, identificacao, no_inicial: No, no_final: No, material: Material, secao: Secao,
                 carga: CargaDistribuida):
        super().__init__(identificacao, no_inicial, no_final, material, secao, carga)

    def graus_liberdade_impedidos(self) -> list:
        glr = []
        gle = self.graus_liberdade()

        if not self.no_inicial.apoio.apoio_livre():
            if self.no_inicial.apoio.dx is False:
                glr.append(gle[0])
            if self.no_inicial.apoio.dy is False:
                glr.append(gle[1])
            if self.no_inicial.apoio.rz is False:
                glr.append(gle[2])

        if not self.no_final.apoio.apoio_livre():
            if self.no_final.apoio.dx is False:
                glr.append(gle[3])
            if self.no_final.apoio.dy is False:
                glr.append(gle[4])
            if self.no_final.apoio.rz is False:
                glr.append(gle[5])

        return glr

    def matriz_rigidez_local(self):
        e = self.material.mod_elastic
        a = self.secao.area
        iz = self.secao.inercia_z
        c = self.comprimento()

        l1 = e * iz / c
        l2 = e * iz / c ** 2
        l3 = e * iz / c ** 3

        k = np.zeros((6, 6))

        # Coluna 1
        k[0][0] = e * a / c
        k[3][0] = -e * a / c

        # Coluna 2
        k[1][1] = 12 * l3
        k[2][1] = 6 * l2
        k[4][1] = -12 * l3
        k[5][1] = 6 * l2

        # Coluna 3
        k[2][2] = 4 * l1
        k[4][2] = -6 * l2
        k[5][2] = 2 * l1

        # Coluna 4
        k[3][3] = e * a / c

        # Coluna 5
        k[4][4] = 12 * l3
        k[5][4] = -6 * l2

        # Coluna 6
        k[5][5] = 4 * l1

        # Matriz de rigidez
        return self.espelhar_matriz_triangular(k)

    def matriz_rotacao(self) -> np.ndarray:
        cos = self.cosseno_angulo_inclinacao()
        sen = self.seno_angulo_inclinacao()

        r = np.zeros((6, 6))

        # Coluna 0
        r[0][0] = cos
        r[1][0] = -sen

        # Coluna 1
        r[0][1] = sen
        r[1][1] = cos

        # Coluna 2
        r[2][2] = 1

        # Coluna 3
        r[3][3] = cos
        r[4][3] = -sen

        # Coluna 4
        r[3][4] = sen
        r[4][4] = cos

        # Coluna 5
        r[5][5] = 1

        return r

    def forcas_equivalentes_nos_local(self) -> np.ndarray:
        feq = np.zeros((6, 1))

        if self.carga.carga_nula():
            return feq
        else:
            c = self.comprimento()
            cos = self.cosseno_angulo_inclinacao()
            sen = self.seno_angulo_inclinacao()

            if self.carga.sistema_coord == SISTEMAS_COORDENADAS[1]:
                qx = self.carga.qx * cos + self.carga.qy * sen
                qz = - self.carga.qx * sen + self.carga.qy * cos
            elif self.carga.sistema_coord == SISTEMAS_COORDENADAS[0]:
                qx = self.carga.qx
                qz = self.carga.qy
            else:
                raise ValueError(f'O valor "{self.carga.sistema_coord}" não é um sistema cartesiano válido!')

            feq[0] = qx * c / 2
            feq[1] = qz * c / 2
            feq[2] = qz * c ** 2 / 12
            feq[3] = feq[0]
            feq[4] = feq[1]
            feq[5] = -feq[2]

            return feq
