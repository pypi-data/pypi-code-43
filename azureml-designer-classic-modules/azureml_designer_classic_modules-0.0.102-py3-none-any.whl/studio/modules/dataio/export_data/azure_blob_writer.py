import os
import tempfile

from azure.common import AzureException, AzureHttpError
from azure.storage.blob import BlockBlobService

from azureml.studio.modulehost.attributes import ItemInfo, ReleaseState
from azureml.studio.common.datatable.data_table import DataTable
from azureml.studio.common.datatypes import DataTypes
from azureml.studio.common.error import InvalidUriError, ErrorMapping, IncorrectAzureStorageOrContainerError, \
    IncorrectAzureStorageOrKeyError, AlreadyExistsError, UnableToUploadToAzureBlobError
from azureml.studio.common.types import AutoEnum
from azureml.studio.core.utils.strutils import generate_random_string
from azureml.studio.modules.dataio.common.azure_blob_utils import AzureBlobUri, BLOB_CONNECT_TIMEOUT_SEC
from azureml.studio.common.io.datatable.data_table_csv_io import DataTableCsvSep, DataTableCsvWriter


class AzureAuthType(AutoEnum):
    SAS = ()
    Account = ()


class BlobFileWriteMode(AutoEnum):
    Error: ItemInfo(name="Error", friendly_name="Error") = ()
    Overwrite: ItemInfo(name="Overwrite", friendly_name="Overwrite") = ()


class BlobFileTypes(AutoEnum):
    ARFF: ItemInfo(name="ARFF",
                   friendly_name="ARFF",
                   release_state=ReleaseState.Alpha) = ()
    CSV = ()
    TSV = ()

    def get_file_extension(self, has_header: bool):
        if self is self.ARFF:
            return DataTypes.ARFF.value.file_extension
        elif self is self.CSV:
            return DataTypes.GENERIC_CSV.value.file_extension if has_header \
                else DataTypes.GENERIC_CSV_NO_HEADER.value.file_extension
        elif self is self.TSV:
            return DataTypes.GENERIC_TSV.value.file_extension if has_header \
                else DataTypes.GENERIC_TSV_NO_HEADER.value.file_extension


def write_to_blob_via_public_sas(
        dt: DataTable,
        sas_blob_uri: str,
        sas_blob_format: BlobFileTypes,
        sas_blob_csv_has_header: bool):
    try:
        blob_uri = AzureBlobUri(sas_blob_uri)
    except ValueError as value_error:
        ErrorMapping.rethrow(value_error, InvalidUriError(sas_blob_uri))

    if not blob_uri.account_name:
        ErrorMapping.throw(InvalidUriError(sas_blob_uri))

    try:
        if blob_uri.sas_token:
            block_blob_service = BlockBlobService(
                account_name=blob_uri.account_name,
                sas_token=blob_uri.sas_token)
        else:
            block_blob_service = BlockBlobService(account_name=blob_uri.account_name)

        return _write_to_blob(
            dt=dt,
            block_blob_service=block_blob_service,
            blob_uri=blob_uri,
            blob_format=sas_blob_format,
            blob_csv_has_header=sas_blob_csv_has_header
        )
    except AzureException as azure_error:
        ErrorMapping.rethrow(azure_error,
                             IncorrectAzureStorageOrContainerError(blob_uri.account_name, blob_uri.container_name))


def write_to_blob_via_account(
        dt: DataTable,
        account_name: str,
        account_key,
        account_blob_path: str,
        account_blob_format: BlobFileTypes,
        account_blob_write_mode: BlobFileWriteMode,
        account_blob_csv_has_header: bool):
    try:
        block_blob_service = BlockBlobService(account_name=account_name, account_key=account_key)

        try:
            blob_uri = AzureBlobUri(account_blob_path)
        except ValueError as value_error:
            ErrorMapping.rethrow(value_error, InvalidUriError(account_blob_path))

        try:
            block_blob_service.get_container_properties(container_name=blob_uri.container_name)
        except AzureHttpError as azure_http_error:
            if azure_http_error.status_code == 403:
                ErrorMapping.rethrow(azure_http_error, IncorrectAzureStorageOrKeyError(account_name))
            else:
                ErrorMapping.rethrow(azure_http_error,
                                     IncorrectAzureStorageOrContainerError(account_name, blob_uri.container_name))

        return _write_to_blob(
            dt=dt,
            block_blob_service=block_blob_service,
            blob_uri=blob_uri,
            blob_format=account_blob_format,
            blob_csv_has_header=account_blob_csv_has_header,
            blob_write_mode=account_blob_write_mode
        )

    except AzureException as azure_error:
        ErrorMapping.rethrow(azure_error,
                             IncorrectAzureStorageOrContainerError(account_name, blob_uri.container_name))


def _write_to_blob(
        dt: DataTable,
        block_blob_service: BlockBlobService,
        blob_uri: AzureBlobUri,
        blob_format: BlobFileTypes,
        blob_csv_has_header: bool,
        blob_write_mode: BlobFileWriteMode = BlobFileWriteMode.Overwrite
):

    if not blob_uri.blob_path:
        blob_uri.blob_path = f"export.{BlobFileTypes.get_file_extension(blob_format, blob_csv_has_header)}"

    blob_existed = block_blob_service.exists(
        container_name=blob_uri.container_name,
        blob_name=blob_uri.blob_path,
        timeout=BLOB_CONNECT_TIMEOUT_SEC
    )

    if blob_existed and blob_write_mode == BlobFileWriteMode.Error:
        ErrorMapping.throw(AlreadyExistsError(blob_uri.blob_path))

    with tempfile.TemporaryDirectory() as temp_dir_name:
        temp_file = generate_random_string()
        temp_file_path = os.path.join(temp_dir_name, temp_file)

        if blob_format is BlobFileTypes.CSV or blob_format is BlobFileTypes.TSV:
            sep = DataTableCsvSep.CSV if blob_format is BlobFileTypes.CSV \
                else DataTableCsvSep.TSV
            DataTableCsvWriter.write(dt=dt,
                                     path_or_buf=temp_file_path,
                                     sep=sep,
                                     has_header=blob_csv_has_header)
        elif blob_format is BlobFileTypes.ARFF:
            raise NotImplementedError()

        try:
            block_blob_service.create_blob_from_path(
                container_name=blob_uri.container_name,
                blob_name=blob_uri.blob_path,
                file_path=temp_file_path,
                timeout=BLOB_CONNECT_TIMEOUT_SEC)
        except AzureException as azure_error:
            ErrorMapping.rethrow(azure_error, UnableToUploadToAzureBlobError(temp_file_path, blob_uri.blob_path))
