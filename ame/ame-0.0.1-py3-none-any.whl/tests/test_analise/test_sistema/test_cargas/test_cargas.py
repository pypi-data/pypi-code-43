import unittest

from ame import CargaDistribuida, CargaNodal

# region Carga Nodal

# (fx, fy, mz)
_DADOS_CARGA_NODAL = [[2.8e3, 21.51e3, -15.1e3],
                      [0, 0, 0],
                      [-14.43e3, 11e3, -5e3],
                      [-0.59e3, 0, 0],
                      [2.8e3, 21.51e3, -15.1e3]]

# (vetor_cargas, carga_nula)
_TESTE_METODOS_CARGA_NODAL = [[[2.8e3, 21.51e3, -15.1e3], False],
                              [[0, 0, 0], True],
                              [[-14.43e3, 11e3, -5e3], False],
                              [[-0.59e3, 0, 0], False]]

_TESTE_EQ_CARGA_NODAL = {(0, 4): True,
                         (0, 2): False,
                         (1, 1): True,
                         (2, 3): False,
                         (4, 2): False}

_ERROS_CARGA_NODAL = [[str(2.8e3), 21.51e3, -15.1e3, TypeError, f'O tipo de dado "{str(str)}" não é válido para '
                                                                f'representar a componente x de uma força nodal!'],
                      [2.8e3, str(21.51e3), -15.1e3, TypeError, f'O tipo de dado "{str(str)}" não é válido para '
                                                                f'representar a componente y de uma força nodal!'],
                      [2.8e3, 21.51e3, str(-15.1e3), TypeError, f'O tipo de dado "{str(str)}" não é válido para '
                                                                f'representar a componente z de um momento nodal!']]
# endregion

# region Carga Distribuída

# (qx, qy, sistema_coord)
_DADOS_CARGA_DIST = [[2.8e3, 21.51e3, 'global'],
                     [0, 0, 'local'],
                     [-14.43e3, 11e3, 'local'],
                     [-0.59e3, 0, 'global'],
                     [2.8e3, 21.51e3, 'global']]

# (vetor_cargas, carga_nula)
_TESTE_METODOS_CARGA_DIST = [[[2.8e3, 21.51e3], False],
                             [[0, 0], True],
                             [[-14.43e3, 11e3], False],
                             [[-0.59e3, 0], False],
                             [[2.8e3, 21.51e3], False]]

_TESTE_EQ_CARGA_DIST = {(0, 4): True,
                        (0, 2): False,
                        (1, 1): True,
                        (2, 3): False,
                        (4, 2): False}

_ERROS_CARGA_DIST = [[str(2.8e3), 21.51e3, 'global', TypeError, 'O tipo de dado "<class \'str\'>" não é válido para '
                                                                'representar a carga distribuída qx!'],
                     [2.8e3, str(21.51e3), 'global', TypeError, 'O tipo de dado "<class \'str\'>" não é válido para '
                                                                'representar a carga distribuída qy!']]


# endregion

class TestCargaDistribuida(unittest.TestCase):
    def test_carga_distribuida(self):
        # Entrada de dados
        cargas = []
        for i in _DADOS_CARGA_DIST:
            c = CargaDistribuida(*i)

            self.assertAlmostEqual(c.qx, i[0])
            self.assertAlmostEqual(c.qy, i[1])
            self.assertEqual(c.sistema_coord, i[2])

            cargas.append(c)

        # Comportamento esperado
        # Métodos
        for t, c in zip(_TESTE_METODOS_CARGA_DIST, cargas):
            self.assertEqual(c.vetor_cargas(), t[0])
            self.assertEqual(c.carga_nula(), t[1])

        # __eq__
        for chave in _TESTE_EQ_CARGA_DIST:
            self.assertEqual(cargas[chave[0]] == cargas[chave[1]], _TESTE_EQ_CARGA_DIST[chave])

        # Erros esperados
        for e in _ERROS_CARGA_DIST:
            with self.assertRaisesRegex(e[3], e[4]):
                CargaDistribuida(*e[:3])


class TestCargaNodal(unittest.TestCase):
    def test_carga_nodal(self):
        cargas = []
        for i in _DADOS_CARGA_NODAL:
            c = CargaNodal(*i)

            self.assertAlmostEqual(c.fx, i[0])
            self.assertAlmostEqual(c.fy, i[1])
            self.assertAlmostEqual(c.mz, i[2])
            self.assertEqual(c.sistema_coord, 'global')

            cargas.append(c)

        # Comportamento esperado
        # Métodos
        for t, c in zip(_TESTE_METODOS_CARGA_NODAL, cargas):
            self.assertEqual(c.vetor_cargas(), t[0])
            self.assertEqual(c.carga_nula(), t[1])

        # __eq__
        for chave in _TESTE_EQ_CARGA_NODAL:
            self.assertEqual(cargas[chave[0]] == cargas[chave[1]], _TESTE_EQ_CARGA_DIST[chave])

        # Erros esperados
        for e in _ERROS_CARGA_NODAL:
            with self.assertRaisesRegex(e[3], e[4]):
                CargaNodal(*e[:3])
