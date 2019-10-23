import numpy as np
def unravel_merged_matrices(merged_flattened_index:int, elements_in_matrices:list):
    '''
    Arguments:
        merged_flattened_index (int): the index of the element in the merged,
            flattened matrix
        elements_in_matrices (list): a list of integers corresponding to the
            number of elements in the matrix at the corresponding index
    Returns:
        flattened_index (int): the flattened index for the matrix to which
            merged_flattened_index belongs to
        matrix_index (int): the index correspoinding to the matrix to which the
            flattened_index belongs to

    '''
    flattened_index = merged_flattened_index
    matrix_index = -1
    for i, num_elements in enumerate(elements_in_matrices):
        if flattened_index < num_elements:
            matrix_index = i
            break
        flattened_index -= num_elements
    return (flattened_index, matrix_index)

def merge_matrices(matrices:list):
    '''
    Arguments:
        matrices (list): a list of matrices (np.ndarray) to merge
    Returns:
        merged (list): a 1D np.ndarray consist of all the elements from matrices
        flattened_matrices (list): a list of 1D np.ndarrays corresponding to the
            flattened matrices from matrices
        elements_per_matrix (list): the number of elements per matrix in
            matrices
    '''
    # dealing with matrices of different shape is cumbersome, so flatten them
    # and leverage 1D mapping.
    flattened_matrices = [mat.flatten() for mat in matrices]

    # save some re compuation
    elements_per_matrix = list(map(len, flattened_matrices))

    # one long, flattened matrix
    merged = np.concatenate(flattened_matrices)
    return merged, flattened_matrices, elements_per_matrix

def matrix_indices_from_merged_array(
    elements_needed:int,
    merged_array:list,
    elements_per_array:list
):
    '''
    Arguments:
        elements_needed (int): how many elements to retrieve

        merged_array (list): a 1D numpy.ndarray that consists of several
            distinct n-dimensional matrices which were flattened and
            concatenate and joined together.

        elements_per_array (list): a list of the total number of elements in
            each of the n-dimensional matrices which make up the merged_array

    Returns:
        raveled_index_matrix_tuples (list): a list of tuples which consists of
            raveled_index (int): the raveled (flattened) index of the element
            matrix_index (int): the matrix to which the raveled_index belongs
                from which merged_array is made from.
    '''
    # argpartition is faster than argmin, but the top smallest k values are not
    # sorted
    smallest_elements = np.argpartition(merged_array, elements_needed)[:elements_needed]
    raveled_index_matrix_tuples = list(map(
        lambda i: unravel_merged_matrices(i, elements_per_array),
        smallest_elements
    ))
    return raveled_index_matrix_tuples

def raveled_indices_of_matrix(raveled_index_matrix_tuples:list, matrix_index:int):
    '''
    Arguments:
        raveled_index_matrix_tuples (list): a list of (raveled_index:int,
            matrix_index:int) tuples
        matrix_index (int): the matrix from which raveled_indices are requested
    Returns:
        indices (list): a list of raveled indices belonging to matrix_index
    '''
    belongs_to_matrix_q = lambda tup: tup[-1] == matrix_index
    index_extractor = lambda tup: tup[0]
    indices = list(map(index_extractor, filter(belongs_to_matrix_q, raveled_index_matrix_tuples)))
    return indices




def shard_rng(maxlen, sublen, stride):
    '''
    A wrapper around `range(start, stop, step)` such that if stop is not evenly
    divisible by step, the last step is `(stop-sublen, stop)`.

    Arguments:
        maxlen (int): the length to shard into steps.
        sublen (int): how long each substep will be.
        stride (int): how far to step.

    Returns:
        ranges (list): a list of (start, stop) sublists. These ranges may overlap.

    '''
    ranges = []
    for i in range(0, maxlen, stride):
        if i + sublen > maxlen:
            ranges.append([maxlen-sublen, maxlen])
            break
        else:
            ranges.append([i, i+sublen])
    return ranges

def weight_rngs(ranges):
    '''
    Helper function for `stitch_mats` with `method=1` (`_stitch1`).
    Arguments:
        ranges (list): a list of (start, stop) sublists.

    Returns:
        weights (list): a 1D array of length `ranges[-1][-1]`. How much to scale
            each index due to overlapping steps.
    '''
    n = ranges[-1][-1]
    bins = map(np.bincount,np.array(ranges).T,(None,None),(n+1,n+1))
    vals = np.subtract(*bins).cumsum()
    weights = 1 / vals[:n,None]
    return weights


def _stitch1(shape, submats, ranges):
    stitched = np.zeros(shape)
    weights = weight_rngs(ranges)
    for submat, (start, stop) in zip(submats, ranges):
        stitched[start:stop] += weights[start:stop] * submat
    return stitched


def _stitch2(shape, submats, ranges):
    ranges = np.array(ranges)
    ro = ranges.ravel().argsort(kind='stable')

    # put 1 for starting and -1 for ending, take cumsum
    cnts = (1-((ro&1)<<1)).cumsum()

    stitched = np.zeros((n,m))
    # add slices
    for submat, (start, stop) in zip(submats,ranges):
        stitched[start:stop] += submat

    rs = ranges.ravel()[ro]
    # divide by overlap
    for start, stop, count in zip(rs[:-1],rs[1:],cnts[:-1]):
        stitched[start:stop] /= count
    return stitched


def stitch_mats(shape, submats, ranges, method=1):
    '''
    Arguments:
        shape (tuple): the shape of the output matrix `(n, m)`.
        submats (list): a list of matrices all with shape `(k, m)`.
        ranges (list): a list of (start, stop) sublists "ranges". These ranges
            are across the first dimension of the output matrix and specifiy
            which region of `n` each submatrix corresponds to.
        method (int): either `1` or `2`. Returns identically results, may affect
            runtime.

    Returns:
        stitched (list): a matrix of shape `(n, m)` where the submats are joined
            together, averaging the values when they overlap (based on `ranges`).
    '''
    fn = _stitch1 if method == 1 else _stitch2
    return fn(shape, submats, ranges)

def shard_mat(mat, ranges):
    '''
    Arguments:
        mat (list): a matrix of shape `(n, m)` to produce submatrices from.
        ranges (list): a list of (start, stop) sublists indicating how to make
            the submatricies (e.g. `mat[start:stop]`)
    Returns:
        submats (list): a list of submats that start and stop as specified in
            `ranges`.
    '''
    return [mat[start:stop] for start, stop in ranges]
