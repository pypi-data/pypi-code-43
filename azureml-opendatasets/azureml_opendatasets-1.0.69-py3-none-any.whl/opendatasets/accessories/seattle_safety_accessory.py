# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Seattle safety."""

from ..dataaccess._seattle_safety_blob_info import SeattleSafetyBlobInfo
from ..dataaccess.blob_parquet_descriptor import BlobParquetDescriptor
from .city_safety_accessory import CitySafetyAccessory
from datetime import datetime
from dateutil import parser


class SeattleSafetyAccessory(CitySafetyAccessory):
    """Seattle city safety accessory class."""

    default_start_date = parser.parse('2000-01-01')
    default_end_date = datetime.today()

    """const instance of blobInfo."""
    _blobInfo = SeattleSafetyBlobInfo()

    data = BlobParquetDescriptor(_blobInfo)
