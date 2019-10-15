# DXF编译器

## 1. 词法：生成Token序列

## 2. 语法：将Token序列转换成抽象语法树
## 语法树结构：
## blocks: [{
##   ... // code: value
##   entities: [{
##     ... // code: value pair for POLYLINE, LINE, POINT, TEXT
##     vertices: [{
##       ...
##     }]
##   }]
## }]
## entities: [{
##   ... // code: value pair for INSERT, TEXT
## }]

def syntax(tokens):
    ast = {'blocks': [], 'entities': []}
    pointer = ast
    for token in tokens:
        if token == {'0': 'SECTION', '2': 'BLOCKS'} or token['0'] == 'ENDBLK':
            pointer = ast['blocks']
        elif token == {'0': 'SECTION', '2': 'ENTITIES'}:
            pointer = ast['entities']
        elif token['0'] == 'BLOCK':
            pointer.append(token)
            pointer = token['entities'] = []
        elif token['0'] == 'POLYLINE':
            pointer.append(token)
            pointer = token['vertices'] = []
        elif token['0'] in {'VERTEX', 'LINE', 'POINT', 'INSERT', 'TEXT'}:
            pointer.append(token)
        elif token['0'] == 'SEQEND':
            pointer = ast['blocks'][-1]['entities']
    return ast

## 3. 遍历：遍历抽象语法树

def foreach_words(words, consumer):
    for code, value in words.items():
        consumer(code, value)

def foreach_vertices(vertices, consumer):
    for vertex in vertices:
        consumer(vertex)

def foreach_shapes(shapes, consumer):
    for shape in shapes:
        vertices = shape.pop('vertices', None)
        consumer(shape)
        if vertices:
            foreach_vertices(vertices, consumer)
            consumer({'0': 'SEQEND', '8': shape['8']})

def foreach_entities(shapes, consumer):
    consumer({'0': 'SECTION', '2': 'ENTITIES'})
    foreach_shapes(shapes, consumer)
    consumer({'0': 'ENDSEC'})

def foreach_blocks(blocks, consumer):
    consumer({'0': 'SECTION', '2': 'BLOCKS'})
    for block in blocks:
        shapes = block.pop('entities')
        consumer(block)
        foreach_shapes(shapes, consumer)
        consumer({'0': 'ENDBLK'})
    consumer({'0': 'ENDSEC'})

def foreach_ast(ast, word_consumer):
    token_consumer = lambda token: foreach_words(token, word_consumer)
    foreach_blocks(ast['blocks'], token_consumer)
    foreach_entities(ast['entities'], token_consumer)
    token_consumer({'0': 'EOF'})
