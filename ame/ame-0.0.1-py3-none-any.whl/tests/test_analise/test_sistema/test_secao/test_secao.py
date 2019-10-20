import unittest

from ame import Secao

_DADOS_SECOES = [[1, 1.3796e-3, 8.1052e-6, 0.1],
                 [2, 1.3796e-3, 8.1052e-6, 0.1],
                 [3, 10.96e-3, 15.52e-6, 0.25],
                 [4, 8.96e-3, None, 0.25],
                 [5, 3.64e-3, 15.52e-6, None]]

_TEST_EQ = {(1, 1): True,
            (1, 2): False,
            (3, 3): True,
            (4, 2): False}

_ERROS = [[1, str(1e-3), 8e-6, 0.1, TypeError, 'O tipo de dado "<class \'str\'>" não é válido para '
                                               'representar a área da seção transversal!'],
          [1, 0, 8e-6, 0.1, ValueError, 'A área da seção transversal deve ser maior que 0!'],
          [1, 1.3e-3, str(8e-3), 0.1, TypeError, 'O tipo de dado "<class \'str\'>" não é válido para '
                                                 'representar o momento de inércia da seção em relação ao eixo z!'],
          [1, 1.3e-3, 0, 0.1, ValueError, 'O momento de inércia em relação ao eixo z da seção deve ser maior que 0!'],
          [1, 1.3e-3, 8e-6, str(0.1e-3), TypeError, 'O tipo de dado "<class \'str\'>" não é válido para '
                                                    'representar a posição da linha neutra em relação ao '
                                                    'eixo z da seção!'],
          [1, 1.3e-3, 8e-6, 0, ValueError, 'A posição da linha neutra da seção em relação à origem do eixo '
                                           'z deve ser maior que 0!']]


class TestSecao(unittest.TestCase):

    # region Propriedades
    def test_secao(self):
        secoes = []
        for i in _DADOS_SECOES:
            secoes.append(Secao(*i))

        # Comportamento esperado
        for i, s in zip(_DADOS_SECOES, secoes):
            self.assertEqual(s.identificacao, i[0])
            self.assertAlmostEqual(s.area, i[1])
            self.assertAlmostEqual(s.inercia_z, i[2])
            self.assertAlmostEqual(s.linha_neutra_z, i[3])

        # __eq__
        for chave in _TEST_EQ:
            self.assertEqual(secoes[chave[0] - 1] == secoes[chave[1] - 1], _TEST_EQ[chave])

        # Erros esperados
        for e in _ERROS:
            with self.assertRaisesRegex(e[4], e[5]):
                Secao(*e[:4:])

    # endregion


if __name__ == '__main__':
    unittest.main()
