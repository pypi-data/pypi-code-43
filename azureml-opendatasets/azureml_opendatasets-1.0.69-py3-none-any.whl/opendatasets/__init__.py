# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Enable consuming Azure open datasets into dataframes and enrich customer data."""

from ._boston_safety import BostonSafety
from ._chicago_safety import ChicagoSafety
from ._noaa_gfs_weather import NoaaGfsWeather
from ._noaa_isd_weather import NoaaIsdWeather
from ._nyc_safety import NycSafety
from ._nyc_tlc_fhv import NycTlcFhv
from ._nyc_tlc_green import NycTlcGreen
from ._nyc_tlc_yellow import NycTlcYellow
from ._public_holidays import PublicHolidays
from ._public_holidays_offline import PublicHolidaysOffline
from ._sanfrancisco_safety import SanFranciscoSafety
from ._seattle_safety import SeattleSafety
from ._us_population_county import UsPopulationCounty
from ._us_population_zip import UsPopulationZip
from ._us_labor_cpi import UsLaborCPI
from ._us_labor_ppi_industry import UsLaborPPIIndustry
from ._us_labor_ppi_commodity import UsLaborPPICommodity
from ._us_labor_ehe_national import UsLaborEHENational
from ._us_labor_ehe_state import UsLaborEHEState
from ._us_labor_laus import UsLaborLAUS
from ._us_labor_lfs import UsLaborLFS
from ._wikipedia import Wikipedia
from ._mnist import MNIST
from ._diabetes import Diabetes

__all__ = [
    'BostonSafety',
    'ChicagoSafety',
    'NoaaGfsWeather',
    'NoaaIsdWeather',
    'NycSafety',
    'NycTlcFhv',
    'NycTlcGreen',
    'NycTlcYellow',
    'PublicHolidays',
    'PublicHolidaysOffline',
    'SanFranciscoSafety',
    'SeattleSafety',
    'UsPopulationCounty',
    'UsPopulationZip',
    'UsLaborCPI',
    'UsLaborPPIIndustry',
    'UsLaborPPICommodity',
    'UsLaborEHENational',
    'UsLaborEHEState',
    'UsLaborLAUS',
    'UsLaborLFS',
    'Wikipedia',
    'MNIST',
    'Diabetes'
]
