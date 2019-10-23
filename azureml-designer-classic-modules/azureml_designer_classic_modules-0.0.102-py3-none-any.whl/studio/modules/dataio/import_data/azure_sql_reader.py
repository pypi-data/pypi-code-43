import os

import pandas as pd
# import pyodbc

from azureml.studio.common.datatable.data_table import DataTable
from azureml.studio.common.error import ErrorMapping, InvalidSQLScriptError
from azureml.studio.core.logger import module_logger as logger, TimeProfile, time_profile

_AZURE_SQL_DRIVER = '{ODBC Driver 17 for SQL Server}'


def read_from_azure_sql(
        database_server_name: str,
        database_name: str,
        sql_account_name: str,
        account_password: str,
        trust_server_certificate: bool,
        sql_stream_reader: str,
):
    _check_msodbcsql_installed()

    # pylint: disable=assignment-from-no-return
    conn = create_connection(
        database_server_name=database_server_name,
        database_name=database_name,
        sql_account_name=sql_account_name,
        account_password=account_password,
        trust_server_certificate=trust_server_certificate
    )

    df_list = list()
    # 50000 is recommended by pandas doc and also really good in common cases
    # http://pandas.pydata.org/pandas-docs/stable/user_guide/io.html#performance
    chunk_size = 50000

    with TimeProfile(f"Dataframe read Azure SQL in chunks with chunk size:{chunk_size}"):
        try:
            for df in pd.read_sql(sql=sql_stream_reader,
                                  con=conn,
                                  chunksize=chunk_size
                                  ):
                df_list.append(df)
        except BaseException as e:
            ErrorMapping.rethrow(e=e, err=InvalidSQLScriptError(sql_stream_reader, e))

    with TimeProfile("Dataframe chunks concat"):
        df = pd.concat(df_list, ignore_index=True)

    with TimeProfile("DataTable Construction"):
        dt = DataTable(df=df)

    return dt


@time_profile
def _check_msodbcsql_installed():
    import distro
    # This installation is a work around for AML Service only.
    linux_distro = distro.linux_distribution()
    if linux_distro[0] == 'Ubuntu':
        import subprocess
        result = subprocess.run("dpkg -l msodbcsql17", stderr=subprocess.PIPE, shell=True)
        output = result.stderr.decode('utf-8')
        if "no packages found" in output:
            if linux_distro == ('Ubuntu', '16.04', 'xenial'):
                os.system(f"apt-get update")
                os.system(f"apt-get install curl -y")
                os.system(f"apt-get install -y apt-transport-https")
                os.system(f"curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -")
                os.system(f"curl https://packages.microsoft.com/config/ubuntu/16.04/prod.list"
                          f" | tee /etc/apt/sources.list.d/mssql-release.list")
                os.system(f"apt-get update")
                os.system(f"ACCEPT_EULA=Y apt-get install msodbcsql17 -y")
                os.system(f"dpkg -l msodbcsql17")
            else:
                raise NotImplementedError(f"Not support Linux version: {linux_distro} yet.")
        else:
            logger.info(f"Found package msodbcsql17")


def create_connection(
        database_server_name: str,
        database_name: str,
        sql_account_name: str,
        account_password: str,
        trust_server_certificate: bool,
        tries=10,
        delay=5,
        backoff=1
):
    pass
    # trust_server_cert_str = 'YES' if trust_server_certificate else 'NO'
    #
    # conn_str = f'DRIVER={_AZURE_SQL_DRIVER};SERVER={database_server_name};PORT=1433;DATABASE={database_name};' \
    #    f'UID={sql_account_name};PWD={account_password};TrustServerCertificate={trust_server_cert_str}'
    #
    # @retry(pyodbc.Error, tries=tries, delay=delay, backoff=backoff)
    # def connect(odbc_conn_str):
    #     return pyodbc.connect(odbc_conn_str)
    #
    # try:
    #     conn = connect(conn_str)
    #     return conn
    # except pyodbc.Error as e:
    #     conn_str_for_logging = f'DRIVER={_AZURE_SQL_DRIVER};SERVER={database_server_name};' \
    #         f'PORT=1433;DATABASE={database_name};UID={sql_account_name};TrustServerCertificate={trust_server_cert_str}'
    #     ErrorMapping.rethrow(e=e, err=ErrorDatabaseConnectionError(conn_str_for_logging))
