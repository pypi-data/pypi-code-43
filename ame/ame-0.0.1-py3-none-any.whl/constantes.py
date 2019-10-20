"""Módulo que contém valores constantes usados em todo_ o programa"""

# Aceleração gravitacional.
G = 9.81  # m/(s^2)

TIPOS_ELEMENTOS = ['PP2']
GRAUS_LIBERDADE_POR_NO = {TIPOS_ELEMENTOS[0]: 3}
TIPOS_ESTRUTURA = ['PORTICO_PLANO']
SISTEMAS_COORDENADAS = ['local', 'global']

CONSTANTES_LEITURA = {0: 'TIPO DE ESTRUTURA:',
                      1: 'TIPO DE ELEMENTO:',
                      2: ['NÓS:', 'ID  X            Y'],
                      3: ['MATERIAIS:', 'ID    E                Poisson         Alpha'],
                      4: ['SEÇÕES TRANSVERSAIS:', 'ID     Area      InerciaX      YLinhaNeutra'],
                      5: ['ELEMENTOS:', 'ID   Nó_i     No_f     Material     Seção'],
                      6: ['RESTRIÇÕES DE APOIO (1=Impedido, 0=Livre):', 'ID   Nó        ux        vy        rz'],
                      7: ['ELEMENTOS CARREGADOS (idsis=1 => Sistema Global, Idsis=0 => Sistema Local)',
                          'ID   Elemento      Idsis         Qx             Qy'],
                      8: ['NÓS CARREGADOS:', 'ID   Nó      fx                fy                mz'],
                      9: '<Fim>'}
