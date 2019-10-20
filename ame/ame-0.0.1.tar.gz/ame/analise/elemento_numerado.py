class ElementoNumerado:
    """Classe abstrata que representa um elemento que deve possuir identificação única no sistema.

    Por exemplo: Nós e barras.
    """

    def __init__(self, identificacao: int):
        self.identificacao = identificacao

    # region Properties

    @property
    def identificacao(self) -> int:
        """Retorna a identificação do elemento de numeração única. Inicia em 1."""
        return self._identificacao

    @identificacao.setter
    def identificacao(self, value):
        if not isinstance(value, int):
            raise TypeError(f'O tipo de dado "{type(value)}" não é válido para representar a identificação de '
                            f'um elemento numerado!')
        elif not value >= 0:
            raise ValueError(f'O elemento numerado deve ser identificado por um número inteiro não menor que 0!')
        else:
            self._identificacao = value

    # endregion
