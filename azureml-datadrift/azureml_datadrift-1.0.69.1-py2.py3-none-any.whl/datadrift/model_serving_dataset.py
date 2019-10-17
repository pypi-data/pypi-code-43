# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Model Serving Dataset."""
import os

EXPORT_FOLDER = "export"
EXPORT_FILENAME = "msd.csv"
EXPORT_PATH = os.path.join(EXPORT_FOLDER, EXPORT_FILENAME)

DATASET_PREFIX = "ModelServingDataset-"

TIMESTAMP_COLUMN = "$Timestamp_Inputs"


class ModelServingDataset:
    """Class represent model serving dataset."""

    def __init__(self, workspace):
        """Constructor.

        :param workspace: workspace of the model serving dataset.
        :type workspace: Workspace
        """
        self.workspace = workspace

    def __repr__(self):
        """Return the string representation of a ModelServingDataset object.

        :return: ModelServingDataset object string
        :rtype: str
        """
        return str(self.__dict__)

    def export_to_csv(self, start_time, end_time):
        """Export model serving dataset to local csv.

        :param start_time: the start time you want to export, in ISO time format.
        :type start_time: str
        :param end_time: the end time you want to export, in ISO time format.
        :type end_time: str
        :return: relative path of the exported csv file.
        :rtype: str
        """
        from azureml.core import Dataset
        dataset = Dataset.get(self.workspace, name=DATASET_PREFIX + self.workspace._workspace_id.split('-')[0])
        from azureml.dataprep import col
        ds = dataset._filter((col(TIMESTAMP_COLUMN) >= start_time) & (col(TIMESTAMP_COLUMN) <= end_time))
        df = ds.to_pandas_dataframe()
        os.makedirs(EXPORT_FOLDER, exist_ok=True)
        df.to_csv(EXPORT_PATH, index=False)
        return EXPORT_PATH
