from azureml.dataprep.api.dataflow import Dataflow
from azureml.dataprep.api.datasources import MSSQLDataSource
from azureml.dataprep.api.engineapi.api import get_engine_api
from azureml.dataprep.api.secretmanager import register_secret

from azureml.studio.common.datatable.data_table import DataTable
from azureml.studio.common.error import ErrorMapping, FailedToReadAzureSQLDatabaseError
from azureml.studio.core.logger import module_logger as logger, TimeProfile


def read_from_azure_sql_with_data_flow(
        database_server_name: str,
        database_name: str,
        sql_account_name: str,
        account_password: str,
        sql_statement: str,
        trust_server_certificate: bool = True,
):
    try:
        secret = register_secret(value=account_password, id='password')

        logger.info(f'Reading from Azure SQL Database: {database_server_name}:{database_name}')
        data_source = MSSQLDataSource(
            server_name=database_server_name,
            database_name=database_name,
            user_name=sql_account_name,
            password=secret,
            trust_server=trust_server_certificate,
        )

        data_flow = Dataflow(engine_api=get_engine_api())
        data_flow = data_flow.read_sql(data_source, sql_statement)

        with TimeProfile(f"Read Azure SQL Database"):
            # Must specify extended_types=True, otherwise will use 'Apache Feather' internally,
            # which is currently not well supported by Dataflow, resulting to execution error.
            # Feather: A format to store data frames. https://github.com/wesm/feather
            df = data_flow.to_pandas_dataframe(extended_types=True)
            return DataTable(df=df)
    except BaseException as e:
        ErrorMapping.rethrow(
            e=e,
            err=FailedToReadAzureSQLDatabaseError(
                database_server_name=database_server_name,
                database_name=database_name,
                sql_statement=sql_statement,
                detailed_message=str(e),
            ),
        )
