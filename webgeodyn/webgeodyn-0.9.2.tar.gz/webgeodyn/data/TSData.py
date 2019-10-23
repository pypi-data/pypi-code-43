import numpy as np
from .measuredata import MeasureData
from .normPnm import semiNormalisedSchmidt
from webgeodyn.constants import rE, rC


# Data for U (tc,ts,sc,ss toroidal/poloidal harmonics coefficients)
class TSData(MeasureData):
    """ Class handling U (toroidal/poloidal harmonics coefficients)."""
    def __init__(self, data, lmax, units, measureType="U", PnmNorm=semiNormalisedSchmidt, gridth=None, gridph=None):
        """ Constructor of TSData class
        :param data: measure data
        :type data: np.array
        :param lmax: maximum degree
        :type lmax: int
        :param units: units of the measure
        :type units: str
        :param measureType: type of the measure (default = 'U')
        :type measureType: str ('U' or 'DIVHU')
        :param PnmNorm: normalisation to use (default: semiNormalisedSchmidt)
        :type PnmNorm: function
        :param gridth: grid on which the theta are evaluated (default: None)
        :type gridth: np.array
        :param gridph: grid on which the theta are evaluated (default: None)
        :type gridph: np.array
        """
        super().__init__(data.shape, lmax, PnmNorm, units, gridth, gridph)
        self.measureType = measureType
        self.initMeasure()
        self.setData(data)

    def initMeasure(self):
        """ Initiates the measure parameters : components, coefs and grids if needed. Called in __init__. """
        self.nk = 2 * self.lmax * (self.lmax + 2)
        self.components = ["th", "ph"]
        self.coefs_list = ["tc", "sc", "ts", "ss"]
        self.initMatrices()
        if self.th is not None and self.ph is not None:
            self.computeGridPnm()

    def setData(self, data):
        """ Sets the input data and extracts the time array and temporal mean of the coefs. Called in __init__.
        :param data: new measure data
        :type data: np.array
        """
        self.clearCache()
        middle = int(data.shape[1]/2)
        midnk = int(self.nk/2)
        self.data = data[:, np.r_[0:midnk, middle:middle+midnk]]
        self.ntimes = data.shape[0]
        self.coefs_mean = np.mean(self.data, axis=0)
        self.has_realisations = False
        if self.data.ndim >= 3:
            self.has_realisations = True

    def lm2k(self, l, m, coef):
        """ Computes the index k of a coef given its name, its degree l and its order m. . Returns None if no coef exists.
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
        addk = 0
        if coef.startswith("s"):
            addk = self.lmax*(self.lmax+2)

        if m == 0:
            if coef == "ts" or coef == "ss":
                return None
            return int(l**2 - 1 + addk)

        if coef.endswith("c"):
            return int(l**2 + 2*m - 2 + addk)
        if coef.endswith("s"):
            return int(l**2 + 2*m - 1 + addk)

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
        harmonic coefficients ts,tc,ss and sc. Called in __init__.
        """
        k = np.arange(2*self.lmax*(self.lmax+2))
        kmod = k % (self.lmax*(self.lmax+2))
        self.l = np.floor(np.sqrt(kmod+1)).astype(int)
        kl2 = (kmod+1-self.l**2)
        self.is_sin = np.logical_and(np.mod(kl2, 2) == 0, kl2 != 0)
        self.is_cos = np.logical_not(self.is_sin)
        self.is_t = k<(self.lmax*(self.lmax+2))
        self.is_s = np.logical_not(self.is_t)
        self.is_tc = np.logical_and(self.is_cos, self.is_t)
        self.is_ts = np.logical_and(self.is_sin, self.is_t)
        self.is_sc = np.logical_and(self.is_cos, self.is_s)
        self.is_ss = np.logical_and(self.is_sin, self.is_s)
        self.coefname = np.where(self.is_tc, "tc",
                                 np.where(self.is_ts, "ts",
                                          np.where(self.is_sc, "sc",
                                                   np.where(self.is_ss, "ss",None))))
        self.m = np.ceil(kl2/2).astype(int)

    def set_expand_dims(self, useRealisations):
        if useRealisations:
            # for broadcast dimension (coef is the second dimension on 3)
            self.is_tc_ = self.expand_dims(self.is_tc)
            self.is_ts_ = self.expand_dims(self.is_ts)
            self.is_sc_ = self.expand_dims(self.is_sc)
            self.is_ss_ = self.expand_dims(self.is_ss)
            self.m_    = self.expand_dims(self.m)
            self.l_    = self.expand_dims(self.l)
            self.m_tc_ = self.m_ * self.is_tc_
            self.m_ts_ = self.m_ * self.is_ts_
            self.m_sc_ = self.m_ * self.is_sc_
            self.m_ss_ = self.m_ * self.is_ss_
            self.lplus1 = self.l_+1
        else:
            self.is_tc_ = self.is_tc
            self.is_ts_ = self.is_ts
            self.is_sc_ = self.is_sc
            self.is_ss_ = self.is_ss
            self.m_    = self.m
            self.l_    = self.l
            self.m_tc_ = self.m_ * self.is_tc_
            self.m_ts_ = self.m_ * self.is_ts_
            self.m_sc_ = self.m_ * self.is_sc_
            self.m_ss_ = self.m_ * self.is_ss_
            self.lplus1 = self.l_+1

    def computeRThetaPhiData(self, r, thlist, phlist, components=None, usegridPnm=False, computeallrealisation=False, irealisation=-1):
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
        if r != rC:
            raise ValueError('Error: for U type measure, r(%f) should be equal to rC(%f)' % (r, rC))

        if self.has_realisations and not computeallrealisation:
            if irealisation < 0:
                realisation_data = np.mean(self.data, axis=2)
            else:
                realisation_data = self.data[:, :, irealisation]
        else:
            realisation_data = self.data

        # Set default components if not given
        if components is None:
            components = ["th", "ph", "norm"]#, "divh"]

        # The computation of norm requires th and ph component
        if ("norm" in components) and not usegridPnm:
            for additionalComponent in self.components:
                if additionalComponent not in components:
                    components.append(additionalComponent)

        print("WILL COMPUTE ", components)

        if self.has_realisations and computeallrealisation:
            result = {component: np.zeros((self.ntimes, len(thlist), len(phlist), realisation_data.shape[2])) for component in components}
            # Use expanded arrays to fit dimension of realisations
            self.set_expand_dims(True)
        else:
            result = {component: np.zeros((self.ntimes, len(thlist), len(phlist))) for component in components}
            self.set_expand_dims(False)

        for ith, th in enumerate(thlist):
            if usegridPnm:
                if not self.has_grid:
                    raise ValueError("The data has no real space (th,ph) grid")
                self.computingState = (ith+1)/self.nth*100
            sinth = np.sin(th)

            if usegridPnm:
                Pnm = self.Pnm[ith]
                dPnm = self.dPnm[ith]
            else:
                Pnm, dPnm = self.computePnm(th)

            if self.has_realisations and computeallrealisation:
                Pnm = self.expand_dims(Pnm)
                dPnm = self.expand_dims(dPnm)

            for iph, ph in enumerate(phlist):
                cosmph = np.cos(self.m_*ph)
                sinmph = np.sin(self.m_*ph)

                if "divhu" in components:
                    # Computation of the Gauss coefficents was already done when the measure DIVHU was created
                    # So we only need to sum them all
                    result["divhu"][:, ith, iph] = np.sum((cosmph*self.is_sc_+sinmph*self.is_ss_) * Pnm * realisation_data, axis=1)

                if "th" in components:
                    fac_tcnm_th = -self.m_tc_ * sinmph/sinth * Pnm
                    fac_tsnm_th = self.m_ts_ * cosmph/sinth * Pnm
                    fac_scnm_th = cosmph * self.is_sc_ * dPnm
                    fac_ssnm_th = sinmph * self.is_ss_ * dPnm
                    result["th"][:, ith, iph] = np.sum(
                            (fac_tcnm_th + fac_tsnm_th + fac_scnm_th + fac_ssnm_th)
                            * realisation_data, axis=1)

                if "ph" in components:
                    fac_tcnm_ph = -cosmph * self.is_tc_ * dPnm
                    fac_tsnm_ph = -sinmph * self.is_ts_ * dPnm
                    fac_scnm_ph = -self.m_sc_ * sinmph/sinth * Pnm
                    fac_ssnm_ph = self.m_ss_ * cosmph/sinth * Pnm
                    result["ph"][:, ith, iph] = np.sum(
                            (fac_tcnm_ph + fac_tsnm_ph + fac_scnm_ph
                             + fac_ssnm_ph) * realisation_data, axis=1)

                if "norm" in components:
                    if "ph" in result:
                        resultph = result["ph"][:, ith, iph]
                    else:
                        resultph = self.cachedRThetaPhiData[r]["ph"][:, ith, iph]
                    if "th" in result:
                        resultth = result["th"][:, ith, iph]
                    else:
                        resultth = self.cachedRThetaPhiData[r]["th"][:, ith, iph]
                    result["norm"][:, ith, iph] = np.sqrt(resultth**2
                                                          + resultph**2)
                # Calculation of divhu as a component
                # NOT USED ANYMORE : See "DIVHU" measure instead
                if "divh" in components:
                    fac_scnm_divh = cosmph/r * self.is_sc_
                    fac_ssnm_divh = sinmph/r * self.is_ss_
                    result["divh"][:, ith, iph] = np.sum(
                             (fac_scnm_divh + fac_ssnm_divh)
                             * self.l_ * (self.l_+1) * Pnm
                             * realisation_data, axis=1)
            # End of the phi loop
        # End of the theta loop

        return result

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
                       + (self.cachedRThetaPhiData[r]["ph"][itime] - self.cachedRThetaPhiData_mean[r]["ph"]) ** 2)

    def _LowesPrefactor(self, l):
        return l * (l + 1) / (2 * l + 1)

    def computeUGeostrophic(self, r, thlist, computeallrealisation=False, irealisation=-1):
        if r != rC:
            raise ValueError('Error: for U type measure, r(%f) should be equal to rC(%f)' % (r, rC))

        if self.has_realisations and not computeallrealisation:
            if irealisation < 0:
                spectral_data = np.mean(self.data, axis=2)
            else:
                spectral_data = self.data[:, :, irealisation]
        else:
            spectral_data = self.data

        if self.has_realisations and computeallrealisation:
            result = np.zeros((self.ntimes, len(thlist), spectral_data.shape[2]))
            # Use expanded arrays to fit dimension of realisations
            self.set_expand_dims(True)
        else:
            result = np.zeros((self.ntimes, len(thlist)))
            self.set_expand_dims(False)

            for ith, th in enumerate(thlist):
                Pnm, dPnm = self.computePnm(th)

                if self.has_realisations and computeallrealisation:
                    dPnm = self.expand_dims(dPnm)

                for l in range(0, self.lmax):
                    k = self.lm2k(l, 0, "tc")
                    result[:, ith] += - spectral_data[:, k] * dPnm[k]

        return result