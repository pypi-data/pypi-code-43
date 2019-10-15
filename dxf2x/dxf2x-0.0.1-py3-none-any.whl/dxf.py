from dxf2x.compiler import syntax, foreach_ast

def lexical(f):
    tokens = []
    for code in f:
        code = code.strip()
        value = f.readline().rstrip('\r\n')
        if code == '0':
            tokens.append({code: value})
        elif tokens:
            tokens[-1][code] = value
    return tokens

def read(filename):
    with open(filename, encoding = 'gbk', errors = 'ignore') as f:
        return syntax(lexical(f))

def write(ast, filename):
    with open(filename, 'w', encoding = 'gbk', errors = 'ignore') as f:
        foreach_ast(ast, lambda code, value: f.write(f'{code}\r\n{value}\r\n'))
