from math import sqrt


class Ponto:
    """Define as propriedades de um ponto no espaço 2D."""

    def __init__(self, x, y):
        """Construtor

        Args:
            x: Coordenada x.
            y: Coordenada y.
        """
        self.x = x
        self.y = y

    def __eq__(self, other):
        if self.x == other.x and self.y == other.y:
            return True
        else:
            return False

    def __repr__(self):
        return f'{type(self).__name__}(x={self.x}, y={self.y})'

    @property
    def x(self) -> float:
        """Retorna a coordenada x do ponto.

        Raises:
            TypeError:
                Se o tipo de dado nõ for float ou int.
        """
        return self._x

    @x.setter
    def x(self, value):
        if not isinstance(value, (float, int)):
            raise TypeError(f'O tipo de dado "{type(value)}" não é válido para representar a coordenada x do ponto!')
        else:
            self._x = value

    @property
    def y(self) -> float:
        """Retorna a coordenada y do ponto.

        Raises:
            TypeError:
                Se o tipo de dado nõ for float ou int.
        """
        return self._y

    @y.setter
    def y(self, value):
        if not isinstance(value, (float, int)):
            raise TypeError(f'O tipo de dado "{type(value)}" não é válido para representar a coordenada y do ponto!')
        else:
            self._y = value

    def distancia_x(self, other) -> float:
        """Retorna a distância entre dois pontos em x (other.x-self.x)."""
        return other.x - self._x

    def distancia_y(self, other) -> float:
        """Retorna a distância entre dois pontos em y (other.y-self.y)."""
        return other.y - self._y

    def distancia(self, other) -> float:
        """Retorna a distância em linha reta entre dois pontos.

        Args:
            other (Ponto): Ponto de referência para o cálculo da distância.
        """
        dx = self.distancia_x(other)
        dy = self.distancia_y(other)
        return sqrt(dx ** 2 + dy ** 2)
