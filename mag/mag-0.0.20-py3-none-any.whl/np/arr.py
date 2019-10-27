import numpy as np

def binarize(data:list, cutoff:float=0.5) -> list:
    '''Converts all values of data to either 1 or 0 depending on
    whether or not the value is greater than cutoff.

    Args:
        data (ndarray): an arbitrary array of numerical values
        cutoff (float): a value bounded [0, 1] determining which values are
            converted to one.

    Returns:
        binary_data (ndarray:int): an array with same dimensions as data where
            all values are either 0 or 1
    '''
    return (data > cutoff).astype(int)

def consecutive(data:list, stepsize:float=1) -> list:
    '''Splits data into subarrays where the values in each array vary by stepsize

    Args:
        data (ndarray): a one dimensional array of sorted values
        stepsize (float): a numeric value specifying how close values should be
            to be considered consecutive
    Returns:
        consecutive_numbers (ndarray): a list of values from data where each
            sublist contains values that are exactly stepsize apart
    '''
    return np.split(data, np.where(np.diff(data) != stepsize)[0]+1)

from mag.py.math import domain
def runs(array:list) -> list:
    '''Returns the [start, stop] values of consectuive numbers in the given array

    Args:
        array (list): a list of values, sorted least to greatest

    Returns:
        runs (list): a list of all runs found in the array, where a run specifies
            the lower and upper bounds of consecutive numbers.
    '''
    return [domain(run) if run.size > 0 else [] for run in consecutive(array)]


def nonzero_1d(data:list) -> list:
    '''Returns the indices of nonzero values in an one-dimensional array.

    Args:
        data (ndarray): an array with one dimension

    Returns:
        indices (ndarray): a one dimensional array containing indicies of data
            which are nonzero
    '''
    return data.nonzero()[0]

def are_same_run(run_a:list, run_b:list, tolerance:int=0) -> bool:
    '''
    Notes:
        - Used by `smooth_runs`
    Arguments:
        run_a (list): a list of intergers consisting of `[start, stop]`
        run_b (list): a list of intergers consisting of `[start, stop]`
        tolerance (int): how far apart run_a and run_b to be considered
            a part of the same run. By default `0`.
    Returns:
        are_same_run (bool): whether or not the two runs are within the
            specified `tolerance`.
    '''
    start_a, stop_a = run_a
    start_b, stop_b = run_b
    if start_a < start_b:
        return start_b - stop_a <= tolerance + 1
    return start_a - stop_b <= tolerance + 1

def merge_runs(run_a:list, run_b:list) -> list:
    return [min(run_a[0], run_b[0]), max(run_a[1], run_b[1])]



def smooth_runs(runs:list, tolerance:int=0):
    '''
    Notes:
        - Assumes `runs` is a list of lists, where each sublist is specifies a
            "run" (start and stop indices) for a given feature. Expected to be
            the output of the function `runs`.

        - Assumes `runs` is _ordered_ (e.g. `runs[0][0] < runs[1][0]`)

    Arguments:
        runs (list): a list of runs, where a run specifies the lower and upper
        bounds of a range.

        tolerance (int): How many _indicies_ between two runs in `runs` for them
            to be considered part of the same run. By default `tolerance` is
            set to `0`.

    Returns:
        smoothed (list): a lists of lists (similar to `runs`), where each run is
            seperated by at most `tolerance` indicies are merged.
    '''
    num_runs = np.inf
    smoothed = np.array(runs)
    while num_runs > len(smoothed):
        # update stopping condition
        num_runs = len(smoothed)

        # collection var for merged runs
        coalesced = np.array([0][:0]).reshape(-1,2)
        for i in range(len(smoothed)):
            run_a = smoothed[i]
            append_flag = True # not yet in coalesced
            for j in range(len(coalesced)):
                run_b = coalesced[j]
                if are_same_run(run_a, run_b, tolerance):
                    append_flag = False # merge into exisitng run
                    coalesced[j] = merge_runs(run_a, run_b)
                    break
            if append_flag:
                coalesced = np.concatenate((coalesced, np.array([run_a])))
        # update smoothed
        smoothed = coalesced
    return smoothed.astype(int).tolist()
