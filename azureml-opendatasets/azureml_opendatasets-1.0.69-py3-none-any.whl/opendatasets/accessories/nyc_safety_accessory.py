# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""New York City safety."""

from ..dataaccess._nyc_safety_blob_info import NycSafetyBlobInfo
from ..dataaccess.blob_parquet_descriptor import BlobParquetDescriptor
from .city_safety_accessory import CitySafetyAccessory
from datetime import datetime
from dateutil import parser


class NycSafetyAccessory(CitySafetyAccessory):
    """New York city safety accessory class."""

    default_start_date = parser.parse('2000-01-01')
    default_end_date = datetime.today()

    """const instance of blobInfo."""
    _blobInfo = NycSafetyBlobInfo()

    data = BlobParquetDescriptor(_blobInfo)
