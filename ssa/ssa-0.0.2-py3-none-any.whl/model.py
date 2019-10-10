import numpy as np
import numbers
import multiprocessing as mp

from .direct import direct
from .output import Output, FullOutput
from .result import FullResult
from .engine import MultiProcessEngine, SimulationTask


class Model:
    """
    A chemical reaction network model.

    Attributes
    ----------

    reactants: np.ndarray, shape = (nr, nx)
    products: np.ndarray, shape = (nr, nx)
    x0: np.ndarray, shape = (nr, )
    k: np.ndarray, shape = (nx, )
    t_max: numbers.Number
    """

    def __init__(
            self,
            reactants: np.ndarray,
            products: np.ndarray,
            x0: np.ndarray,
            t_max: numbers.Number,
            k: np.ndarray,
            output: Output = None,
            n_procs: int = 1):
        self.reactants = reactants
        self.products = products
        
        self.reaction_matrix = products - reactants

        self.x0 = x0
        self.t_max = t_max
        self.k = k

        if output is None:
            output = FullOutput()
        self.output = output

        self.engine = MultiProcessEngine(n_procs=n_procs)

        self.nr, self.nx = reactants.shape

        self._configure()

    def _configure(self):
        self.reactants.shape = (self.nr, self.nx)
        self.products.shape = (self.nr, self.nx)
        self.reaction_matrix.shape = (self.nr, self.nx)
        self.x0.flatten()
        self.k.flatten()
        if not isinstance(self.t_max, numbers.Number) or not np.isfinite(self.t_max):
            raise ValueError("t_max must be a finite integer.")

    def simulate(
            self,
            alg = None,
            n_reps: int = 1,
            **kwargs):
        # choose algorithm
        if alg is None:
            alg = direct

        # algorithm arguments
        alg_args = dict(
            reactants = self.reactants,
            reaction_matrix = self.reaction_matrix,
            x0 = self.x0,
            k = self.k,
            t_max = self.t_max,
            output = self.output.create_empty(),
            **kwargs)

        list_ts = []
        list_xs = []
        # create tasks
        tasks = []
        for _ in range(n_reps):
            task = SimulationTask(alg, alg_args)
            tasks.append(task)

        # run
        ret = self.engine.execute(tasks)

        # collect results
        list_ts = []
        list_xs = []
        for ts, xs in ret:
            list_ts.append(ts)
            list_xs.append(xs)
        
        return FullResult(list_ts, list_xs, self.t_max)

