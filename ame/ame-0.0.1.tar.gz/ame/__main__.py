import ame


def acoes(e: ame.Estrutura):
    p = ame.Ploter(e)
    while True:
        print('\n> Digite o número correspondente à ação que deseja executar:')
        acao = int(input('1 - Calcular os esforços e os deslocamentos\n'
                         '2 - Exibir as propriedades da estrutura\n'
                         '3 - Exibir os diagramas de esforços de um elemento específico\n'
                         '4 - Salvar os esforços e os deslocamentos em um arquivo\n'
                         '5 - Sair\n\n'))

        if acao == 1:
            print(p.imprimir_resultados())
        elif acao == 2:
            print(e)
        elif acao == 3:
            elem = int(input('\n> Digite o número do elemento: '))
            try:
                p.plotar_graficos_elemento(elem)
                break
            except Exception:
                print(f'ERRO: O elemento {elem} não é válido!')
        elif acao == 4:
            arq = input('\n> Digite o nome do arquivo sem a extensão: ')
            p.salvar_resultados(arq + '.txt')
            print(f'O arquivo "{arq}.txt" foi salvo com sucesso!\n')
        elif acao == 5:
            break
        else:
            print('Opção inválida!\n')

        v = input('\n> Você deseja retornar ao menu de opções? (s/n)')
        if v == 's':
            continue
        else:
            break


def main():
    print(80 * '=')
    print(f'AME {ame.__version__} - Biblioteca de análise matricial de estruturas')
    print(80 * '=')
    print(f'Desenvolvedor: {ame.__author__}')
    print(f'Lattes: http://lattes.cnpq.br/7475621793968286')
    print(80 * '-' + '\n\n')

    arq = ''

    while True:
        try:
            arq = input('> Digite o nome do arquivo de extensão ".ame": ')
            e = ame.Estrutura(arq if '.ame' in arq else arq + '.ame')
            break
        except FileNotFoundError:
            print(f'ERRO: O arquivo "{arq}" não existe!\n')

    acoes(e)

    print('\n\nFim da execução!')


if __name__ == '__main__':
    main()
