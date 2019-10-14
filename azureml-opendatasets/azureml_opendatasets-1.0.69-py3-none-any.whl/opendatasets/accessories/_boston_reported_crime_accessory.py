# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Boston crime."""

from ..dataaccess._boston_reported_crime_blob_info import BostonReportedCrimeBlobInfo
from ..dataaccess.blob_parquet_descriptor import BlobParquetDescriptor
from ._city_reported_crime_accessory import CityReportedCrimeAccessory
from datetime import datetime
from dateutil import parser


class BostonReportedCrimeAccessory(CityReportedCrimeAccessory):
    """Boston city crime accessory class."""

    default_start_date = parser.parse('2015-06-01')
    default_end_date = datetime.today()

    """const instance of blobInfo."""
    _blobInfo = BostonReportedCrimeBlobInfo()

    data = BlobParquetDescriptor(_blobInfo)
