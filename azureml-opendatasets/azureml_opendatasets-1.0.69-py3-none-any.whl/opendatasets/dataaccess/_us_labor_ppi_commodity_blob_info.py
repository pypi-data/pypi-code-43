# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Blob info of US labor ppi commodity data."""

from .base_blob_info import BaseBlobInfo


class UsLaborPPICommodityBlobInfo(BaseBlobInfo):
    """Blob info of US labor ppi commodity Data."""

    def __init__(self):
        """Initialize Blob Info."""
        self.registry_id = 'us_labor_ppi_commodity'
        self.blob_account_name = 'azureopendatastorage'
        self.blob_container_name = "laborstatisticscontainer"
        self.blob_relative_path = "ppi_commodity/"
        self.blob_sas_token = ''
