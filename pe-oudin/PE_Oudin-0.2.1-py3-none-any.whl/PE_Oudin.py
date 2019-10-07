__LastUpdate__ = '2019/10/07'
__CreatedBy__ = 'Dror Paz'

from math import cos, sin, acos, sqrt, pi
from calendar import monthrange, isleap
from datetime import datetime
from typing import Tuple, Union, Collection
from numbers import Real

try:
    from dateutil.parser import parse
except ImportError:
    pass

'''
This is a pure python implementation of the R - AirGR PEdaily_Oudin function.
Original source found at https://github.com/cran/airGR/blob/master/R/PEdaily_Oudin.R
Changes from the original include:
 - Support single day as well as multiple days (list, numpy array, pandas etc.). 
 - Get latitude in degrees or radians (default degrees).
 - Can choose output units (usefull for GR2M and GR2A). 
 
'''


class PE_Oudin:
    DEG_UNIT_STRINGS = ('deg', 'degree', 'degrees')
    RAD_UNIT_STRAINGS = ('rad', 'radian', 'radians')
    VALID_OUT_UNITS = ['mm/day', 'mm/month', 'mm/year']
    DEFAULT_PE_UNIT = 'mm/day'

    def __init__(self):
        pass

    @classmethod
    def pe_oudin_daily(cls, temp: Union[Real, Collection[Real]], date: Union[datetime, Collection[datetime]], lat: Real,
                       lat_unit: str = 'deg', out_units: str = DEFAULT_PE_UNIT):
        """
        Calculate potential evapotranspiration from temperature.

        ## Usage:
        For single value:
        >>>temp = 20 # Degrees celsius
        >>>date = datetime(2018,1,1)
        >>>lat = 32 # Degrees
        >>>lat_unit = 'deg' # Optional, and default. Can also be 'rad'
        >>>out_units = 'mm/day' # Optional, and default. Can also be 'mm/month', 'mm/year'

        >>>PE_Oudin.pe_oudin_daily(temp, date, lat, lat_unit, out_units)

        For multiple values (list, pandas series etc.):

        >>>temp = [20, 25] # Degrees celcius
        >>>date = [datetime(2018,1,1), datetime(2018,1,1)]
        >>>lat = 32 # Degrees
        >>>lat_unit = 'deg' # Optional, and default. Can also be 'rad'
        >>>out_units = 'mm/day' # Optional, and default. Can also be 'mm/month', 'mm/year'

        >>>PE_Oudin.pe_oudin_daily(temp, date, lat, lat_unit, out_units)
        Args:
            temp (Real): temperature in celsius (or iterable of such).
            date (datetime): datetime-like object (or iterable of such).
            lat (Real): latitude in degrees or radians.
            lat_unit (str): unit of latitude ("deg" or "rad").
            out_units (str): unit of output ('mm/day', 'mm/month', 'mm/year')

        Returns (Float, list(Floats)): Potential evapotranspiration in units [out_units]

        """

        # Converting latitude to radians
        if lat_unit.lower() in cls.DEG_UNIT_STRINGS:
            lat_rad = float(lat) * pi / 180
        elif lat_unit.lower() in cls.RAD_UNIT_STRAINGS:
            lat_rad = float(lat)
        else:
            raise ValueError(f'lat_unit must be "deg" (for degrees) or "rad" (for radians). got {lat_unit}')

        # Asserting valid output unit
        if out_units.lower() not in cls.VALID_OUT_UNITS:
            raise ValueError('Requested output units [%s] not supported. Must be one of %s' % (out_units, validUnits))

        # calculating for iterable of values
        if isinstance(temp, Collection) and isinstance(date, Collection):
            if len(temp) == len(date):
                out_pe_list = []
                for i in range(len(temp)):
                    out_pe = cls._single_point_pe_oudin(temp[i], date[i], lat_rad)
                    out_pe = cls._convert_output_units(out_pe, date[i], out_unit=out_units)
                    out_pe_list.append(out_pe)
                return out_pe_list
            else:
                raise ValueError(f'temp and date must be the same length (got {len(temp)} and '
                                 f'{len(date)})')

        elif isinstance(temp, Collection) or isinstance(date, Collection):
            raise ValueError(f'temp and date must be both Collections or both single values. '
                             f'Got {type(temp)} and {type(date)}')
        # calculating for single value
        else:
            out_pe = cls._single_point_pe_oudin(temp, date, lat_rad)
            out_pe = cls._convert_output_units(out_pe, date, out_unit=out_units)
            return out_pe

    @classmethod
    def _convert_output_units(cls, pot_evap: Real, date: datetime, out_unit: str = DEFAULT_PE_UNIT) -> (float, int):
        f"""
        Convert PE units from default ({cls.DEFAULT_PE_UNIT}) to requested units.
        Args:
            pot_evap (Real): evapotransporation in mm/day.
            doy (int): day of year
            year (int, None): the year or None
            out_unit (str): one of: {cls.VALID_OUT_UNITS}

        Returns (int, float): Potential evapotranspiration in requested units.

        """

        if out_unit.lower() == cls.DEFAULT_PE_UNIT:
            return pot_evap

        year = date.year
        month = date.month

        if out_unit.lower() == 'mm/month':
            return pot_evap * monthrange(year, month)[1]

        elif out_unit.lower() == 'mm/year':
            days_in_year = 365 if not isleap(year) else 366
            return pot_evap * days_in_year

        else:
            raise ValueError('Requested units [%s] not supported. Must be one of %s' % (out_unit, cls.VALID_OUT_UNITS))

    @classmethod
    def _single_point_pe_oudin(cls, temp: Real, date: datetime, lat_rad: Real) -> Real:
        """
        This function is copied from the R package implementation.
        For any questions regarding the algorithm please contact Olivier Delaigue <airGR at irstea.fr>
        """
        jd = date.timetuple().tm_yday
        fi = lat_rad
        cosfi = cos(fi)

        teta = 0.4093 * sin(jd / 58.1 - 1.405)
        costeta = cos(teta)
        cosgz = max(0.001, cos(fi - teta))

        cosom = 1 - cosgz / cosfi / costeta
        if cosom < (-1):
            cosom = (-1)
        elif cosom > 1:
            cosom = 1

        cosom2 = cosom ** 2

        if cosom2 >= 1:
            sinom = 0
        else:
            sinom = sqrt(1 - cosom2)

        om = acos(cosom)
        cospz = cosgz + cosfi * costeta * (sinom / om - 1)
        if cospz < 0.001:
            cospz = 0.001
        eta = 1 + cos(jd / 58.1) / 30
        ge = 446 * om * cospz * eta
        if temp >= -5:
            pot_evap = ge * (temp + 5) / 100 / 28.5
        else:
            pot_evap = 0
        return pot_evap


if __name__ == '__main__':
    example_temp = [20, 25]  # Degrees celcius
    example_date = [datetime(2018, 1, 1), datetime(2018, 1, 1)]
    example_lat = 32  # Degrees (but can be set to radians)
    example_lat_unit = 'deg'  # Optional, and default. Can also be 'rad'
    example_out_units = 'mm/day'  # Optional, and default. Can also be 'mm/month' or 'mm/year'

    # Run program with single value
    pe = PE_Oudin.pe_oudin_daily(example_temp[0], example_date[0], example_lat, example_lat_unit, example_out_units)
    print(pe)

    # Run program with multiple values
    pe = PE_Oudin.pe_oudin_daily(example_temp, example_date, example_lat, example_lat_unit, example_out_units)

    print(pe)
