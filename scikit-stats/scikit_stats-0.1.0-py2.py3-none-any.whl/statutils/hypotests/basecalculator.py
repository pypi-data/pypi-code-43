#!/usr/bin/python
from typing import Dict, Union, Optional, Tuple

import numpy as np
from .parameters import POI
from zfit.core.loss import BaseLoss
from zfit.minimizers.minimizer_minuit import MinuitMinimizer
from zfit.minimizers.fitresult import FitResult
from zfit.minimizers.baseminimizer import BaseMinimizer
from contextlib import ExitStack


def q(cls, nll1: np.array, nll2: np.array, bestfit, poival, onesided=True,
      onesideddiscovery=False) -> np.array:
    """ Compute difference between log-likelihood values."""
    q = nll1 - nll2
    sel = ~(np.isnan(q) | np.isinf(q))
    q = q[sel]
    if isinstance(bestfit, np.ndarray):
        bestfit = bestfit[sel]
    zeros = np.zeros(q.shape)

    if onesideddiscovery:
        condition = (bestfit < poival) | (q < 0)
        q = np.where(condition, zeros, q)
    elif onesided:
        condition = (bestfit > poival) | (q < 0)
        q = np.where(condition, zeros, q)
    else:
        q = q

    return q


def pll(minimizer, loss, poi) -> float:
    """ Compute minimum profile likelihood for given parameters values. """
    with ExitStack() as stack:
        param = poi.parameter
        stack.enter_context(param.set_value(poi.value))
        param.floating = False
        minimum = minimizer.minimize(loss=loss)
        param.floating = True
    return minimum.fmin


class BaseCalculator(object):
    # TODO allow more than one parameter of interest

    def __init__(self, input: Union[BaseLoss, FitResult], minimizer: Optional[BaseMinimizer] = MinuitMinimizer):
        """Base class for calculator.

            Args:
                input (`zfit.core.BaseLoss`/`zfit.minimizers.fitresult import FitResult`): loss
                minimizer (`zfit.minimizers.baseminimizer.BaseMinimizer`, optionnal): minimizer to use to find
                    loss function minimun
        """

        if isinstance(input, FitResult):
            self._loss = input.loss
            self._bestfit = input
        else:
            self._loss = input
            self._bestfit = None
        self._minimizer = minimizer()
        self.minimizer.verbosity = 0

        # cache of the observed nll values
        self._obs_nll = {}

    @property
    def loss(self):
        return self._loss

    @property
    def minimizer(self):
        return self._minimizer

    @property
    def bestfit(self):
        """
        Returns the best fit values.
        """
        if getattr(self, "_bestfit", None):
            return self._bestfit
        else:
            print("Get fit best values!")
            self.minimizer.verbosity = 5
            mininum = self.minimizer.minimize(loss=self.loss)
            self.minimizer.verbosity = 0
            self._bestfit = mininum
            return self._bestfit

    @bestfit.setter
    def bestfit(self, value):
        """
        Set the best fit values.

            Args:
                value (`zfit.minimizers.fitresult import FitResult`)
        """
        if not isinstance(value, FitResult):
            raise ValueError()
        self._bestfit = value

    @property
    def model(self):
        return self.loss.model

    @property
    def constraints(self):
        return self.loss.constraints

    def obs_nll(self, poi):
        """ Compute observed negative log-likelihood values."""
        ret = np.empty(len(poi))
        for i, p in enumerate(poi):
            if p not in self._obs_nll.keys():
                nll = pll(self.minimizer, self.loss, p)
                self._obs_nll[p] = nll
            ret[i] = self._obs_nll[p]
        return ret

    def qobs(self, poinull, onesided=True, onesideddiscovery=False, qtilde=False):
        """ Compute observed $$\\Delta$$ log-likelihood values."""
        print("Compute qobs for the null hypothesis!")

        poiparam = poinull.parameter
        bf = self.bestfit.params[poiparam]["value"]
        if qtilde and bf < 0:
            bestfitpoi = POI(poiparam, 0)
        else:
            bestfitpoi = POI(poiparam, bf)
            self._obs_nll[bestfitpoi] = self.bestfit.fmin

        nll_poinull_obs = self.obs_nll(poinull)
        nll_bestfitpoi_obs = self.obs_nll(bestfitpoi)
        qobs = q(nll_poinull_obs, nll_bestfitpoi_obs, bestfitpoi.value, poinull.value, onesided=onesided,
                 onesideddiscovery=onesideddiscovery)

        return qobs

    def pvalue(self, poinull, poialt=None, qtilde=False, onesided=True,
               onesideddiscovery=False) -> Tuple[np.array, np.array]:
        """Computes pvalues for the null and alternative hypothesis.

        Args:
            poinull (Iterable[`hypothests.POI`]): parameters of interest for the null hypothesis
            poialt (Iterable[`hypothests.POI`], optionnal): parameters of interest for the alternative hypothesis
            qtilde (bool, optionnal): if `True` use the $$\tilde{q}$$ test statistics else (default) use
                the $$q$$ test statistic
            onesided (bool, optionnal): if `True` (default) computes onesided pvalues
            onesideddiscovery (bool, optionnal): if `True` (default) computes onesided pvalues for a discovery
                test
        Returns:
            Tuple(`numpy.array`, `numpy.array`): pnull, palt
        """
        return self._pvalue(poinull=poinull, poialt=poialt, qtilde=qtilde, onesided=onesided,
                            onesideddiscovery=onesideddiscovery)

    def _pvalue(self, poinull, poialt, qtilde, onesided, onesideddiscovery):

        raise NotImplementedError

    def expected_pvalue(self, poinull, poialt, nsigma, CLs=False) -> Dict[int, np.array]:
        """Computes the expected pvalues and error bands for different values of $$\\sigma$$ (0=expected/median)

        Args:
            poinull (Iterable[`hypothests.POI`]): parameters of interest for the null hypothesis
            poialt (Iterable[`hypothests.POI`], optionnal): parameters of interest for the alternative hypothesis
            nsigma (`numpy.array`): array of values of $$\\sigma$$ to compute the expected pvalue
            CLs (bool, optionnal): if `True` computes pvalues as $$p_{cls}=p_{null}/p_{alt}=p_{clsb}/p_{cls}$$
                else as $$p_{clsb} = p_{null}$

        Returns:
            Dict($$\\sigma$$, `numpy.array`): dictionnary of pvalue arrays for each $$\\sigma$$ value
        """
        return self._expected_pvalue(poinull=poinull, poialt=poialt, nsigma=nsigma, CLs=CLs)

    def _expected_pvalue(self, poinull, poialt, nsigma, CLs):

        raise NotImplementedError

    def expected_poi(self, poinull, poialt, nsigma, alpha=0.05, CLs=False):
        """Computes the expected parameter of interest values such that the expected p_values == $$\alpha$$
        for different values of $$\\sigma$$ (0=expected/median)
        """

        return self._expected_poi(poinull=poinull, poialt=poialt, nsigma=nsigma, alpha=alpha, CLs=CLs)

    def _expected_poi(self, poinull, poialt, nsigma, alpha, CLs):

        raise NotImplementedError
