import numpy as np
import pandas as pd
import pkg_resources
from openscm.scmdataframe import ScmDataFrame
from pymagicc import MAGICCData

from .base import BaseSCM


def _get_magicc6_fname(sce):
    return pkg_resources.resource_filename("pymagicc", "MAGICC6/run/{}".format(sce))


def load_emissions():
    # hack hack hack
    # only industrial emissions, lazy but will get the picture
    mdata = MAGICCData(_get_magicc6_fname("RCP85.SCEN"))
    emissions = (
        mdata.filter(
            region="World", variable="Emissions|CO2|MAGICC Fossil and Industrial"
        )
        .timeseries()
        .T.squeeze()
    )
    emissions.name = None
    emissions.index = [d.year for d in emissions.index]
    newindex = np.arange(2007, 2100)

    emissions_reindexed = emissions.reindex(index=newindex)
    emissions_reindexed.interpolate(method="linear", inplace=True)
    emissions_reindexed = pd.DataFrame(emissions_reindexed)

    mdata = MAGICCData(_get_magicc6_fname("HISTRCP_CO2I_EMIS.IN"))
    historical_emissions = mdata.timeseries().sum(axis=0)
    historical_emissions.index = mdata["year"]

    emis = pd.concat(
        [emissions_reindexed, historical_emissions]
    )  # lazy but fine for mucking around
    emis = emis.sort_index()

    return emis.index, emis.values


time_index, co2_emissions = load_emissions()


class AR5IR(BaseSCM):
    name = "ar5ir"

    a1 = 0.2240
    tau1 = 394.4
    a2 = 0.2824
    tau2 = 36.54
    a3 = 0.2763
    tau3 = 4.304
    co2_pi = 278
    f2x = 3.74
    c1 = 0.631
    d1 = 8.4
    c2 = 0.429
    d2 = 409.5
    co2_2x = False

    def __init__(self, **kwargs):
        super(AR5IR, self).__init__(**kwargs)
        for kwarg, value in kwargs.items():
            setattr(self, kwarg, value)

        self.co2_emissions = co2_emissions.copy()

        if self.co2_2x:
            self.co2_emissions = 2 * self.co2_emissions

    def _run_single(self, run_params, variables=None):
        if variables is not None and variables != ["Surface Temperature"]:
            raise ValueError("ar5ir only calculates Surface Temperature")
        # Ignoring the requested Varaibles
        for kwarg, value in run_params.items():
            setattr(self, kwarg, value)

        self.calculate_co2_concentrations()
        self.calculate_co2_radiative_forcing()
        self.calculate_temperatures()

        return ScmDataFrame(
            pd.Series(self.temperatures, index=time_index),
            columns={
                "unit": ["K"],
                "variable": ["Surface Temperature"],
                "region": ["World"],
                "model": ["ar5ir"],
                "scenario": ["unspecified"],
            },
        )

    def calculate_co2_concentrations(self):
        a0 = 1 - self.a1 - self.a2 - self.a3
        a = np.array([a0, self.a1, self.a2, self.a3])
        for a_val in a:
            assert 1 >= a_val >= 0, "that's not going to work"
        tau = np.array([10 ** 10, self.tau1, self.tau2, self.tau3])
        co2_concentration_perturbations = np.nan * np.zeros(
            (len(self.co2_emissions), 4)
        )
        co2_concentration_perturbations[0, :] = 0

        gtc_ppm_conv_factor = 18 / (
            5.14 * 12
        )  # molw.air / (m_atmos * molw.C), no idea why...
        temp = self.co2_emissions[:, np.newaxis] * a * gtc_ppm_conv_factor
        factor = 1 - 1 / tau
        for i in range(len(self.co2_emissions[:-1])):
            co2_concentration_perturbations[i + 1, :] = (  # assuming one year timestep
                co2_concentration_perturbations[i, :] * factor + temp[i]
            )

        self.co2_concentrations = (
            co2_concentration_perturbations.sum(axis=1) + self.co2_pi
        )

    def calculate_co2_radiative_forcing(self):
        self.co2_radiative_forcing = (
            self.f2x / np.log(2) * np.log(self.co2_concentrations / self.co2_pi)
        )

    def calculate_temperatures(self):
        c = np.array([self.c1, self.c2])
        d = np.array([self.d1, self.d2])
        temp_perturbations = np.nan * np.zeros((len(self.co2_emissions), 2))
        temp_perturbations[0, :] = 0

        factor = 1 - 1 / d
        temp = self.co2_radiative_forcing[:, np.newaxis] * c / d
        for i in range(len(self.co2_radiative_forcing[:-1])):
            temp_perturbations[i + 1, :] = (
                temp_perturbations[i] * factor + temp[i]
            )  # assuming one year timestep

        self.temperatures = temp_perturbations.sum(axis=1)
