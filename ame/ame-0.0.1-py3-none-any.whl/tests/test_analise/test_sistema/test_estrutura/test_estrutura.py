import unittest
from pathlib import Path
from ame import No, Apoio, Material, Secao, CargaNodal, CargaDistribuida, Estrutura, PP2
from typing import List, Tuple
import numpy as np

PP = 'PP2'

ARQS = [(PP, 'pp.ame')]

# region Pórtico Plano
APOIOS = {PP: [Apoio(False, False, True),
               Apoio(False, False, False)]}

MATERIAIS = {PP: [Material(1, 205e9, 0.2, 1.2e-5),
                  Material(2, 25e9, 0.2, 1e-5)]}

SECOES = {PP: [Secao(1, 1.3796e-3, 8.1052e-6, 0.1),
               Secao(2, 2.3758e-3, 2.3952e-5, 0.1)]}

CARGAS_NODAIS = {PP: [CargaNodal(-5e3, 1e3, 13e3)]}

CARGAS_DIST = [CargaDistribuida(1e3, -2e3, 'local'),
               CargaDistribuida(0.0, 4e3, 'local'),
               CargaDistribuida(1.5e3, -0.5e3)]

NOS = {PP: [No(1, 0.0, 0.0, CargaNodal(), APOIOS[PP][0]),
            No(2, 4.0, 0.0, CargaNodal(), APOIOS[PP][1]),
            No(3, 0, 2, CargaNodal(), Apoio()),
            No(4, 4, 4, CARGAS_NODAIS[PP][0], Apoio()),
            No(5, 5, 5, CargaNodal(), Apoio())]}

ELEMENTOS = {PP: [PP2(1, NOS[PP][0], NOS[PP][2], MATERIAIS[PP][1], SECOES[PP][0], CargaDistribuida()),
                  PP2(2, NOS[PP][2], NOS[PP][3], MATERIAIS[PP][0], SECOES[PP][0], CARGAS_DIST[0]),
                  PP2(3, NOS[PP][1], NOS[PP][3], MATERIAIS[PP][0], SECOES[PP][1], CARGAS_DIST[1]),
                  PP2(4, NOS[PP][3], NOS[PP][4], MATERIAIS[PP][0], SECOES[PP][0], CARGAS_DIST[2])]}


# endregion


def estruturas() -> List[Tuple[str, Estrutura]]:
    ests = []
    for i in ARQS:
        arq = str(Path(__file__).parent.parent.parent.parent.joinpath(f'exemplos\\{i[1]}'))
        ests.append((i[0], Estrutura(arq)))
    return ests


class TestEstrutura(unittest.TestCase):

    def test_leitura_nos(self):
        for e in estruturas():
            for no1, no2 in zip(e[1].nos, NOS[e[0]]):
                self.assertEqual(no1, no2)

    def test_leitura_materiais(self):
        for e in estruturas():
            for mat1, mat2 in zip(e[1].materiais, MATERIAIS[e[0]]):
                self.assertEqual(mat1, mat2)

    def test_leitura_secoes(self):
        for e in estruturas():
            for sec1, sec2 in zip(e[1].secoes, SECOES[e[0]]):
                self.assertEqual(sec1, sec2)

    def test_leitura_elementos(self):
        for e in estruturas():
            for el1, el2 in zip(e[1].elementos, ELEMENTOS[e[0]]):
                self.assertEqual(el1, el2)

    def test_graus_liberdade_por_no(self):
        dados = {PP: 3}

        for e in estruturas():
            self.assertEqual(e[1].graus_liberdade_por_no(), dados[e[0]])

    def test_graus_liberdade_impedidos(self):
        dados = {PP: [1, 2, 4, 5, 6]}

        for e in estruturas():
            self.assertEqual(e[1].graus_liberdade_impedidos(), dados[e[0]])

    def test_graus_liberdade_livres(self):
        dados = {PP: [3, 7, 8, 9, 10, 11, 12, 13, 14, 15]}

        for e in estruturas():
            self.assertEqual(e[1].graus_liberdade_livres(), dados[e[0]])

    def test_graus_liberdade(self):
        dados = {PP: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]}

        for e in estruturas():
            self.assertEqual(e[1].graus_liberdade(), dados[e[0]])

    def test_graus_matriz_rigidez(self):
        dados = {PP: np.array([[405260.0, 303945.0, 0.0, 202630.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                               [303945.0, 50940551.35514407, 25206841.94181896, 81022.52849385509, -50636606.35514407,
                                -25206841.94181896, -222922.4715061449, 0.0, 0.0, 0.0],
                               [0.0, 25206841.94181896, 30071343.442415625, 445844.9430122898, -25206841.94181896,
                                -12826343.442415625, 445844.9430122898, 0.0, 0.0, 0.0],
                               [202630.0, 81022.52849385509, 445844.9430122898, 1891409.8100409661, 222922.4715061449,
                                -445844.9430122898, 743074.9050204831, 0.0, 0.0, 0.0],
                               [0.0, -50636606.35514407, -25206841.94181896, 222922.4715061449, 155073237.93391955,
                                121673391.0046604, -1460481.2864608746, -103515976.5787755, -96466549.06284145,
                                -3524713.7579670195],
                               [0.0, -25206841.94181896, -12826343.442415625, -445844.9430122898, 121673391.0046604,
                                238102070.02119112, 3078868.8149547298, -96466549.06284145, -103515976.5787755,
                                3524713.7579670195],
                               [0.0, -222922.4715061449, 445844.9430122898, 743074.9050204831, -1460481.2864608746,
                                3078868.8149547298, 11095928.153996993, 3524713.7579670195, -3524713.7579670195,
                                2349809.171978014],
                               [0.0, 0.0, 0.0, 0.0, -103515976.5787755, -96466549.06284145, 3524713.7579670195,
                                103515976.5787755, 96466549.06284145, 3524713.7579670195],
                               [0.0, 0.0, 0.0, 0.0, -96466549.06284145, -103515976.5787755, -3524713.7579670195,
                                96466549.06284145, 103515976.5787755, -3524713.7579670195],
                               [0.0, 0.0, 0.0, 0.0, -3524713.7579670195, 3524713.7579670195, 2349809.171978014,
                                3524713.7579670195, -3524713.7579670195, 4699618.343956028]])}

        for e in estruturas():
            self.assertTrue(np.array_equal(e[1].matriz_rigidez().toarray(), dados[e[0]]))

    def test_forcas_nodais_aplicadas(self):
        dados = {PP: np.array([0., 0., 0., 0., 0., 0., 0., 0., 0., -5000., 1000., 13000., 0., 0., 0.])}

        for e in estruturas():
            self.assertTrue(np.array_equal(e[1].forcas_nodais_aplicadas(), dados[e[0]]))

    def test_forcas_nodais_totais(self):
        dados = {PP: np.array([0.0, 0.0, 0.0, -8000.0, 0.0, 5333.333333333333, 4000.0, -3000.0, -3333.333333333334,
                               -7939.339828220179, -2353.5533905932734, 10764.297739604484, 1060.6601717798212,
                               -353.55339059327366, 235.70226039551585])}

        for e in estruturas():
            self.assertTrue(np.array_equal(e[1].forcas_nodais_totais(), dados[e[0]]))

    def test_deslocamentos(self):
        dados = {PP: np.array([0.0, 0.0, 0.010756869758238894, 0.0, 0.0, 0.0, -0.012364850776379367,
                               -0.0004058289346022399, -0.0029664633519087386, -0.012689919032664103,
                               1.0606240535392592e-05, 0.005536676195008725, -0.017923906367813363,
                               0.005248129418523512, 0.005135448277088667])}

        for e in estruturas():
            self.assertTrue(np.array_equal(e[1].deslocamentos(), dados[e[0]]))

    def test_nos_apoiados(self):
        dados = {PP: (NOS[PP][0],
                      NOS[PP][1])}

        for e in estruturas():
            self.assertTrue(e[1].nos_apoiados() == dados[e[0]])

    def test_nos_carregados(self):
        dados = {PP: (NOS[PP][3],)}

        for e in estruturas():
            self.assertTrue(e[1].nos_carregados() == dados[e[0]])

    def test_elementos_carregados(self):
        dados = {PP: (ELEMENTOS[PP][1],
                      ELEMENTOS[PP][2],
                      ELEMENTOS[PP][3])}

        for e in estruturas():
            self.assertTrue(e[1].elementos_carregados() == dados[e[0]])


if __name__ == '__main__':
    unittest.main()
