import unittest

from ame import No, CargaNodal, Apoio

# (x, y)
_ENTRADA_NOS = ((1, 5.11, 61.9, CargaNodal(10, 10, 10), Apoio(True, False, True)),
                (2, -15.7, 63.5, CargaNodal(10, 20, 10), Apoio(True, True, True)),
                (3, 21.21, -9.69, CargaNodal(10, 15, 10), Apoio(False, False, True)),
                (1, 5.11, 61.9, CargaNodal(10, 10, 10), Apoio(True, False, True)))

# graus_liberdade
_TESTES_METODOS = {'PP2': [[1, 2, 3],
                           [4, 5, 6],
                           [7, 8, 9],
                           [1, 2, 3]],
                   'TP2': [[1, 2],
                           [3, 4],
                           [5, 6],
                           [1, 2]]}

_TESTES_EQ = {(1, 1): True,
              (4, 4): True,
              (1, 2): False,
              (2, 3): False}

_ERROS = [[1, 5.11, 61.9, 'CargaNodal(10, 10, 10)', Apoio(True, False, True), TypeError,
           f'O tipo de dado "{str(str)}" não é válido para representar a carga nodal!'],
          [1, 5.11, 61.9, CargaNodal(10, 10, 10), 'Apoio(True, False, True)', TypeError,
           f'O tipo de dado "{str(str)}" não é válido para representar um apoio!']]


class TestNo(unittest.TestCase):

    def test_no(self):
        nos = []
        for i in _ENTRADA_NOS:
            no = No(*i)

            self.assertAlmostEqual(no.identificacao, i[0])
            self.assertAlmostEqual(no.x, i[1])
            self.assertAlmostEqual(no.y, i[2])
            self.assertEqual(no.carga, i[3])
            self.assertEqual(no.apoio, i[4])

        # Teste métodos
        for tipo_el in _TESTES_METODOS:
            for i, no in enumerate(nos):
                self.assertEqual(no.graus_liberdade(tipo_el), _TESTES_METODOS[tipo_el][i])

        # Testes erros
        for e in _ERROS:
            with self.assertRaisesRegex(e[5], e[6]):
                No(*e[:5:])


if __name__ == '__main__':
    unittest.main()
