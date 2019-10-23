import os
import io

from azureml.studio.common.datatypes import DataTypes
from azureml.studio.common.datatable.data_table import DataTable
from azureml.studio.common.datatable.data_table_directory import DataTableDirectory
from azureml.studio.core.logger import TimeProfile, common_logger
from azureml.studio.core.utils.strutils import remove_suffix
from azureml.studio.modulehost.handler.sidecar_files import SideCarFileBundle, FileDumper, AzureMLOutputDumper
from azureml.studio.modulehost.handler.sidecar_files import DataFrameSchemaDumper
from azureml.studio.core.utils.fileutils import get_file_name, make_file_name, iter_files
from azureml.studio.modulehost.handler.data_handler import DataTableDatasetHandler, DataTableCsvHandler, \
    ITransformHandler, ILearnerHandler, DataTableCsvNoHeaderHandler, DataTableTsvHandler, DataTableTsvNoHeaderHandler, \
    ZipHandler, IClusterHandler, IRecommenderHandler
from azureml.studio.common.io.directory_loader import load_from_directory
from azureml.studio.common.io.transform_directory import save_transform_to_directory, TransformDirectory
from azureml.studio.core.io.visualizer import ExistFileVisualizer
from azureml.studio.core.io.data_frame_directory import save_data_frame_to_directory
from azureml.studio.core.io.model_directory import save_model_to_directory, ModelDirectory, pickle_loader
from azureml.studio.common.io.data_table_io import get_meta_data_file_path

_DATA_TYPE_HANDLERS = {
    DataTypes.DATASET: DataTableDatasetHandler,
    DataTypes.GENERIC_CSV: DataTableCsvHandler,
    DataTypes.GENERIC_CSV_NO_HEADER: DataTableCsvNoHeaderHandler,
    DataTypes.GENERIC_TSV: DataTableTsvHandler,
    DataTypes.GENERIC_TSV_NO_HEADER: DataTableTsvNoHeaderHandler,
    DataTypes.TRANSFORM: ITransformHandler,
    DataTypes.LEARNER: ILearnerHandler,
    DataTypes.CLUSTER: IClusterHandler,
    DataTypes.ZIP: ZipHandler,
    DataTypes.RECOMMENDER: IRecommenderHandler,
}

_DATA_TYPE_SAVERS = {
    DataTypes.DATASET: save_data_frame_to_directory,
    DataTypes.LEARNER: save_model_to_directory,
    DataTypes.CLUSTER: save_model_to_directory,
    DataTypes.RECOMMENDER: save_model_to_directory,
    DataTypes.TRANSFORM: save_transform_to_directory,
}


def learner_cluster_dumper(model_type, file_name):
    """Return a dumper to dump LEARNER, CLUSTER, TRANSFORM in ModelDirectory."""
    def model_dumper(save_to):
        return {'model_type': model_type, 'file_name': file_name}
    return model_dumper


class OutputHandler:
    @staticmethod
    def handle_output_directory(data, file_path, file_name, data_type, saver):
        """Store the output data to directory with a save function.

        This method assume that the data in the directory has been stored in old logic.
        TODO: Store the data here and replace the old logic.
        """

        # Update visualization
        visualizers = []
        extension = '.' + data_type.value.file_extension
        # Using `strutils.remove_suffix` instead of built-in `os.path.splitext` here.
        # Because some data types have multi-level extensions such as '.nh.csv', '.dataset.parquet',
        # which the built-in method does not handle correctly.
        file_name_without_extension = remove_suffix(file_name, extension)
        bundle = OutputHandler._get_or_create_bundle(data)
        if bundle.visualizer:
            visualization_file = make_file_name(
                file_name_without_extension,
                bundle.visualizer.file_extension,
            )
            visualizers = [
                ExistFileVisualizer('Visualization', visualization_file),
            ]

        extensions = {}
        kwargs = {}
        if data_type == DataTypes.DATASET:
            # Add datatable meta to extension
            dt_meta_path = get_meta_data_file_path(file_name)
            if os.path.exists(os.path.join(file_path, dt_meta_path)):
                extensions['DataTableMeta'] = dt_meta_path

            # Add schema of datatable
            # Check the type to avoid bug when sidecarfiles bundle is passed in some hack case of extra_folder
            if isinstance(data, DataTable):
                kwargs['schema'] = DataFrameSchemaDumper(data).dump_to_dict()
                kwargs['data'] = data.data_frame

            # Add other fields
            kwargs['file_path'] = file_name
            kwargs['overwrite_if_exist'] = False
            kwargs['validate_if_exist'] = False

        elif data_type in {DataTypes.CLUSTER, DataTypes.LEARNER, DataTypes.RECOMMENDER}:
            # Add model_dumper for CLUSTER and LEANER and RECOMMENDER
            kwargs['model_dumper'] = learner_cluster_dumper(data_type.value.name, file_name)

        elif data_type == DataTypes.TRANSFORM:
            # Add file_path for TRANSFORM
            kwargs['file_path'] = file_name

        saver(
            save_to=file_path,
            visualizers=visualizers,
            extensions=extensions,
            **kwargs,
        )
        common_logger.info(f"Writing meta successfully, datatype={data_type}")

    @staticmethod
    def handle_output(data, file_path, file_name, data_type, sidecar_files_only=False, azureml_output_folder=None):
        handler = _DATA_TYPE_HANDLERS.get(data_type)
        if not handler:
            raise NotImplementedError(f"DataType {data_type} does not support output for now")

        # `data` comes from module's return tuple,
        # may be an `OutputPortBundle` or "pure" object (such as `DataTable`, `BaseLearner`, etc.).
        #   1) When `data` is a "pure" object, generate a default `OutputPortBundle` here to perform the
        #      sidecar files handling.
        #   2) When `data` is an `OutputPortBundle` object already, use it directly.
        #      Modules can generate custom visualization methods using this mechanism.
        bundle = OutputHandler._get_or_create_bundle(data)

        # save data file if needed
        if not sidecar_files_only:
            full_path = os.path.join(file_path, file_name)
            with TimeProfile(f"Create file '{get_file_name(full_path)}' via {handler.__name__}"):
                handler.handle_output(bundle.data, full_path)

        # dump sidecar files
        extension = '.' + data_type.value.file_extension
        # Using `strutils.remove_suffix` instead of built-in `os.path.splitext` here.
        # Because some data types have multi-level extensions such as '.nh.csv', '.dataset.parquet',
        # which the built-in method does not handle correctly.
        file_name_without_extension = remove_suffix(file_name, suffix=extension)
        dumpers = [FileDumper(file_path, file_name_without_extension)]
        if azureml_output_folder:
            dumpers.append(AzureMLOutputDumper(azureml_output_folder, file_name_without_extension))
        bundle.dump_sidecar_files(dumpers, file_name_without_extension)

        saver = _DATA_TYPE_SAVERS.get(data_type)
        if saver:
            OutputHandler.handle_output_directory(data, file_path, file_name, data_type, saver)

    @staticmethod
    def _get_or_create_bundle(obj):
        if isinstance(obj, SideCarFileBundle):
            return obj
        else:
            return SideCarFileBundle.create(obj)


class InputHandler:
    @staticmethod
    def handle_input_directory(file_path):
        with TimeProfile(f"Try to read from {file_path} via meta"):
            directory = load_from_directory(file_path, model_loader=pickle_loader)
            common_logger.info(f"Load meta data from directory successfully, data={directory}, type={type(directory)}")

            # If the directory is DataFrame, convert it to DataTable
            if isinstance(directory, DataTableDirectory):
                return directory.data_table

            # If the directory is Model, return model if model data is loaded
            elif isinstance(directory, (ModelDirectory, TransformDirectory)) and directory.data is not None:
                common_logger.info(f"Load {directory.TYPE_NAME} successfully, data={directory.data}")
                return directory.data

            raise Exception(f"Unsupported directory type: {directory.dir_type}")

    @staticmethod
    def handle_input(file_path, file_name, data_type=None):
        full_path = os.path.join(file_path, file_name)
        handler = _DATA_TYPE_HANDLERS.get(data_type)
        if not handler:
            raise NotImplementedError(f"DataType {data_type} does not support input for now")

        with TimeProfile(f"Read from '{get_file_name(full_path)}' via {handler.__name__}"):
            return handler.handle_argument_string(full_path)

    @staticmethod
    def handle_input_from_stream(stream: io.BytesIO, data_type=None):
        handler = _DATA_TYPE_HANDLERS.get(data_type)

        if not handler:
            raise NotImplementedError(f"DataType {data_type} does not support input for now")

        if (handler is DataTableDatasetHandler) or (handler is DataTableCsvHandler):
            raise NotImplementedError('DataType {data_type} does not support handle_input_from_stream for now')

        return handler.handle_stream_source(stream)

    @staticmethod
    def handle_input_from_file_name(full_file_path, data_type=None):
        """De-serialization iLearner and iTransform into a python object
        Currently to support Deployment Service for reading resources

        :param full_file_path: full file path, including file name and file extension.
        :param data_type: specify data type explicitly, if not specified, refer from the file extension.
        :return: BaseLearner or BaseTransform
        """
        file_path = os.path.dirname(full_file_path)
        file_name = os.path.basename(full_file_path)

        if not data_type:
            data_type = DataTypes.from_file_name(file_name)

        return InputHandler.handle_input(file_path, file_name, data_type)

    @staticmethod
    def handle_input_one_file(file_path):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Invalid file_path '{file_path}'")

        if os.path.isfile(file_path):
            common_logger.info(f"A regular file '{file_path}' is provided, try loading the file directly.")
            return InputHandler.handle_input_from_file_name(file_path)
        common_logger.info(f"A folder '{file_path}' is provided, try loading a valid file in the folder.")
        for f in iter_files(file_path):
            try:
                common_logger.info(f"Try loading regular file '{f}'.")
                return InputHandler.handle_input_from_file_name(f)
            except BaseException as e:
                common_logger.warning(f"Try parsing file '{f}' failed, exception={e}")
        raise FileNotFoundError(f"No valid input file in path '{file_path}'")
