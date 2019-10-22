import numpy as np
from scipy.special import lpmn


class MeasureData():
    """
    Mother class of GHData and TSData. Handles the measure data.
    """
    def __array_wrap__(self, result):
        """
        Reimplementation of __array_wrap__ Numpy method.

        :param result: result to add to data
        :type result: any
        :return: data + result
        :rtype: np.array
        """
        return np.array(self.data + result)

    def __init__(self, shape, lmax, PnmNorm,
                 units=None, gridth=None, gridph=None):
        """
        Constructor of MeasureData. Set all members.

        :param shape: shape of the data
        :type shape: tuple
        :param lmax: maximum degree of the measure
        :type lmax: int
        :param PnmNorm: normalisation to use for Legendre polynomials
        :type PnmNorm: function
        :param units: unit of measure (default=None)
        :type units: str
        :param gridth: grid where thetas are evaluated (default=None)
        :type gridth: np.array
        :param gridph: grid where phis are evaluated (default=None)
        :type gridph: np.array
        """
        self.data = np.zeros(shape)
        self.lmax = lmax
        self.PnmNorm = PnmNorm
        self.computingState = 0
        self.cachedRThetaPhiData = {}
        self.cachedRThetaPhiData_mean = {}
        self.units = units
        self.has_grid = False
        self.th = None
        self.ph = None
        if gridth is not None and gridph is not None:
            self.setGrid(gridth, gridph)

    def truncate(self, lmax):
        """ Updates the data to keep only the data corresponding to l<lmax
        :param lmax: new maximum degree
        :type lmax: int
        """
        if lmax > self.lmax:
            print("WARNING: truncation should be less that %i"%self.lmax)
            return
        self.lmax = lmax
        self.initMeasure()
        self.setData(self.data)

    def setGrid(self, gridth, gridph):
        """ Saves the theta and phi grids (and their dimensions) given when building the data.
        :param gridth: grid where thetas are evaluated
        :type gridth: np.array
        :param gridph: grid where phis are evaluated
        :type gridph: np.array
        """
        self.th = gridth
        self.ph = gridph
        self.nth = self.th.shape[0]
        self.nph = self.ph.shape[0]
        self.has_grid = True

    def computePnm(self, th):
        """ Computes the associated Legendre polynomials for a given theta.
        :param th: theta where Pnm are evaluated
        :type th: float
        :return: list of the Legendre polynomial
        :rtype:
        """
        z = np.cos(th)
        # Scipy function lpmn computes the Legendre polynomials
        # and their derivative for all orders 0..lmax and degrees 0..lmax
        Pnm, dPnm = lpmn(self.lmax, self.lmax, z)
        # Apply the chosen normalisation on Pnm
        # TODO : Check if normalisation exists
        norm_constants = self.PnmNorm(self.lmax)
        Pnm *= norm_constants
        # The derivative should be given wrt. theta (python gives it wrt. z)
        dPnm *= -np.sin(th)*norm_constants

        # Reshape (l,m) to k
        Pnmk = Pnm[self.m, self.l]
        dPnmk = dPnm[self.m, self.l]

        return Pnmk, dPnmk

    def computeGridPnm(self):
        """ Computes associated Legendre polynomials on the theta grid stored in self.th. """
        if not self.has_grid:
            raise ValueError("Can not compute Pnm along grid, data has no defined real space (th,ph) grid")
        self.Pnm = np.zeros((self.nth, self.nk))
        self.dPnm = np.zeros((self.nth, self.nk))
        for i_theta, theta in enumerate(self.th):
            self.Pnm[i_theta], self.dPnm[i_theta] = self.computePnm(theta)

    def clearCache(self):
        """ Clears the cached data (usually called when setting new data) """
        self.cachedRThetaPhiData = {}
        self.cachedRThetaPhiData_mean = {}

    def getComponentsToCompute(self, r, component):
        """ Returns the list of components necessary to compute component.

        :param r: Radius of computation
        :type r: float
        :param component: Component to compute
        :type component: str
        :return: First one lists the components to compute, \
                 second one the components that are computing (cache is created but is None)
        :rtype: list, list
        """

        # Initialise the cached data
        if r not in self.cachedRThetaPhiData:
            self.cachedRThetaPhiData[r] = {}

        components = [component]
        # Check if additional components are needed (r and th and ph for norm)
        if component == "norm":
            for additionalComponent in self.components:
                components.append(additionalComponent)

        toCompute = []
        computing = []

        # Check if the computation states of the asked components
        for c in components:
            # If no cached data exists, add c to the components to compute
            if c not in self.cachedRThetaPhiData[r]:
                toCompute.append(c)
            # If cached data exists but is None it means that c is being computed
            elif self.cachedRThetaPhiData[r][c] is None:
                computing.append(c)

        return toCompute, computing

    def isAlreadyComputed(self, r, component):
        """ Tells if a component is to be computed or being computed.

        :param r: Radius of computation
        :type r: float
        :param component: Component to check
        :type component: str
        :return: First bool tells if the component is to be computed, \
                 second one tells if the component is being computed
        :rtype: bool,bool
        """
        toCompute, computing = self.getComponentsToCompute(r, component)
        return len(toCompute) > 0, len(computing) > 0

    def getRThetaPhiGridData(self, r, itime, removemean, component):
        """
        Computes the data on the angular grid for a given grid and caches it.

        :param r: radius of computation
        :type r: float
        :param itime: index of the computation date
        :type itime: int
        :param removemean: indicating if the mean should be removed when computing
        :type removemean: bool
        :param component: component to compute
        :type component: str
        :return: computed data
        :rtype: np.array
        """
        if not self.has_grid:
            raise ValueError("Can not get grid data, data has no defined real space (th,ph) grid")
        toCompute, computing = self.getComponentsToCompute(r, component)

        for component in toCompute:
            self.cachedRThetaPhiData[r][component] = None

        if len(toCompute) > 0:
            result = self.computeRThetaPhiData(r, self.th, self.ph, toCompute, usegridPnm=True, computeallrealisation=False, irealisation=-1)
            for component in toCompute:
                print("Preparing to cache data for ", component) # DEBUG
                self.cachedRThetaPhiData[r][component] = result[component]
                if(component == "norm"): print(result[component])

            self.calculateTemporalMean(r, toCompute)

        if removemean:
            if component == "norm":
                return self.computeNorm(r, itime)
            else:
                return self.cachedRThetaPhiData[r][component][itime] - self.cachedRThetaPhiData_mean[r][component]
        else:
            return self.cachedRThetaPhiData[r][component][itime]

    def computeSpectra(self, spectraType, spectraDate, itime):
        self.computingState = 0

        if spectraType == "spectraofmean":
            # Do ensemble AND temporal mean
            if self.has_realisations:
                mean_gauss_coefs = self.data.mean(axis=(0, 2))
            # Do temporal mean if no realisations
            else:
                mean_gauss_coefs = self.data.mean(axis=0)

            self.computingState = 50
            # Compute the spectra of the mean
            degrees, spectrum_to_return = self.computeLowes(mean_gauss_coefs, squared=False)

        elif spectraType == "meanofspectra":
            squared_data = np.square(self.data)

            n_times = squared_data.shape[0]

            if self.has_realisations:
                n_realisations = squared_data.shape[2]
                full_lowes_spectrum = np.zeros((n_times, n_realisations, self.lmax))

                for i_t in range(0, n_times):
                    self.computingState = i_t / n_times * 100
                    for i_real in range(0, n_realisations):
                        degrees, full_lowes_spectrum[i_t, i_real] = self.computeLowes(squared_data[i_t, :, i_real], squared=True)

                # Do temporal and ensemble mean of the computed spectra
                spectrum_to_return = full_lowes_spectrum.mean(axis=(0, 1))
            else:
                full_lowes_spectrum = np.zeros((n_times, self.lmax))

                for i_t in range(0, n_times):
                    self.computingState = i_t / n_times * 100
                    degrees, full_lowes_spectrum[i_t] = self.computeLowes(squared_data[i_t, :], squared=True)

                # Do temporal  mean of the computed spectra
                spectrum_to_return = full_lowes_spectrum.mean(axis=0)

        elif spectraType == "deviation":
            if self.has_realisations:
                mean_gauss_coefs = self.data.mean(axis=2)
            else:
                raise ValueError('Cannot compute deviation if the measure has no realisation.')

            n_realisations = self.data.shape[2]
            sq_deviation_gauss = np.zeros_like(self.data)
            for i_real in range(0, n_realisations):
                self.computingState = i_real / n_realisations * 50
                sq_deviation_gauss[:, :, i_real] = np.square(self.data[:, :, i_real] - mean_gauss_coefs)

            n_times = self.data.shape[0]
            full_lowes_spectrum = np.zeros((n_times, n_realisations, self.lmax))

            for i_t in range(0, n_times):
                self.computingState = 50 + i_t / n_times * 50
                for i_real in range(0, n_realisations):
                    degrees, full_lowes_spectrum[i_t, i_real] = self.computeLowes(sq_deviation_gauss[i_t, :, i_real], squared=True)

            # Do temporal and ensemble mean of the computed spectra
            spectrum_to_return = full_lowes_spectrum.mean(axis=(0, 1))

        elif spectraType == "dated":

            if self.has_realisations:
                gauss_coefs = self.data.mean(axis=2)
            else:
                gauss_coefs = self.data

            self.computingState = 50
            degrees, spectrum_to_return = self.computeLowes(gauss_coefs[itime], squared=False)

        else:
            raise ValueError('Spectra type not understood')

        self.computingState = 100

        return degrees, spectrum_to_return

    def computeLowes(self, gauss_coefs, squared):
        degrees = self.l

        if degrees.shape != gauss_coefs.shape or degrees.ndim != 1:
            raise ValueError(
                'Problem while computing Lowes spectrum. Got {} and {} that are not the same or not unidimensionnal'.format(
                    degrees.shape, gauss_coefs.shape))

        if not squared:
            squared_gauss_coefs = np.square(gauss_coefs)
        else:
            squared_gauss_coefs = gauss_coefs

        lowes_spectrum = np.zeros(self.lmax, dtype=np.float64)

        for i_l, l in enumerate(degrees):
            # Indexes of arrays start from 0 so the index is l-1
            lowes_spectrum[l - 1] += self._LowesPrefactor(l) * squared_gauss_coefs[i_l]

        return np.unique(degrees), lowes_spectrum

    def calculateTemporalMean(self, r, components):
        """
        Computes the temporal mean and stores it in the cache.

        :param r: radius where to compute the norm
        :type r: float
        :param components: list of components for which the norm should be comuputed
        :type components: list
        """
        if r not in self.cachedRThetaPhiData_mean:
            self.cachedRThetaPhiData_mean[r] = {}

        for component in components:
            self.cachedRThetaPhiData_mean[r][component] = np.mean(self.cachedRThetaPhiData[r][component], axis=0)

    def expand_dims(self, v):
        """
        Returns a copy of v with expanded dimensions to fit realisations

        :param v: Numpy array to expand
        :type v: np.ndarray (Ndim)
        :return: np.ndarray (1 x Ndim x 1)
        """
        return np.expand_dims(np.expand_dims(v.copy(), 1), 0)

