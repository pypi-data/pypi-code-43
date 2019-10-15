from dxf2x.compiler import syntax, foreach_ast

def lexical(f):
    return [{code: value
             for code, value in [word.split(':', 1)
                                 for word in line.rstrip('\n').split('\t')]}
            for line in f
            if line.startswith('0:')]

def read(filename):
    with open(filename, errors = 'ignore') as f:
        return syntax(lexical(f))

def write(ast, filename):
    with open(filename, 'w', errors = 'ignore') as fout:
        is_empty = True
        def word_consumer(code, value):
            nonlocal is_empty
            if is_empty:
                is_empty = False
            else:
                fout.write('\n' if code == '0' else '\t')
            fout.write(f'{code}:{value}')
        foreach_ast(ast, word_consumer)
        fout.write('\n')
