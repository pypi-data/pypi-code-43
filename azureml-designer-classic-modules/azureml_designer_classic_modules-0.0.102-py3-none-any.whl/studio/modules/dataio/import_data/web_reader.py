import os
import tempfile
import urllib

from azureml.studio.common.error import ErrorMapping, CouldNotDownloadFileError, InvalidUriError
from azureml.studio.common.types import AutoEnum
from azureml.studio.common.utils.retry_utils import retry
from azureml.studio.core.utils.strutils import generate_random_string
from azureml.studio.common.io.datatable.data_table_arff_reader import DataTableArffReader
from azureml.studio.common.io.datatable.data_table_csv_io import DataTableCsvSep, DataTableCsvReader
from azureml.studio.common.io.datatable.data_table_svmlight_reader import DataTableSvmLightReader


class WebSourceDataFormat(AutoEnum):
    CSV = ()
    TSV = ()
    ARFF = ()
    SvmLight = ()


def read_csv(input_url: str, data_format: WebSourceDataFormat, has_header: bool):
    with DownloadAsTempFile(input_url=input_url) as temp_file:
        sep = DataTableCsvSep.CSV if data_format is WebSourceDataFormat.CSV else DataTableCsvSep.TSV
        return DataTableCsvReader.read(filepath_or_buffer=temp_file,
                                       sep=sep,
                                       has_header=has_header)


def read_arff(input_url: str):
    with DownloadAsTempFile(input_url=input_url) as temp_file:
        return DataTableArffReader.read(filepath_or_buffer=temp_file)


def read_svmlight(input_url: str):
    with DownloadAsTempFile(input_url=input_url) as temp_file:
        return DataTableSvmLightReader.read(filepath_or_buffer=temp_file)


class DownloadAsTempFile:
    def __init__(self, input_url, tries=10, delay=5, backoff=1):
        self.input_url = input_url
        self.temp_dir = tempfile.TemporaryDirectory()
        temp_file = generate_random_string()
        self.temp_file = os.path.join(self.temp_dir.name, temp_file)

        @retry(urllib.error.URLError, tries=tries, delay=delay, backoff=backoff)
        def download_with_retry(url_to_download, file_name):
            urllib.request.urlretrieve(url_to_download, file_name)

        self.download_func = download_with_retry

    def __enter__(self):
        try:
            self.download_func(self.input_url, self.temp_file)
        except urllib.error.URLError as url_error:
            ErrorMapping.rethrow(url_error, CouldNotDownloadFileError(self.input_url))
        except ValueError as value_error:
            ErrorMapping.rethrow(value_error, InvalidUriError(self.input_url))
        return self.temp_file

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.temp_dir.__exit__(exc_type, exc_val, exc_tb)
