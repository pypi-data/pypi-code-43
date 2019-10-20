class Apoio:
    """Define as propriedades de um apoio de nós."""

    def __init__(self, dx: bool = True, dy: bool = True, rz: bool = True):
        """Construtor.

        Deve-se marcar True para a deslocabilidade que for livre e False para a que for restrita.

        Args:
            dx: Deslocabilidade do apoio em x.
            dy: Deslocabilidade do apoio em y.
            rz: Rotação do apoio em torno de z.
        """
        self.dx = dx
        self.dy = dy
        self.rz = rz

    def __repr__(self):
        return f'{type(self).__name__}(dx={self.dx}, dy={self.dy}, rz={self.rz})'

    def __eq__(self, other):
        """Teste de igualdade entre instâncias da classe.

        Args:
            other(Apoio): Instância de referência.
        """
        return bool(self.dx == other.dx and self.dy == self.dy and self.rz == other.rz)

    # region Propriedades

    @property
    def dx(self) -> bool:
        """Retorna True se dx for livre e False caso contrário.

        Raises:
            TypeError:
                Se o tipo de dado não for bool.
        """
        return self._dx

    @dx.setter
    def dx(self, value):
        if not isinstance(value, bool):
            raise TypeError(f'O tipo de dado "{type(value)}" não é válido para representar a deslocabilidade do grau '
                            f'de liberdade dx!')
        else:
            self._dx = value

    @property
    def dy(self) -> bool:
        """Retorna True se dy for livre e False caso contrário.

        Raises:
            TypeError:
                Se o tipo de dado não for bool.
        """
        return self._dy

    @dy.setter
    def dy(self, value):
        if not isinstance(value, bool):
            raise TypeError(
                f'O tipo de dado "{type(value)}" não é válido para representar a deslocabilidade do grau '
                f'de liberdade dy!')
        else:
            self._dy = value

    @property
    def rz(self) -> bool:
        """Retorna True se rz for livre e False caso contrário.

        Raises:
            TypeError:
                Se o tipo de dado não for bool.
        """
        return self._rz

    @rz.setter
    def rz(self, value):
        if not isinstance(value, bool):
            raise TypeError(
                f'O tipo de dado "{type(value)}" não é válido para representar a deslocabilidade do grau '
                f'de liberdade rz!')
        else:
            self._rz = value

        # endregion

    def apoio_livre(self) -> bool:
        """Retorna True se o apoio for completamente livre e False caso contrário."""
        return self.dx == self.dy == self.rz == True
