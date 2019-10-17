import base64

import pytest

from azureml.studio.common.credential import SecureString
from azureml.studio.common.error import InvalidUriError, IncorrectAzureStorageOrKeyError, \
    IncorrectAzureBlobNameError, IncorrectAzureContainerError, ColumnCountNotEqualError, NotEqualColumnNamesError, \
    NotCompatibleColumnTypesError
from azureml.studio.modules.dataio.import_data.azure_blob_reader import BlobDataFormat
from azureml.studio.modules.dataio.import_data.import_data import ImportDataModule, ReaderDataSourceOrSink, \
    ReaderAuthenticationType


@pytest.fixture
def unittest_account_name():
    return "amlstudiomodulev2test"


@pytest.fixture
def unittest_account_key():
    # For test only
    return SecureString(base64.b64decode(
        "MQBKADAATABBACsATQBFADMAbABTAFUAawBSAFMAcQBtAFYAVwB5AE8ATQBTAE0AawBuAFMAZQBGAEMANABBAHkA"
        "ZABuAHoAZQBTAGoAdAA2AHUASgBKAFkAVwBXAGcANwByAEgANQBIAGEAagArAGEAOQBSAGgASABuAG4ATQBLAC8A"
        "ZwBLAFMAMABOAHoASgBqAFQAUwBNAHkAcAA3AHAAdgA2AEgASABRAD0APQA=").decode("utf-8"))


def test_load_csv():
    # pylint: disable=no-value-for-parameter
    dt = ImportDataModule.run(
        source=ReaderDataSourceOrSink.AzureBlobStorage,
        auth_type=ReaderAuthenticationType.PublicOrSAS,
        sas_blob_uri="https://amlstudiomodulev2test.blob.core.windows.net/unittest-csv/input_csv_with_header.csv",
        sas_blob_format=BlobDataFormat.CSV,
        sas_blob_csv_has_header=True)[0]
    assert dt.number_of_rows == 3
    assert dt.column_names == ['C1', 'C2', 'C3']


@pytest.mark.parametrize(
    "sas_url", [
        "https://amlstudiomodulev2test.blob.core.windows.net/unittest-csv/input_csv_with_header.csv?"
        "sp=r&st=2019-03-08T06:15:28Z&se=2099-03-08T14:15:28Z&spr=https&sv=2018-03-28"
        "&sig=c20XFX1y7sCS8m%2FdLe0fGtok23t1eE8UySoh0Y%2BcRII%3D&sr=b",
        "https://amlstudiomodulev2test.blob.core.windows.net/unittest-csv/input%20csv%20with%20header.csv?"
        "sp=r&st=2019-03-12T11:24:16Z&se=2099-03-12T19:24:16Z&spr=https&sv=2018-03-28"
        "&sig=qHYPjRPLUWQMo1M%2BFUOssEw07VxYe%2Ba547oNNgcKFWc%3D&sr=b"
    ])
def test_load_csv_with_sas_token(sas_url):
    # pylint: disable=no-value-for-parameter
    dt = ImportDataModule.run(
        source=ReaderDataSourceOrSink.AzureBlobStorage,
        auth_type=ReaderAuthenticationType.PublicOrSAS,
        sas_blob_uri=sas_url,
        sas_blob_format=BlobDataFormat.CSV,
        sas_blob_csv_has_header=True)[0]
    assert dt.number_of_rows == 3
    assert dt.column_names == ['C1', 'C2', 'C3']


def test_load_csv_with_account(unittest_account_name, unittest_account_key):
    # pylint: disable=no-value-for-parameter
    dt = ImportDataModule.run(
        source=ReaderDataSourceOrSink.AzureBlobStorage,
        auth_type=ReaderAuthenticationType.Account,
        account_name=unittest_account_name,
        account_key=unittest_account_key,
        account_blob_path="/unittest-csv/input_csv_with_header.csv",
        account_blob_format=BlobDataFormat.CSV,
        account_blob_csv_has_header=True)[0]
    assert dt.number_of_rows == 3
    assert dt.column_names == ['C1', 'C2', 'C3']


def test_load_csv_with_account_in_container(unittest_account_name, unittest_account_key):
    # pylint: disable=no-value-for-parameter
    dt = ImportDataModule.run(
        source=ReaderDataSourceOrSink.AzureBlobStorage,
        auth_type=ReaderAuthenticationType.Account,
        account_name=unittest_account_name,
        account_key=unittest_account_key,
        account_blob_path="unittest-csv",
        account_blob_format=BlobDataFormat.CSV,
        account_blob_csv_has_header=False)[0]

    # There are 4 files in all, 2 of them have 3 lines in each, 3 of them have 4 lines in each
    assert dt.number_of_rows == 18
    assert dt.column_names == ['Col1', 'Col2', 'Col3']


def test_load_csv_with_account_with_wildcard(unittest_account_name, unittest_account_key):
    # pylint: disable=no-value-for-parameter
    dt = ImportDataModule.run(
        source=ReaderDataSourceOrSink.AzureBlobStorage,
        auth_type=ReaderAuthenticationType.Account,
        account_name=unittest_account_name,
        account_key=unittest_account_key,
        account_blob_path="/unittest-csv/*_with_header.csv",
        account_blob_format=BlobDataFormat.CSV,
        account_blob_csv_has_header=True)[0]
    # Two files expected
    # /unittest-csv/input_csv_with_header.csv and /unittest-csv/dirtest/input_csv_with_header.csv
    assert dt.number_of_rows == 6
    assert dt.column_names == ['C1', 'C2', 'C3']


def test_load_arff_with_sas_token():
    # pylint: disable=no-value-for-parameter
    dt = ImportDataModule.run(
        source=ReaderDataSourceOrSink.AzureBlobStorage,
        auth_type=ReaderAuthenticationType.PublicOrSAS,
        sas_blob_uri="https://amlstudiomodulev2test.blob.core.windows.net/unittest-arff/input_arff.arff?"
                     "sp=r&st=2019-03-07T11:59:02Z&se=2099-03-07T19:59:02Z&spr=https&sv=2018-03-28"
                     "&sig=M01wKnO9xu6AWC6dNmdT4O%2BoH5CWJvjCdGGRLWWfqkQ%3D&sr=b",
        sas_blob_format=BlobDataFormat.ARFF)[0]
    assert dt.number_of_rows == 3


def test_load_arff_with_sas_token_in_container():
    # pylint: disable=no-value-for-parameter
    dt = ImportDataModule.run(
        source=ReaderDataSourceOrSink.AzureBlobStorage,
        auth_type=ReaderAuthenticationType.PublicOrSAS,
        sas_blob_uri="https://amlstudiomodulev2test.blob.core.windows.net/unittest-arff",
        sas_blob_format=BlobDataFormat.ARFF)[0]

    # There are 8 files in all, 4 of them have 3 lines in each, 4 of them have 4 lines in each
    assert dt.number_of_rows == 6


@pytest.mark.parametrize(
    "invalid_url", [
        "dummy_url",
        "https://.blob.core.windows.net/unittest-arff"
    ])
def test_invalid_url_excpetion_via_public_sas(invalid_url):
    with pytest.raises(InvalidUriError):
        # pylint: disable=no-value-for-parameter
        ImportDataModule.run(
            source=ReaderDataSourceOrSink.AzureBlobStorage,
            auth_type=ReaderAuthenticationType.PublicOrSAS,
            sas_blob_uri=invalid_url,
            sas_blob_format=BlobDataFormat.ARFF)


@pytest.mark.parametrize(
    "invalid_url, expected_error", [
        ("https://amlstudiomodulev2test.blob.core.windows.net/private/input_csv_with_header.csv",
         IncorrectAzureBlobNameError),
        ("https://amlstudiomodulev2test.blob.core.windows.net/private/input_csv_with_header.csv?"
         "sp=r&st=1900-03-11T09:24:44Z&se=1900-03-11T17:24:44Z&spr=https&sv=2018-03-28"
         "&sig=S5q3KTSh95qYKVD2Axy3UGxxhXuk8J9k411X6i6AB7c%3D&sr=b", IncorrectAzureStorageOrKeyError)
    ])
def test_auth_errors_via_public_sas(invalid_url, expected_error):
    with pytest.raises(expected_error):
        # pylint: disable=no-value-for-parameter
        ImportDataModule.run(
            source=ReaderDataSourceOrSink.AzureBlobStorage,
            auth_type=ReaderAuthenticationType.PublicOrSAS,
            sas_blob_uri=invalid_url,
            sas_blob_format=BlobDataFormat.CSV,
            sas_blob_csv_has_header=True)


def test_exceptions_via_account(unittest_account_name, unittest_account_key):
    with pytest.raises(IncorrectAzureContainerError):
        # pylint: disable=no-value-for-parameter
        ImportDataModule.run(
            source=ReaderDataSourceOrSink.AzureBlobStorage,
            auth_type=ReaderAuthenticationType.Account,
            account_name=unittest_account_name,
            account_key=unittest_account_key,
            account_blob_path="dummy_container",
            account_blob_format=BlobDataFormat.ARFF)

    with pytest.raises(IncorrectAzureStorageOrKeyError):
        # pylint: disable=no-value-for-parameter
        ImportDataModule.run(
            source=ReaderDataSourceOrSink.AzureBlobStorage,
            auth_type=ReaderAuthenticationType.Account,
            account_name=unittest_account_name,
            account_key=SecureString("dummy_key"),
            account_blob_path="dummy_container",
            account_blob_format=BlobDataFormat.ARFF)


def test_invalid_blob_name_error(unittest_account_name, unittest_account_key):
    # Test invalid SAS path
    with pytest.raises(IncorrectAzureBlobNameError):
        # pylint: disable=no-value-for-parameter
        ImportDataModule.run(
            source=ReaderDataSourceOrSink.AzureBlobStorage,
            auth_type=ReaderAuthenticationType.PublicOrSAS,
            sas_blob_uri="https://amlstudiomodulev2test.blob.core.windows.net/unittest-csv/not-exist-file.csv",
            sas_blob_format=BlobDataFormat.CSV,
            sas_blob_csv_has_header=True)

    # Test invalid blob path
    with pytest.raises(IncorrectAzureBlobNameError):
        # pylint: disable=no-value-for-parameter
        ImportDataModule.run(
            source=ReaderDataSourceOrSink.AzureBlobStorage,
            auth_type=ReaderAuthenticationType.Account,
            account_name=unittest_account_name,
            account_key=unittest_account_key,
            account_blob_path="/unittest-csv/not-exist-file.csv",
            account_blob_format=BlobDataFormat.CSV,
            account_blob_csv_has_header=False)

    # Test empty container
    with pytest.raises(IncorrectAzureBlobNameError,
                       match="Failed to find any Azure storage blobs under container "):
        # pylint: disable=no-value-for-parameter
        ImportDataModule.run(
            source=ReaderDataSourceOrSink.AzureBlobStorage,
            auth_type=ReaderAuthenticationType.Account,
            account_name=unittest_account_name,
            account_key=unittest_account_key,
            account_blob_path="/unittest-empty",
            account_blob_format=BlobDataFormat.CSV,
            account_blob_csv_has_header=False)

    # Test invalid blob wildcard path
    with pytest.raises(IncorrectAzureBlobNameError,
                       match="Failed to find any Azure storage blobs with wildcard path "):
        # pylint: disable=no-value-for-parameter
        ImportDataModule.run(
            source=ReaderDataSourceOrSink.AzureBlobStorage,
            auth_type=ReaderAuthenticationType.Account,
            account_name=unittest_account_name,
            account_key=unittest_account_key,
            account_blob_path="/unittest-csv/*_not_exist_wildcard_path.csv",
            account_blob_format=BlobDataFormat.CSV,
            account_blob_csv_has_header=False)


def test_load_inconsistent_csv_files(unittest_account_name, unittest_account_key):
    # Test inconsistent column count
    with pytest.raises(ColumnCountNotEqualError,
                       match='Column count in file '):
        # pylint: disable=no-value-for-parameter
        ImportDataModule.run(
            source=ReaderDataSourceOrSink.AzureBlobStorage,
            auth_type=ReaderAuthenticationType.Account,
            account_name=unittest_account_name,
            account_key=unittest_account_key,
            account_blob_path="/inconsistent-csv/diff-count/*.csv",
            account_blob_format=BlobDataFormat.CSV,
            account_blob_csv_has_header=True)

    # Test inconsistent column names
    with pytest.raises(NotEqualColumnNamesError,
                       match='Column names are not the same for column '):
        # pylint: disable=no-value-for-parameter
        ImportDataModule.run(
            source=ReaderDataSourceOrSink.AzureBlobStorage,
            auth_type=ReaderAuthenticationType.Account,
            account_name=unittest_account_name,
            account_key=unittest_account_key,
            account_blob_path="/inconsistent-csv/diff-name/*.csv",
            account_blob_format=BlobDataFormat.CSV,
            account_blob_csv_has_header=True)

    # Test inconsistent column types
    with pytest.raises(NotCompatibleColumnTypesError,
                       match='Column element types are not compatible for column '):
        # pylint: disable=no-value-for-parameter
        ImportDataModule.run(
            source=ReaderDataSourceOrSink.AzureBlobStorage,
            auth_type=ReaderAuthenticationType.Account,
            account_name=unittest_account_name,
            account_key=unittest_account_key,
            account_blob_path="/inconsistent-csv/diff-type/*.csv",
            account_blob_format=BlobDataFormat.CSV,
            account_blob_csv_has_header=True)


def test_load_inconsistent_arff_files(unittest_account_name, unittest_account_key):
    # Test inconsistent column count
    with pytest.raises(ColumnCountNotEqualError,
                       match='Column count in file '):
        # pylint: disable=no-value-for-parameter
        ImportDataModule.run(
            source=ReaderDataSourceOrSink.AzureBlobStorage,
            auth_type=ReaderAuthenticationType.Account,
            account_name=unittest_account_name,
            account_key=unittest_account_key,
            account_blob_path="/inconsistent-arff/diff-count/*.arff",
            account_blob_format=BlobDataFormat.ARFF)

    # Test inconsistent column names
    with pytest.raises(NotEqualColumnNamesError,
                       match='Column names are not the same for column '):
        # pylint: disable=no-value-for-parameter
        ImportDataModule.run(
            source=ReaderDataSourceOrSink.AzureBlobStorage,
            auth_type=ReaderAuthenticationType.Account,
            account_name=unittest_account_name,
            account_key=unittest_account_key,
            account_blob_path="/inconsistent-arff/diff-name/*.arff",
            account_blob_format=BlobDataFormat.ARFF)

    # Test inconsistent column types
    with pytest.raises(NotCompatibleColumnTypesError,
                       match='Column element types are not compatible for column '):
        # pylint: disable=no-value-for-parameter
        ImportDataModule.run(
            source=ReaderDataSourceOrSink.AzureBlobStorage,
            auth_type=ReaderAuthenticationType.Account,
            account_name=unittest_account_name,
            account_key=unittest_account_key,
            account_blob_path="/inconsistent-arff/diff-type/*.arff",
            account_blob_format=BlobDataFormat.ARFF)
