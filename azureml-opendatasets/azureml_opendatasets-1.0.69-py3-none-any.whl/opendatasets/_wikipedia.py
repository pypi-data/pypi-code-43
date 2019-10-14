# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Wikipedia."""

from .dataaccess._wikipedia_blob_info import WikipediaBlobInfo
from azureml.data import FileDataset
from azureml.data._dataset import _DatasetTelemetryInfo
from azureml.core.dataset import Dataset
from azureml.telemetry.activity import ActivityType, log_activity
from ._utils.telemetry_utils import get_opendatasets_logger, get_run_common_properties
import logging


class Wikipedia:
    """Wikipedia class."""

    @staticmethod
    def get_file_dataset(enable_telemetry: bool = True) -> FileDataset:
        blobInfo = WikipediaBlobInfo()
        url_paths = blobInfo.get_url()
        print("__name__:" + __name__)
        if enable_telemetry:
            logger = get_opendatasets_logger("WIKI", verbosity=logging.INFO)
            log_properties = get_run_common_properties()
            log_properties['RegistryId'] = blobInfo.registry_id
            log_properties['Path'] = url_paths
            with log_activity(
                    logger,
                    'get_file_dataset',
                    ActivityType.PUBLICAPI,
                    custom_dimensions=log_properties):
                ds = Dataset.File.from_files(path=url_paths)
                ds._telemetry_info = _DatasetTelemetryInfo(entry_point='PythonSDK.OpenDataset')
                return ds
        else:
            ds = Dataset.File.from_files(path=url_paths)
            ds._telemetry_info = _DatasetTelemetryInfo(entry_point='PythonSDK.OpenDataset')
            return ds
