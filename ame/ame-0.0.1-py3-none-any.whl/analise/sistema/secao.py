from typing import Optional

from ame.analise.elemento_numerado import ElementoNumerado


class Secao(ElementoNumerado):
    """Classe que implementa as propriedades de uma seção transversal de um elemento."""

    def __init__(self, identificacao: int, area: float, inercia_z: Optional[float] = None,
                 linha_neutra_z: Optional[float] = None):
        """
        Args:
            area: Área bruta da seção transversal da seção. 
            inercia_z: Momento de inércia em relação à origem do eixo z.
            linha_neutra_z: Posição da linha neutra em relação ao eixo z.
        """
        super().__init__(identificacao)
        self.area = area

        if linha_neutra_z is None:
            self._linha_neutra_z = None
        else:
            self.linha_neutra_z = linha_neutra_z

        if inercia_z is None:
            self._inercia_z = None
        else:
            self.inercia_z = inercia_z

    def __eq__(self, other):
        """Definição de igualdade entre seções.

        Args:
            other(Secao): Instância de referência.
        """
        return bool(self.identificacao == other.identificacao and self.area == other.area and
                    self.inercia_z == other.inercia_z and self.linha_neutra_z == other.linha_neutra_z)

    def __repr__(self):
        return f'SEÇÃO {self.identificacao}:\n' \
               f'área: {self.area}\n' \
               f'inércia z: {self.inercia_z}\n' \
               f'linha neutra z: {self.linha_neutra_z}\n'

    # region Properties

    @property
    def area(self) -> float:
        """Retorna a área bruta da seção transversal.

        Raises
            TypeError
                Se o tipo de dado não for int ou float.
            ValueError
                Se a área da seção não for maior que 0.
        """
        return self._area

    @area.setter
    def area(self, value):
        if not isinstance(value, (float, int)):
            raise TypeError(f'O tipo de dado "{type(value)}" não é válido para representar a área da seção '
                            f'transversal!')
        elif not value > 0:
            raise ValueError(f'A área da seção transversal deve ser maior que 0!')
        else:
            self._area = value

    @property
    def linha_neutra_z(self) -> Optional[float]:
        """Posição da linha neutra em relação à origem do eixo x.

        Raises
            TypeError
                Se o tipo de dado não for float ou int.
            ValueError
                Se a posição da linha neutra não for maior que 0.
        """
        return self._linha_neutra_z

    @linha_neutra_z.setter
    def linha_neutra_z(self, value: float):
        if not isinstance(value, (int, float)):
            raise TypeError(f'O tipo de dado "{type(value)}" não é válido para representar a posição da linha '
                            f'neutra em relação ao eixo z da seção!')
        elif not value > 0:
            raise ValueError(f'A posição da linha neutra da seção em relação à origem do eixo z deve ser maior que 0!')
        else:
            self._linha_neutra_z = value

    @property
    def inercia_z(self) -> Optional[float]:
        """Momento de inércia em relação ao eixo z da seção.

        Raises
            TypeError
                Se o tipo de dado não for float ou int.
            ValueError
                Se o momento de inércia da seção não for maior que 0.
        """
        return self._inercia_z

    @inercia_z.setter
    def inercia_z(self, value: float):
        if not isinstance(value, (int, float)):
            raise TypeError(f'O tipo de dado "{type(value)}" não é válido para representar o momento de inércia '
                            f'da seção em relação ao eixo z!')
        elif not value > 0:
            raise ValueError(f'O momento de inércia em relação ao eixo z da seção deve ser maior que 0!')
        else:
            self._inercia_z = value

    # endregion
