# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Diabetes data."""

from .dataaccess._diabetes_blob_info import DiabetesBlobInfo
from azureml.core import Dataset
from azureml.data import TabularDataset
from azureml.telemetry.activity import ActivityType, log_activity
from ._utils.telemetry_utils import get_opendatasets_logger, get_run_common_properties
import logging


class Diabetes:
    """Diabetes data class."""

    _blobInfo = DiabetesBlobInfo()

    @staticmethod
    def _get_logger_prop(blobInfo: DiabetesBlobInfo):
        log_properties = get_run_common_properties()
        log_properties['RegistryId'] = blobInfo.registry_id
        log_properties['Path'] = blobInfo.get_data_wasbs_path()
        return log_properties

    @staticmethod
    def get_tabular_dataset(
            enable_telemetry: bool = True) -> TabularDataset:
        _url_path = Diabetes._blobInfo.get_url()
        _seperator = '\t'
        if enable_telemetry:
            logger = get_opendatasets_logger("Diabetes", verbosity=logging.INFO)
            log_properties = Diabetes._get_logger_prop(Diabetes._blobInfo)
            with log_activity(
                    logger,
                    'get_tabular_dataset',
                    ActivityType.PUBLICAPI,
                    custom_dimensions=log_properties):
                return Dataset.Tabular.from_delimited_files(path=_url_path, separator=_seperator)
        else:
            return Dataset.Tabular.from_delimited_files(path=_url_path, separator=_seperator)
