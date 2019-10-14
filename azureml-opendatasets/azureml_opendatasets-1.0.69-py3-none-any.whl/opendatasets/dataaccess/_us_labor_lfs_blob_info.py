# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Blob info of US labor lfs data."""

from .base_blob_info import BaseBlobInfo


class UsLaborLFSBlobInfo(BaseBlobInfo):
    """Blob info of US labor lfs Data."""

    def __init__(self):
        """Initialize Blob Info."""
        self.registry_id = 'us_labor_lfs'
        self.blob_account_name = 'azureopendatastorage'
        self.blob_container_name = "laborstatisticscontainer"
        self.blob_relative_path = "lfs/"
        self.blob_sas_token = ''
