REPEAT_CHAR = '.'

FASTA_CHARS = set('actgrykmswbdhuvn-')
ENCODE_ORDER = list('actgu')

INCLUDE_URACIL = False
INCLUDE_REPEAT = False

FASTA_ENCODEX = {
    'a': 'a',
    'c': 'c',
    't': 't',
    'g': 'g',
    'u': 'u',
    'r': 'ag',
    'y': 'ctu',
    'k': 'gtu',
    'm': 'ac',
    's': 'cg',
    'w': 'atu',
    'b': 'cgtu',
    'd': 'agtu',
    'h': 'actu',
    'v': 'acg',
    'n': 'actgu',
    '-': ''
}



FASTA_DECODEX = {
    'a'    : 'a',
    'c'    : 'c',
    't'    : 't',
    'g'    : 'g',
    'u'    : 'u',
    'ag'   : 'r',
    'ctu'  : 'y',
    'ct'   : 'y',
    'gtu'  : 'k',
    'gt'   : 'k',
    'ac'   : 'm',
    'cg'   : 's',
    'atu'  : 'w',
    'at'   : 'w',
    'cgtu' : 'b',
    'cgt'  : 'b',
    'agtu' : 'd',
    'agt'  : 'd',
    'actu' : 'h',
    'act'  : 'h',
    'acg'  : 'v',
    'acgtu': 'n',
    'acgt' : 'n',
    ''     : '-'
}

FASTA_COMPLEMENTS = {
    'a': 't',
    'c': 'g',
    't': 'a',
    'g': 'c',
    'u': 'u', # based on bedtools
    'r': 'y',
    'y': 'r',
    'k': 'm',
    'm': 'k',
    's': 's',
    'w': 'w',
    'b': 'v',
    'd': 'h',
    'h': 'd',
    'v': 'b',
    'n': 'n',
    '-': '-',
    'A': 'T',
    'C': 'G',
    'T': 'A',
    'G': 'C',
    'U': 'U',
    'R': 'Y',
    'Y': 'R',
    'K': 'M',
    'M': 'K',
    'S': 'S',
    'W': 'W',
    'B': 'V',
    'D': 'H',
    'H': 'D',
    'V': 'B',
    'N': 'N',
    '-': '-'
}
