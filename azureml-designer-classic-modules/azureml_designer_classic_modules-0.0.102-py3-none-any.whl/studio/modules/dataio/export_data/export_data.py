from azureml.studio.modulehost.attributes import ItemInfo, ReleaseState, ModuleMeta, DataTableInputPort, \
    ModeParameter, StringParameter, CredentialParameter, BooleanParameter, ColumnPickerParameter, \
    DefaultColumnCategory, SelectedColumnCategory, IntParameter
from azureml.studio.common.credential import SecureString
from azureml.studio.common.datatable.data_table import DataTableColumnSelection
from azureml.studio.common.datatable.data_table import DataTable
from azureml.studio.common.types import AutoEnum
from azureml.studio.modulehost.module_reflector import module_entry, BaseModule
from azureml.studio.modules.dataio.export_data.azure_blob_writer import AzureAuthType, BlobFileWriteMode, \
    BlobFileTypes, write_to_blob_via_public_sas, write_to_blob_via_account


class WriterDataSourceOrSink(AutoEnum):
    HiveQuery: ItemInfo(name="HiveQuery",
                        friendly_name="Hive Query",
                        release_state=ReleaseState.Alpha) = ()
    SqlAzure: ItemInfo(name="SqlAzure",
                       friendly_name="Azure SQL Database",
                       release_state=ReleaseState.Alpha) = ()
    AzureTable: ItemInfo(name="AzureTable",
                         friendly_name="Azure Table",
                         release_state=ReleaseState.Alpha) = ()
    AzureBlobStorage: ItemInfo(name="AzureBlobStorage", friendly_name="Azure Blob Storage") = ()


class TableWriteMode(AutoEnum):
    Insert = ()
    Merge = ()
    Replace = ()
    InsertOrReplace = ()
    InsertOrMerge = ()


class HiveDataLocation(AutoEnum):
    HDFS = ()
    Azure = ()


class ExportDataModule(BaseModule):

    @staticmethod
    @module_entry(ModuleMeta(
        name="Export Data",
        description="Writes a dataset to Azure blob storage",
        category="Data Input and Output",
        version="2.0",
        owner="Microsoft Corporation",
        family_id="7A391181-B6A7-4AD4-B82D-E419C0D6522C",
        release_state=ReleaseState.Alpha,
        is_deterministic=False,
    ))
    def run(
            dataset: DataTableInputPort(
                name="Dataset",
                friendly_name="Dataset",
                description="The dataset to be written.",
            ),
            destination: ModeParameter(
                WriterDataSourceOrSink,
                name="Please Specify Data Destination",
                friendly_name="Please specify data destination",
                description="Data destination can be HTTP, FTP, anonymous HTTPS or FTPS,"
                            " a file in blob storage, and so on.",
                default_value=WriterDataSourceOrSink.AzureBlobStorage,
            ),
            azure_auth: ModeParameter(
                AzureAuthType,
                name="Please Specify Authentication Type",
                friendly_name="Please specify authentication type",
                description="Indicates SAS or account credentials for authorization.",
                default_value=AzureAuthType.Account,
                parent_parameter="Please Specify Data Destination",
                parent_parameter_val=(WriterDataSourceOrSink.AzureBlobStorage, ),
            ),
            sas_blob_uri: StringParameter(
                name="SAS URI for blob",
                friendly_name="SAS URI for blob",
                description="The SAS URI of the blob to be written to.",
                parent_parameter="Please Specify Authentication Type",
                parent_parameter_val=(AzureAuthType.SAS,),
            ),
            account_name: StringParameter(
                name="Azure Account Name",
                friendly_name="Azure account name",
                description="Name of the Windows Azure Storage account.",
                parent_parameter="Please Specify Authentication Type",
                parent_parameter_val=(AzureAuthType.Account,),
            ),
            account_key: CredentialParameter(
                name="Azure Account Key",
                friendly_name="Azure account key",
                description="Key associated with the Windows Azure Storage account.",
                parent_parameter="Please Specify Authentication Type",
                parent_parameter_val=(AzureAuthType.Account,),
                credential_descriptor="AzureStorageCredential,Azure Account Name",
            ),
            account_blob_path: StringParameter(
                name="Path to blob beginning with container",
                friendly_name="Path to blob beginning with container",
                description="Path to file in blob storage beginning with container name.",
                parent_parameter="Please Specify Authentication Type",
                parent_parameter_val=(AzureAuthType.Account,),
            ),
            account_blob_write_mode: ModeParameter(
                BlobFileWriteMode,
                name="Azure blob storage write mode",
                friendly_name="Azure blob storage write mode",
                description="Choose the method of writing blob files.",
                default_value=BlobFileWriteMode.Error,
                parent_parameter="Please Specify Authentication Type",
                parent_parameter_val=(AzureAuthType.Account,),
            ),
            sas_blob_format: ModeParameter(
                BlobFileTypes,
                name="File format for SAS file",
                friendly_name="File format for SAS file",
                description="Indicates whether file is CSV, TSV, or ARFF.",
                default_value=BlobFileTypes.CSV,
                parent_parameter="Please Specify Authentication Type",
                parent_parameter_val=(AzureAuthType.SAS,),
            ),
            sas_blob_csv_has_header: BooleanParameter(
                name="Write SAS header row",
                friendly_name="Write SAS header row",
                description="Indicates whether file should have header row.",
                default_value=False,
                parent_parameter="File format for SAS file",
                parent_parameter_val=(BlobFileTypes.CSV, BlobFileTypes.TSV),
            ),
            account_blob_format: ModeParameter(
                BlobFileTypes,
                name="File format for blob file",
                friendly_name="File format for blob file",
                description="Indicates whether blob file is CSV, TSV, or ARFF.",
                default_value=BlobFileTypes.CSV,
                parent_parameter="Please Specify Authentication Type",
                parent_parameter_val=(AzureAuthType.Account,),
            ),
            account_blob_csv_has_header: BooleanParameter(
                name="Write blob header row",
                friendly_name="Write blob header row",
                description="Indicates whether blob file should have header row.",
                default_value=False,
                parent_parameter="File format for blob file",
                parent_parameter_val=(BlobFileTypes.CSV, BlobFileTypes.TSV),
            ),
            table_auth_type: ModeParameter(
                AzureAuthType,
                name="Please Specify Table Authentication Type",
                friendly_name="Please specify table authentication type",
                description="SAS or user credentials for table.",
                default_value=AzureAuthType.Account,
                parent_parameter="Please Specify Data Destination",
                parent_parameter_val=(WriterDataSourceOrSink.AzureTable, ),
            ),
            table_sas: StringParameter(
                name="Table SAS URI",
                friendly_name="Table SAS URI",
                description="SAS URI for table in Windows Azure Storage.",
                parent_parameter="Please Specify Table Authentication Type",
                parent_parameter_val=(AzureAuthType.SAS,),
            ),
            table_account_name: StringParameter(
                name="Table Account Name",
                friendly_name="Table account name",
                description="User name for Windows Azure Storage.",
                parent_parameter="Please Specify Table Authentication Type",
                parent_parameter_val=(AzureAuthType.Account,),
            ),
            table_account_key: CredentialParameter(
                name="Table Account Key",
                friendly_name="Table account key",
                description="Password for Windows Azure Storage.",
                parent_parameter="Please Specify Table Authentication Type",
                parent_parameter_val=(AzureAuthType.Account,),
                credential_descriptor="AzureStorageCredential,Table Account Name",
            ),
            table_names: StringParameter(
                name="Table name",
                friendly_name="Table name",
                description="Name of table in Windows Azure Storage.",
                parent_parameter="Please Specify Table Authentication Type",
                parent_parameter_val=(AzureAuthType.Account,),
            ),
            partition_key: ColumnPickerParameter(
                name="Partition Key",
                friendly_name="Partition key",
                description="Column that specified the partition key. If the column does not exist,"
                            " it uses the column name as the partition key for all entries.",
                default_value=DefaultColumnCategory.NONE,
                parent_parameter="Please Specify Data Destination",
                parent_parameter_val=(WriterDataSourceOrSink.AzureTable, ),
                column_picker_for="Dataset",
                single_column_selection=True,
                column_selection_categories=(SelectedColumnCategory.All, ),
            ),
            row_key: ColumnPickerParameter(
                name="Azure Table Row Key",
                friendly_name="Azure table row key",
                description="Column that specified the row key. Defaults to a GUID based row key.",
                default_value=DefaultColumnCategory.NONE,
                parent_parameter="Please Specify Data Destination",
                parent_parameter_val=(WriterDataSourceOrSink.AzureTable, ),
                column_picker_for="Dataset",
                single_column_selection=True,
                column_selection_categories=(SelectedColumnCategory.All, ),
            ),
            azure_table_origin_columns: ColumnPickerParameter(
                name="Azure Table Origin Columns",
                friendly_name="Azure table origin columns",
                description="Selected columns.",
                default_value=DefaultColumnCategory.All,
                parent_parameter="Please Specify Data Destination",
                parent_parameter_val=(WriterDataSourceOrSink.AzureTable, ),
                column_picker_for="Dataset",
                single_column_selection=False,
                column_selection_categories=(SelectedColumnCategory.All, ),
            ),
            azure_table_destination_columns: StringParameter(
                name="Azure Table Destination Columns",
                friendly_name="Azure table destination columns",
                description="Names of columns that are to be saved. * can be used "
                            "if Azure Table Origin Columns is also *.",
                parent_parameter="Please Specify Data Destination",
                parent_parameter_val=(WriterDataSourceOrSink.AzureTable, ),
            ),
            azure_table_write_mode: ModeParameter(
                TableWriteMode,
                name="Azure Table Write Mode",
                friendly_name="Azure table write mode",
                description="Decides behaviour on existing entry.",
                default_value=TableWriteMode.InsertOrReplace,
                parent_parameter="Please Specify Data Destination",
                parent_parameter_val=(WriterDataSourceOrSink.AzureTable, ),
            ),
            hive_table_name: StringParameter(
                name="Hive table name",
                friendly_name="Hive table name",
                description="Name of table in Hive.",
                parent_parameter="Please Specify Data Destination",
                parent_parameter_val=(WriterDataSourceOrSink.HiveQuery, ),
            ),
            h_cat_uri: StringParameter(
                name="HCatalog Server Uri",
                friendly_name="HCatalog server URI",
                description="Templeton endpoint.",
                parent_parameter="Please Specify Data Destination",
                parent_parameter_val=(WriterDataSourceOrSink.HiveQuery, ),
            ),
            hadoop_username: StringParameter(
                name="Hadoop User Account Name",
                friendly_name="Hadoop user account name",
                description="Hadoop HDFS/HDInsight username.",
                parent_parameter="Please Specify Data Destination",
                parent_parameter_val=(WriterDataSourceOrSink.HiveQuery, ),
            ),
            hadoop_password: CredentialParameter(
                name="Hadoop User Account Password",
                friendly_name="Hadoop user account password",
                description="Hadoop HDFS/HDInsight password.",
                parent_parameter="Please Specify Data Destination",
                parent_parameter_val=(WriterDataSourceOrSink.HiveQuery, ),
                credential_descriptor="AzureStorageCredential,Hadoop User Account Name",
            ),
            data_location: ModeParameter(
                HiveDataLocation,
                name="Location Of Output Data",
                friendly_name="Location of output data",
                description="Specify HDFS or Azure for outputDir",
                default_value=HiveDataLocation.HDFS,
                parent_parameter="Please Specify Data Destination",
                parent_parameter_val=(WriterDataSourceOrSink.HiveQuery, ),
            ),
            hdfs_uri: StringParameter(
                name="HDFS Server Uri",
                friendly_name="HDFS server URI",
                description="HDFS rest endpoint.",
                parent_parameter="Location Of Output Data",
                parent_parameter_val=(HiveDataLocation.HDFS,),
            ),
            hive_azure_account_name: StringParameter(
                name="Azure User Account Name",
                friendly_name="Azure storage account name",
                description="Azure user account name.",
                parent_parameter="Location Of Output Data",
                parent_parameter_val=(HiveDataLocation.Azure,),
            ),
            hive_azure_storage_key: CredentialParameter(
                name="Azure Storage Key",
                friendly_name="Azure storage key",
                description="Azure storage key.",
                parent_parameter="Location Of Output Data",
                parent_parameter_val=(HiveDataLocation.Azure,),
                credential_descriptor="AzureStorageCredential,Azure User Account Name",
            ),
            hive_container_name: StringParameter(
                name="Azure Container Name",
                friendly_name="Azure container name",
                description="Azure container name.",
                parent_parameter="Location Of Output Data",
                parent_parameter_val=(HiveDataLocation.Azure,),
            ),
            database_server_name: StringParameter(
                name="Database Server Name",
                friendly_name="Database server name",
                description="SQL database server.",
                parent_parameter="Please Specify Data Destination",
                parent_parameter_val=(WriterDataSourceOrSink.SqlAzure, ),
            ),
            database_name: StringParameter(
                name="Database Name",
                friendly_name="Database name",
                description="SQL database instance.",
                parent_parameter="Please Specify Data Destination",
                parent_parameter_val=(WriterDataSourceOrSink.SqlAzure, ),
            ),
            server_user_account: StringParameter(
                name="Server User Account Name",
                friendly_name="Server user account name",
                description="SQL account name.",
                parent_parameter="Please Specify Data Destination",
                parent_parameter_val=(WriterDataSourceOrSink.SqlAzure, ),
            ),
            server_user_password: CredentialParameter(
                name="Server User Account Password",
                friendly_name="Server user account password",
                description="SQL account password.",
                parent_parameter="Please Specify Data Destination",
                parent_parameter_val=(WriterDataSourceOrSink.SqlAzure, ),
                credential_descriptor="SqlAzureCredential,Database Server Name,Server User Account Name",
            ),
            trust_server_certificate: BooleanParameter(
                name="Trust Server Certificate",
                friendly_name="Accept any server certificate (insecure)",
                description="Setting for TrustServerCertificate in connection string, insecure if checked",
                default_value=False,
                parent_parameter="Please Specify Data Destination",
                parent_parameter_val=(WriterDataSourceOrSink.SqlAzure, ),
            ),
            origin_columns: StringParameter(
                name="Comma separated list of columns to be saved",
                friendly_name="Comma separated list of columns to be saved",
                description="Comma separated list of the columns in the dataset "
                            "that will be saved to the SQL datatable.",
                parent_parameter="Please Specify Data Destination",
                parent_parameter_val=(WriterDataSourceOrSink.SqlAzure, ),
            ),
            destination_table: StringParameter(
                name="Data Table Name",
                friendly_name="Data table name",
                description="Data table where the dataset will be written. The table must already exist.",
                parent_parameter="Please Specify Data Destination",
                parent_parameter_val=(WriterDataSourceOrSink.SqlAzure, ),
            ),
            destination_columns: StringParameter(
                name="Comma separated list of datatable columns",
                friendly_name="Comma separated list of datatable columns",
                description="List of columns in the datatable that must provide a one-to-one mapping "
                            "to the dataset column list.",
                parent_parameter="Please Specify Data Destination",
                parent_parameter_val=(WriterDataSourceOrSink.SqlAzure, ),
            ),
            sql_azure_write_rows_n: IntParameter(
                name="SQL Azure Number Of Rows To Write",
                friendly_name="Number of rows written per SQL Azure operation",
                description="Number of rows which would be written to the table per operation.",
                default_value=50,
                parent_parameter="Please Specify Data Destination",
                parent_parameter_val=(WriterDataSourceOrSink.SqlAzure, ),
                min_value=1,
                max_value=200,
            ),
            treat_errors_as_warnings: BooleanParameter(
                name="Treat Errors as Warnings",
                friendly_name="Allow writer success with sporadic failures, note warnings in log file",
                description="If a small number of write failures occur, allow the writer to show success. "
                            "Failed lines will be noted in log file. "
                            "Note: Rollbacks in case of failures are not currently supported.",
                default_value=False,
                parent_parameter="Please Specify Data Destination",
                parent_parameter_val=(WriterDataSourceOrSink.SqlAzure, ),
            )
    ) -> (
    ):
        input_values = locals()
        return ExportDataModule._run_impl(**input_values),

    @classmethod
    def _run_impl(
            cls,
            dataset: DataTable,
            destination: WriterDataSourceOrSink,
            azure_auth: AzureAuthType,
            sas_blob_uri: str,
            account_name: str,
            account_key: SecureString,
            account_blob_path: str,
            account_blob_write_mode: BlobFileWriteMode,
            sas_blob_format: BlobFileTypes,
            sas_blob_csv_has_header: bool,
            account_blob_format: BlobFileTypes,
            account_blob_csv_has_header: bool,
            table_auth_type: AzureAuthType,
            table_sas: str,
            table_account_name: str,
            table_account_key: SecureString,
            table_names: str,
            partition_key: DataTableColumnSelection,
            row_key: DataTableColumnSelection,
            azure_table_origin_columns: DataTableColumnSelection,
            azure_table_destination_columns: str,
            azure_table_write_mode: TableWriteMode,
            hive_table_name: str,
            h_cat_uri: str,
            hadoop_username: str,
            hadoop_password: SecureString,
            data_location: HiveDataLocation,
            hdfs_uri: str,
            hive_azure_account_name: str,
            hive_azure_storage_key: SecureString,
            hive_container_name: str,
            database_server_name: str,
            database_name: str,
            server_user_account: str,
            server_user_password: SecureString,
            trust_server_certificate: bool,
            origin_columns: str,
            destination_table: str,
            destination_columns: str,
            sql_azure_write_rows_n: int,
            treat_errors_as_warnings: bool
    ):
        destination_friendly_name = cls._args.destination.friendly_name
        if destination == WriterDataSourceOrSink.SqlAzure:
            raise NotImplementedError(f"Unsupported input '{destination}' for parameter '{destination_friendly_name}'")
        elif destination == WriterDataSourceOrSink.AzureBlobStorage:
            if azure_auth == AzureAuthType.SAS:
                write_to_blob_via_public_sas(
                    dt=dataset,
                    sas_blob_uri=sas_blob_uri,
                    sas_blob_format=sas_blob_format,
                    sas_blob_csv_has_header=sas_blob_csv_has_header
                )
            elif azure_auth == AzureAuthType.Account:
                write_to_blob_via_account(
                    dt=dataset,
                    account_name=account_name,
                    account_key=account_key.value,
                    account_blob_path=account_blob_path,
                    account_blob_format=account_blob_format,
                    account_blob_write_mode=account_blob_write_mode,
                    account_blob_csv_has_header=account_blob_csv_has_header
                )
            else:
                raise NotImplementedError(
                    f"Unsupported input '{azure_auth}' for parameter '{cls._args.azure_auth.friendly_name}'")
        elif destination == WriterDataSourceOrSink.HiveQuery:
            raise NotImplementedError(f"Unsupported input '{destination}' for parameter '{destination_friendly_name}'")
        elif destination == WriterDataSourceOrSink.AzureTable:
            raise NotImplementedError(f"Unsupported input '{destination}' for parameter '{destination_friendly_name}'")
        else:
            raise NotImplementedError(f"Unsupported input '{destination}' for parameter '{destination_friendly_name}'")
