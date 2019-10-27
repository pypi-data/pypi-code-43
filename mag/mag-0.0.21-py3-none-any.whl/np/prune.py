import numpy as np
from mag.np.mat import (
    merge_matrices,
    matrix_indices_from_merged_array,
    raveled_indices_of_matrix
)

def prune_method(method:str)->str:
    '''
    Helper function for handling str / int prune method argument

    Arguments:
        method (str / int): the method by which the model was prunned. Valid
            options include:
                0: "weight_pruning"
                1: "unit_pruning"
    Returns:
        method (str): a valid pruning method
    '''
    VALID_PRUNING_METHODS = ['weight_pruning', 'unit_pruning']
    if method == 0: method = 'weight_pruning'
    if method == 1: method = 'unit_pruning'
    if method not in VALID_PRUNING_METHODS:  method = 'weight_pruning'
    return method



def apply_weight_prunning(matrix:list, indices:list, inplace:bool=False):
    '''
    Arguments:
        matrix (list): a (np.ndarray) numeric matrix, assumed to have dims 2.
        indices (list): a list of indicies (corresponding to flattened matrix)
            to set to zero.
        inplace (bool): whether or not to update the passed matrix or copy it
            and return the updated copy.
    Returns:
        updated: the updated matrix where indicies are set to zero
    '''
    mat = matrix if inplace else np.copy(matrix)
    # python map doesn't work with empty list
    if len(indices) > 0:
        rows, cols = np.transpose(list(map(
            lambda i: np.unravel_index(i, mat.shape),
            indices
        )))
        mat[rows, cols] = 0
    return mat

def apply_unit_prunning(matrix:list, indices:list, inplace:bool=False):
    '''
    Arguments:
        matrix (list): a (np.ndarray) numeric matrix, assumed to have dims 2.
        indices (list): a list of indicies (corresponding to columns) to set to
            zero.
        inplace (bool): whether or not to update the passed matrix or copy it
            and return the updated copy.
    Returns:
        updated: the updated matrix where indicies are set to zero
    '''
    mat = matrix if inplace else np.copy(matrix)
    # python map doesn't work with empty list
    if len(indices) > 0:
        mat[:, indices] = 0
    return mat


def prune_k_percent(matrices:list, percent:float, method='weight_pruning'):
    '''
    Arguments:
        matrices (list): a list of numeric matrices. Each element in the list
            matrices is assumed to be a numpy.ndarray corresopnding to a weight
            matrix.

        percent (float): the percent of the smallest values to be set to zero.

        method (str / int):
            "weight_pruning" (0): sets the lowest k percent of elements in
                matrices to zero.

            "unit_pruning" (1): sets the lowest k percent of columns, based on
                the columns' l2 norm, in matrices to zero
    Returns:
        results (list):
    '''
    if method == 'unit_pruning' or method == 1:
        to_merge = [np.linalg.norm(matrix, axis=0) for matrix in matrices]
        prune_fn = apply_unit_prunning
    else:
        to_merge = matrices
        prune_fn = apply_weight_prunning

    merged, flattened_matrices, elements_per_matrix = merge_matrices(to_merge)
    # percent to int
    number_of_indices_needed = int(np.round(percent * len(merged)))
    raveled_index_matrix_tuples = matrix_indices_from_merged_array(
        number_of_indices_needed, merged, elements_per_matrix
    )

    results = []
    for matrix_index, matrix in enumerate(matrices):
        indices = raveled_indices_of_matrix(raveled_index_matrix_tuples, matrix_index)
        results.append(prune_fn(matrix, indices, False))
    return results
