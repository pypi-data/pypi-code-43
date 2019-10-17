#    This file is part of qdpy.
#
#    qdpy is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of
#    the License, or (at your option) any later version.
#
#    qdpy is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with qdpy. If not, see <http://www.gnu.org/licenses/>.

"""A collection of all algorithms based on Evolutionary algorithms."""

__all__ = ["Evolution", "RandomSearchMutPolyBounded", "MutPolyBounded", "RandomSearchMutGaussian", "MutGaussian", "CMAES"]

########### IMPORTS ########### {{{1

from timeit import default_timer as timer
from typing import Optional, Tuple, List, Iterable, Iterator, Any, TypeVar, Generic, Union, Sequence, MutableSet, MutableSequence, Type, Callable, Generator, Mapping, MutableMapping, overload
import warnings
import numpy as np
import copy
from functools import partial
import random
from inspect import signature


from .base import *
from qdpy.utils import *
from qdpy.base import *
from qdpy.containers import *
from qdpy import tools


########### EVOLUTION CLASSES ########### {{{1

class Evolution(QDAlgorithm):
    """TODO"""
    _select_fn: Optional[Callable]
    _select_or_initialise_fn: Optional[Callable]
    _select_or_initialise_fn_nb_parameters: int
    _vary_fn: Callable[[IndividualLike], IndividualLike]
    _tell_fn: Optional[Callable]

    def __getstate__(self):
        odict = super().__getstate__()
        del odict['_select_fn']
        del odict['_select_or_initialise_fn']
        del odict['_vary_fn']
        del odict['_tell_fn']
        return odict

    def __init__(self, container: Container, budget: int,
            vary: Callable[[IndividualLike], IndividualLike],
            select: Optional[Callable[[Container], IndividualLike]] = None,
            select_or_initialise: Optional[Callable[[Container], Tuple[IndividualLike, bool]]] = None,
            tell: Optional[Callable] = None, **kwargs):
        super().__init__(container, budget, **kwargs)
        if select is not None and select_or_initialise is not None:
            raise ValueError("Only one of `select` and `select_or_initialise` can be provided.")
        self._select_fn = select
        self._select_or_initialise_fn = select_or_initialise
        self._vary_fn = vary # type: ignore
        self._tell_fn = tell # type: ignore
        # Find the number of parameters of self._select_or_initialise_fn
        if self._select_or_initialise_fn is not None:
            sig = signature(self._select_or_initialise_fn)
            self._select_or_initialise_fn_nb_parameters = len(sig.parameters)
            if self._select_or_initialise_fn_nb_parameters == 0:
                raise ValueError("`select_or_initialise` function must take at least one parameter.")

    def _internal_ask(self, base_ind: IndividualLike) -> IndividualLike:
        # Select the next individual
        perform_variation: bool = False
        if self._select_fn is not None:
            selected: IndividualLike = copy.deepcopy(self._select_fn(self.container))
            if not isinstance(selected, IndividualLike):
                if isinstance(selected, Sequence) and isinstance(selected[0], IndividualLike):
                    selected = selected[0]
                else:
                    raise RuntimeError("`select` function returned an unknown type of individual.")
            perform_variation = True
        elif self._select_or_initialise_fn is not None:
            if self._select_or_initialise_fn_nb_parameters == 1:
                selected, perform_variation = self._select_or_initialise_fn(self.container)
            elif self._select_or_initialise_fn_nb_parameters >= 2:
                selected, perform_variation = self._select_or_initialise_fn(self.container, base_ind)
            selected = copy.deepcopy(selected)
            if perform_variation and not isinstance(selected, IndividualLike):
                raise RuntimeError("`select_or_initialise` function returned an unknown type of individual.")
        else:
            raise RuntimeError("Either `select` or `select_or_initialise` must be provided.")

        # Vary the suggestion
        if perform_variation:
            varied = self._vary_fn(selected) # type: ignore
            if not isinstance(varied, IndividualLike):
                if is_iterable(varied) and isinstance(varied[0], IndividualLike):
                    varied = varied[0]
                elif is_iterable(varied):
                    pass # Try anyway
                else:
                    raise RuntimeError("`vary` function returned an unknown type of individual.")
                base_ind[:] = varied
            else:
                return varied
        else:
            if isinstance(selected, IndividualLike):
                return selected
            else:
                base_ind[:] = selected
        return base_ind

    def _internal_tell(self, individual: IndividualLike, added_to_container: bool) -> None:
        if self._tell_fn is not None:
            self._tell_fn(individual, added_to_container)




@registry.register
class RandomSearchMutPolyBounded(Evolution):
    """TODO"""
    ind_domain: DomainLike
    sel_pb: float
    init_pb: float
    mut_pb: float
    eta: float

    def __init__(self, container: Container, budget: int,
            dimension: int, ind_domain: DomainLike = (0., 1.),
            sel_pb: float = 0.5, init_pb: float = 0.5, mut_pb: float = 0.2, eta: float = 20.,
            **kwargs):
        self.ind_domain = ind_domain
        self.sel_pb = sel_pb
        self.init_pb = init_pb
        self.mut_pb = mut_pb
        self.eta = eta

        #init_fn = partial(np.random.uniform, ind_domain[0], ind_domain[1], dimension)
        init_fn = partial(lambda dim, base_ind: [random.uniform(ind_domain[0], ind_domain[1]) for _ in range(dim)], dimension)
        select_or_initialise = partial(tools.sel_or_init,
                sel_fn = tools.sel_random,
                sel_pb = sel_pb,
                init_fn = init_fn,
                init_pb = init_pb)
        vary = partial(tools.mut_polynomial_bounded, low=ind_domain[0], up=ind_domain[1], eta=eta, mut_pb=mut_pb)

        super().__init__(container, budget, dimension=dimension, # type: ignore
                select_or_initialise=select_or_initialise, vary=vary, **kwargs)


@registry.register
class MutPolyBounded(RandomSearchMutPolyBounded):
    """TODO"""
    def __init__(self, container: Container, budget: int,
            dimension: int, ind_domain: DomainLike = (0., 1.),
            mut_pb: float = 0.2, eta: float = 20., **kwargs):
        super().__init__(container, budget, dimension=dimension,
                ind_domain=ind_domain,
                sel_pb=1.0, init_pb=0.0,
                mut_pb=mut_pb, eta=eta, **kwargs)


@registry.register
class RandomSearchMutGaussian(Evolution):
    """TODO"""
    sel_pb: float
    init_pb: float
    mut_pb: float
    mu: float
    sigma: float

    def __init__(self, container: Container, budget: int,
            dimension: int, sel_pb: float = 0.5, init_pb: float = 0.5, mut_pb: float = 0.2,
            mu: float = 0., sigma: float = 1.0, **kwargs):
        self.sel_pb = sel_pb
        self.init_pb = init_pb
        self.mut_pb = mut_pb
        self.mu = mu
        self.sigma = sigma

        #init_fn = partial(np.random.normal, self.mu, self.sigma, dimension)
        init_fn = partial(lambda dim, base_ind: [random.normalvariate(self.mu, self.sigma) for _ in range(dim)], dimension)
        select_or_initialise = partial(tools.sel_or_init,
                sel_fn = tools.sel_random,
                sel_pb = sel_pb,
                init_fn = init_fn,
                init_pb = init_pb)
        vary = partial(tools.mut_gaussian, mu=mu, sigma=sigma, mut_pb=mut_pb)

        super().__init__(container, budget, dimension=dimension, # type: ignore
                select_or_initialise=select_or_initialise, vary=vary, **kwargs)


@registry.register
class MutGaussian(RandomSearchMutGaussian):
    """TODO"""
    def __init__(self, container: Container, budget: int,
            dimension: int, mut_pb: float = 0.2,
            mu: float = 0., sigma: float = 1.0, **kwargs):
        super().__init__(container, budget, dimension=dimension,
                sel_pb=1.0, init_pb=0.0,
                mut_pb=mut_pb, mu=mu, sigma=sigma, **kwargs)


try:
    import cma

    @registry.register
    class CMAES(QDAlgorithm):
        """TODO"""
        ind_domain: Optional[DomainLike]
        sigma0: float
        es: Any
        _pop_inds: MutableSequence[IndividualLike]
        _pop_fitness_vals: MutableSequence[Any]

        def __init__(self, container: Container, budget: int,
                dimension: int, ind_domain: Optional[DomainLike] = None,
                sigma0: float = 1.0,
                ignore_if_not_added_to_container: bool = False, **kwargs):
            super().__init__(container, budget, dimension=dimension, **kwargs)
            self.sigma0 = sigma0
            self.ind_domain = ind_domain
            self.ignore_if_not_added_to_container = ignore_if_not_added_to_container
            self._opts: MutableMapping[str, Any] = {}
            if ind_domain is not None:
                self._opts['bounds'] = list(ind_domain)
            if self._batch_size is not None:
                self._opts['popsize'] = self._batch_size
            self.es = cma.CMAEvolutionStrategy([0.] * dimension, sigma0, self._opts)
            self._pop_inds = []
            self._pop_fitness_vals = []
            if self._batch_size is None:
                self._batch_size = self.es.popsize

        def _internal_ask(self, base_ind: IndividualLike) -> IndividualLike:
            base_ind[:] = self.es.ask(1)[0]
            return base_ind

        def _internal_tell(self, individual: IndividualLike, added_to_container: bool) -> None:
            if self.ignore_if_not_added_to_container and not added_to_container:
                return
            self._pop_inds += [individual]
            self._pop_fitness_vals += [-1. * x for x in individual.fitness.values]
            if len(self._pop_inds) >= self.es.popsize:
                try:
                    self.es.tell(self._pop_inds, self._pop_fitness_vals)
                except RuntimeError:
                    pass
                else:
                    self._pop_inds.clear()
                    self._pop_fitness_vals.clear()


except ImportError:
    @registry.register # type: ignore
    class CMAES(QDAlgorithm): # type: ignore
        def __init__(self, *args, **kwargs):
            raise NotImplementedError("`CMAES` needs the 'cma' package to be installed and importable.")
        def _internal_ask(self, base_ind: IndividualLike) -> IndividualLike:
            raise NotImplementedError("`CMAES` needs the 'cma' package to be installed and importable.")




# MODELINE	"{{{1
# vim:expandtab:softtabstop=4:shiftwidth=4:fileencoding=utf-8
# vim:foldmethod=marker
