# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""DataDriftDetector helps you detect whether your model's training data has drifted from its scoring data.

You can use this package to run individual Data Drift jobs and/or enable a Data Drift schedule.
"""

from .datadriftdetector import DataDriftDetector
from .alert_configuration import AlertConfiguration
from ._datadiff import Metric, MetricType
from .model_serving_dataset import ModelServingDataset
from azureml._base_sdk_common import __version__ as VERSION
from azureml.core import Dataset
from azureml.contrib.datadrift._dataset_extensions import detect_drift

Dataset.detect_drift = detect_drift

__all__ = ["DataDriftDetector", "Metric", "MetricType", "AlertConfiguration", "ModelServingDataset"]
__version__ = VERSION
