# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Blob info of US labor cpi data."""

from .base_blob_info import BaseBlobInfo


class UsLaborCPIBlobInfo(BaseBlobInfo):
    """Blob info of US labor cpi Data."""

    def __init__(self):
        """Initialize Blob Info."""
        self.registry_id = 'us_labor_cpi'
        self.blob_account_name = 'azureopendatastorage'
        self.blob_container_name = "laborstatisticscontainer"
        self.blob_relative_path = "cpi/"
        self.blob_sas_token = ''
