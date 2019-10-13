
from scipy.sparse import csr_matrix
import sparse_dot_topn.sparse_dot_topn as ct
import numpy as np

def cosimtop(A, B, ntop, lower_bound=0):

    '''
    Optimized cosine similarity computation.
    :param A: First matrix.
    :param B: Second matrix.
    :param ntop: Top n for each row.
    :param lower_bound: Lower bound for each row.
    :return: Cosine similarity matrix.
    '''
    
    A = A.tocsr()
    B = B.tocsr()
    M, _ = A.shape
    _, N = B.shape
    idx_dtype = np.int32
    nnz_max = M * ntop
    indptr = np.zeros(M + 1, dtype = idx_dtype)
    indices = np.zeros(nnz_max, dtype = idx_dtype)
    data = np.zeros(nnz_max, dtype = A.dtype)
    ct.sparse_dot_topn(
        M, N, np.asarray(A.indptr, dtype = idx_dtype),
        np.asarray(A.indices, dtype = idx_dtype),
        A.data,
        np.asarray(B.indptr, dtype = idx_dtype),
        np.asarray(B.indices, dtype = idx_dtype),
        B.data,
        ntop,
        lower_bound,
        indptr, 
        indices, 
        data
    )
    return csr_matrix(
        (data, indices, indptr), 
        shape=(M, N)
    )