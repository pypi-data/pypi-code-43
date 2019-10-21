import base64
import pytest

from azureml.studio.common.credential import SecureString
from azureml.studio.common.error import ErrorDatabaseConnectionError, FailedToReadAzureSQLDatabaseError
from azureml.studio.modulehost.constants import ColumnTypeName, ElementTypeName
from azureml.studio.modules.dataio.import_data.azure_sql_reader import create_connection
from azureml.studio.modules.dataio.import_data.import_data import ImportDataModule, ReaderDataSourceOrSink


@pytest.fixture
def unittest_azure_sql():
    return AzureSQLInfo(
        database_server_name="amlstudiomodulev2test.database.windows.net",
        database_name="unittest",
        sql_account_name="azureml",
        account_password=SecureString(base64.b64decode("c15MWksjaDNhbjYmQXY=").decode("utf-8"))
    )


def test_load_sql(unittest_azure_sql):
    sql = "Select * From dbo.ProductCategory"
    # pylint: disable=no-value-for-parameter
    dt = ImportDataModule.run(
        source=ReaderDataSourceOrSink.SqlAzure,
        database_server_name=unittest_azure_sql.database_server_name,
        database_name=unittest_azure_sql.database_name,
        sql_account_name=unittest_azure_sql.sql_account_name,
        account_password=unittest_azure_sql.account_password,
        trust_server_certificate=True,
        sql_stream_reader=sql)[0]
    assert dt.number_of_rows == 4
    assert dt.number_of_columns == 7
    assert dt.get_column_type(0) == ColumnTypeName.NUMERIC
    assert dt.get_element_type(0) == ElementTypeName.INT
    assert dt.get_column_type(1) == ColumnTypeName.STRING
    assert dt.get_element_type(1) == ElementTypeName.STRING
    assert dt.get_column_type(2) == ColumnTypeName.STRING
    assert dt.get_element_type(2) == ElementTypeName.STRING
    assert dt.get_column_type(3) == ColumnTypeName.DATETIME
    assert dt.get_element_type(3) == ElementTypeName.DATETIME
    assert dt.get_column_type(4) == ColumnTypeName.BINARY
    assert dt.get_element_type(4) == ElementTypeName.BOOL
    assert dt.get_column_type(5) == ColumnTypeName.NUMERIC
    assert dt.get_element_type(5) == ElementTypeName.FLOAT
    assert dt.get_column_type(6) == ColumnTypeName.NUMERIC
    assert dt.get_element_type(6) == ElementTypeName.INT


@pytest.mark.skip(reason="Cannot support SQL due to dependency issue")
def test_connection_exception(unittest_azure_sql):
    with pytest.raises(ErrorDatabaseConnectionError):
        create_connection(
            database_server_name=unittest_azure_sql.database_server_name,
            database_name=unittest_azure_sql.database_name,
            sql_account_name=unittest_azure_sql.sql_account_name,
            account_password="Invalid password",
            trust_server_certificate=True,
            tries=3,
            delay=1,
            backoff=1
        )


def test_sql_query_exception_invalid_server_name(unittest_azure_sql):
    with pytest.raises(
            FailedToReadAzureSQLDatabaseError,
            match="Failed to read data from Azure SQL Database: The server was not found or was not accessible."):
        sql = "Select * From dbo.ProductCategory"
        # pylint: disable=no-value-for-parameter
        ImportDataModule.run(
            source=ReaderDataSourceOrSink.SqlAzure,
            database_server_name="wrong_server_name",
            database_name=unittest_azure_sql.database_name,
            sql_account_name=unittest_azure_sql.sql_account_name,
            account_password=unittest_azure_sql.account_password,
            trust_server_certificate=True,
            sql_stream_reader=sql)


def test_sql_query_exception_invalid_db_name(unittest_azure_sql):
    with pytest.raises(
            FailedToReadAzureSQLDatabaseError,
            match="Failed to read data from Azure SQL Database: Login failed."):
        sql = "Select * From dbo.ProductCategory"
        # pylint: disable=no-value-for-parameter
        ImportDataModule.run(
            source=ReaderDataSourceOrSink.SqlAzure,
            database_server_name=unittest_azure_sql.database_server_name,
            database_name="wrong_db_name",
            sql_account_name=unittest_azure_sql.sql_account_name,
            account_password=unittest_azure_sql.account_password,
            trust_server_certificate=True,
            sql_stream_reader=sql)


def test_sql_query_exception_invalid_account(unittest_azure_sql):
    with pytest.raises(
            FailedToReadAzureSQLDatabaseError,
            match="Failed to read data from Azure SQL Database: Login failed."):
        sql = "Select * From dbo.ProductCategory"
        # pylint: disable=no-value-for-parameter
        ImportDataModule.run(
            source=ReaderDataSourceOrSink.SqlAzure,
            database_server_name=unittest_azure_sql.database_server_name,
            database_name=unittest_azure_sql.database_name,
            sql_account_name="wrong_account_name",
            account_password=unittest_azure_sql.account_password,
            trust_server_certificate=True,
            sql_stream_reader=sql)


def test_sql_query_exception_invalid_password(unittest_azure_sql):
    with pytest.raises(
            FailedToReadAzureSQLDatabaseError,
            match="Failed to read data from Azure SQL Database: Login failed."):
        sql = "Select * From dbo.ProductCategory"
        # pylint: disable=no-value-for-parameter
        ImportDataModule.run(
            source=ReaderDataSourceOrSink.SqlAzure,
            database_server_name=unittest_azure_sql.database_server_name,
            database_name=unittest_azure_sql.database_name,
            sql_account_name=unittest_azure_sql.sql_account_name,
            account_password=SecureString("wrong_password"),
            trust_server_certificate=True,
            sql_stream_reader=sql)


def test_sql_query_exception_invalid_sql(unittest_azure_sql):
    with pytest.raises(
            FailedToReadAzureSQLDatabaseError,
            match="Failed to read data from Azure SQL Database: Could not execute provided query."):
        sql = "Invalid SQL Query!"
        # pylint: disable=no-value-for-parameter
        ImportDataModule.run(
            source=ReaderDataSourceOrSink.SqlAzure,
            database_server_name=unittest_azure_sql.database_server_name,
            database_name=unittest_azure_sql.database_name,
            sql_account_name=unittest_azure_sql.sql_account_name,
            account_password=unittest_azure_sql.account_password,
            trust_server_certificate=True,
            sql_stream_reader=sql)


class AzureSQLInfo:
    def __init__(self, database_server_name, database_name, sql_account_name, account_password):
        self.database_server_name = database_server_name
        self.database_name = database_name
        self.sql_account_name = sql_account_name
        self.account_password = account_password
