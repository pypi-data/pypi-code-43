import numpy as np
from .measuredata import MeasureData
from .normPnm import semiNormalisedSchmidt
from webgeodyn.constants import rE


class GHData(MeasureData):
    """ Class handling MF or SV, DIFF, ER data (g and h harmonics coefficients)."""
    def __init__(self, data, lmax, units, measureType, PnmNorm=semiNormalisedSchmidt, gridth=None, gridph=None):
        """ Constructor of GHData class
        :param data: measure data
        :type data: np.array
        :param lmax: maximum degree
        :type lmax: int
        :param units: units of the measure
        :type units: str
        :param measureType: type of the measure
        :type measureType: str ('SV', 'MF' or 'LOD')
        :param PnmNorm: normalisation to use (default: semiNormalisedSchmidt)
        :type PnmNorm: function
        :param gridth: grid on which the theta are evaluated
        :type gridth: np.array
        :param gridph: grid on which the theta are evaluated
        :type gridph: np.array
        """
        super().__init__(data.shape, lmax, PnmNorm, units, gridth, gridph)
        self.measureType = measureType
        self.initMeasure()
        self.setData(data)

    def initMeasure(self):
        """ Initiates the measure parameters : components, coefs and grids if needed. Called in __init__. """
        self.nk = self.lmax * (self.lmax + 2)
        self.components = ["r", "th", "ph"]
        # Only one coef for LOD
        if self.measureType == "LOD":
            self.coefs_list = ["LOD"]
        elif self.measureType == "EF":
            self.coefs_list = ["q", "s"]
        else:
            self.coefs_list = ["g", "h"]
        self.initMatrices()
        if self.th is not None and self.ph is not None:
            self.computeGridPnm()

    def setData(self, data):
        """ Sets the input data and extracts the time array and temporal mean of the coefs. Called in __init__.
        :param data: measure data
        :type data: np.array
        """
        #  Clear cached data to avoid keeping old data
        self.clearCache()
        self.data = data[:, :self.nk]
        self.ntimes = data.shape[0]
        self.coefs_mean = np.mean(self.data, axis=0)
        self.has_realisations = False
        if self.data.ndim >= 3:
            self.has_realisations = True

    def lm2k(self, l, m, coef):
        """ Computes the index k of a coef given its name, its degree l and its order m. Returns None if no coef exists.
        :param l: spherical harmonic degree
        :type l: int
        :param m: spherical harmonic order
        :type m: int
        :param coef: type of coef
        :type coef: str ('g', 'h' or 'LOD')
        :return: index of the coef in data
        :rtype: int or None
        """
        if m > l:
            return None
        if m == 0:
            if coef == "h" or coef == "s":
                return None
            return int(l ** 2 - 1)
        if coef == "g" or coef == "q":
            return int(l ** 2 + 2 * m - 2)
        if coef == "h" or coef == "s":
            return int(l ** 2 + 2 * m - 1)
        if coef == "LOD":
            return 0

    def k2lm(self, k):
        """ Returns the degree, the order and the name of a coef of given k.
        :param k: index of the coef
        :type k: int
        :return: degree, order and name of the coef of index k
        :rtype: int, int, str
        """
        return self.l[k], self.m[k], self.coefname[k]

    def initMatrices(self):
        """ Creates the matrices that allow to identify and index the spherical
        harmonic coefficients g and h. Called in __init__.
        """
        k = np.arange(self.lmax * (self.lmax + 2))
        self.l = np.floor(np.sqrt(k + 1)).astype(int)
        kl2 = (k + 1 - self.l ** 2)
        self.is_h = np.logical_and(np.mod(kl2, 2) == 0, kl2 != 0)
        self.is_g = np.logical_not(self.is_h)
        self.coefname = np.where(self.is_g, "g", "h")
        self.m = np.ceil(kl2 / 2).astype(int)

    def set_expand_dims(self, useRealisations):
        """
        Expands the dims of degrees and orders to be able to broadcast realisations. Also creates the l+1 array.

        :param useRealisations: expands only if this is True
        :type useRealisations: bool
        """
        if useRealisations:
            # for broadcast dimension (coef is the second dimension on 3)
            self.is_h_ = self.expand_dims(self.is_h)
            self.is_g_ = self.expand_dims(self.is_g)
            self.m_ = self.expand_dims(self.m)
            self.l_ = self.expand_dims(self.l)
        else:
            self.is_h_ = self.is_h
            self.is_g_ = self.is_g
            self.m_ = self.m
            self.l_ = self.l
        self.lplus1 = self.l_ + 1

    def computeRThetaPhiData(self, r, thlist, phlist, components=None, usegridPnm=False, computeallrealisation=False,
                             irealisation=-1):
        """ Computes the components of the quantity described by the spherical harmonic potential
        given radius, a colatitude list and a longitude list.

        :param r: radius at which the computation is done
        :type r: float
        :param thlist: list containing the colatitudes at which the computation is done
        :type thlist: list
        :param phlist: list containing the longitudes at which the computation is done
        :type phlist: list
        :param components: list of components to compute (default to ["r", "th", "ph", "norm"])
        :type components: list
        :param usegridPnm: boolean indicating if the Pnm computed previously should be used (default=False)
        :type usegridPnm: bool
        :param computeallrealisation: boolean indicating if the computation should be on all realisations or on the mean (default=False)
        :type computeallrealisation: bool
        :param irealisation: index of the realisation to use (default=-1 and takes the mean instead)
        :type irealisation: int
        :return: result of the computation
        :rtype: dict of np.array of dim (date x n_ph x n_th)
        """
        # Default value of components
        if components is None:
            components = ["r", "th", "ph", "norm"]

        if ("norm" in components) and not usegridPnm:  # if norm, require th and ph component
            for component in self.components:
                if component not in components:
                    components.append(component)

        if self.has_realisations and not computeallrealisation:
            if irealisation < 0:
                realisation_data = np.mean(self.data, axis=2)
            else:
                realisation_data = self.data[:, :, irealisation]
        else:
            realisation_data = self.data

        if self.has_realisations and computeallrealisation:
            result = {component: np.zeros((self.ntimes, len(thlist), len(phlist), realisation_data.shape[2]))
                      for component in components}
            # Use expanded arrays to fit dimension of realisations
            self.set_expand_dims(True)
        else:
            result = {component: np.zeros((self.ntimes, len(thlist), len(phlist))) for component in components}
            self.set_expand_dims(False)

        # Compute a handy prefactor before looping
        rEr_lplus2 = (rE / r) ** (self.l_ + 2)

        # Loop on the colatitude list
        for ith, th in enumerate(thlist):
            if usegridPnm:
                if not self.has_grid:
                    raise ValueError("The data has no real space (th,ph) grid")
                self.computingState = (ith + 1) / self.nth * 100
            sinth = np.sin(th)
            if usegridPnm:
                Pnm = self.Pnm[ith]
                dPnm = self.dPnm[ith]
            else:
                Pnm, dPnm = self.computePnm(th)

            if self.has_realisations and computeallrealisation:
                Pnm = self.expand_dims(Pnm)
                dPnm = self.expand_dims(dPnm)

            # Loop on the longitude list
            for iph, ph in enumerate(phlist):
                # Calculate the radial component
                if "r" in components:
                    fac_gnm_r = self.lplus1 * rEr_lplus2 * np.cos(self.m_ * ph) * self.is_g_
                    fac_hnm_r = self.lplus1 * rEr_lplus2 * np.sin(self.m_ * ph) * self.is_h_
                    result["r"][:, ith, iph] = np.sum(
                        ((fac_gnm_r + fac_hnm_r) * realisation_data) * Pnm,
                        axis=1)

                # Calculate the component along theta
                if "th" in components:
                    fac_gnm_th = - rEr_lplus2 * np.cos(self.m_ * ph)
                    fac_hnm_th = - rEr_lplus2 * np.sin(self.m_ * ph)
                    result["th"][:, ith, iph] = np.sum(
                        (fac_gnm_th * (realisation_data * self.is_g_)
                         + fac_hnm_th * (realisation_data * self.is_h_))
                        * dPnm,
                        axis=1)

                # Calculate the component along phi
                if "ph" in components:
                    fac_gnm_ph = rEr_lplus2 * self.m_ * np.sin(self.m_ * ph) / sinth
                    fac_hnm_ph = - rEr_lplus2 * self.m_ * np.cos(self.m_ * ph) / sinth
                    result["ph"][:, ith, iph] = np.sum(
                        (fac_gnm_ph * (realisation_data * self.is_g_)
                         + fac_hnm_ph * (realisation_data * self.is_h_))
                        * Pnm,
                        axis=1)

                # Calculate the norm of the obtained vector
                if "norm" in components:
                    if "r" in result:
                        resultr = result["r"][:, ith, iph]
                    else:
                        resultr = self.cachedRThetaPhiData[r]["r"][:, ith, iph]

                    if "th" in result:
                        resultth = result["th"][:, ith, iph]
                    else:
                        resultth = self.cachedRThetaPhiData[r]["th"][:, ith, iph]

                    if "ph" in result:
                        resultph = result["ph"][:, ith, iph]
                    else:
                        resultph = self.cachedRThetaPhiData[r]["ph"][:, ith, iph]

                    result["norm"][:, ith, iph] = np.sqrt(resultr ** 2 + resultth ** 2 + resultph ** 2)

        # End of angular loops

        return result

    def _LowesPrefactor(self, l):
        return l + 1

    def computeNorm(self, r, itime):
        """
        Computes norm at a certain time and place using cached data.

        :param r: radius at which to evaluate the norm
        :type r: float
        :param itime: index of time
        :type itime: int
        :return: Numpy array
        :rtype: np.array
        """
        return np.sqrt((self.cachedRThetaPhiData[r]["th"][itime] - self.cachedRThetaPhiData_mean[r]["th"]) ** 2
                       + (self.cachedRThetaPhiData[r]["ph"][itime] - self.cachedRThetaPhiData_mean[r]["ph"]) ** 2
                       + (self.cachedRThetaPhiData[r]["r"][itime] - self.cachedRThetaPhiData_mean[r]["r"]) ** 2)
