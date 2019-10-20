import numpy as np
from matplotlib import pyplot as plt
from prettytable import PrettyTable

import ame


class Ploter:
    def __init__(self, estrutura: ame.Estrutura):
        self.estrutura = estrutura

    def plotar_graficos_elemento(self, n_elemento: int):
        """Plota os gráficos de esforços de um elemento qualquer."""
        resultado = self.estrutura.elementos[n_elemento - 1].esforcos(self.estrutura.deslocamentos())
        x = resultado[:, 0]
        normal = resultado[:, 1]
        fletor = resultado[:, 2]
        cortante = resultado[:, 3]

        fig, graficos = plt.subplots(3, 1)
        graficos[0].fill_between(x, 0, normal, facecolor='green')
        graficos[0].set_ylabel('Esforço normal (N)')
        graficos[0].set_title(f'Esforços no elemento {n_elemento}')

        graficos[1].fill_between(x, 0, fletor, facecolor='orange')
        graficos[1].set_ylabel('Momento Fletor (Nm)')

        graficos[2].fill_between(x, 0, cortante, facecolor='gray')
        graficos[2].set_ylabel('Esforço cortante (N)')
        graficos[2].set_xlabel('Posição (m)')

        plt.show()

    def imprimir_resultados(self) -> str:
        desloc_estr = self.estrutura.deslocamentos()
        n = self.estrutura.graus_liberdade_por_no()

        s1 = 79 * '=' + '\n'

        r = s1
        r += f'AME {ame.__version__}\n'
        r += f'Desenvolvedor: {ame.__author__}\n'
        r += s1 + '\n'

        desloc = PrettyTable()
        desloc.title = 'DESLOCAMENTOS'
        desloc.field_names = ['Nó', 'dx (mm)', 'dy (mm)', 'rz (rad)']
        for i in range(1, len(self.estrutura.nos) + 1):
            desloc.add_row([i, desloc_estr[n * i - 3] * 1000, desloc_estr[n * i - 2] * 1000, desloc_estr[n * i - 1]])

        r += str(desloc) + '\n\n'

        for elemento in self.estrutura.elementos:
            esforcos = PrettyTable()
            esforcos.title = f'ESFORÇOS NO ELEMENTO {elemento.identificacao}'
            esforcos.field_names = ['Seção', 'x (m)', 'Normal (N)', 'Momento fletor (Nm)', 'Cortante (N)']
            resultado_el = elemento.esforcos(desloc_estr)
            posicao = np.linspace(0, elemento.comprimento(), len(resultado_el))
            for j, x in enumerate(posicao):
                esforcos.add_row([j + 1, f'{x:.3f}', f'{resultado_el[j][1]:.3f}', f'{resultado_el[j][2]:.3f}',
                                  f'{resultado_el[j][3]:.3f}'])
            r += str(esforcos) + '\n\n'

        return r

    def salvar_resultados(self, nome_arquivo: str = 'resultados.txt'):
        with open(file=nome_arquivo, mode='w', encoding='utf-8') as arq:
            arq.write(self.imprimir_resultados())
