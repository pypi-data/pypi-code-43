import numpy as np
# from ntai.codex.numpy.utils import make_encodex_matrix, invert_codex

ENCODING_a      = [1,0,0,0,0,0]
ENCODING_c      = [0,1,0,0,0,0]
ENCODING_g      = [0,0,1,0,0,0]
ENCODING_t      = [0,0,0,1,0,0]
ENCODING_u      = [0,0,0,0,1,0]
ENCODING_repeat = [0,0,0,0,0,1]
INCLUDE_URACIL = False
INCLUDE_REPEAT = False

NUMPY_FASTA_ENCODEX = {
    '-': 0, # e is used to represent '-' as a python variable
    'a': 1,
    'c': 2,
    'g': 3,
    't': 4,
    'u': 5,
    'r': 6,
    'y': 7,
    'k': 8,
    'm': 9,
    's': 10,
    'w': 11,
    'b': 12,
    'd': 13,
    'h': 14,
    'v': 15,
    'n': 16,
    '_': 17, # E is used to represent '_' as a python variable
    'A': 18,
    'C': 19,
    'G': 20,
    'T': 21,
    'U': 22,
    'R': 23,
    'Y': 24,
    'K': 25,
    'M': 26,
    'S': 27,
    'W': 28,
    'B': 29,
    'D': 30,
    'H': 31,
    'V': 32,
    'N': 33
}
