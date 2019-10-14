# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Define the class for representing the intent to promote an intermediate output to an Azure Machine Learning Dataset.

Intermediate data (output), in pipeline by default will not become an Azure Machine Learning Dataset. To promote
them to Azure Machine Learning Datasets, please call the to_dataset method on the PipelineData class.
"""
from copy import copy


class PipelineOutputDataset(object):
    """
    Represent intermediate data that will be promoted to an Azure Machine Learning Dataset.

    Once an intermediate data is promoted to an Azure Machine Learning dataset, it will also be consumed as a Dataset
    instead of a DataReference in subsequent steps.

    :param pipeline_data: The PipelineData that represents the intermediate output which will be promoted to
        a Dataset.
    :type pipeline_data: azureml.pipeline.core.PipelineData
    """

    def __init__(self, pipeline_data):
        """
        Create an intermediate data that will be promoted to an Azure Machine Learning Dataset.

        :param pipeline_data: The PipelineData that represents the intermediate output which will be promoted to
            a Dataset.
        :type pipeline_data: azureml.pipeline.core.PipelineData
        """
        self._pipeline_data = pipeline_data

        self._registration_name = None
        self._create_new_version = None
        self._input_mode = "mount"
        self._input_path_on_compute = None

    def register(self, name, create_new_version=True):
        """
        Register the output dataset to the workspace.

        :param name: The name of the registered dataset once the intermediate data is produced.
        :type name: str
        :param create_new_version: Whether to create a new version of the dataset if the data source changes. Defaults
            to True. By default, all intermediate output will output to a new location when a pipeline runs, so
            it is highly recommended to keep this flag set to True.
        :return:
        """
        other = self._clone()
        other._registration_name = name
        other._create_new_version = create_new_version
        return other

    @property
    def name(self):
        """
        Output name of the PipelineData.

        :return: The output name of the PipelineData.
        :rtype: str
        """
        return self._output_name

    def as_download(self, path_on_compute=None):
        """
        Set input the consumption mode of the dataset to download.

        :param path_on_compute: The path on the compute to download the dataset to. Defaults to None, which means
            we will pick a path for you.
        :type path_on_compute: str
        :return: The modified PipelineOutputDataset.
        :rtype: azureml.pipeline.core.pipeline_output_dataset.PipelineOutputDataset
        """
        return self._set_mode("download", path_on_compute=path_on_compute)

    def as_mount(self, path_on_compute=None):
        """
        Set input the consumption mode of the dataset to mount.

        :param path_on_compute: The path on the compute to mount the dataset to. Defaults to None, which means
            we will pick a path for you.
        :type path_on_compute: str
        :return: The modified PipelineOutputDataset.
        :rtype: azureml.pipeline.core.pipeline_output_dataset.PipelineOutputDataset
        """
        return self._set_mode("mount", path_on_compute=path_on_compute)

    def as_direct(self):
        """
        Set input the consumption mode of the dataset to direct.

        In this mode, you will get the ID of the dataset and in your script you can call Dataset.get_by_id to retrieve
        the dataset. run.input_datasets['{dataset_name}'] will return the Dataset instead.

        :return: The modified PipelineOutputDataset.
        :rtype: azureml.pipeline.core.pipeline_output_dataset.PipelineOutputDataset
        """
        return self._set_mode("direct", path_on_compute=None)

    def create_input_binding(self):
        """
        Create input binding.

        :return: The InputPortBinding with this PipelineData as the source.
        :rtype: azureml.pipeline.core.graph.InputPortBinding
        """
        from azureml.pipeline.core import InputPortBinding

        if not self._input_mode:
            raise RuntimeError("Input mode cannot be None or empty.")

        return InputPortBinding(
            name=self._pipeline_data._name,
            bind_object=self._pipeline_data,
            bind_mode=self._input_mode,
            path_on_compute=self._input_path_on_compute,
            overwrite=False,
        )

    @property
    def input_name(self):
        """
        Input name of the PipelineOutputDataset.

        You can use this name to retrieve the materialized dataset through environment environment variable or
        run.input_datasets.

        :return: Input name of the PipelineOutputDataset.
        :rtype: str
        """
        return self._pipeline_data._name

    @property
    def _output_name(self):
        return self._pipeline_data._output_name

    @property
    def _data_type_short_name(self):
        return "AzureMLDataset"

    def _set_producer(self, producer):
        self._pipeline_data._set_producer(producer)

    @property
    def _producer(self):
        return self._pipeline_data._producer

    def _clone(self):
        return copy(self)

    def _set_mode(self, mode, path_on_compute):
        other = self._clone()
        other._input_mode = mode
        other._input_path_on_compute = path_on_compute
        return other


class _DatasetRegistration:
    def __init__(self, name, create_new_version):
        self._name = name
        self._create_new_version = create_new_version

    @property
    def name(self):
        return self._name

    @property
    def create_new_version(self):
        return self._create_new_version
