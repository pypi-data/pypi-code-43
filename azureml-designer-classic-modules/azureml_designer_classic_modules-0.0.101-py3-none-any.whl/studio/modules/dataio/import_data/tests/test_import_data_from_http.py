import pytest

from azureml.studio.common.error import CouldNotDownloadFileError, InvalidUriError
from azureml.studio.modules.dataio.import_data.import_data import ImportDataModule, ReaderDataSourceOrSink,\
    WebSourceDataFormat
from azureml.studio.modules.dataio.import_data.web_reader import DownloadAsTempFile


def test_load_csv():
    # pylint: disable=no-value-for-parameter
    dt = ImportDataModule.run(
        source=ReaderDataSourceOrSink.Http,
        input_url="https://amlstudiomodulev2test.blob.core.windows.net/unittest-csv/input_csv.csv",
        data_format=WebSourceDataFormat.CSV,
        csv_tsv_has_header=False)[0]
    assert dt.number_of_rows == 3
    assert dt.column_names == ['Col1', 'Col2', 'Col3']


def test_load_csv_with_header():
    # pylint: disable=no-value-for-parameter
    dt = ImportDataModule.run(
        source=ReaderDataSourceOrSink.Http,
        input_url="https://amlstudiomodulev2test.blob.core.windows.net/unittest-csv/input_csv_with_header.csv",
        data_format=WebSourceDataFormat.CSV,
        csv_tsv_has_header=True)[0]
    assert dt.number_of_rows == 3


def test_load_tsv():
    # pylint: disable=no-value-for-parameter
    dt = ImportDataModule.run(
        source=ReaderDataSourceOrSink.Http,
        input_url="https://amlstudiomodulev2test.blob.core.windows.net/unittest-tsv/input_tsv.tsv",
        data_format=WebSourceDataFormat.TSV,
        csv_tsv_has_header=False)[0]
    assert dt.number_of_rows == 3
    assert dt.column_names == ['Col1', 'Col2', 'Col3']


def test_load_tsv_with_header():
    # pylint: disable=no-value-for-parameter
    dt = ImportDataModule.run(
        source=ReaderDataSourceOrSink.Http,
        input_url="https://amlstudiomodulev2test.blob.core.windows.net/unittest-tsv/input_tsv_with_header.tsv",
        data_format=WebSourceDataFormat.TSV,
        csv_tsv_has_header=True)[0]
    assert dt.number_of_rows == 3


def test_load_arff():
    # pylint: disable=no-value-for-parameter
    dt = ImportDataModule.run(
        source=ReaderDataSourceOrSink.Http,
        input_url="https://amlstudiomodulev2test.blob.core.windows.net/unittest-arff/input_arff.arff",
        data_format=WebSourceDataFormat.ARFF)[0]
    assert dt.number_of_rows == 3


def test_load_svmlight():
    # pylint: disable=no-value-for-parameter
    dt = ImportDataModule.run(
        source=ReaderDataSourceOrSink.Http,
        input_url="https://amlstudiomodulev2test.blob.core.windows.net/unittest-svmlight/input_svmlight.svmlight",
        data_format=WebSourceDataFormat.SvmLight)[0]
    assert dt.number_of_rows == 6


def test_download_exception():
    with pytest.raises(CouldNotDownloadFileError):
        with DownloadAsTempFile(input_url="https://dummy_host/dummy_path", tries=3, delay=1, backoff=1) as temp_file:
            print(temp_file)

    with pytest.raises(InvalidUriError):
        with DownloadAsTempFile(input_url="dummy_url", tries=3, delay=1, backoff=1) as temp_file:
            print(temp_file)
