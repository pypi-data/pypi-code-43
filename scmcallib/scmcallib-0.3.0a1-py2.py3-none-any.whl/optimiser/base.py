class BaseOptimiser(object):
    """Base class for various optimising backends"""

    name = "base"

    def find_best_fit(self, evaluator, x0, **kwargs):
        raise NotImplementedError

    def minimise(self, evaluator, x0, **kwargs):
        raise NotImplementedError

    def process_minimisation_results(self, res):
        raise NotImplementedError
