import numpy as np
from ntai.codex.numpy.defaults import (
    INCLUDE_URACIL,
    INCLUDE_REPEAT,
    ENCODING_a,
    ENCODING_c,
    ENCODING_g,
    ENCODING_t,
    ENCODING_u,
    ENCODING_repeat
)

def validate_base_encoding(name, encoding):
    if np.cumsum(encoding)[-1] != 1:
        msg = 'base encoding for {} should be one hot!'.format(name)
        raise ValueError(msg)
    if encoding.size != 6:
        msg = 'base encoding for {} should be of shape (6, )!'.format(name)
        raise ValueError(msg)

def make_encodex_matrix(
    encodex:dict,
    a:list       = ENCODING_a,
    c:list       = ENCODING_c,
    g:list       = ENCODING_g,
    t:list       = ENCODING_t,
    u:list       = ENCODING_u,
    repeat:list  = ENCODING_repeat
) -> list:
    _a = np.array(a)
    _c = np.array(c)
    _g = np.array(g)
    _t = np.array(t)
    _u = np.array(u)
    _r = np.array(repeat)
    encodings = [('a', _a),('c', _c),('g', _g,),('t', _t,),('u', _u,),('r', _r)]
    for c, encoding in encodings:
        validate_base_encoding(c, encoding)

    e = np.zeros((6, ), dtype=np.int64) # '-'
    r = _a + g
    y = _c + _t + _u
    k = _g + _t + _u
    m = _a + _c
    s = _c + _g
    w = _a + _t + _u
    b = _c + _g + _t + _u
    d = _a + _g + _t + _u
    h = _a + _c + _t + _u
    v = _a + _c + _g
    n = _a + _c + _g + _t + _u
    E =  e + _r
    A = _a + _r
    C = _c + _r
    G = _g + _r
    T = _t + _r
    U = _u + _r
    R =  r + _r
    Y =  y + _r
    K =  k + _r
    M =  m + _r
    S =  s + _r
    W =  w + _r
    B =  b + _r
    D =  d + _r
    H =  h + _r
    V =  v + _r
    N =  n + _r


    encodex_matrix = np.array([
       # 0, 1, 2, 3, 4, 5, 6, 7, 8, 9,10,11,12,13,14,15,16,
        e, _a,_c,_g,_t,_u, r, y, k, m, s, w, b, d, h, v, n,
       #17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33
        E,  A, C, G, T, U, R, Y, K, M, S, W, B, D, H, V, N,
    ])
    return encodex_matrix[list(encodex.values())]


def invert_encodex(encodex:dict) -> dict:
    k, v = zip(*encodex.items())
    return dict(zip(v, k))

def find_row(matrix:list, row:list) -> int:
    return np.where(np.all(matrix == row, axis=1))[0][0]

def _char_to_int(char:str, encodex:dict)->int:
    return encodex[char]

def _sequence_to_indices(sequence:str, encodex:dict)->list:
    fn = lambda c: _char_to_int(c, encodex)
    return list(map(fn, sequence))


def lookup_channel_index(
    channel:int,
    encodex:dict,
    encodex_matrix:list
) -> int:
    return np.argmax(encodex_matrix[_char_to_int(channel, encodex)])


def get_channel_indices(
    encodex: dict,
    encodex_matrix: list,
    include_uracil: bool = INCLUDE_URACIL,
    include_repeat: bool = INCLUDE_REPEAT
) -> list:
    # drop uracil or repeat channel as needed
    channels = 'acgt'
    if include_uracil: channels += 'u'
    if include_repeat: channels += '_'
    fn = lambda c: lookup_channel_index(c, encodex, encodex_matrix)
    return list(map(fn, channels))


def encode(
    sequence:str,
    encodex: dict,
    encodex_matrix: list = None,
    include_uracil: bool = INCLUDE_URACIL,
    include_repeat: bool = INCLUDE_REPEAT
):
    # convert from string to integers
    indices = np.array(_sequence_to_indices(sequence, encodex))
    if encodex_matrix is None:
        encodex_matrix = make_encodex_matrix(encodex=encodex)
    # extract the rows from the encoding matrix in order as they appear in seq
    results = encodex_matrix[indices]
    channel_indices = get_channel_indices(encodex, encodex_matrix, include_uracil, include_repeat)
    # filter results
    return results[:, channel_indices].tolist()

def decode(
    encoded:list,
    encodex: dict,
    encodex_matrix: list = None,
    include_uracil: bool = INCLUDE_URACIL,
    include_repeat: bool = INCLUDE_REPEAT,
    decodex: dict = None
):

    if encodex_matrix is None:
        encodex_matrix = make_encodex_matrix(encodex=encodex)
    if decodex is None:
        decodex = invert_encodex(encodex)

    channel_indices = get_channel_indices(encodex, encodex_matrix, include_uracil, include_repeat)
    filtered_matrix = encodex_matrix[:, channel_indices]
    keys = list(map(lambda r: find_row(filtered_matrix, r), encoded))
    return ''.join(list(map(lambda k: decodex[k], keys)))
