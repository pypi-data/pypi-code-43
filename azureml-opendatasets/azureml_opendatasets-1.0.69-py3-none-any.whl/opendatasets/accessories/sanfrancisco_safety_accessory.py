# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""San Francisco safety."""

from ..dataaccess._sanfrancisco_safety_blob_info import SanFranciscoSafetyBlobInfo
from ..dataaccess.blob_parquet_descriptor import BlobParquetDescriptor
from .city_safety_accessory import CitySafetyAccessory
from datetime import datetime
from dateutil import parser


class SanFranciscoSafetyAccessory(CitySafetyAccessory):
    """San Francisco city safety accessory class."""

    default_start_date = parser.parse('2000-01-01')
    default_end_date = datetime.today()

    """const instance of blobInfo."""
    _blobInfo = SanFranciscoSafetyBlobInfo()

    data = BlobParquetDescriptor(_blobInfo)
