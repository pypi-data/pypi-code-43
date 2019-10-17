import os
import re
import tempfile

import pandas as pd
from azure.common import AzureException, AzureHttpError
from azure.storage.blob import BlockBlobService

from azureml.studio.modulehost.attributes import ItemInfo, ReleaseState
from azureml.studio.common.datatable.data_table import DataTable
from azureml.studio.common.error import ErrorMapping, InvalidUriError, IncorrectAzureStorageOrContainerError, \
    IncorrectAzureBlobNameError, CouldNotOpenFileError, IncorrectAzureStorageOrKeyError, IncorrectAzureContainerError, \
    ColumnCountNotEqualError, NotEqualColumnNamesError, NotCompatibleColumnTypesError
from azureml.studio.core.logger import module_logger, time_profile, TimeProfile
from azureml.studio.common.types import AutoEnum
from azureml.studio.core.utils.strutils import generate_random_string
from azureml.studio.modules.dataio.common.azure_blob_utils import AzureBlobUri, BLOB_CONNECT_TIMEOUT_SEC
from azureml.studio.common.io.datatable.data_table_arff_reader import DataTableArffReader
from azureml.studio.common.io.datatable.data_table_csv_io import DataTableCsvReader, DataTableCsvSep


class ReaderAuthenticationType(AutoEnum):
    PublicOrSAS: ItemInfo(name="PublicOrSAS", friendly_name="Public or SAS") = ()
    Account: ItemInfo(name="Account", friendly_name="Storage Account") = ()


class BlobDataFormat(AutoEnum):
    ARFF: ItemInfo(name="ARFF", friendly_name="ARFF") = ()
    CSV: ItemInfo(name="CSV", friendly_name="CSV") = ()
    TSV: ItemInfo(name="TSV", friendly_name="TSV") = ()
    DelimitedText: ItemInfo(name="DelimitedText",
                            friendly_name="CSV with encoding",
                            release_state=ReleaseState.Alpha
                            ) = ()
    Excel: ItemInfo(name="Excel",
                    friendly_name="Excel",
                    release_state=ReleaseState.Alpha) = ()


class DelimitedTextDelimiterType(AutoEnum):
    Comma: ItemInfo(name="Comma", friendly_name="Comma") = ()
    Tab: ItemInfo(name="Tab", friendly_name="Tab") = ()
    Semicolon: ItemInfo(name="Semicolon", friendly_name="Semicolon") = ()


class DelimitedTextEncodingType(AutoEnum):
    utf_8: ItemInfo(name="utf_8", friendly_name="Unicode(UTF-8)") = ()
    utf_16: ItemInfo(name="utf_16", friendly_name="Unicode") = ()
    big5: ItemInfo(name="big5", friendly_name="Chinese Traditional (Big5)") = ()
    gb2312: ItemInfo(name="gb2312", friendly_name="Chinese Simplified (GB2312)") = ()
    Windows_1252: ItemInfo(name="Windows_1252", friendly_name="Western European (Windows)") = ()
    x_mac_korean: ItemInfo(name="x_mac_korean", friendly_name="Korean (Mac)") = ()
    x_mac_chinesesimp: ItemInfo(name="x_mac_chinesesimp", friendly_name="Chinese Simplified (Mac)") = ()
    utf_32: ItemInfo(name="utf_32", friendly_name="Unicode (UTF-32)") = ()
    us_ascii: ItemInfo(name="us_ascii", friendly_name="US-ASCII") = ()
    x_cp20936: ItemInfo(name="x_cp20936", friendly_name="Chinese Simplified (GB2312-80)") = ()
    iso_8859_1: ItemInfo(name="iso_8859_1", friendly_name="Western European (ISO)") = ()
    iso_8859_8: ItemInfo(name="iso_8859_8", friendly_name="Hebrew (ISO-Visual)") = ()
    iso_2022_jp: ItemInfo(name="iso_2022_jp", friendly_name="Japanese (JIS)") = ()
    iso_2022_kr: ItemInfo(name="iso_2022_kr", friendly_name="Korean (ISO)") = ()
    x_cp50227: ItemInfo(name="x_cp50227", friendly_name="Chinese Simplified (ISO-2022)") = ()
    GB18030: ItemInfo(name="GB18030", friendly_name="Chinese Simplified (GB18030)") = ()
    utf_7: ItemInfo(name="utf_7", friendly_name="Unicode (UTF-7)") = ()


class ExcelFormat(AutoEnum):
    Sheet: ItemInfo(name="Sheet", friendly_name="Excel sheet") = ()
    Table: ItemInfo(name="Table", friendly_name="Excel table") = ()


def read_blobs_via_public_sas(
        sas_blob_uri: str,
        sas_blob_format: BlobDataFormat,
        sas_blob_csv_has_header: bool):

    module_logger.info('Initialize AzureBlobUri')

    try:
        blob_uri = AzureBlobUri(sas_blob_uri)
    except ValueError as value_error:
        ErrorMapping.rethrow(value_error, InvalidUriError(sas_blob_uri))

    if not blob_uri.account_name:
        ErrorMapping.throw(InvalidUriError(sas_blob_uri))

    module_logger.info('Initialize BlockBlobService')
    try:
        if blob_uri.sas_token:
            block_blob_service = BlockBlobService(
                account_name=blob_uri.account_name,
                sas_token=blob_uri.sas_token)
        else:
            block_blob_service = BlockBlobService(account_name=blob_uri.account_name)

        return _read_blobs(
            block_blob_service=block_blob_service,
            blob_uri=blob_uri,
            blob_format=sas_blob_format,
            blob_csv_has_header=sas_blob_csv_has_header
        )

    except AzureException as azure_error:
        ErrorMapping.rethrow(azure_error,
                             IncorrectAzureStorageOrContainerError(blob_uri.account_name, blob_uri.container_name))


def read_blobs_via_account(
        account_name: str,
        account_key,
        account_blob_path: str,
        account_blob_format: BlobDataFormat,
        delimiter_type: DelimitedTextDelimiterType,
        delimited_text_encoding: DelimitedTextEncodingType,
        excel_format: ExcelFormat,
        excel_name: str,
        account_blob_csv_has_header: bool):

    module_logger.info('Initialize BlockBlobService')
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
                                     IncorrectAzureContainerError(blob_uri.container_name))

        return _read_blobs(
            block_blob_service=block_blob_service,
            blob_uri=blob_uri,
            blob_format=account_blob_format,
            blob_csv_has_header=account_blob_csv_has_header
        )

    except AzureException as azure_error:
        ErrorMapping.rethrow(azure_error,
                             IncorrectAzureStorageOrContainerError(account_name, blob_uri.container_name))


@time_profile
def _read_blobs(
    block_blob_service: BlockBlobService,
    blob_uri: AzureBlobUri,
    blob_format: BlobDataFormat,
    blob_csv_has_header: bool
):

    if blob_uri.blob_path:
        if _is_wildcard_path(blob_uri.blob_path):
            filtered_blobs = _get_all_blobs_with_wildcard_path(
                block_blob_service=block_blob_service,
                blob_uri=blob_uri,
            )

            if not filtered_blobs:
                ErrorMapping.throw(IncorrectAzureBlobNameError(blob_wildcard_path=blob_uri.blob_path))

            return _load_blobs(
                block_blob_service=block_blob_service,
                container_name=blob_uri.container_name,
                blob_list=filtered_blobs,
                blob_format=blob_format,
                blob_csv_has_header=blob_csv_has_header
            )
        else:
            try:
                blob_existed = block_blob_service.exists(
                    container_name=blob_uri.container_name,
                    blob_name=blob_uri.blob_path,
                    timeout=BLOB_CONNECT_TIMEOUT_SEC
                )
            except AzureHttpError as azure_http_error:
                if azure_http_error.status_code == 403:
                    ErrorMapping.rethrow(azure_http_error, IncorrectAzureStorageOrKeyError(blob_uri.account_name))
                else:
                    ErrorMapping.rethrow(azure_http_error, IncorrectAzureBlobNameError(blob_uri.blob_path))

            if not blob_existed:
                ErrorMapping.throw(IncorrectAzureBlobNameError(blob_uri.blob_path))

            return _load_blob(
                block_blob_service=block_blob_service,
                container_name=blob_uri.container_name,
                blob_path=blob_uri.blob_path,
                blob_format=blob_format,
                blob_csv_has_header=blob_csv_has_header
            )
    else:
        all_blobs = _list_blobs(
            block_blob_service=block_blob_service,
            container_name=blob_uri.container_name)

        if not all_blobs:
            ErrorMapping.throw(IncorrectAzureBlobNameError(container_name=blob_uri.container_name))

        return _load_blobs(
            block_blob_service=block_blob_service,
            container_name=blob_uri.container_name,
            blob_list=all_blobs,
            blob_format=blob_format,
            blob_csv_has_header=blob_csv_has_header
        )


@time_profile
def _load_blobs(
    block_blob_service: BlockBlobService,
    container_name,
    blob_list,
    blob_format: BlobDataFormat,
    blob_csv_has_header: bool
):

    with tempfile.TemporaryDirectory() as temp_dir_name:
        temp_file_list = list()
        for blob in blob_list:
            temp_file = generate_random_string()
            temp_file_path = os.path.join(temp_dir_name, temp_file)
            try:
                block_blob_service.get_blob_to_path(
                    container_name=container_name,
                    blob_name=blob.name,
                    file_path=temp_file_path,
                    timeout=BLOB_CONNECT_TIMEOUT_SEC)
            except AzureException as azure_error:
                ErrorMapping.rethrow(azure_error, CouldNotOpenFileError(blob.name, azure_error))
            temp_file_list.append(temp_file_path)

        dt_list = list()
        blob_names = [blob.name for blob in blob_list]
        if blob_format is BlobDataFormat.CSV or blob_format is BlobDataFormat.TSV:
            sep = DataTableCsvSep.CSV if blob_format is BlobDataFormat.CSV \
                else DataTableCsvSep.TSV
            dt_list = DataTableCsvReader.read_files(
                file_list=temp_file_list,
                sep=sep,
                has_header=blob_csv_has_header)
        elif blob_format is BlobDataFormat.ARFF:
            dt_list = DataTableArffReader.read_files(temp_file_list)

        return _concat_data(dt_list, blob_names)


@time_profile
def _load_blob(
    block_blob_service: BlockBlobService,
    container_name,
    blob_path,
    blob_format: BlobDataFormat,
    blob_csv_has_header: bool
):
    with tempfile.TemporaryDirectory() as temp_dir_name:
        temp_file = generate_random_string()
        temp_file_path = os.path.join(temp_dir_name, temp_file)

        try:
            block_blob_service.get_blob_to_path(
                container_name=container_name,
                blob_name=blob_path,
                file_path=temp_file_path,
                timeout=BLOB_CONNECT_TIMEOUT_SEC)
        except AzureException as azure_error:
            ErrorMapping.rethrow(azure_error, CouldNotOpenFileError(blob_path, azure_error))

        if blob_format is BlobDataFormat.CSV or blob_format is BlobDataFormat.TSV:
            sep = DataTableCsvSep.CSV if blob_format is BlobDataFormat.CSV \
                else DataTableCsvSep.TSV
            return DataTableCsvReader.read(filepath_or_buffer=temp_file_path,
                                           sep=sep,
                                           has_header=blob_csv_has_header)
        elif blob_format is BlobDataFormat.ARFF:
            return DataTableArffReader.read(temp_file_path)


def _is_wildcard_path(blob_path):
    return "*" in blob_path or "?" in blob_path


def _first_pos_of_wildcard_char(blob_path: str):
    a_pos = blob_path.find("*")
    q_pos = blob_path.find("?")
    if a_pos == -1:
        return q_pos
    elif q_pos == -1:
        return a_pos
    else:
        return min(a_pos, q_pos)


def _convert_wildcard_to_regex(blob_path):
    return f"^{re.escape(blob_path)}$".replace("\\*", ".*").replace("\\?", ".")


def _get_all_blobs_with_wildcard_path(block_blob_service: BlockBlobService, blob_uri: AzureBlobUri):
    wildcard_char_pos = _first_pos_of_wildcard_char(blob_uri.blob_path)
    prefix = blob_uri.blob_path[:wildcard_char_pos]

    pattern = re.compile(_convert_wildcard_to_regex(blob_uri.blob_path))
    all_blobs = _list_blobs(
        block_blob_service=block_blob_service,
        container_name=blob_uri.container_name,
        prefix=prefix)
    filtered_blobs = [blob for blob in all_blobs if pattern.match(blob.name)]
    return filtered_blobs


def _list_blobs(
        block_blob_service: BlockBlobService,
        container_name,
        prefix=None,
):
    blob_list = list()
    next_marker = None
    while True:
        blobs = block_blob_service.list_blobs(
            container_name=container_name,
            prefix=prefix,
            num_results=1000,
            marker=next_marker)
        next_marker = blobs.next_marker
        blob_list.extend(blobs)
        if not next_marker:
            break
    return blob_list


def _concat_data(dt_list, blob_names):
    if len(dt_list) != len(blob_names):
        raise ValueError(f"Inconsistent input list length. dt_list: {len(dt_list)} != blob_names: {len(blob_names)}")

    if not dt_list:
        return DataTable()

    if len(dt_list) == 1:
        return dt_list[0]

    first_dt = dt_list[0]
    for dt_idx in range(1, len(dt_list)):
        cur_dt = dt_list[dt_idx]
        if first_dt.number_of_columns != cur_dt.number_of_columns:
            ErrorMapping.throw(
                ColumnCountNotEqualError(filename_1=blob_names[0],
                                         filename_2=blob_names[dt_idx],
                                         column_count_1=first_dt.number_of_columns,
                                         column_count_2=cur_dt.number_of_columns))

        for i in range(first_dt.number_of_columns):
            if first_dt.column_names[i] != cur_dt.column_names[i]:
                ErrorMapping.throw(NotEqualColumnNamesError(col_index=i,
                                                            dataset1=blob_names[0],
                                                            dataset2=blob_names[dt_idx]))

            if first_dt.get_column_type(i) != cur_dt.get_column_type(i) or \
                    first_dt.get_element_type(i) != cur_dt.get_element_type(i):
                ErrorMapping.throw(NotCompatibleColumnTypesError(first_col_names=first_dt.get_column_name(i),
                                                                 first_dataset_names=blob_names[0],
                                                                 second_dataset_names=blob_names[dt_idx]))
    df_list = [dt.data_frame for dt in dt_list]
    with TimeProfile("Dataframe chunks concat"):
        df = pd.concat(df_list, ignore_index=True)

    with TimeProfile("DataTable Construction"):
        dt = DataTable(df=df, meta_data=first_dt.meta_data)

    return dt
