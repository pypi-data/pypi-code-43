# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Dataset consumption configuration."""

import re

from azureml.exceptions import UserErrorException


class DatasetConsumptionConfig:
    """Represent how to deliver the dataset to the compute target.

    dataset: represents the dataset that will be consumed in the run.
    name: represents the name of the dataset in the run, which can be different to the registered name.
    The name will be registered as environment variable and can be used in data plane.
    mode: defines how the dataset should be delivered to the compute target. There are currently three modes:
    1. Direct: consume the dataset as dataset.
    2. Download: download the dataset and consume the dataset as downloaded path.
    3. Mount: mount the dataset and consume the dataset as mount path.
    """

    _SUPPORTED_MODE = {'direct', 'mount', 'download'}

    def __init__(self, name, dataset, mode='direct', path_on_compute=None):
        """Represent how to deliver the dataset to the compute target.

        :param name: The name of the dataset inside the run.
        :type name: str
        :param dataset: The dataset to be delivered.
        :type dataset: azureml.data._dataset._Dataset
        :param mode: How to deliver the data: direct, mount, or download
        :type mode: str
        :param path_on_compute: The target path on the compute to make the data available at. The folder structure
            of the source data will be kept, however, we might add prefixes to this folder structure to avoid
            collision. We recommend calling `tabular_dataset.to_path` to see the output folder structure.
        :type path_on_compute: str
        """
        mode = mode.lower()
        DatasetConsumptionConfig._validate_mode(dataset, mode)
        self.dataset = dataset
        self.name = self._validate_name(name) if name else None
        self.mode = mode
        self.path_on_compute = path_on_compute

    @staticmethod
    def _validate_name(name):
        if re.search(r"^[a-z_]+[a-z0-9_]*$", name):
            return name
        raise UserErrorException("Invalid name {}. Only allow lowercase and underscore and begin with letters".format(
            name
        ))

    @staticmethod
    def _validate_mode(dataset, mode):
        from azureml.data import FileDataset

        if mode not in DatasetConsumptionConfig._SUPPORTED_MODE:
            raise UserErrorException("Invalid mode '{}'. Mode can only be mount, download, or direct".format(mode))

        if not isinstance(dataset, FileDataset):
            if mode == 'download' or mode == 'mount':
                raise UserErrorException("{} does not support {}. Only FileDataset supports {}".format(
                    type(dataset), mode, mode
                ))

    def as_download(self, path_on_compute=None):
        """Set the mode to download.

        :param path_on_compute: The target path on the compute to make the data available at.
        :type path_on_compute: str
        """
        return DatasetConsumptionConfig(name=self.name, dataset=self.dataset,
                                        mode='download', path_on_compute=path_on_compute)

    def as_mount(self, path_on_compute=None):
        """Set the mode to mount.

        :param path_on_compute: The target path on the compute to make the data available at.
        :type path_on_compute: str
        """
        return DatasetConsumptionConfig(name=self.name, dataset=self.dataset,
                                        mode='mount', path_on_compute=path_on_compute)
