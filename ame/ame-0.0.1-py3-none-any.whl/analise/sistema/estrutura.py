from typing import List, Tuple

import numpy as np
from scipy import sparse
from scipy.sparse.linalg import spsolve

from ame.analise.sistema.apoios import Apoio
from ame.analise.sistema.cargas import CargaNodal, CargaDistribuida
from ame.analise.sistema.elementos import ElementoBarra, PP2
from ame.analise.sistema.material import Material
from ame.analise.sistema.no import No
from ame.analise.sistema.secao import Secao
from ame.constantes import CONSTANTES_LEITURA as CTES
from ame.constantes import TIPOS_ELEMENTOS, GRAUS_LIBERDADE_POR_NO, SISTEMAS_COORDENADAS


class Estrutura:
    """Define as propriedades de uma estrutura."""

    def __init__(self, arquivo_dados: str):
        """Construtor.

        Args:
            arquivo_dados: Endereço do arquivo de dados.
        """
        self._nos = []
        self._materiais = []
        self._elementos = []
        self._secoes = []
        self._apoios = []
        self._tipo_estrutura = None
        self._tipo_elemento = None

        self.arquivo_dados = arquivo_dados

        self._carregar_dados_entrada()

    def __repr__(self):
        txt = 'ESTRUTURA:\n'

        txt += '\tNÓS:\n'
        for i in self.nos:
            apx = 'livre' if i.apoio.dx is True else 'impedido'
            apy = 'livre' if i.apoio.dy is True else 'impedido'
            apz = 'livre' if i.apoio.rz is True else 'impedido'
            txt += f'\t\tNó {i.identificacao}: \n' \
                   f'\t\t\tPosição: x={i.x}m, y={i.y}m\n' \
                   f'\t\t\tCarga nodal: fx={i.carga.fx}N, fy={i.carga.fy}N, mz={i.carga.mz}Nm\n' \
                   f'\t\t\tApoios: dx={apx}, dy={apy}, mz={apz}\n'

        txt += '\tMATERIAIS:\n'
        for i in self.materiais:
            txt += f'\t\tMaterial {i.identificacao}:\n' \
                   f'\t\t\tE: {i.mod_elastic:.2e}Pa\n' \
                   f'\t\t\tPoisson: {i.poisson}\n' \
                   f'\t\t\tAlpha: {i.coef_dilat_termica:.2e}°C^-1\n' \
                   f'\t\t\tG: {i.modulo_cisalhamento():.2e}Pa\n'

        txt += '\tSEÇÕES:\n'
        for i in self.secoes:
            txt += f'\t\tSeção {i.identificacao}:\n' \
                   f'\t\t\tÁrea={i.area:.3e}m^2\n' \
                   f'\t\t\tInércia z={i.inercia_z:.3e}m^4\n' \
                   f'\t\t\tLinha neutra: {i.linha_neutra_z}m\n'

        txt += '\tELEMENTOS:\n'
        for i in self.elementos:
            txt += f'\t\tElemento {i.identificacao}:\n' \
                   f'\t\t\tComprimento: {i.comprimento():.2f}m\n' \
                   f'\t\t\tNó inicial: {i.no_inicial.identificacao}\n' \
                   f'\t\t\tNó final: {i.no_final.identificacao}\n' \
                   f'\t\t\tMaterial: {i.material.identificacao}\n' \
                   f'\t\t\tSeção: {i.secao.identificacao}\n' \
                   f'\t\t\tCargas: qx={i.carga.qx}N/m, qy={i.carga.qy}N/m\n' \
                   f'\t\t\tSistema de coordenadas das cargas: {i.carga.sistema_coord}\n'

        return txt

    # region Propriedades
    @property
    def arquivo_dados(self) -> str:
        """Retorna o endereço do arquivo de dados."""
        return self._arquivo_dados

    @arquivo_dados.setter
    def arquivo_dados(self, value):
        if not isinstance(value, str):
            raise TypeError(f'O tipo de dados "{type(value)}" não é capaz de representar o endereço do '
                            f'arquivos que contém os dados de entrada!')
        else:
            self._arquivo_dados = value

    @property
    def tipo_estrutura(self) -> str:
        """Retorna o tipo de estrutura."""
        return self._tipo_estrutura

    @property
    def tipo_elemento(self) -> str:
        """Retorna o tipo de elemento que compõe a estrutura."""
        return self._tipo_elemento

    @property
    def nos(self) -> List[No]:
        """Retorna a lista de nós que compõem a estrutura."""
        return self._nos

    @property
    def materiais(self) -> List[Material]:
        """Retorna a lista de materiais dos elementos da estrutura."""
        return self._materiais

    @property
    def elementos(self) -> List[PP2]:
        """Retorna a lista de elementos que compõem a estrutura."""
        return self._elementos

    @property
    def secoes(self) -> List[Secao]:
        """Retorna a lista de seções que compõem os elementos."""
        return self._secoes

    # endregion

    # region Métodos referentes à leitura de dados.
    def _ler_tipo_estrutura(self):
        """Lê o arquivo de dados e armazena o tipo de esturura em `self.tipo_estrutura`."""
        with open(file=self.arquivo_dados, mode='r', encoding='utf-8') as arq:
            texto_arq = arq.readlines()
            for i, linha in enumerate(texto_arq):
                if CTES[0] in linha:
                    self._tipo_estrutura = texto_arq[i + 1].split()[0]
                    break

    def _ler_tipo_elemento(self):
        """Lê o arquivo de dados e armazena o tipo de elemento em `self.tipo_elemento`."""
        with open(file=self.arquivo_dados, mode='r', encoding='utf-8') as arq:
            texto_arq = arq.readlines()
            for i, linha in enumerate(texto_arq):
                if CTES[1] in linha:
                    self._tipo_elemento = texto_arq[i + 1].split()[0]
                    break

    def _ler_nos(self):
        """Lê os nós da estrutura, cria as instâncias de No e as armazena em `self.nos`.

        Raises:
            TypeError:
                Se o tipo de dado passado para a composição do nó não for numérico.
            TypeError:
                Se a numeração do nó lido no momento não seguir uma ordem crescente ou se o dado passado não
                for numérico.
        """
        # Serão adicionados apoios livres e cargas nulas a todos os nós.
        apoio_livre = Apoio()
        carga_nula = CargaNodal()

        with open(file=self.arquivo_dados, mode='r', encoding='utf-8') as arq:
            texto_arq = arq.readlines()
            for i, linha in enumerate(texto_arq):
                # Variáveis auxiliares
                ct1 = CTES[2][0].lower().split()
                ct2 = CTES[2][1].lower().split()
                lin = linha.lower().split()
                txt = texto_arq[i + 1].lower().split()

                if ''.join(ct1) in ''.join(lin) and ''.join(ct2) in ''.join(txt):
                    j = i + 2
                    dados_txt = texto_arq[j].split()
                    dados = len(dados_txt) * [0]
                    id_no = 0

                    # Verificação dos dados de entrada.
                    while bool(dados_txt):
                        try:
                            dados[0] = int(dados_txt[0])
                            dados[1::] = list(map(float, dados_txt[1::]))
                        except ValueError:
                            raise TypeError('No arquivo de entrada de dados, todos os dados referentes a '
                                            'um nó devem ser valores numéricos!')
                        id_no += 1
                        if not id_no == dados[0]:
                            raise TypeError(f'A numeração do nó {id_no} está inconsistente!')

                        self._adicionar_no(No(dados[0], dados[1], dados[2], carga_nula, apoio_livre))

                        # Continuidade na iteração
                        j += 1
                        dados_txt = texto_arq[j].split()
                    break

    def _ler_materiais(self):
        """Lê os nós da estrutura e os armazena em `self.nos`.

        Raises:
            TypeError:
                Se o tipo de dado passado para a composição do material não for numérico.
            TypeError:
                Se a numeração do material lido no momento não seguir uma ordem crescente ou se o dado passado não
                for numérico.
        """
        with open(file=self.arquivo_dados, mode='r', encoding='utf-8') as arq:
            texto_arq = arq.readlines()
            for i, linha in enumerate(texto_arq):
                # Variáveis auxiliares.
                ct1 = CTES[3][0].lower().split()
                ct2 = CTES[3][1].lower().split()
                lin = linha.lower().split()
                txt = texto_arq[i + 1].lower().split()

                if ''.join(ct1) in ''.join(lin) and ''.join(ct2) in ''.join(txt):
                    j = i + 2
                    dados_txt = texto_arq[j].split()
                    dados = len(dados_txt) * [0]
                    id_mat = 0

                    # Verificação da entrada de dados.
                    while bool(dados_txt):
                        try:
                            dados[0] = int(dados_txt[0])
                            dados[1::] = list(map(float, dados_txt[1::]))
                        except ValueError:
                            raise TypeError('No arquivo de entrada de dados, todos os dados referentes a '
                                            'um material devem ser valores numéricos!')

                        id_mat += 1
                        if not id_mat == dados[0]:
                            raise TypeError(f'A numeração do material {id_mat} está inconsistente!')

                        self._adicionar_material(Material(*dados))

                        # Continuação das iterações.
                        j += 1
                        dados_txt = texto_arq[j].split()
                    break

    def _ler_secoes_transversais(self):
        """Lê os nós da estrutura e os armazena em `self.secoes`.

        Raises:
            TypeError:
                Se o tipo de dado passado para a composição da seção não for numérico.
            TypeError:
                Se a numeração da seção lida no momento não seguir uma ordem crescente ou se o dado passado não
                for numérico.
        """
        with open(file=self.arquivo_dados, mode='r', encoding='utf-8') as arq:
            texto_arq = arq.readlines()
            for i, linha in enumerate(texto_arq):
                # Variáveis auxiliares.
                ct1 = CTES[4][0].lower().split()
                ct2 = CTES[4][1].lower().split()
                lin = linha.lower().split()
                txt = texto_arq[i + 1].lower().split()

                if ''.join(ct1) in ''.join(lin) and ''.join(ct2) in ''.join(txt):
                    j = i + 2
                    dados_txt = texto_arq[j].split()
                    dados = len(dados_txt) * [0]
                    id_sec = 0

                    # Verificação da entrada de dados.
                    while bool(dados_txt):
                        try:
                            dados[0] = int(dados_txt[0])
                            dados[1::] = list(map(float, dados_txt[1::]))
                        except ValueError:
                            raise TypeError('No arquivo de entrada de dados, todos os dados referentes a '
                                            'uma seção transversal devem ser valores numéricos!')
                        id_sec += 1
                        if not id_sec == dados[0]:
                            raise TypeError(f'A numeração da seção {id_sec} está inconsistente!')

                        self._adicionar_secao_transversal(Secao(*dados))

                        # Continuação das iterações.
                        j += 1
                        dados_txt = texto_arq[j].split()
                    break

    def _ler_elementos(self):
        """Cria os elementos a partir do arquivo de dados. Armazena os elementos na lista `self.elementos`.

        Raises:
            TypeError:
                Se o tipo de dado passado para a composição da seção não for numérico.
            TypeError:
                Se a numeração da seção lida no momento não seguir uma ordem crescente ou se o dado passado não
                for numérico.
        """
        # Carga nula
        carga_nula = CargaDistribuida()

        with open(file=self.arquivo_dados, mode='r', encoding='utf-8') as arq:
            texto_arq = arq.readlines()
            for i, linha in enumerate(texto_arq):
                # Variáveis auxiliares.
                ct1 = CTES[5][0].lower().split()
                ct2 = CTES[5][1].lower().split()
                lin = linha.lower().split()
                txt = texto_arq[i + 1].lower().split()

                if ''.join(ct1) in ''.join(lin) and ''.join(ct2) in ''.join(txt):
                    j = i + 2
                    dados_txt = texto_arq[j].split()

                    # Verificação da entrada de dados
                    while len(dados_txt) == len(txt):
                        try:
                            dados = list(map(int, dados_txt))
                        except ValueError:
                            raise TypeError('No arquivo de entrada de dados, todos os valores referentes aos elementos '
                                            'devem ser números inteiros!')
                        entrada = [dados[0],
                                   self.nos[dados[1] - 1],
                                   self.nos[dados[2] - 1],
                                   self.materiais[dados[3] - 1],
                                   self.secoes[dados[4] - 1]]

                        if self.tipo_elemento == TIPOS_ELEMENTOS[0]:  # PP2
                            entrada.append(carga_nula)
                            self._adicionar_elemento(PP2(*entrada))
                        else:
                            raise ValueError(f'O tipo de elemento "{self.tipo_elemento}" não foi implementado!')

                        # Continuação das iterações.
                        j += 1
                        dados_txt = texto_arq[j].split()
                    break

    def _ler_apoios(self):
        """Lê os dados dos apoios no arquivo de dados e os associa aos respectivos nós.

        Raises:
            ValueError:
                Se houver alguma restrição de apoio que não seja representada por 0 ou 1.
            TypeError:
                Se houverem valores não numéricos no arquivo de dados.
        """
        with open(file=self.arquivo_dados, mode='r', encoding='utf-8') as arq:
            texto_arq = arq.readlines()
            for i, linha in enumerate(texto_arq):
                # Variáveis auxiliares.
                ct1 = CTES[6][0].lower().split()
                ct2 = CTES[6][1].lower().split()
                lin = linha.lower().split()
                txt = texto_arq[i + 1].lower().split()

                if ''.join(ct1) in ''.join(lin) and ''.join(ct2) in ''.join(txt):
                    j = i + 2
                    dados_txt = texto_arq[j].split()

                    # Verificação da entrada de dados.
                    while bool(dados_txt):
                        try:
                            dados = list(map(int, dados_txt))
                            if any(0 != k != 1 for k in dados[2::]):
                                raise ValueError('As restrições de apoio devem ser representadas apenas por 0 e 1!')
                        except ValueError:
                            raise TypeError('No arquivo de entrada de dados, todos os dados referentes a '
                                            'um apoio devem ser valores numéricos e inteiros!')

                        apoio = Apoio(dados[2] == 0,
                                      dados[3] == 0,
                                      dados[4] == 0)

                        no_ref = dados[1] - 1

                        # Verificação de apoios já existentes.
                        for no in self.nos:
                            if no.apoio == apoio:
                                self.nos[no_ref].apoio = no.apoio
                                break
                        else:
                            self.nos[no_ref].apoio = apoio

                        # Continuação das iterações.
                        j += 1
                        dados_txt = texto_arq[j].split()
                    break

    def _ler_cargas_nodais(self):
        """Lê os dados das cargas nodais no arquivo de dados e os associa aos respectivos nós.

        Raises:
            TypeError:
                Se houverem valores não numéricos no arquivo de dados.
        """
        with open(file=self.arquivo_dados, mode='r', encoding='utf-8') as arq:
            texto_arq = arq.readlines()
            for i, linha in enumerate(texto_arq):
                # Variáveis auxiliares.
                ct1 = CTES[8][0].lower().split()
                ct2 = CTES[8][1].lower().split()
                lin = linha.lower().split()
                txt = texto_arq[i + 1].lower().split()

                if ''.join(ct1) in ''.join(lin) and ''.join(ct2) in ''.join(txt):
                    j = i + 2
                    dados_txt = texto_arq[j].split()

                    # Verificação dos dados de entrada
                    while bool(dados_txt):
                        try:
                            dados = [int(j) if i < 2 else float(j) for i, j in enumerate(dados_txt)]
                        except ValueError:
                            raise TypeError('No arquivo de entrada de dados, todos os dados referentes a '
                                            'uma carga nodal devem ser valores numéricos!')

                        carga = CargaNodal(*dados[2::])
                        no_ref = dados[1] - 1

                        # Verificação de carga já existente.
                        for no in self.nos:
                            if no.carga == carga:
                                self.nos[no_ref].carga = no.carga
                                break
                        else:
                            self.nos[no_ref].carga = carga

                        # Continuação das iterações
                        j += 1
                        dados_txt = texto_arq[j].split()
                    break

    def _ler_cargas_elementos(self):
        """Lê os dados das cargas dos elementos no arquivo de dados e os associa aos respectivos elementos.

        Raises:
            TypeError:
                Se houverem valores não numéricos no arquivo de dados.
        """
        sist = SISTEMAS_COORDENADAS
        # Adicionar carga nula em todos os elementos.
        with open(file=self.arquivo_dados, mode='r', encoding='utf-8') as arq:
            texto_arq = arq.readlines()
            for i, linha in enumerate(texto_arq):
                # Variáveis auxiliares
                ct1 = CTES[7][0].lower().split()
                ct2 = CTES[7][1].lower().split()
                lin = linha.lower().split()

                # Verifica se o arquivo chegou ao fim.
                if CTES[9] in linha:
                    break
                else:
                    txt = texto_arq[i + 1].lower().split()

                if ''.join(ct1) in ''.join(lin) and ''.join(ct2) in ''.join(txt):
                    j = i + 2
                    dados_txt = texto_arq[j].split()

                    # Verificação dos dados de entrada
                    while bool(dados_txt):
                        try:
                            dados = [int(j) if i < 3 else float(j) for i, j in enumerate(dados_txt)]
                        except ValueError:
                            raise TypeError('No arquivo de entrada de dados, todos os dados referentes a '
                                            'uma carga distribuída devem ser valores numéricos!')

                        carga_dist = CargaDistribuida(dados[3], dados[4], sist[1] if dados[2] == 1 else sist[0])
                        el_ref = dados[1] - 1

                        self.elementos[el_ref].carga = carga_dist

                        # Continuação da iteração
                        j += 1
                        dados_txt = texto_arq[j].split()
                    break

    def _carregar_dados_entrada(self):
        """Faz a leitura do arquivo de dados e armazena tais dados em uma instância de `Estrutura`."""
        self._ler_tipo_estrutura()
        self._ler_tipo_elemento()
        self._ler_nos()
        self._ler_materiais()
        self._ler_secoes_transversais()
        self._ler_apoios()
        self._ler_elementos()
        self._ler_cargas_elementos()
        self._ler_cargas_nodais()

    # endregion

    # region Adicionar componentes à estrutura
    def _adicionar_no(self, no: No):
        """Adiciona um nó ao conjunto de elementos da estrutura"""
        if not isinstance(no, No):
            TypeError(f'O tipo de dado "{type(no)}" não é capaz de representar um nó!')
        else:
            self._nos.append(no)

    def _adicionar_material(self, material: Material):
        """Adiciona um material à lista de materiais dos elementos da estrutura."""
        if not isinstance(material, Material):
            TypeError(f'O tipo de dado "{type(material)}" não é válido para a representação '
                      f'de um material!')
        else:
            self._materiais.append(material)

    def _adicionar_elemento(self, elemento: ElementoBarra):
        if not isinstance(elemento, ElementoBarra):
            raise TypeError(f'O tipo de dado "{type(elemento)}" não é válido para representar um elemento '
                            f'de barra!')
        else:
            self._elementos.append(elemento)

    def _adicionar_secao_transversal(self, secao: Secao):
        if not isinstance(secao, Secao):
            raise TypeError(f'O tipo de dado "{type(secao)}" não é válido para representar '
                            f'uma seção transversal!')
        else:
            self._secoes.append(secao)

    # endregion
    def graus_liberdade_por_no(self) -> int:
        """Retorna o número de graus de liberdade por nó."""
        return GRAUS_LIBERDADE_POR_NO[self.tipo_elemento]

    def graus_liberdade_impedidos(self) -> list:
        """Retorna um vetor ccom os graus de liberdade restringidos."""
        glimp = []
        for elemento in self.elementos:
            for i in elemento.graus_liberdade_impedidos():
                glimp.append(i)

        return list(set(glimp))

    def graus_liberdade_livres(self) -> list:
        """Retorna um vetor com os graus de liberdade livres da estrutura."""
        gll = []

        for elemento in self.elementos:
            for i in elemento.graus_liberdade_livres():
                gll.append(i)

        # Utilização do set para impedir elementos repetidos.
        return list(set(gll))

    def graus_liberdade(self) -> list:
        """Retorna todos os graus de liberdade da estrutura."""
        gl_est = []
        for elemento in self.elementos:
            for i in elemento.graus_liberdade():
                gl_est.append(i)

        return list(set(gl_est))

    def matriz_rigidez(self):
        """Retorna a matriz de rigidez da estrutura em formato de matriz esparsa `csr_matrix`."""
        ks = {}
        glimp = self.graus_liberdade_impedidos()
        n_glivres = len(self.graus_liberdade_livres())

        # Montagem da matriz de rigidez completa
        for elemento in self.elementos:
            kel = elemento.matriz_rigidez_global()
            gle = elemento.graus_liberdade()

            for i, ie in enumerate(gle):
                for j, je in enumerate(gle):
                    if kel[i][j] != 0:
                        coords = (ie - 1, je - 1)
                        if coords not in ks:
                            ks[coords] = kel[i][j]
                        else:
                            ks[coords] = ks[coords] + kel[i][j]

        # Redução da matriz de rigidez com a exclusão dos graus de liberdade impedidos.
        ks_tmp = ks.copy()
        for c in ks_tmp:
            for g in glimp:
                if (g - 1) in c and c in ks:
                    del ks[c]
                    break

        # Correção das coordenadas dos dados da matriz de rigidez após a exclusão dos graus
        # de liberdade impedidos.
        lin = np.array([i[0] for i in ks])
        col = np.array([i[1] for i in ks])
        dados = np.array(list(ks.values()))

        for i, l in enumerate(lin):
            for j in glimp:
                if l > j - 1:
                    lin[i] -= 1

        for i, c in enumerate(col):
            for j in glimp:
                if c > j - 1:
                    col[i] -= 1

        # Criação da matriz esparsa
        kest = sparse.coo_matrix((dados, (lin, col)), shape=(n_glivres, n_glivres))

        # Conversão para o tipo de matriz csr_matrix.
        return kest.tocsr()

    def forcas_nodais_aplicadas(self) -> np.ndarray:
        """Retorna um vetor contendo apenas as cargas nodais aplicadas, desconsiderando-se as distribuídas."""
        cargas_nodais = np.zeros(len(self.graus_liberdade()))
        nos_carregados = self.nos_carregados()

        for no in nos_carregados:
            for gl, forca in zip(no.graus_liberdade(self.tipo_elemento), no.carga.vetor_cargas()):
                cargas_nodais[gl - 1] = forca

        return cargas_nodais

    def forcas_nodais_totais(self) -> np.ndarray:
        """Retorna um vetor contendo as cargas nodais aplicadas somadas com as parcelas oriundas das cargas
        distribuídas nos elementos."""
        f_cargas_nodais = self.forcas_nodais_aplicadas()

        # Se for PP2, acrescentar as cargas atuantes no elemento.
        if self.tipo_elemento == TIPOS_ELEMENTOS[0]:
            for elemento in self.elementos:
                if not elemento.carga.carga_nula():
                    forca_equiv = elemento.forcas_equivalentes_nos_global()
                    gl_elem = elemento.graus_liberdade()

                    for gl, esforco in zip(gl_elem, forca_equiv):
                        if not esforco[0] == 0:
                            f_cargas_nodais[gl - 1] = f_cargas_nodais[gl - 1] + esforco[0]

        return f_cargas_nodais

    def deslocamentos(self):
        # Forças equivalentes nos graus de liberdade livres.
        gl_estr = self.graus_liberdade()
        gl_impedidos = self.graus_liberdade_impedidos()
        gl_livres = self.graus_liberdade_livres()
        feq = np.zeros(len(gl_estr))
        desloc_final = np.copy(feq)

        k = self.matriz_rigidez()
        feq = self.forcas_nodais_totais()
        feq = np.delete(feq, [i - 1 for i in gl_estr if i in gl_impedidos])

        desloc = spsolve(k, feq.T)

        for i, j in zip(gl_livres, desloc):
            desloc_final[i - 1] = j

        return desloc_final

    def nos_apoiados(self) -> Tuple[No]:
        """Retorna uma tupla que contém os nós que possuem apoios."""
        return tuple(no for no in self.nos if not no.apoio.apoio_livre())

    def nos_carregados(self) -> Tuple[No]:
        """Retorna uma tupla que contém os nós carregados."""
        return tuple(no for no in self.nos if not no.carga.carga_nula())

    def elementos_carregados(self) -> Tuple[PP2]:
        """Retorna uma tupla que contém os elementos carregados."""
        return tuple(elemento for elemento in self.elementos if not elemento.carga.carga_nula())
