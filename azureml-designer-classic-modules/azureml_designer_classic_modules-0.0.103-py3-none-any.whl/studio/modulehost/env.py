import os

from abc import ABCMeta, abstractmethod
from pathlib import Path

from azureml.studio.modulehost.attributes import InputPort, OutputPort
from azureml.studio.common.error import AlghostRuntimeError
from azureml.studio.core.logger import module_host_logger as log, TimeProfile, indented_logging_block
from azureml.studio.modulehost.handler.port_io_handler import InputHandler, OutputHandler
from azureml.studio.common.datatypes import DataTypes
from azureml.studio.core.utils.fileutils import ensure_folder, make_file_name, iter_files
from azureml.studio.core.utils.strutils import quote
from azureml.studio.core.utils.jsonutils import dump_to_json_file
from azureml.studio.core.io.any_directory import has_meta


class RuntimeEnv(metaclass=ABCMeta):
    @abstractmethod
    def handle_input_port(self, annotation, param_value):
        pass

    @abstractmethod
    def handle_output_port(self, data, annotation, param_value):
        pass


class FolderRuntimeEnv(RuntimeEnv):
    _AZUREML_EXTRA_OUTPUT_FOLDER = 'dataset_profile'
    _DATA_FILE_NAME = 'data'
    _DATA_TYPE_FILE_NAME = 'data_type.json'

    def _get_absolute_path(self, folder):
        return folder

    @staticmethod
    def _print_dir_hierarchy_to_log(path):
        log.debug(f"Content of directory {path}:")
        with indented_logging_block():
            for f in iter_files(path):
                log.debug(Path(f).relative_to(path))

    def handle_input_port(self, annotation, param_value):
        if not isinstance(annotation, InputPort):
            raise AlghostRuntimeError(f"annotation must be type of InputPort")

        with TimeProfile(f"Handle input port {quote(annotation.name)}"):
            file_path = None if param_value is None else self._get_absolute_path(param_value.folder)
            if not file_path:
                if annotation.is_optional:
                    log.warning(f"File '{file_path}' does not exist.")
                    return None
                else:
                    raise AlghostRuntimeError(f"Input port '{annotation.name}' is not optional, "
                                              f"but not specified with a path.")

            # Currently, dataset team loads the dataset to local machine in a lazy way
            # By design, the os.walk function would trigger the full stream download
            # So, we add a TimeProfile here to explicitly track the stream loading time
            with TimeProfile(f"Mount/Download dataset to '{file_path}'"):
                self._print_dir_hierarchy_to_log(file_path)

            # This block of code supports both of the cases for backward compatibility.
            # Using new directory based logic if meta file exists.
            if has_meta(file_path):
                return InputHandler.handle_input_directory(file_path)

            # For the legacy implementation (prior to alghost 0.0.52),
            # 'data type' and 'file name' are defined by a naming convention
            # that 'data type' is saved as a 'data_type.json' file and
            # 'file name' is constant 'data'.
            #
            # Start from alghost 0.0.53, these information are given by SMT
            # explicitly via param_value, making it capable to support
            # user-uploaded datasets, which does not need to follow the
            # naming conventions.

            log.info("Meta file not found, fallback to legacy handler.")

            data_type = param_value.data_type
            data_type_file = os.path.join(file_path, self._DATA_TYPE_FILE_NAME)
            if not data_type:
                if not os.path.exists(data_type_file):
                    log.info("Datatype file not found, fallback to handling one file logic.")
                    return InputHandler.handle_input_one_file(file_path)
                data_type = DataTypes.from_json_file(data_type_file)

            file_name = param_value.file_name
            if not file_name:
                extension = data_type.value.file_extension
                file_name = make_file_name(self._DATA_FILE_NAME, extension)

            log.info(f"Folder: '{file_path}'")
            log.info(f"File Name: '{file_name}'")
            log.info(f"Data type: '{data_type.value.name}'")

            data = InputHandler.handle_input(file_path, file_name, data_type)

            # Create and dump sidecar files of input data to extra_output folder
            if param_value.extra_folder:
                with TimeProfile('Output sidecar files for input port'):
                    file_path = self._get_absolute_path(param_value.extra_folder)
                    azureml_output_folder = os.path.join(self._AZUREML_EXTRA_OUTPUT_FOLDER, param_value.extra_folder)
                    self._do_handle_output_port(data, file_path, data_type,
                                                sidecar_files_only=True,
                                                azureml_output_folder=azureml_output_folder)

            return data

    def handle_output_port(self, data, annotation, param_value):
        if not isinstance(annotation, OutputPort):
            raise AlghostRuntimeError(f"annotation must be type of OutputPort")

        with TimeProfile(f"Handle output port {quote(annotation.name)}"):
            file_path = self._get_absolute_path(param_value)
            data_type = annotation.return_type
            self._do_handle_output_port(data, file_path, data_type)

    def _do_handle_output_port(self, data, file_path, data_type, sidecar_files_only=False, azureml_output_folder=None):
        extension = data_type.value.file_extension
        file_name = make_file_name(self._DATA_FILE_NAME, extension)
        log.info(f"Data type: {data_type.value.name}")

        # Need to create directory for output port first if not exist
        log.info(f"Create directory: '{file_path}'")
        ensure_folder(file_path)

        OutputHandler.handle_output(data, file_path, file_name, data_type,
                                    sidecar_files_only=sidecar_files_only,
                                    azureml_output_folder=azureml_output_folder,
                                    )

        # write output data type to data_type.json file, for later usage
        self.save_data_type_to_file(data_type, file_path)

    def save_data_type_to_file(self, data_type, file_path):
        with TimeProfile(f"Create data type file '{self._DATA_TYPE_FILE_NAME}'"):
            dump_to_json_file(data_type.value.to_dict(), os.path.join(file_path, self._DATA_TYPE_FILE_NAME))

    def save_module_statistics_to_file(self, module_statistics_attributes, folder: str, file_name: str):
        folder = self._get_absolute_path(folder)
        os.makedirs(folder, exist_ok=True)
        local_file_path = os.path.join(folder, file_name)
        dump_to_json_file(module_statistics_attributes, local_file_path)


class JesRuntimeEnv(FolderRuntimeEnv):
    _ENVIRON_PREFIX = 'AZUREML_DATAREFERENCE_'

    @classmethod
    def is_valid_env_name(cls, name):
        if not isinstance(name, str):
            raise TypeError(f"Expected str but got {type(name)}")
        return name.startswith(cls._ENVIRON_PREFIX)

    def _get_absolute_path(self, env_name):
        env_full_name = f"{self._ENVIRON_PREFIX}{env_name}"
        env_value = os.environ.get(env_full_name)
        log.debug(f"ENV {env_full_name}: {env_value}")
        return env_value


class FileBasedRuntimeEnv(RuntimeEnv):
    def __init__(self, base_dir):
        self._base_dir = base_dir

    def handle_input_port(self, annotation, param_value):
        file_path = self._base_dir
        _, extension = os.path.splitext(param_value)
        file_name = param_value
        data_type = DataTypes.from_extension(extension)

        data = InputHandler.handle_input(file_path, file_name, data_type)
        return data

    def handle_output_port(self, data, annotation, param_value):
        file_path = os.path.join(self._base_dir, 'gen')
        file_name = param_value
        data_type = annotation.return_type

        os.makedirs(file_path, exist_ok=True)
        OutputHandler.handle_output(data, file_path, file_name, data_type)
