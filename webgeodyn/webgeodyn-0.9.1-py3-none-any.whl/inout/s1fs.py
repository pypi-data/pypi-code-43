import numpy as np
from webgeodyn.processing import spectra
from webgeodyn.filters import time
from webgeodyn.constants import rE, rC
from webgeodyn.models import Models, Model


def load(dataDirectory, dataModel, keepRealisations=False):
    """ Loading function for s1fs data. Also adds the data to the dataModel.

    :param dataDirectory: directory where the data is located
    :type dataDirectory: str (path)
    :param dataModel: Model to which the data should be added
    :type dataModel: Model
    :param keepRealisations: indicating if realisations should be kept or averaged (not used)
    :type keepRealisations: bool (default: False)
    :return: 0 if everything went well, -1 otherwise
    :rtype: int
    """
    # load times
    #    times = np.loadtxt(os.path.join(dataDirectory,"time.S1fs2"), skiprows=1)
    datafile_time = dataDirectory[0:15] + "time.S1fs_pm0.8"
    times = np.loadtxt(datafile_time, skiprows=1)

    # Reading MF @ CMB in NS units
    #    gnmC = np.loadtxt(os.path.join(dataDirectory,"gnm_1.53846.S1fs2"), skiprows=1)
    gnmC = np.loadtxt(dataDirectory, skiprows=1)
    print("!! unscaled data !!")

    # detect lmax
    lmax = (-2 + np.sqrt(4 + 4 * gnmC.shape[1])) / 2
    if int(lmax) != lmax:
        raise ValueError("Data length %i does not correspond to lmax*(lmax+2)" % gnmC.shape[1])
    else:
        lmax = int(lmax)

    print('lmax NS:', lmax)
    print("from core surface to Earth's surface... ")

    fac_c2a = np.zeros((lmax))
    for j in range(lmax):
        l = j + 1
        fac_c2a[j] = (rC / rE) ** (2 * l + 4)

    # gnm: from earth's surface to core surface
    n = lmax * (lmax + 2)
    nt = times.shape[0]
    gnmE = np.zeros((nt, n))

    k = 0
    for j in range(lmax):
        l = j + 1
        for m in range(2 * l + 1):
            gnmE[:, k] = gnmC[:, k] * np.sqrt(fac_c2a[j])
            k = k + 1

    dataModel.addMeasure("MF", "MF", lmax, "nT", gnmE, times=times)

    # Reading U @ CMB in NS units
    #    data = np.loadtxt(os.path.join(dataDirectory,"unm_1.53846.S1fs2"), skiprows=1)
    datafile_unm = dataDirectory[0:15] + "unm" + dataDirectory[18::]
    data = np.loadtxt(datafile_unm, skiprows=1)
    lmax = (-2 + np.sqrt(4 + 4 * (data.shape[1]) / 2)) / 2
    if int(lmax) != lmax:
        raise ValueError("Data length %i does not correspond to 2*lmax*(lmax+2)" % data.shape[1])
    else:
        lmax = int(lmax)
    dataModel.addMeasure("U", "U", lmax, "km/yr", data, times=times)

    return 0


def num2dim_S1fs(dataModel_adim):
    print("scale num. data...")
    ####################################################################""
    # 1) dimensionalize time following Lhuillier et al, 2011
    # 2) dimensionalize mag field by fitting MF spectrum to that of chaos
    # 3) dimensionalize flow by using t_dim and rC/rC_adim

    rC_adim = 1.53846154

    ####################################################################""
    # 1)
    # ... calculate MF power spectrum

    MFarray = dataModel_adim.measures['MF'].data.T
    lmax_adim = dataModel_adim.measures['MF'].lmax
    nt = dataModel_adim.measures['MF'].data.shape[0]
    S_MF = spectra.spatial_spectrum_mag(MFarray, nt, lmax_adim)
    Sm_MF = np.mean(S_MF, axis=1)
    t_MF = dataModel_adim.times
    dt_adim = dataModel_adim.times[1] - dataModel_adim.times[0]

    # ... calculate SV power spectrum
    [SVarray, t_SV] = time.deriv_series(MFarray, t_MF)
    S_SV = spectra.spatial_spectrum_mag(SVarray, nt - 2, lmax_adim)
    Sm_SV = np.mean(S_SV, axis=1)

    # ... calculate tau_SV
    tau_SV = np.sqrt(Sm_MF / Sm_SV)
    LL = np.linspace(1, lmax_adim, lmax_adim, dtype=int)

    # ... fit as 1/l for l in [2-13]
    LLin = np.linspace(2, 13, 12, dtype=int)
    XXin = np.log10(LLin)
    YYin = np.log10(tau_SV[LLin - 1])
    ZZin = XXin + YYin  # sppose YY=-XX+ZZ
    tau_SV0 = 10 ** (np.mean(ZZin))

    fac_T = 415 / tau_SV0
    print('T scaling factor', fac_T)

    dt_dim = dt_adim * fac_T;  # 415 yrs from Lhuillier et al 2011
    t_MF_dim = t_MF * fac_T;
    t_MF_dim = t_MF_dim - t_MF_dim[0];

    print("... time scaled following Lhuillier et al (2011).")

    ####################################################################""
    # 2)
    var_dim = np.loadtxt("/home/gilletn/recherche/inversion/geomag_mfsv/covariances/var_mfsv_ref_chaos3.txt")
    varMF_dim = var_dim[:, 0]
    lm_chaos = varMF_dim.shape[0]
    LL = np.linspace(1, lm_chaos, lm_chaos, dtype=int)
    fac = (LL + 1) * (2 * LL + 1);
    specMF_dim = varMF_dim * fac;

    LLin = np.linspace(2, 13, 12, dtype=int)

    ZZ = np.log10(specMF_dim[LL - 1]) - np.log10(Sm_MF[LL - 1])
    pow_ratio = 10 ** (np.mean(ZZ[LLin - 1]))

    fac_B = np.sqrt(pow_ratio)
    print('B scaling factor', fac_B)

    MFarray_dim = MFarray * fac_B  # in nT !!
    #    [SVarray_dim, t_SV_dim] = time.deriv_series(MFarray_dim,t_MF_dim) # in nT/yr !!
    print("... mag field scaled by fitting num. MF spectra to CHAOS.")

    #########################################################
    # 3)
    Uarray = dataModel_adim.measures['U'].data.T
    lu_adim = dataModel_adim.measures['U'].lmax

    fac_L = (rC / rC_adim)
    print('L scaling factor', fac_L)

    U_dim = Uarray * fac_L / fac_T  # in km/yr !!

    #########################################################

    dataModel_dim = Model()
    dataModel_dim.addMeasure(measureName='MF', measureType='MF', lmax=lmax_adim, units='nT', data=MFarray_dim.T,
                             rmsdata=None, times=t_MF_dim)
    dataModel_dim.addMeasure(measureName='U', measureType='U', lmax=lmax_adim, units='km/yr', data=U_dim.T,
                             rmsdata=None, times=t_MF_dim)

    return dataModel_dim, fac_T, fac_B, fac_L
