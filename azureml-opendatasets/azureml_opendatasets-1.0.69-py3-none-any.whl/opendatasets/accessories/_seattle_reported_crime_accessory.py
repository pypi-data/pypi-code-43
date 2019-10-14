# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Seattle crime."""

from ..dataaccess._seattle_reported_crime_blob_info import SeattleReportedCrimeBlobInfo
from ..dataaccess.blob_parquet_descriptor import BlobParquetDescriptor
from ._city_reported_crime_accessory import CityReportedCrimeAccessory
from datetime import datetime
from dateutil import parser


class SeattleReportedCrimeAccessory(CityReportedCrimeAccessory):
    """Seattle city crime accessory class."""

    default_start_date = parser.parse('2000-01-01')
    default_end_date = datetime.today()

    """const instance of blobInfo."""
    _blobInfo = SeattleReportedCrimeBlobInfo()

    data = BlobParquetDescriptor(_blobInfo)
