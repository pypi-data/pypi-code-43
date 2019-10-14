# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains functionality for referencing single or multiple files in datastores or public URLs.

For more information, see the article [Add & register
datasets](https://docs.microsoft.com/azure/machine-learning/service/how-to-create-register-datasets).
To get started working with a file dataset, see https://aka.ms/filedataset-samplenotebook.
"""

import os
import re
import tempfile
from azureml.data._dataset import _Dataset, _get_path_from_step
from azureml.data._dataprep_helper import dataprep, dataprep_fuse, get_dataflow_for_execution
from azureml.data._loggerfactory import track, _LoggerFactory
from azureml.data.constants import _PUBLIC_API
from azureml.data.dataset_error_handling import _try_execute


_logger = None


def _get_logger():
    global _logger
    if _logger is None:
        _logger = _LoggerFactory.get_logger(__name__)
    return _logger


class FileDataset(_Dataset):
    """Represents a collection of file references in datastores or public URLs to use in Azure Machine Learning.

    A FileDataset defines a series of lazily-evaluated, immutable operations to load data from the
    data source into file streams. Data is not loaded from the source until FileDataset is asked to deliver data.

    A FileDataset is created using the :func:`azureml.data.dataset_factory.FileDatasetFactory.from_files` method
    of the FileDatasetFactory class.

    For more information, see the article `Add & register
    datasets <https://docs.microsoft.com/azure/machine-learning/service/how-to-create-register-datasets>`_.
    To get started working with a file dataset, see https://aka.ms/filedataset-samplenotebook.

    .. remarks::

        FileDataset can be used as input of an experiment run. It can also be registered to workspace
        with a specified name and be retrieved by that name later.

        FileDataset can be subsetted by invoking different subsetting methods available on this class.
        The result of subsetting is always a new FileDataset.

        The actual data loading happens when FileDataset is asked to deliver the data into another
        storage mechanism (e.g. files downloaded or mounted to local path).
    """

    def __init__(self):
        """Initialize the FileDataset object.

        This constructor is not supposed to be invoked directly. Dataset is intended to be created using
        :class:`azureml.data.dataset_factory.FileDatasetFactory` class.
        """
        super().__init__()

    @track(_get_logger, custom_dimensions={'app_name': 'FileDataset'}, activity_type=_PUBLIC_API)
    def to_path(self):
        """Get a list of file paths for each file stream defined by the dataset.

        .. remarks::
            The file paths are relative paths for local files when the file streams are downloaded or mounted.

            A common prefix will be removed from the file paths based on how data source was
            specified to create the dataset. For example:

            .. code-block:: python

                datastore = Datastore.get(workspace, 'workspaceblobstore')
                dataset = Dataset.File.from_files((datastore, 'animals/dog/year-*/*.jpg'))
                print(dataset.to_path())

                # ['year-2018/1.jpg'
                #  'year-2018/2.jpg'
                #  'year-2019/1.jpg']

                dataset = Dataset.File.from_files('https://dprepdata.blob.core.windows.net/demo/green-small/*.csv')

                print(dataset.to_path())
                # ['/green_tripdata_2013-08.csv']

        :return: Returns an array of file paths.
        :rtype: numpy.ndarray
        """
        dataflow, portable_path = _add_portable_path_column(self._dataflow)
        dataflow = get_dataflow_for_execution(dataflow, 'to_path', 'FileDataset')
        df = dataflow.to_pandas_dataframe()
        import numpy
        import pandas
        if not isinstance(df, pandas.DataFrame):
            # TODO: remove this check once it is fixed in dprep to return `DataFrame({})` rather than `DataFrame.empty`
            return numpy.empty(0, numpy.object)
        if df.empty:
            return numpy.empty(0, numpy.object)
        return df[portable_path].values

    @track(_get_logger, custom_dimensions={'app_name': 'FileDataset'}, activity_type=_PUBLIC_API)
    def download(self, target_path=None, overwrite=False):
        """Download file streams defined by the dataset as local files.

        :param target_path: The local directory to download the files to. If None, the data will be downloaded
            into a temporary directory.
        :type target_path: str
        :param overwrite: Indicates whether to overwrite existing files. The default is False.
            Existing files will be overwritten if True, otherwise an exception will be raised.
        :type overwrite: bool
        :return: Returns an array of file paths for each file downloaded.
        :rtype: numpy.ndarray
        """
        import numpy
        target_path = target_path or tempfile.mkdtemp()
        target_path = os.path.abspath(target_path)
        download_list = [os.path.abspath(os.path.join(target_path, '.' + p)) for p in self.to_path()]
        if not overwrite:
            for p in download_list:
                if os.path.exists(p):
                    raise RuntimeError('File "{}" already exists. Set overwrite=True to overwrite it.'
                                       .format(p))
        base_path = dataprep().api.datasources.LocalFileOutput(target_path)

        dataflow, portable_path = _add_portable_path_column(self._dataflow)
        dataflow = dataflow.write_streams(
            streams_column='Path',
            base_path=base_path,
            file_names_column=portable_path)

        dataflow = get_dataflow_for_execution(dataflow, 'to_path', 'FileDataset')
        _try_execute(dataflow.run_local)
        return numpy.asarray(download_list, 'O')

    @track(_get_logger, custom_dimensions={'app_name': 'FileDataset'}, activity_type=_PUBLIC_API)
    def mount(self, mount_point=None):
        """Mount file streams defined by the dataset as local files.

        .. remarks::
            A context manager will be returned to manage the lifecycle of the mount. To unmount, exit
            from the context manager.
            Mount is only supported on Unix or Unix-like operating systems and the FUSE library must be present. If you
            are running inside a docker container, the docker container must be started with the `--privileged` flag
            or started with `--cap-add SYS_ADMIN --device /dev/fuse`.

        :param mount_point: The local directory to mount the files to. If None, the data will be mounted into a
            temporary directory, which you can find by calling the `MountContext.mount_point` instance method.
        :type mount_point: str
        :return: Returns a context manager for managing the lifecycle of the mount.
        :rtype: azureml.dataprep.fuse.daemon.MountContext
        """
        try:
            mount = dataprep_fuse().mount
        except OSError:
            raise OSError('Mount is only supported on Unix or Unix-like operating systems and the FUSE library '
                          'must be present. For more information, please refer to the remarks section of '
                          'FileDataset.mount\'s documentation.')

        mount_point = mount_point or tempfile.mkdtemp()
        mount_point = os.path.abspath(mount_point)
        if os.path.ismount(mount_point):
            raise RuntimeError('"{0}" is already mounted. Run `sudo umount "{0}"` to unmount it.'
                               .format(mount_point))

        base_path = _find_path_prefix(self._dataflow)
        dataflow = get_dataflow_for_execution(self._dataflow, 'mount', 'FileDataset')

        return mount(
            dataflow=dataflow,
            files_column='Path',
            mount_point=mount_point,
            base_path=base_path,
            foreground=False)

    @track(_get_logger, custom_dimensions={'app_name': 'FileDataset'}, activity_type=_PUBLIC_API)
    def skip(self, count):
        """Skip file streams from the top of the dataset by the specified count.

        :param count: The number of file streams to skip.
        :type count: int
        :return: Returns a new FileDataset object representing a dataset with file streams skipped.
        :rtype: azureml.data.FileDataset
        """
        return FileDataset._create(self._dataflow.skip(count), self._properties, telemetry_info=self._telemetry_info)

    @track(_get_logger, custom_dimensions={'app_name': 'FileDataset'}, activity_type=_PUBLIC_API)
    def take(self, count):
        """Take a sample of file streams from top of the dataset by the specified count.

        :param count: The number of file streams to take.
        :type count: int
        :return: Returns a new FileDataset object representing the sampled dataset.
        :rtype: azureml.data.FileDataset
        """
        return FileDataset._create(self._dataflow.take(count), self._properties, telemetry_info=self._telemetry_info)

    @track(_get_logger, custom_dimensions={'app_name': 'FileDataset'}, activity_type=_PUBLIC_API)
    def take_sample(self, probability, seed=None):
        """Take a random sample of file streams in the dataset approximately by the probability specified.

        :param probability: The probability of a file stream being included in the sample.
        :type probability: float
        :param seed: An optional seed to use for the random generator.
        :type seed: int
        :return: Returns a new FileDataset object representing the sampled dataset.
        :rtype: azureml.data.FileDataset
        """
        return FileDataset._create(
            self._dataflow.take_sample(probability, seed), self._properties, telemetry_info=self._telemetry_info)

    @track(_get_logger, custom_dimensions={'app_name': 'FileDataset'}, activity_type=_PUBLIC_API)
    def random_split(self, percentage, seed=None):
        """Split file streams in the dataset into two parts randomly and approximately by the percentage specified.

        :param percentage: The approximate percentage to split the Dataset by. This must be a number between 0.0
            and 1.0.
        :type percentage: float
        :param seed: An optional seed to use for the random generator.
        :type seed: int
        :return: Returns a tuple of new FileDataset objects representing the two datasets after the split.
        :rtype: (azureml.data.FileDataset, azureml.data.FileDataset)
        """
        dataflow1, dataflow2 = self._dataflow.random_split(percentage, seed)
        return (
            FileDataset._create(dataflow1, self._properties, telemetry_info=self._telemetry_info),
            FileDataset._create(dataflow2, self._properties, telemetry_info=self._telemetry_info)
        )


def _add_portable_path_column(dataflow):
    prefix_path = _find_path_prefix(dataflow)
    portable_path = 'Portable Path'
    get_portable_path = dataprep().api.functions.get_portable_path
    col = dataprep().api.expressions.col
    return dataflow.add_column(get_portable_path(col('Path'), prefix_path), portable_path, 'Path'), portable_path


def _find_path_prefix(dataflow):
    # TODO: move this logic to Engine
    steps = dataflow._get_steps()
    step_types = [s.step_type for s in steps]
    special_block_types = {'Microsoft.DPrep.ToCsvStreamsBlock',
                           'Microsoft.DPrep.ToParquetStreamsBlock',
                           'Microsoft.DPrep.ToDataFrameDirectoryBlock'}
    if len(special_block_types.intersection(step_types)) > 0:
        return None
    step_type = steps[0].step_type
    step_arguments = steps[0].arguments
    if hasattr(step_arguments, 'to_pod'):
        step_arguments = step_arguments.to_pod()
    path = _get_path_from_step(step_type, step_arguments)
    return None if path is None else _get_prefix(path, dataflow)


def _get_prefix(path, dataflow):
    from azureml.dataprep.api.functions import get_portable_path

    if '*' in path:
        return '/'.join(re.split(r'/|\\', path.split('*')[0])[:-1])

    if path.startswith('http://') or path.startswith('https://'):
        return path[:path.rindex('/')]

    dataflow = dataflow.add_column(get_portable_path(dataflow['Path']), 'PortablePath', 'Path')
    paths = dataflow.take(1).to_pandas_dataframe()['PortablePath']
    if len(paths) == 0:
        return None
    if len(paths) == 1 and paths[0].endswith(path):
        return path.replace('\\', '/')[:path.rindex('/')]
    return path
