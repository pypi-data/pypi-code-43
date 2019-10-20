import unittest

from ame.analise.sistema.material import Material

_DADOS_MATERIAIS = [[1, 20e9, 0.2, 1e-4],
                    [2, 50e9, 0.3, 1.2e-4],
                    [3, 200e9, 0.4, 1.3e-4],
                    [1, 20e9, 0.2, 1e-4],
                    [2, 50e9, 0.3, 1.2e-4]]

_TESTES_METODOS = [8333333333.333334,
                   19230769230.76923,
                   71428571428.57143,
                   8333333333.333334,
                   19230769230.76923]

_TESTES_EQ = {(1, 2): False,
              (1, 1): True,
              (2, 2): True,
              (3, 5): False,
              (1, 1): True}

_ERROS = [[1, 200e9, str(0.2), 1e-4, TypeError, f'O tipo de dado "{str(str)}" não é válido para representar '
                                                'o Coeficiente de Poisson!'],
          [1, 200e9, -0.2, 1e-4, ValueError, f'O valor do Coeficiente de Poisson deve ser maior que 0 e no '
                                             f'máximo 0.5!'],
          [1, 200e9, 0.6, 1e-4, ValueError, f'O valor do Coeficiente de Poisson deve ser maior que 0 e no '
                                            f'máximo 0.5!'],
          [1, str(200e9), 0.2, 1e-4, TypeError, 'O tipo de dado "<class \'str\'>" não é válido para representar o '
                                                'módulo de elasticidade!'],
          [1, -200e9, 0.2, 1e-4, ValueError, 'O valor do módulo de elasticidade deve ser maior que 0!'],
          [1, 200e9, 0.2, str(1e-4), TypeError, 'O tipo de dado "<class \'str\'>" não é válido para representar '
                                                'o coeficiente de dilatação térmica!'],
          [1, 200e9, 0.2, -1e4, ValueError, 'O valor do coeficiente de dilatação térmica deve ser maior que 0!']]


class TestMaterial(unittest.TestCase):
    """Testes da classe Material."""

    def test_material(self):
        # Entrada de dados
        materiais = []
        for i in _DADOS_MATERIAIS:
            materiais.append(Material(*i))

        # Comportamento esperado
        # Teste __eq__
        for chave in _TESTES_EQ:
            self.assertEqual(materiais[chave[0] - 1] == materiais[chave[1] - 1], _TESTES_EQ[chave])

        # Teste métodos
        for m, t in zip(materiais, _TESTES_METODOS):
            self.assertAlmostEqual(m.modulo_cisalhamento(), t)

        # Erros
        for e in _ERROS:
            with self.assertRaisesRegex(e[4], e[5]):
                Material(*e[:4:])
