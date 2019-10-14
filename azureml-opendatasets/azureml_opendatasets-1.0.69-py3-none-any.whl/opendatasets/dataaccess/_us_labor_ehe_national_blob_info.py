# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Blob info of US labor ehe national data."""

from .base_blob_info import BaseBlobInfo


class UsLaborEHENationalBlobInfo(BaseBlobInfo):
    """Blob info of US labor ehe national Data."""

    def __init__(self):
        """Initialize Blob Info."""
        self.registry_id = 'us_labor_ehe_national'
        self.blob_account_name = 'azureopendatastorage'
        self.blob_container_name = "laborstatisticscontainer"
        self.blob_relative_path = "ehe_national/"
        self.blob_sas_token = ''
