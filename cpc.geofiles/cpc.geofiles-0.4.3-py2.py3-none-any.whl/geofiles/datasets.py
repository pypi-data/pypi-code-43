"""
Defines a Dataset object. Datasets contain one or more data arrays, QC info, etc.
"""

# Third-party
import numpy as np


class Dataset:
    """
    Base Dataset class
    """
    def __init__(self, data_type=None):
        self.data_type = data_type
        self.dates_with_files_not_loaded = set()
        self.files_not_loaded = set()
        self.dates_loaded = set()


class Observation(Dataset):
    """
    Observation Dataset
    """
    def __init__(self, obs=None):
        Dataset.__init__(self, data_type='observation')
        self.data_type = 'observation'
        self.obs = obs


class Forecast(Dataset):
    """
    Forecast Dataset
    """
    def __init__(self):
        Dataset.__init__(self, data_type='forecast')
        self.data_type = 'forecast'


class EnsembleForecast(Forecast):
    """
    Ensemble Forecast Dataset
    """
    def __init__(self, ens=None, ens_mean=None, ens_spread=None):
        Forecast.__init__(self)
        self.ens = ens
        self._ens_mean = ens_mean
        self._ens_spread = ens_spread

    def get_ens_mean(self):
        """
        Returns the ensemble mean

        Since ens_mean is defined as a property which calls this method, it won't take up memory
        by default

        ### Returns

        - array: ensemble mean
        """
        return np.nanmean(self.ens, axis=1) if self._ens_mean is None else self._ens_mean

    ens_mean = property(get_ens_mean)

    def get_ens_spread(self):
        """
        Returns the ensemble spread

        Since ens_spread is defined as a property which calls this method, it won't take up memory
        by default

        ### Returns

        - array: ensemble spread
        """
        return np.nanstd(self.ens, axis=1) if self._ens_spread is None else self._ens_spread

    ens_spread = property(get_ens_spread)


class DeterministicForecast(Forecast):
    """
    Ensemble Forecast Dataset
    """
    def __init__(self, fcst=None):
        Forecast.__init__(self)
        self.fcst = fcst


class Climatology(Dataset):
    """
    Climatology Dataset
    """
    def __init__(self, climo=None):
        Dataset.__init__(self, data_type='climatology')
        self.data_type = 'climatology'
        self.climo = climo
