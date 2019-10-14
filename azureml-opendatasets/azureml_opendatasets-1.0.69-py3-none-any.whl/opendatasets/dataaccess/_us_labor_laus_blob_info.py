# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Blob info of US labor laus data."""

from .base_blob_info import BaseBlobInfo


class UsLaborLAUSBlobInfo(BaseBlobInfo):
    """Blob info of US labor laus Data."""

    def __init__(self):
        """Initialize Blob Info."""
        self.registry_id = 'us_labor_laus'
        self.blob_account_name = 'azureopendatastorage'
        self.blob_container_name = "laborstatisticscontainer"
        self.blob_relative_path = "laus/"
        self.blob_sas_token = ''
