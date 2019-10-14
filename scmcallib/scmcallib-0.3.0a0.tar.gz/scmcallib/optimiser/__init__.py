from .scipy import OptimiserScipy
from .bayesopt import OptimiserBayesOpt

_optimisers = [OptimiserScipy, OptimiserBayesOpt]


def get_optimiser(optimiser_name):
    for o in _optimisers:
        if o.name == optimiser_name.lower():
            return o

    raise ValueError(
        "No optimiser named {}. Options include {}".format(
            optimiser_name, [m.name for m in _optimisers]
        )
    )
