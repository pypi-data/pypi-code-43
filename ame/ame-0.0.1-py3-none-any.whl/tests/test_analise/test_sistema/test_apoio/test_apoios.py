import unittest

from ame import Apoio

_APOIOS = [[True, True, True],
           [False, False, False],
           [True, False, False],
           [True, True, True]]

_TESTES_METODOS = [True,
                   False,
                   False,
                   True]

_TESTE_EQ = {(0, 3): True,
             (0, 0): True,
             (0, 1): False,
             (2, 3): False}

_ERROS = [[str(True), True, True, TypeError, f'O tipo de dado "{str(str)}" não é válido para representar a '
                                             f'deslocabilidade do grau de liberdade dx!'],
          [True, str(True), True, TypeError, f'O tipo de dado "{str(str)}" não é válido para representar a '
                                             f'deslocabilidade do grau de liberdade dy!'],
          [True, True, str(True), TypeError, f'O tipo de dado "{str(str)}" não é válido para representar a '
                                             f'deslocabilidade do grau de liberdade rz!']]


class TestApoio(unittest.TestCase):
    def test_apoios(self):
        # Entrada de dados
        apoios = []
        for i in _APOIOS:
            apoios.append(Apoio(*i[1::]))

        # Comportamento esperado
        for i, t in enumerate(_TESTES_METODOS):
            self.assertIs(apoios[i].apoio_livre(), t)

        for chave in _TESTE_EQ:
            self.assertEqual(apoios[chave[0]] == apoios[chave[1]], _TESTE_EQ[chave])

        # Erros
        for e in _ERROS:
            with self.assertRaisesRegex(e[3], e[4]):
                Apoio(*e[:3:])


if __name__ == '__main__':
    unittest.main()
