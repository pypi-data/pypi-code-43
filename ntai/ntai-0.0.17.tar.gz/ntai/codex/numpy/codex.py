import numpy as np
from ntai.codex.numpy.defaults import (
    NUMPY_FASTA_ENCODEX,
    INCLUDE_URACIL,
    INCLUDE_REPEAT,
    ENCODING_a,
    ENCODING_c,
    ENCODING_g,
    ENCODING_t,
    ENCODING_u,
    ENCODING_repeat
)

from ntai.codex.defaults import (
    FASTA_COMPLEMENTS
)

from ntai.codex.numpy.utils import (
    make_encodex_matrix, invert_encodex,
    encode, decode
)

NUMPY_FASTA_ENCODEX_MATRIX = make_encodex_matrix(
    NUMPY_FASTA_ENCODEX,
    ENCODING_a,
    ENCODING_c,
    ENCODING_g,
    ENCODING_t,
    ENCODING_u,
    ENCODING_repeat
)

NUMPY_FASTA_DECODEX = invert_encodex(NUMPY_FASTA_ENCODEX)

class Codex:

    def __init__(
        self,
        include_uracil:bool = INCLUDE_URACIL,
        include_repeat:bool = INCLUDE_REPEAT,
        encodex: dict       = NUMPY_FASTA_ENCODEX,
        decodex: dict       = NUMPY_FASTA_DECODEX,
        encodex_matrix: list = NUMPY_FASTA_ENCODEX_MATRIX
    ):
        '''
        Arguments:
            include_uracil (bool): whether or not uracil should be included in the
                embedding. By default False.

            include_repeat (bool): wehtehr or not repeated masked regions should be
                included in the embedding. By default False.

            encodex (dict): the dictionary converting fasta characters to
                nucleotides.

            decodex (dict): the dictionary converting nucleotide characters to
                fasta characters.
        '''
        self.include_uracil = include_uracil
        self.include_repeat = include_repeat
        self.encodex = encodex
        if decodex is None:
            decodex = invert_encodex(encodex)
        self.decodex = decodex
        if encodex_matrix is None:
            encodex_matrix = make_encodex_matrix(encodex=encodex)
        self.encodex_matrix = encodex_matrix


    def encode(self, sequence):
        return encode(
            sequence,
            encodex = self.encodex,
            encodex_matrix = self.encodex_matrix,
            include_uracil = self.include_uracil,
            include_repeat = self.include_repeat
        )

    def decode(self, encoded):
        return decode(
            encoded,
            encodex = self.encodex,
            encodex_matrix = self.encodex_matrix,
            include_uracil = self.include_uracil,
            include_repeat = self.include_repeat,
            decodex        = self.decodex
        )
        
    def complement(self, seq):
        return ''.join(list(map(lambda c: FASTA_COMPLEMENTS[c], list(seq))))
