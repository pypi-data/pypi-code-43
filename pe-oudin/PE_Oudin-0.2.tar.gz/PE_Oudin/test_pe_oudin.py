__author__ = 'Dror Paz'
__createdOn__ = '2019/10/08'

import pytest
from datetime import datetime
from .PE_Oudin import PE_Oudin


def test_pe_oudin():
    example_temp = [20, 25]  # Degrees celcius
    date = [datetime(2018, 1, 1), datetime(2018, 1, 1)]
    example_lat = 32  # Degrees (but can be set to radians)
    example_lat_unit = 'deg'  # Optional, and default. Can also be 'rad'
    example_out_units = 'mm/day'  # Optional, and default. Can also be 'mm/month' or 'mm/year'

    # Run program with single value
    pe = PE_Oudin.pe_oudin_daily(example_temp[0], date[0], example_lat, example_lat_unit, example_out_units)
    assert pe == pytest.approx(1.948655)

    # Run program with multiple values
    pe = PE_Oudin.pe_oudin_daily(example_temp, date, example_lat, example_lat_unit, example_out_units)
    assert pe == pytest.approx((1.948655, 2.338386))
