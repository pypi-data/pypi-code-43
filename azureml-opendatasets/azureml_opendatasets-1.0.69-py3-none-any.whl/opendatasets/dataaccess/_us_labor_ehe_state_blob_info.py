# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Blob info of US labor ehe state data."""

from .base_blob_info import BaseBlobInfo


class UsLaborEHEStateBlobInfo(BaseBlobInfo):
    """Blob info of US labor ehe state Data."""

    def __init__(self):
        """Initialize Blob Info."""
        self.registry_id = 'us_labor_ehe_state'
        self.blob_account_name = 'azureopendatastorage'
        self.blob_container_name = "laborstatisticscontainer"
        self.blob_relative_path = "ehe_state/"
        self.blob_sas_token = ''
