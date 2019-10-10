from abc import ABC, abstractmethod
import numpy as np
import numba as nb


class Output(ABC):

    @abstractmethod
    def __init__(self):
        super().__init__()
        self.t_max = None

    def create_empty(self):
        return Output()

    def initialize(self, t0, x0, t_max):
        self.t_max = t_max

    def finalize(self):
        pass

    def append(self, t, x):
        pass

    def as_ndarrays(self):
        pass


class FullOutput(Output):

    def __init__(self):
        super().__init__()
        self.ts = []
        self.xs = []

    def create_empty(self):
        return FullOutput()

    def initialize(self, t0, x0, t_max):
        super().initialize(t0, x0, t_max)
        # append initial state
        self.append(t0, x0)

    def append(self, t, x):
        if t > self.t_max:
            return
        self.ts.append(t)
        self.xs.append(x)

    def as_ndarrays(self):
        ts = np.array(self.ts)
        xs = np.array(self.xs)
        return ts, xs


class ArrayOutput(Output):

    def __init__(self, ts: np.ndarray):
        super().__init__()
        self.ts = ts
        self.nt = None
        self.xs = None
        self.x_prev = None
        self.cur_ix = None

    def create_empty(self):
        return ArrayOutput(self.ts)

    def initialize(self, t0, x0, t_max):
        super().initialize(t0, x0, t_max)

        # restrict array to times <= t_max
        self.ts = np.array([t for t in self.ts if t <= t_max])
        self.nt = len(self.ts)

        # prepare states
        self.xs = np.full((self.nt, len(x0)), np.nan)
        self.x_prev = x0

        # reset current array index
        self.cur_ix = 0

        # append initial state
        self.append(t0, x0)

    def append(self, t, x):
        # fill for all time points before t with the previous state
        while self.cur_ix < self.nt and self.ts[self.cur_ix] < t:
            self.xs[self.cur_ix, :] = self.x_prev
            self.cur_ix += 1

        # special case: hit exactly the time point
        # fill with new x
        if self.cur_ix < self.nt and self.ts[self.cur_ix] == t:
            self.xs[self.cur_ix, :] = x
            self.cur_ix += 1

        # remember latest x
        self.x_prev = x

    def finalize(self):
        while self.cur_ix < self.nt:
            self.xs[self.cur_ix, :] = self.x_prev
            self.cur_ix += 1

    def as_ndarrays(self):
        if self.cur_ix < self.nt:
            raise ValueError(
                "ArrayOutput not filled completely.")
        return self.ts, self.xs
