import argparse
import os
import uuid
import json
import dpath.util
import re
import azureml.core
import azureml.dataprep as dprep
import base64
import zlib
from azureml.core import Dataset, Run, Datastore
from azureml.dataprep.api.errorhandlers import UnexpectedError
from azureml.studio.core.io.data_frame_directory import DataFrameDirectory
from azureml.studio.core.data_frame_schema import DataFrameSchema
from azureml.studio.core.logger import logger, TimeProfile, time_profile
from azureml.studio.internal.error_handler import error_handler
from msrest.exceptions import HttpOperationError
from azureml.dataprep.api.dataflow import Dataflow
from ..common.workspaceutil import get_workspace, get_time_as_string
from azureml.studio.internal.error import ErrorMapping, IncorrectAzureStorageOrKeyError, \
    CouldNotOpenFileError, CouldNotDownloadFileError, InvalidDatasetError, \
    IncorrectAzureMLDatastoreError

logger.debug(f'Executing {os.path.abspath(__file__)}')
logger.debug(f"Azure ML SDK Version: {azureml.core.VERSION}")
logger.debug(f"DataPrep Version: {azureml.dataprep.__version__}")


def ensure_dir(file_path):
    """Check if the directory exists"""
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)


def convert_to_lowercase(input_request_dto):
    """Convert capital letters in dictionary to lowercase"""
    new = {}
    for key, value in input_request_dto.items():
        if isinstance(value, dict):
            value = convert_to_lowercase(value)
        new_key = key[0].lower() + key[1:]
        new[new_key] = value
    return new


def check_url_format(url_str):
    """Check if input string is a url"""
    result = re.search('^(https?)://.*$', url_str)
    return True if result else False


class ImportTabularDataModule:
    _HTTP_SOURCE = 'HttpSource'
    _HTTP_PATH_KEY = 'httpUrl'
    _AZURE_SQL_DATABASE_PATH_KEY = 'sqlDataPath/sqlQuery'
    _AZURE_FILE_PATH_KEY = 'azureFilePath'
    _OTHERS_PATH_KEY = 'relativePath'

    @classmethod
    def __init__(cls, input_dict):
        cls.run_obj = Run.get_context()
        cls.workspace = get_workspace()
        cls.input_dataset_request_dto = input_dict['Input_dataset_request_DTO']
        cls.datastore_type = input_dict['Data_store_type']
        cls.override_datastore_name = input_dict['Override_data_store_name']
        cls.override_data_path = input_dict['Override_data_path']
        cls.dataset = None

    @staticmethod
    def get_datastore_type(workspace, datastore_name):
        """Check the data store type: http, sql, blob, adlgen1, adlgen2"""
        try:
            if datastore_name == '' or datastore_name is None:
                return ImportTabularDataModule._HTTP_SOURCE
            datastore = Datastore(workspace, datastore_name)
            return datastore.datastore_type
        except Exception as azureml_datastore_error:
            logger.error(f"{get_time_as_string()} Exception in get_datastore_type(): {str(azureml_datastore_error)}.")
            ErrorMapping.rethrow(azureml_datastore_error, IncorrectAzureMLDatastoreError(datastore_name=datastore_name, workspace_name=workspace))

    @staticmethod
    def get_path_key(store_type):
        """Get the key defined in requestDto"""
        if store_type in ['AzureSqlDatabase', 'AzurePostgreSql']:
            path_key = ImportTabularDataModule._AZURE_SQL_DATABASE_PATH_KEY
        elif store_type in ['AzureFile']:
            path_key = ImportTabularDataModule._AZURE_FILE_PATH_KEY
        elif store_type in ['HttpSource']:
            path_key = ImportTabularDataModule._HTTP_PATH_KEY
        else:
            path_key = ImportTabularDataModule._OTHERS_PATH_KEY
        return path_key

    @classmethod
    @time_profile
    def process_input_dataset_request_dto(cls, input_dataset_request_dto):
        """
        Process requestDto received from UI
        1. set name using run.tags.node_id
        2. register as hidden dataset
        3. set sourceProperties as None
        4. override datastore_name and data_path using override_datastore_name and override_data_path when available
        """
        try:
            # check if a json string or a compressed string
            if input_dataset_request_dto.startswith('{') and input_dataset_request_dto.endswith('}'):
                request = json.loads(input_dataset_request_dto)
            else:
                base64de = base64.b64decode(input_dataset_request_dto)
                decompressed_request_dto = zlib.decompress(base64de).decode('utf-8')
                request = json.loads(decompressed_request_dto)

            request = convert_to_lowercase(request)

            # send http register request to service endpoint
            is_offline_run = cls.run_obj.id.startswith('OfflineRun')
            if not is_offline_run:
                node_id = cls.run_obj.tags.get('azureml.nodeid')
                if node_id is None:
                    node_id = str(uuid.uuid4())[:8]
            else:
                node_id = str(uuid.uuid4())[:8]
            logger.debug(f'set name using node_id: {node_id}')

            request['name'] = 'dataset_' + str(node_id)
            request['isVisible'] = False
            request['sourceProperties'] = None  # workaround for nonhttp_override_none 2019/09/19

            if cls.override_data_path is None and cls.override_datastore_name is None:
                logger.info(f"{get_time_as_string()} Process input request dto is done.")
                logger.info(f"Return original request dto: {json.dumps(request)}")
                return request

            new_datapath = {}
            store_name = None
            if dpath.util.search(request, "dataPath/datastoreName"):
                store_name = dpath.util.get(request, 'dataPath/datastoreName')
            logger.debug(f'store_name: {store_name}')

            is_old_http_source = False
            if cls._HTTP_PATH_KEY in request['dataPath']:
                is_old_http_source = True

            is_new_http_source = False
            if cls.override_data_path is not None and check_url_format(cls.override_data_path):
                is_new_http_source = True

            if cls.override_datastore_name is not None and store_name != cls.override_datastore_name:
                store_name = cls.override_datastore_name

            store_type = ImportTabularDataModule.get_datastore_type(cls.workspace, store_name)
            path_key = ImportTabularDataModule.get_path_key(store_type)
            path = dpath.util.get(request['dataPath'], path_key)
            if cls.override_data_path is not None and path != cls.override_data_path:
                path = cls.override_data_path
                if is_new_http_source:
                    store_name = None
                    path_key = cls._HTTP_PATH_KEY

            dpath.util.new(new_datapath, 'datastoreName', store_name)
            dpath.util.new(new_datapath, path_key, path)

            request['dataPath'] = new_datapath
            if is_old_http_source:
                request['sourceProperties'] = None

            logger.info(f"{get_time_as_string()} Process input request dto is done.")
            logger.info(f"New request dto: {json.dumps(request)}")
            return request
        except Exception as err:
            logger.error(f"{get_time_as_string()} Process input dataset request dto error: {str(err)}")
            raise err

    @classmethod
    @time_profile
    def generate_dataflow(cls) -> 'Dataflow':
        """Register requestDto to data set service endpoint"""
        try:
            logger.info('Start to register dto request.')
            request = cls.process_input_dataset_request_dto(cls.input_dataset_request_dto)
            cls.dataset = Dataset._client()._register_from_request(cls.workspace, request, as_pending=False,
                                                                   exist_ok=True, update_if_exists=True)
            data_definition = cls.dataset.get_definition()
            logger.debug(f'Dataflow for registered requestDto:\n{data_definition.to_json()}')
            logger.debug(f"{get_time_as_string()} Register input request dto is done and registered dataset id: {cls.dataset.id}")
            return data_definition

        except HttpOperationError as http_error:
            if bool(re.search('Datastore(.*)Not found', str(http_error))):
                ErrorMapping.rethrow(http_error, IncorrectAzureStorageOrKeyError(request['dataPath']['datastoreName']))
            elif 'Requested file(s) does not exist or specified credential does not have access to read' in str(http_error):
                ErrorMapping.rethrow(http_error, CouldNotOpenFileError(file_name=request['dataPath']['relativePath']))
            elif 'The dataset type of the dataset is not Tabular' in str(http_error):
                ErrorMapping.rethrow(http_error, CouldNotDownloadFileError(file_url=request['dataPath']['httpUrl']))
        except Exception as err:
            logger.error(f"{get_time_as_string()} Exception in register from request: {str(err)}")
            raise err

    @classmethod
    # @ErrorHandler('./error_folder')
    @error_handler
    @time_profile
    def run(cls, input_dict: dict = None) -> DataFrameDirectory:
        """Convert the dataset to pandas dataframe and create data frame directory object"""

        if 'Input_dataset_request_DTO' in input_dict:
            cls.input_dataset_request_dto = input_dict['Input_dataset_request_DTO']
        if 'Data_store_type' in input_dict:
            cls.datastore_type = input_dict['Data_store_type']
        if 'Override_data_store_name' in input_dict:
            cls.override_datastore_name = input_dict['Override_data_store_name']
        if 'Override_data_path' in input_dict:
            cls.override_data_path = input_dict['Override_data_path']

        data_flow = cls.generate_dataflow()
        try:
            logger.info(f'Start to create output port dfd')
            if data_flow is not None:
                # call Dataflow.to_pandas_dataframe(extended_types=True)
                data_frame = Dataflow.to_pandas_dataframe(data_flow, extended_types=True)
                if data_frame is None:
                    ErrorMapping.throw(InvalidDatasetError(dataset1=cls.dataset.id))
                schema = DataFrameSchema.data_frame_to_dict(data_frame)
        except UnexpectedError as azureml_dataprep_unexpectederr:
            raise azureml_dataprep_unexpectederr

        output_port_dfd = DataFrameDirectory.create(data=data_frame, schema=schema)
        logger.info(f"{get_time_as_string()} Create output port dtd is done")
        return output_port_dfd

@time_profile
def main(args):
    """
    Import data set from various data sources received from studio UI
    1.create input parameters dictionary
    2.initialize an import tabular data module
    3.register input dataset request dto to service endpoint and return a data frame directory
    4.save dataset as parquet and create schema/visualization sidecar files
    :param args:
    :return:
    """
    input_dataset_request_dto = args.input_dataset_request_dto
    datastore_type = args.datastore_type
    override_datastore_name = args.override_datastore_name
    override_data_path = args.override_data_path
    output_dir = args.output_dir

    logger.debug(f'Received argument --input_dataset_request_dto: {input_dataset_request_dto}.')
    logger.debug(f'Received argument --datastore_type: {datastore_type}.')
    logger.debug(f'Received argument --override_datastore_name: {override_datastore_name}.')
    logger.debug(f'Received argument --override_data_path: {override_data_path}.')
    logger.debug(f'Received argument --output_dir: {output_dir}.')

    input_dict = {'Input_dataset_request_DTO': input_dataset_request_dto, 'Data_store_type': datastore_type,
                  'Override_data_store_name': override_datastore_name, 'Override_data_path': override_data_path,
                  }

    import_tabular_data_module = ImportTabularDataModule(input_dict)

    data_frame_directory = import_tabular_data_module.run(input_dict)

    with TimeProfile('Save dataset and sidecar files'):
        ensure_dir(output_dir)
        data_frame_directory.dump(output_dir, overwrite_if_exist=True, validate_if_exist=True)

    logger.info(f"{get_time_as_string()} Save data set and sidecar files is done.")


def configs(parser):
    parser.add_argument("--input_dataset_request_dto", type=str, help="Input dataset request Dto string")
    parser.add_argument("--datastore_type", type=str, help="Data store type")
    parser.add_argument("--override_datastore_name", type=str, help="New data store name", default=None)
    parser.add_argument("--override_data_path", type=str, help="New data path", default=None)
    parser.add_argument("--output_dir", type=str, help="OutputPath for infer values from Output Ports")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    configs(parser)

    if os.environ.get('AML_PARAMETER_Override_data_store_name') == 'True':
        print("AML_PARAMETER_Override_data_store_name " + os.environ['AML_PARAMETER_Override_data_store_name'])
    else:
        print("There is no AML_PARAMETER_Override_data_store_name environment variable.")
    if os.environ.get('AML_PARAMETER_Override_data_path') == 'True':
        print("AML_PARAMETER_Override_data_path " + os.environ['AML_PARAMETER_Override_data_path'])
    else:
        print("There is no AML_PARAMETER_Override_data_path environment variable.")
    args, unknown = parser.parse_known_args()

    main(args)
