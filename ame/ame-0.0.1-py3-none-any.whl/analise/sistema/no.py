from typing import Optional

from ame.analise.elemento_numerado import ElementoNumerado
from ame.analise.geometria.ponto import Ponto
from ame.analise.sistema.apoios import Apoio
from ame.analise.sistema.cargas import CargaNodal
from ame.constantes import GRAUS_LIBERDADE_POR_NO


class No(ElementoNumerado, Ponto):
    """Classe que define as propriedades de um nó."""

    def __init__(self, identificacao: int, x: float, y: float, carga: CargaNodal = None, apoio: Optional[Apoio] = None):
        """Construtor.

        Args:
            identificacao: Número inteiro que identifica o nó.
            x: Coordenada x do nó.
            y: Coordenada y do nó.
            carga: Carga aplicada no nó.
            apoio: Apoio do nó.
        """
        ElementoNumerado.__init__(self, identificacao)
        Ponto.__init__(self, x, y)

        if carga is None:
            self._carga = None
        else:
            self.carga = carga

        if apoio is None:
            self._apoio = None
        else:
            self.apoio = apoio

        self._graus_liberdade = None

    def __eq__(self, other):
        return bool(self.identificacao == other.identificacao and self.x == other.x and self.y == other.y and
                    self.carga == other.carga and self.apoio == other.apoio)

    def __repr__(self):
        return f'{type(self).__name__}(id={self.identificacao}, x={self.x}, y={self.y})'

    # region Properties
    @property
    def carga(self) -> CargaNodal:
        """Retorna a carga nodal atuante no nó."""
        return self._carga

    @carga.setter
    def carga(self, value):
        if not isinstance(value, CargaNodal):
            raise TypeError(f'O tipo de dado "{type(value)}" não é válido para representar a carga nodal!')
        else:
            self._carga = value

    @property
    def apoio(self) -> Optional[Apoio]:
        """Retorna o apoio que atua no nó, caso este apoio exista."""
        return self._apoio

    @apoio.setter
    def apoio(self, value):
        if not isinstance(value, Apoio):
            raise TypeError(f'O tipo de dado "{type(value)}" não é válido para representar um apoio!')
        else:
            self._apoio = value

    # endregion

    def graus_liberdade(self, tipo_elemento: str) -> list:
        """Retorna um vetor com os graus de liberdade do nó.

        Args:
            tipo_elemento: Tipo de elemento que o nó está compondo.
        """
        try:
            n = GRAUS_LIBERDADE_POR_NO[tipo_elemento]
        except KeyError:
            raise KeyError(f'O tipo de elemento "{tipo_elemento}" não é válido!')

        gl = []
        for i in range(1, n + 1):
            gl.append(n * self.identificacao - (n - i))

        return gl
