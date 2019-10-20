from unittest import TestCase

from ame import Ponto

# (x, y)
_COORDENADAS_PONTOS = ((5.11, 61.9),
                       (-15.7, 63.5),
                       (21.21, -9.69))
# {(p1, p2): (dx, dy, dt)}
_TESTES = {(0, 1): (-20.81, 1.6, 20.871418255595376),
           (1, 2): (36.91, -73.19, 81.97026412059436),
           (2, 0): (-16.1, 71.59, 73.3780491700345),
           (0, 2): (16.1, -71.59, 73.3780491700345)}

# (x, y, tipo de erro, mensagem do erro)
_ERROS = (('3.14', 0, TypeError, f'O tipo de dado "{str(str)}" não é válido para representar a '
                                 'coordenada x do ponto!'),
          (0, '3.14', TypeError, f'O tipo de dado "{str(str)}" não é válido para representar a '
                                 'coordenada y do ponto!'))


class TestPonto(TestCase):

    def test_ponto(self):
        # Entrada de dados
        pontos = []
        for i in _COORDENADAS_PONTOS:
            p = Ponto(*i)
            self.assertAlmostEqual(p.x, i[0])
            self.assertAlmostEqual(p.y, i[1])
            pontos.append(p)

        # Métodos
        for i, t in enumerate(_TESTES):
            self.assertAlmostEqual(pontos[t[0]].distancia_x(pontos[t[1]]), _TESTES[t][0])
            self.assertAlmostEqual(pontos[t[0]].distancia_y(pontos[t[1]]), _TESTES[t][1])
            self.assertAlmostEqual(pontos[t[0]].distancia(pontos[t[1]]), _TESTES[t][2])

        # Erros
        for e in _ERROS:
            with self.assertRaisesRegex(*e[2::]):
                Ponto(*e[:2:])
