import numpy as np
import numbers


class ArrayResult:
    """
    Result only for the same given timepoints for all replicates.
    """

    def __init__(
            self,
            ts,
            matrix_xs,
            t_max):
        self.ts = ts
        self.matrix_xs = matrix_xs
        self.t_max = t_max


class FullResult:
    """
    The entire trajectories generated and output, possibly for different
    timepoints for different replicates.
    """

    def __init__(
            self,
            list_ts,
            list_xs,
            t_max):
        self.list_ts = list_ts
        self.list_xs = list_xs
        self.t_max = t_max

    def for_timepoints(self, ts = None, r_indices = None) -> ArrayResult:
        """
        Generate an `ArrayResult` for the given timepoints. Note that if
        no timepoints are passed and the xs and ts were generated using
        an ArrayOutput, then the values in the ArrayResult will be exactly
        those in the FullResult already.
        """
        if ts is None:
            ts = self.get_all_timepoints()

        if r_indices is None:
            r_indices = list(range(len(self.list_ts)))
        if isinstance(r_indices, numbers.Number):
            r_indices = [r_indices]

        if np.max(ts) > self.t_max:
            raise ValueError(
                f"Value of {np.max(ts)} requested but t_max in analysis "
                f"was {self.t_max}.")

        nr = len(r_indices)
        nt = len(ts)
        nx = len(self.list_xs[0][0])

        # initialize matrix
        matrix_xs = np.zeros((nr, nt, nx))

        # iterate over 
        for ir in r_indices:
            xs = self._replicate_for_timepoints(ts, ir)
            matrix_xs[ir, ...] = xs

        return ArrayResult(ts, matrix_xs, self.t_max)


    def get_all_timepoints(self):
        """
        Return union of all time points.
        """
        ts = np.concatenate(self.list_ts)
        ts = np.unique(ts)  # also sorts
        return ts

    def _replicate_for_timepoints(self, ts, ir):
        _ts = self.list_ts[ir]
        _xs = self.list_xs[ir]
        ind = np.searchsorted(a=_ts, v=ts, side='left')
        ind = np.minimum(ind, len(_ts) -1)
        xs = _xs[ind, ...]
        return xs
