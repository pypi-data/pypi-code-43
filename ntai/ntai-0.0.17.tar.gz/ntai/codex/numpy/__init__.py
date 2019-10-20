from .codex import Codex as NPCodex
from .codex import (
    NUMPY_FASTA_ENCODEX,
    NUMPY_FASTA_ENCODEX_MATRIX,
    NUMPY_FASTA_DECODEX,
    INCLUDE_URACIL,
    INCLUDE_REPEAT,
    ENCODING_a,
    ENCODING_c,
    ENCODING_g,
    ENCODING_t,
    ENCODING_u,
    ENCODING_repeat,
)

from .utils import (
    make_encodex_matrix,
    invert_encodex,
    find_row,
    lookup_channel_index,
    get_channel_indices
)
