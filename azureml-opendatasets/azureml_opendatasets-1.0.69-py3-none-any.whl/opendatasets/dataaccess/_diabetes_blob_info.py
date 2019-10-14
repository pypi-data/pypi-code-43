# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Blob info of Diabetes Data."""

from .base_blob_info import BaseBlobInfo


class DiabetesBlobInfo(BaseBlobInfo):
    """Blob info of Diabetes Data."""

    def __init__(self):
        """Initialize Blob Info."""
        self.registry_id = 'sample-diabetes'
        self.blob_account_name = 'azureopendatastorage'
        self.blob_container_name = "mlsamples"
        self.blob_relative_path = "diabetes"
        self.blob_sas_token = (
            "?st=2019-09-26T05%3A09%3A06Z&se=9999-09-27T05%3A09%3A00Z&sp=rl&sv=2018-03-28&sr=c"
            # [SuppressMessage("Microsoft.Security", "CS002:SecretInNextLine", Justification="Offline sas token")]
            r"&sig=Evqi6vSCX2Fagz1BCCfr9SbbAcSmnFxhBipK71vyM%2FA%3D")

    def get_url(self):
        """Get the url of Dataset."""
        self._update_blob_info()
        return 'https://%s.blob.core.windows.net/%s/diabetes/diabetes.tab.txt' % (
            self.blob_account_name,
            self.blob_container_name)
