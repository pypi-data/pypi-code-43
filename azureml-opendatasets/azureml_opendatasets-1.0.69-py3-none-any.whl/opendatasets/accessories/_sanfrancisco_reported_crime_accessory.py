# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""San Francisco crime."""

from ..dataaccess._sanfrancisco_reported_crime_blob_info import SanFranciscoReportedCrimeBlobInfo
from ..dataaccess.blob_parquet_descriptor import BlobParquetDescriptor
from ._city_reported_crime_accessory import CityReportedCrimeAccessory
from datetime import datetime
from dateutil import parser


class SanFranciscoReportedCrimeAccessory(CityReportedCrimeAccessory):
    """San Francisco city crime accessory class."""

    default_start_date = parser.parse('2000-01-01')
    default_end_date = datetime.today()

    """const instance of blobInfo."""
    _blobInfo = SanFranciscoReportedCrimeBlobInfo()

    data = BlobParquetDescriptor(_blobInfo)
