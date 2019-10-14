# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Blob info of US population by county data."""

from .base_blob_info import BaseBlobInfo


class UsPopulationCountyBlobInfo(BaseBlobInfo):
    """Blob info of US population by county Data."""

    def __init__(self):
        """Initialize Blob Info."""
        self.registry_id = 'us-decennial-census-county'
        self.blob_account_name = 'azureopendatastorage'
        self.blob_container_name = "censusdatacontainer"
        self.blob_relative_path = "release/us_population_county/"
        self.blob_sas_token = ''
