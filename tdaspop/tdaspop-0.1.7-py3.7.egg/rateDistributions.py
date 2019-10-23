"""
"""
from __future__ import absolute_import, print_function, division
__all__ = ['PowerLawRates']
import numpy as np
from astropy.cosmology import Planck15
from . import BaseRateDistributions


class PowerLawRates(BaseRateDistributions):
    """
    Concrete implementation of `RateDistributions` providing rates and TDO
    numbers and samples as a function of redshift when the volumetric rate can
    be expressed as a power law in redshift. This is instantiated by the following
    parameters and has the attributes and methods listed


    Parameters
    ----------
    rng : `np.random.RandomState`
        random state needed for generation
    cosmo : `astropy.cosmology` instance, defaults to Planck15
        Cosmology used in the calculation of volumes etc. 
    alpha_rate :`np.float` defaults to 2.6e-5
    beta_rate : `np.float` defaults to 1.5
    zbin_edges : sequence of floats, defaults to `None`
        Available method of having non-uniform redshift bins by specifying
        the edgees of the bins. To specify `n` bins, this sequence must have a
        length of `n + 1`. Has higher preference compared to setting values for
        `zlower`, `zhigher` and `numBins` which necessarily require uniformly
        spaced bin, and must be set to `None` for other methods to be used.
    zlower : `np.float`, defaults to 1.0e-8 
        Lower end of the redshift distribution, which is used in one of the
        available methods to set the redshift bins. Must be used in concert
        with `zhigher`, and `numBins` with `zbin_edges` set to `None` for this
        to work.
    zhigher : `np.float`, defaults to 1.4,
        Higher end of the redshift distribution, which is used in one of the
        available methods to set the redshift bins. Must be used in concert
        with `zlower`, and `numBins` with `zbin_edges` set to `None` for this
        to work.
    num_bins : `int`, defaults to 28,
        number of bins, assuming uniform redshift bins as one of the variables
        for use in setting the redshift bins. Must be used in concert
        with `zlower`, and `zhigher` with `zbin_edges` set to `None` for this
        to work.
    survey_duration :`np.float`, unit of years, defaults to 10.0
        number of years of survey
    sky_area : `np.float`, unit of sq deg,  defaults to 10.0 
        Used if `skyFraction` is set to `None`. The area of the sky over which
        the samples are calculated. Exactly one of `sky_area` and `skyFraction`
        must be provided.
    sky_fraction : `np.float`, defaults to `None`
        if not `None` the fraction of the sky over which samples are studied.
        if `None`, this is set by `sky_area`. Exactly one of `sky_area` and
        `skyFraction` must be provided.

    Attributes
    ----------
    - rate: The variable rate is a single power law with numerical
        coefficients (alpha, beta)  passed into the instantiation. The rate is
        the number of variables at redshift z per comoving volume per unit
        observer time over the entire sky expressed in units of 
        numbers/Mpc^3/year 
    - A binning in redshift is used to perform the calculation of the expected
        number of variables.
    - It is assumed that the change of rates and volume within a redshift bin
        is negligible enough that samples to the true distribution may be drawn
        by obtaining number of variable samples of z from a uniform distribution
        within the z bin.
    - The expected number of variables in each of these redshift bins is
        computed using the rate above at the midpoint of the redshift bin, using
        a cosmology to compute the comoving volume for the redshift bin
    - The actual numbers of variables are determined by a Poisson Distribution
        using the expected number of variables in each redshift bin,
        determined with a random state passed in as an argument.
        This number must be integral.

    """
    def __init__(self,
                 rng,
                 cosmo=Planck15,
                 alpha_rate=2.6e-5,
                 beta_rate=1.5,
                 zbin_edges=None,
                 zlower=1.0e-8,
                 zhigher=1.4,
                 num_bins=20,
                 survey_duration=10.,
                 sky_area=10.0, # Unit of degree square
                 sky_fraction=None):
        """
        Basic constructor for class. Parameters are in the class definition.
        """
        self._rng = rng
        self._cosmo = cosmo
        self.alpha_rate = alpha_rate
        self.beta_rate = beta_rate
        self.DeltaT = survey_duration
        self._zsamples = None

        # Set the zbins depending on which parameters were provided
        self._set_zbins(zbin_edges, zlower, zhigher, num_bins)

        # Set the sky fraction depending on which parameters were provided
        self._set_skyfraction(sky_area, sky_fraction)
        self._num_sources = None
        _ = self.num_sources_realized

    @property
    def randomState(self):
        if self._rng is None:
            raise ValueError('rng must be provided')
        return self._rng

    @property
    def cosmology(self):
        return self._cosmo

    def _set_skyfraction(self, sky_area, sky_fraction):
        """
        Private helper function to handle the sky_area and sky_fraction
        """
        assert not bool(sky_fraction and sky_area), "Both `sky_fraction` and `sky_area` cannot be specified" 
        assert bool(sky_fraction or sky_area), "At least one of `sky_fraction` and `sky_area` have to be specified"
        if sky_fraction is None:
            self._sky_area = sky_area
            self._sky_fraction = self.sky_area * np.radians(1.)**2.0  / 4.0 / np.pi

        if sky_area is None:
            self._sky_fraction = sky_fraction 
            self._sky_area = self.sky_fraction / (np.radians(1.)**2.0  / 4.0 / np.pi)

        return None

    @property
    def sky_fraction(self):
        return self._sky_fraction

    @property
    def sky_area(self):
        """
        fraction of the sky
        """
        return self._sky_area

    def _set_zbins(self, zbin_edges, zlower, zhigher, num_bins):
        """
        """
        if zbin_edges is None:
            zbin_edges = np.linspace(zlower, zhigher, num_bins)

        assert len(zbin_edges) > 0
        
        self.zlower = zbin_edges.min()
        self.zhigher = zbin_edges.max()
        self.num_bins = len(zbin_edges) - 1
        self._zbin_edges = zbin_edges
        return None

    @property
    def zbin_edges(self):
        return self._zbin_edges

    def volumetric_rate(self, z):
        """
        The volumetric rate at a redshift z in units of number of TDOs/ comoving
        volume in Mpc^3/yr in rest frame years according to the commonly used
        power-law expression 

        .. math:: rate(z) = \alpha (h/0.7)^3 (1.0 + z)^\beta
        
        Parameters
        ----------
        z : array-like, mandatory 
            redshifts at which the rate is evaluated

        Examples
        --------
        """
        res = self.alpha_rate * (1.0 + z)**self.beta_rate
        res *= ((self.cosmology.h / 0.7) **3.)
        return res

    @staticmethod
    def volume_in_zshell(zbin_edges, cosmo, skyfrac):
        """returns the comoving volume for the redshift shells
        specified by `zbin_edges` for the cosmology `cosmo`
        and sky fraction `skyfrac`

        Paramters
        ---------
        zbin_edges : `np.ndarray` of floats
            edges of the redshift bins/shells.
        cosmo : `astropy.cosmology.cosmology` instance
            cosmology for which the comoving volumes will be
            calculated.
        skyfrac : `np.float`
            The sky fraction (area / total sky area) covered by
            this sample.
        """
        # Comoving volume of the univere in between zlower and zhigher
        vols = cosmo.comoving_volume(zbin_edges)

        # Comoving volume in each bin
        vol = np.diff(vols)
        vol *= skyfrac

        return vol
 
    @property
    def z_sample_sizes(self):
        """Number of TDO in each redshift bin with the bins being
        defined by the class parameters


        Returns
        -------
        num_in_volshells : `np.ndaray` of floats
            Expected number of objects in volume shells
            defined by the redshift bin edges.
        """
        DeltaT = self.DeltaT
        skyFraction = self.sky_fraction
        zbinEdges = self.zbin_edges
        z_mids = 0.5 * (zbinEdges[1:] + zbinEdges[:-1])

        vol = self.volume_in_zshell(zbinEdges, self.cosmology,
                                    self.sky_fraction)

        num_in_vol_shells = vol * self.volumetric_rate(z_mids)
        num_in_vol_shells *= DeltaT / (1.0 + z_mids)
        return num_in_vol_shells.value

    @property
    def num_sources_realized(self):
        """The number of TDO sources realized in each redshift bin set
        through a Poisson sampling of the expected number of sources.
        """
        if self._num_sources is None:
            self._num_sources = self.randomState.poisson(lam=self.z_sample_sizes)
        return self._num_sources

    @property
    def z_samples(self):
        if self._zsamples is None:
            zbinEdges =  self.zbin_edges
            num_sources = self.num_sources_realized
            x = zbinEdges[:-1]
            y = zbinEdges[1:]
            arr = (self.randomState.uniform(low=xx, high=yy, size=zz).tolist()
                                           for (xx, yy, zz) in zip(x,y, num_sources))
            self._zsamples = np.asarray(list(_x for _lst in arr
                                             for _x in _lst))
        return self._zsamples
