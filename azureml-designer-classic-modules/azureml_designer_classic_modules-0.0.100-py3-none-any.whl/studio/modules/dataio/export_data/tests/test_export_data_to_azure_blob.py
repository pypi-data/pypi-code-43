import base64

import pandas as pd
import pytest

from azureml.studio.common.credential import SecureString
from azureml.studio.common.datatable.data_table import DataTable
from azureml.studio.common.error import AlreadyExistsError
from azureml.studio.common.io.datatable.data_table_csv_io import DataTableCsvReader, DataTableCsvSep
from azureml.studio.modules.dataio.export_data.azure_blob_writer import AzureAuthType, BlobFileTypes, BlobFileWriteMode
from azureml.studio.modules.dataio.export_data.export_data import ExportDataModule, WriterDataSourceOrSink


@pytest.fixture
def input_data_table_1():
    return DataTable(
        pd.DataFrame(
            columns=["A", "B", "C"],
            data=[
                [0, 1, 2],
                [3, 4, 5],
                [6, 7, 8],
                [9, 10, 11]
            ]))


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


def test_write_csv_with_sas_token(input_data_table_1):
    sas_blob_uri = "https://amlstudiomodulev2test.blob.core.windows.net/unittest-export/input_csv_with_header.csv" \
                   "?sp=rcwd&st=2019-03-11T09:27:33Z&se=2099-03-11T17:27:33Z&spr=https" \
                   "&sv=2018-03-28&sig=SUvZAq3xeY9gKKYyVl2SKrmMCeCR6RFNrDurM5qdiwM%3D&sr=b"

    # pylint: disable=no-value-for-parameter
    ExportDataModule.run(
        dataset=input_data_table_1,
        destination=WriterDataSourceOrSink.AzureBlobStorage,
        azure_auth=AzureAuthType.SAS,
        sas_blob_uri=sas_blob_uri,
        sas_blob_format=BlobFileTypes.CSV,
        sas_blob_csv_has_header=True)

    dt = DataTableCsvReader.read(
        filepath_or_buffer=sas_blob_uri,
        sep=DataTableCsvSep.CSV,
        has_header=True
    )
    assert dt.number_of_rows == 4
    assert dt.column_names == ['A', 'B', 'C']


def test_write_csv_with_account(input_data_table_1, unittest_account_name, unittest_account_key):
    sas_blob_uri = "https://amlstudiomodulev2test.blob.core.windows.net/unittest-export/input_tsv_with_header.csv"

    # pylint: disable=no-value-for-parameter
    ExportDataModule.run(
        dataset=input_data_table_1,
        destination=WriterDataSourceOrSink.AzureBlobStorage,
        azure_auth=AzureAuthType.Account,
        account_name=unittest_account_name,
        account_key=unittest_account_key,
        account_blob_path="/unittest-export/input_tsv_with_header.csv",
        account_blob_format=BlobFileTypes.TSV,
        account_blob_csv_has_header=True,
        account_blob_write_mode=BlobFileWriteMode.Overwrite)

    dt = DataTableCsvReader.read(
        filepath_or_buffer=sas_blob_uri,
        sep=DataTableCsvSep.TSV,
        has_header=True
    )
    assert dt.number_of_rows == 4
    assert dt.column_names == ['A', 'B', 'C']


def test_write_csv_with_account_in_container(input_data_table_1, unittest_account_name, unittest_account_key):
    sas_blob_uri = "https://amlstudiomodulev2test.blob.core.windows.net/unittest-export/export.csv"

    # pylint: disable=no-value-for-parameter
    ExportDataModule.run(
        dataset=input_data_table_1,
        destination=WriterDataSourceOrSink.AzureBlobStorage,
        azure_auth=AzureAuthType.Account,
        account_name=unittest_account_name,
        account_key=unittest_account_key,
        account_blob_path="/unittest-export",
        account_blob_format=BlobFileTypes.CSV,
        account_blob_csv_has_header=True,
        account_blob_write_mode=BlobFileWriteMode.Overwrite)

    dt = DataTableCsvReader.read(
        filepath_or_buffer=sas_blob_uri,
        sep=DataTableCsvSep.CSV,
        has_header=True
    )
    assert dt.number_of_rows == 4
    assert dt.column_names == ['A', 'B', 'C']


def test_write_csv_with_account_with_error_mode(input_data_table_1, unittest_account_name, unittest_account_key):
    with pytest.raises(AlreadyExistsError):
        # pylint: disable=no-value-for-parameter
        ExportDataModule.run(
            dataset=input_data_table_1,
            destination=WriterDataSourceOrSink.AzureBlobStorage,
            azure_auth=AzureAuthType.Account,
            account_name=unittest_account_name,
            account_key=unittest_account_key,
            account_blob_path="/unittest-export/input_csv_with_header.csv",
            account_blob_format=BlobFileTypes.CSV,
            account_blob_csv_has_header=True,
            account_blob_write_mode=BlobFileWriteMode.Error)
