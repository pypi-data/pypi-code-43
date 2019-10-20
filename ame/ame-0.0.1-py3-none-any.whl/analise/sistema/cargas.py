from typing import List

from ame.constantes import SISTEMAS_COORDENADAS


class Carga:
    """Classe abstrata que representa as três componentes espaciais de um esforço."""

    def __init__(self, sistema_coord: str = 'global'):
        """
        Args:
            sistema_coord: Sistema cartesiano de atuação da carga (se 'local' ou 'global').
        """
        self.sistema_coord = sistema_coord

    # region properties

    @property
    def sistema_coord(self) -> str:
        """Retorna o sistema cartesiano de atuação da carga no elemento (se no sistema global ou local).

        Raises
            TypeError:
                Se o tipo de dado não for str.
            ValueError:
                Se a string passada não for 'local' ou 'global'.
        """
        return self._sistema_coord

    @sistema_coord.setter
    def sistema_coord(self, value):
        if value not in SISTEMAS_COORDENADAS:
            raise ValueError(f'O valor "{value}" não representa um sistema cartesiano válido!')
        else:
            self._sistema_coord = value

    # endregion

    def carga_nula(self) -> bool:
        """Retorna True se todas as componentes da carga forem nulas e False caso contrário."""
        return all(i == 0 for i in self.vetor_cargas())

    def vetor_cargas(self) -> list:
        pass


class CargaDistribuida(Carga):
    """Define as propriedades das forças aplicadas sobre o domínio de um elemento."""

    def __init__(self, qx: float = 0, qy: float = 0, sistema_coord: str = 'global'):
        """
        Args:
            qx: Força distribuída ao longo do eixo x.
            qy: Força distribuída ao longo do eixo y.
        """
        super().__init__(sistema_coord)
        self.qx = qx
        self.qy = qy

    def __eq__(self, other):
        return bool(self.qx == other.qx and self.qy == self.qy and self.sistema_coord == other.sistema_coord)

    def __repr__(self):
        return f'{type(self).__name__}(qx={self.qx}, qy={self.qy}, sistema={self.sistema_coord})'

    @property
    def qx(self) -> float:
        """Retorna o valor da carga distribuída atuante no eixo x.

        Raises
            ValueError:
                Se o tipo dado não for int ou float.

        """
        return self._qx

    @qx.setter
    def qx(self, value):
        if not isinstance(value, (float, int)):
            raise TypeError(f'O tipo de dado "{type(value)}" não é válido para representar a carga distribuída qx!')
        else:
            self._qx = value

    @property
    def qy(self) -> float:
        """Retorna o valor da carga distribuída atuante no eixo y.

        Raises
            ValueError:
                Se o tipo dado não for int ou float.

        """
        return self._qy

    @qy.setter
    def qy(self, value):
        if not isinstance(value, (float, int)):
            raise TypeError(f'O tipo de dado "{type(value)}" não é válido para representar a carga distribuída qy!')
        else:
            self._qy = value

    def vetor_cargas(self) -> list:
        """Retorna o vetor de cargas do nó respeitadndo a ordem dos graus de liberdade."""
        return [self.qx, self.qy]


class CargaNodal(Carga):
    """Classe que define as propriedades de uma força aplicada em um nó a partir de suas componentes cartesianas."""

    def __init__(self, fx: float = 0, fy: float = 0, mz: float = 0):
        """
        Args:
            fx: Força pontual aplicada na direção x.
            fy: Força pontual aplicada na direção y.
            mz: Momento pontual aplicado na direção z.
        """
        super().__init__(sistema_coord='global')
        self.fx = fx
        self.fy = fy
        self.mz = mz

    def __repr__(self):
        return f'{type(self).__name__}(fx={self.fx}, fy={self.fy}, mz={self.mz})'

    def __eq__(self, other):
        return bool(self.fx == other.fx and self.fy == other.fy and self.mz == other.mz)

    @property
    def fx(self) -> float:
        """Retorna a componente em x da força nodal.

        Raises
            TypeError:
                Se o tipo de dado for diferente de int ou float.

        """
        return self._fx

    @fx.setter
    def fx(self, value):
        if not isinstance(value, (float, int)):
            raise TypeError(f'O tipo de dado "{type(value)}" não é válido para representar a componente x de '
                            f'uma força nodal!')
        else:
            self._fx = value

    @property
    def fy(self) -> float:
        """Retorna a componente em y da força nodal.

        Raises
            TypeError:
                Se o tipo de dado for diferente de int ou float.

        """
        return self._fy

    @fy.setter
    def fy(self, value):
        if not isinstance(value, (float, int)):
            raise TypeError(f'O tipo de dado "{type(value)}" não é válido para representar a componente y de '
                            f'uma força nodal!')
        else:
            self._fy = value

    @property
    def mz(self) -> float:
        """Retorna momento nodal que atua en torno do eixo z.

        Raises
            TypeError:
                Se o tipo de dado for diferente de int ou float.

        """
        return self._mz

    @mz.setter
    def mz(self, value):
        if not isinstance(value, (float, int)):
            raise TypeError(f'O tipo de dado "{type(value)}" não é válido para representar a componente z de '
                            f'um momento nodal!')
        else:
            self._mz = value

    def vetor_cargas(self) -> List[float]:
        """Retorna o vetor de cargas do nó respeitadndo a ordem dos graus de liberdade."""
        return [self.fx, self.fy, self.mz]
