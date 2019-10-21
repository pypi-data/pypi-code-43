from azureml.studio.modulehost.attributes import ItemInfo, ModeParameter, StringParameter, BooleanParameter, \
    CredentialParameter, ScriptParameter, IntParameter, ReleaseState, DataTableOutputPort, ModuleMeta
from azureml.studio.common.credential import SecureString
from azureml.studio.common.types import AutoEnum
from azureml.studio.modulehost.module_reflector import module_entry, BaseModule
from azureml.studio.modules.dataio.import_data.azure_blob_reader import BlobDataFormat, \
    DelimitedTextDelimiterType, DelimitedTextEncodingType, ExcelFormat, read_blobs_via_public_sas, \
    read_blobs_via_account, ReaderAuthenticationType
from azureml.studio.modules.dataio.import_data.dataprep_sql_reader import read_from_azure_sql_with_data_flow
from azureml.studio.modules.dataio.import_data.web_reader import WebSourceDataFormat, read_csv, read_arff, read_svmlight


class ReaderDataSourceOrSink(AutoEnum):
    Http: ItemInfo(name="Http", friendly_name="Web URL via HTTP") = ()
    HiveQuery: ItemInfo(name="HiveQuery", friendly_name="Hive Query", release_state=ReleaseState.Alpha) = ()
    SqlAzure: ItemInfo(name="SqlAzure", friendly_name="Azure SQL Database") = ()
    AzureTable: ItemInfo(name="AzureTable",
                         friendly_name="Azure Table",
                         release_state=ReleaseState.Alpha) = ()
    AzureBlobStorage: ItemInfo(name="AzureBlobStorage", friendly_name="Azure Blob Storage") = ()
    PowerQuery: ItemInfo(name="PowerQuery",
                         friendly_name="Data Feed Provider",
                         release_state=ReleaseState.Alpha) = ()
    DocumentDB: ItemInfo(name="DocumentDB",
                         friendly_name="Azure Cosmos DB",
                         release_state=ReleaseState.Alpha) = ()


class PropertyScan(AutoEnum):
    TopN = ()
    ScanAll = ()


class DataLocation(AutoEnum):
    HDFS = ()
    Azure: ItemInfo(name="Azure", friendly_name="Azure Blob Storage (WASB)") = ()


class ReaderUrlContents(AutoEnum):
    OData: ItemInfo(name="OData", friendly_name="OData") = ()


class ImportDataModule(BaseModule):

    @staticmethod
    @module_entry(ModuleMeta(
        name="Import Data",
        description="Loads data from external sources on the web; from Azure blob storage",
        category="Data Input and Output",
        version="4.0",
        owner="Microsoft Corporation",
        family_id="4E1B0FE6-ADED-4B3F-A36F-39B8862B9004",
        release_state=ReleaseState.Alpha,
        is_deterministic=False,
    ))
    def run(
            source: ModeParameter(
                ReaderDataSourceOrSink,
                name="Please Specify Data Source",
                friendly_name="Data source",
                description="Data source can be HTTP, FTP, anonymous HTTPS or FTPS, a file in Azure BLOB storage,"
                            " an Azure table, an Azure SQL Database, a Hive table or an OData endpoint.",
                default_value=ReaderDataSourceOrSink.AzureBlobStorage,
            ),
            input_url: StringParameter(
                name="URL",
                friendly_name="Data source URL",
                description="URL for HTTP",
                parent_parameter="Please Specify Data Source",
                parent_parameter_val=(ReaderDataSourceOrSink.Http, ),
            ),
            data_format: ModeParameter(
                WebSourceDataFormat,
                name="Data format",
                friendly_name="Data format",
                description="File type for HTTP or Windows Azure blob",
                default_value=WebSourceDataFormat.CSV,
                parent_parameter="Please Specify Data Source",
                parent_parameter_val=(ReaderDataSourceOrSink.Http, ),
            ),
            csv_tsv_has_header: BooleanParameter(
                name="CSV or TSV has Header Row",
                friendly_name="CSV or TSV has header row",
                description="Indicates if CSV or TSV file has a header row",
                default_value=False,
                parent_parameter="Data format",
                parent_parameter_val=(WebSourceDataFormat.CSV, WebSourceDataFormat.TSV),
            ),
            database_server_name: StringParameter(
                name="Database Server Name",
                friendly_name="Database server name",
                description="SQL database server",
                parent_parameter="Please Specify Data Source",
                parent_parameter_val=(ReaderDataSourceOrSink.SqlAzure, ),
            ),
            database_name: StringParameter(
                name="Database Name",
                friendly_name="Database name",
                description="SQL database instance",
                parent_parameter="Please Specify Data Source",
                parent_parameter_val=(ReaderDataSourceOrSink.SqlAzure, ),
            ),
            sql_account_name: StringParameter(
                name="Server User Account Name",
                friendly_name="User name",
                description="SQL account name",
                parent_parameter="Please Specify Data Source",
                parent_parameter_val=(ReaderDataSourceOrSink.SqlAzure, ),
            ),
            account_password: CredentialParameter(
                name="Server User Account Password",
                friendly_name="Password",
                description="SQL account password",
                parent_parameter="Please Specify Data Source",
                parent_parameter_val=(ReaderDataSourceOrSink.SqlAzure, ),
                credential_descriptor="SqlAzureCredential,Database Server Name,Server User Account Name",
            ),
            trust_server_certificate: BooleanParameter(
                name="Trust Server Certificate",
                friendly_name="Accept any server certificate (insecure)",
                description="Setting for TrustServerCertificate in connection string, insecure if checked.",
                default_value=False,
                parent_parameter="Please Specify Data Source",
                parent_parameter_val=(ReaderDataSourceOrSink.SqlAzure, ),
            ),
            sql_stream_reader: ScriptParameter(
                name="Database Query",
                friendly_name="Database query",
                description="SQL query",
                parent_parameter="Please Specify Data Source",
                parent_parameter_val=(ReaderDataSourceOrSink.SqlAzure, ),
                script_name="script.sql",
            ),
            auth_type: ModeParameter(
                ReaderAuthenticationType,
                name="Please Specify Authentication Type",
                friendly_name="Authentication type",
                description="Public or SAS URI or user credentials",
                default_value=ReaderAuthenticationType.Account,
                parent_parameter="Please Specify Data Source",
                parent_parameter_val=(ReaderDataSourceOrSink.AzureBlobStorage, ),
            ),
            sas_blob_uri: StringParameter(
                name="URI",
                friendly_name="Blob URI",
                description="Uniform Resource Identifier with Shared Access Signature or Public Access",
                parent_parameter="Please Specify Authentication Type",
                parent_parameter_val=(ReaderAuthenticationType.PublicOrSAS, ),
            ),
            account_name: StringParameter(
                name="Account Name",
                friendly_name="Account name",
                description="Name of the Windows Azure Storage account",
                parent_parameter="Please Specify Authentication Type",
                parent_parameter_val=(ReaderAuthenticationType.Account, ),
            ),
            account_key: CredentialParameter(
                name="Account Key",
                friendly_name="Account key",
                description="Key associated with the Windows Azure Storage account",
                parent_parameter="Please Specify Authentication Type",
                parent_parameter_val=(ReaderAuthenticationType.Account, ),
                credential_descriptor="AzureStorageCredential,Account Name",
            ),
            account_blob_path: StringParameter(
                name="Path to container or directory or blob",
                friendly_name="Path to container, directory or blob",
                description="Path to blob or name of table",
                parent_parameter="Please Specify Authentication Type",
                parent_parameter_val=(ReaderAuthenticationType.Account, ),
            ),
            sas_blob_format: ModeParameter(
                BlobDataFormat,
                name="File format",
                friendly_name="File format",
                description="File format of blob storage data read using URI",
                default_value=BlobDataFormat.CSV,
                parent_parameter="Please Specify Authentication Type",
                parent_parameter_val=(ReaderAuthenticationType.PublicOrSAS, ),
            ),
            account_blob_format: ModeParameter(
                BlobDataFormat,
                name="Blob File format",
                friendly_name="Blob file format",
                description="File format of blob storage data",
                default_value=BlobDataFormat.CSV,
                parent_parameter="Please Specify Authentication Type",
                parent_parameter_val=(ReaderAuthenticationType.Account, ),
            ),
            delimiter_type: ModeParameter(
                DelimitedTextDelimiterType,
                name="Column delimiter",
                friendly_name="Column delimiter format",
                description="Column delimiter format",
                default_value=DelimitedTextDelimiterType.Comma,
                parent_parameter="Blob File format",
                parent_parameter_val=(BlobDataFormat.DelimitedText,),
            ),
            delimited_text_encoding: ModeParameter(
                DelimitedTextEncodingType,
                name="Encoding Format",
                friendly_name="Encoding format",
                description="Encoding format",
                default_value=DelimitedTextEncodingType.utf_8,
                parent_parameter="Blob File format",
                parent_parameter_val=(BlobDataFormat.DelimitedText,),
            ),
            excel_format: ModeParameter(
                ExcelFormat,
                name="Excel data format",
                friendly_name="Excel data format",
                description="Data format for excel",
                default_value=ExcelFormat.Sheet,
                parent_parameter="Blob File format",
                parent_parameter_val=(BlobDataFormat.Excel,),
            ),
            excel_name: StringParameter(
                name="Excel sheet or embedded table name",
                friendly_name="Excel sheet or embedded table name",
                description="Name of sheet or embedded table",
                parent_parameter="Excel data format",
                parent_parameter_val=(ExcelFormat.Table, ExcelFormat.Sheet),
            ),
            account_blob_csv_has_header: BooleanParameter(
                name="File has Header Row",
                friendly_name="File has header row",
                description="Whether CSV file read using account credentials has a header row",
                default_value=False,
                parent_parameter="Blob File format",
                parent_parameter_val=(BlobDataFormat.CSV,
                                      BlobDataFormat.TSV,
                                      BlobDataFormat.Excel,
                                      BlobDataFormat.DelimitedText),
            ),
            sas_blob_csv_has_header: BooleanParameter(
                name="URI file has Header Row",
                friendly_name="URI file has header row",
                description="Whether CSV file read using URI has a header row",
                default_value=False,
                parent_parameter="File format",
                parent_parameter_val=(BlobDataFormat.CSV, BlobDataFormat.TSV),
            ),
            table_auth_type: ModeParameter(
                ReaderAuthenticationType,
                name="Please Specify Table Authentication Type",
                friendly_name="Authentication type",
                description="URI or user credentials for table",
                default_value=ReaderAuthenticationType.Account,
                parent_parameter="Please Specify Data Source",
                parent_parameter_val=(ReaderDataSourceOrSink.AzureTable, ),
            ),
            table_sas: StringParameter(
                name="Table URI",
                friendly_name="Table URI",
                description="SAS or Public Access URI for table in Windows Azure Storage",
                parent_parameter="Please Specify Table Authentication Type",
                parent_parameter_val=(ReaderAuthenticationType.PublicOrSAS, ),
            ),
            table_account_name: StringParameter(
                name="Table Account Name",
                friendly_name="Account name",
                description="User name for Windows Azure Storage",
                parent_parameter="Please Specify Table Authentication Type",
                parent_parameter_val=(ReaderAuthenticationType.Account, ),
            ),
            table_account_key: CredentialParameter(
                name="Table Account Key",
                friendly_name="Account key",
                description="Password for Windows Azure Storage",
                parent_parameter="Please Specify Table Authentication Type",
                parent_parameter_val=(ReaderAuthenticationType.Account, ),
                credential_descriptor="AzureStorageCredential,Table Account Name",
            ),
            table_names: StringParameter(
                name="Table name",
                friendly_name="Table name",
                description="Name of table in Windows Azure Storage",
                parent_parameter="Please Specify Table Authentication Type",
                parent_parameter_val=(ReaderAuthenticationType.Account, ),
            ),
            scan_mode: ModeParameter(
                PropertyScan,
                name="Rows to scan for Property names",
                friendly_name="Rows to scan for property names",
                description="Choose whether to scan the properties of all entities or only the Top N entities "
                            "to determine columns of dataset. ScanAll should be selected only if it is likely "
                            "that a table property does not appear until near the bottom of the table",
                default_value=PropertyScan.TopN,
                parent_parameter="Please Specify Table Authentication Type",
                parent_parameter_val=(ReaderAuthenticationType.Account, ),
            ),
            rows_to_scan: IntParameter(
                name="Rows count for TopN",
                friendly_name="Rows count for TopN",
                description="Number of rows to scan to compile columns list; zero (\"0\") indicates all rows",
                default_value=10,
                parent_parameter="Rows to scan for Property names",
                parent_parameter_val=(PropertyScan.TopN, ),
                min_value=1,
            ),
            sas_scan_mode: ModeParameter(
                PropertyScan,
                name="Rows to scan for Property names via SAS",
                friendly_name="Rows to scan for property names via SAS",
                description="Choose whether to scan the properties of all entities or only the Top N entities "
                            "to determine columns of dataset via SAS. ScanAll should be selected only if it is likely"
                            " that a table property does not appear until near the bottom of the table",
                default_value=PropertyScan.TopN,
                parent_parameter="Please Specify Table Authentication Type",
                parent_parameter_val=(ReaderAuthenticationType.PublicOrSAS, ),
            ),
            sas_rows_to_scan: IntParameter(
                name="Rows count for TopN via SAS",
                friendly_name="Rows count for TopN via SAS",
                description="Number of rows to scan to compile columns list via SAS; zero (\"0\") indicates all rows",
                default_value=10,
                parent_parameter="Rows to scan for Property names via SAS",
                parent_parameter_val=(PropertyScan.TopN, ),
                min_value=1,
            ),
            hive_stream_reader: ScriptParameter(
                name="Hive Database Query",
                friendly_name="Hive database query",
                description="HQL query",
                parent_parameter="Please Specify Data Source",
                parent_parameter_val=(ReaderDataSourceOrSink.HiveQuery, ),
                script_name="script.hql",
            ),
            h_cat_uri: StringParameter(
                name="HCatalog Server Uri",
                friendly_name="HCatalog server URI",
                description="Templeton endpoint",
                default_value="(yourclustername).azurehdinsight.net",
                parent_parameter="Please Specify Data Source",
                parent_parameter_val=(ReaderDataSourceOrSink.HiveQuery, ),
            ),
            hadoop_username: StringParameter(
                name="Hadoop User Account Name",
                friendly_name="Hadoop user account name",
                description="Hadoop HDFS/HDInsight username",
                default_value="admin",
                parent_parameter="Please Specify Data Source",
                parent_parameter_val=(ReaderDataSourceOrSink.HiveQuery, ),
            ),
            hadoop_password: CredentialParameter(
                name="Hadoop User Account Password",
                friendly_name="Hadoop user account password",
                description="Hadoop HDFS/HDInsight password",
                parent_parameter="Please Specify Data Source",
                parent_parameter_val=(ReaderDataSourceOrSink.HiveQuery, ),
                credential_descriptor="AzureStorageCredential,Hadoop User Account Name",
            ),
            data_location: ModeParameter(
                DataLocation,
                name="Location Of Output Data",
                friendly_name="Location of output data",
                description="Specify HDFS or Azure for outputDir",
                default_value=DataLocation.Azure,
                parent_parameter="Please Specify Data Source",
                parent_parameter_val=(ReaderDataSourceOrSink.HiveQuery, ),
            ),
            hdfs_uri: StringParameter(
                name="HDFS Server Uri",
                friendly_name="HDFS server URI",
                description="HDFS rest endpoint",
                default_value="(yourclustername).azurehdinsight.net",
                parent_parameter="Location Of Output Data",
                parent_parameter_val=(DataLocation.HDFS, ),
            ),
            azure_account_name: StringParameter(
                name="Azure User Account Name",
                friendly_name="Storage account name",
                description="Azure storage account name",
                parent_parameter="Location Of Output Data",
                parent_parameter_val=(DataLocation.Azure, ),
            ),
            azure_storage_key: CredentialParameter(
                name="Azure Storage Key",
                friendly_name="Storage key",
                description="Azure storage key",
                parent_parameter="Location Of Output Data",
                parent_parameter_val=(DataLocation.Azure, ),
                credential_descriptor="AzureStorageCredential,Azure User Account Name",
            ),
            container_name: StringParameter(
                name="Azure Container Name",
                friendly_name="Container name",
                description="Azure container name",
                default_value="(yourclustername)",
                parent_parameter="Location Of Output Data",
                parent_parameter_val=(DataLocation.Azure, ),
            ),
            url_content: ModeParameter(
                ReaderUrlContents,
                name="Please Specify Data Content Type",
                friendly_name="Data content type",
                description="Data format type",
                default_value=ReaderUrlContents.OData,
                parent_parameter="Please Specify Data Source",
                parent_parameter_val=(ReaderDataSourceOrSink.PowerQuery, ),
            ),
            power_query_url: StringParameter(
                name="Source URL",
                friendly_name="Data Source URL",
                description="URL for Power Query data source",
                parent_parameter="Please Specify Data Source",
                parent_parameter_val=(ReaderDataSourceOrSink.PowerQuery, ),
            ),
            document_db_server: StringParameter(
                name="Azure DocumentDB Server",
                friendly_name="Endpoint URL",
                description="Azure Cosmos DB server name",
                parent_parameter="Please Specify Data Source",
                parent_parameter_val=(ReaderDataSourceOrSink.DocumentDB, ),
            ),
            document_db_database_name: StringParameter(
                name="Database ID",
                friendly_name="Database ID",
                description="Azure Cosmos DB database name",
                parent_parameter="Please Specify Data Source",
                parent_parameter_val=(ReaderDataSourceOrSink.DocumentDB, ),
            ),
            document_db_password: CredentialParameter(
                name="DocumentDB Key",
                friendly_name="Azure Cosmos DB Key",
                description="API key for Azure Cosmos DB instance",
                parent_parameter="Please Specify Data Source",
                parent_parameter_val=(ReaderDataSourceOrSink.DocumentDB, ),
                credential_descriptor="SqlAzureCredential,Azure DocumentDB Server,Database ID",
            ),
            document_db_collection: StringParameter(
                name="Collection ID",
                friendly_name="Collection ID",
                description="Azure Cosmos DB collection name",
                parent_parameter="Please Specify Data Source",
                parent_parameter_val=(ReaderDataSourceOrSink.DocumentDB, ),
            ),
            document_db_query: ScriptParameter(
                name="SQL Query",
                friendly_name="SQL query",
                description="SQL query for Azure Cosmos DB",
                parent_parameter="Please Specify Data Source",
                parent_parameter_val=(ReaderDataSourceOrSink.DocumentDB, ),
                script_name="docdb.sql",
            ),
            document_db_query_params: ScriptParameter(
                name="SQL Query parameters",
                friendly_name="SQL query parameters",
                description="SQL query parameters for Azure Cosmos DB",
                parent_parameter="Please Specify Data Source",
                parent_parameter_val=(ReaderDataSourceOrSink.DocumentDB, ),
                script_name="params.json",
            ),
            infer_schema: BooleanParameter(
                name="Allow Inconsistent Schema",
                friendly_name="Scan the entire collection for inferring dataset schema",
                description="Scan the entire collection for infering Azure Machine Learning dataset schema. "
                            "This operation may take longer depending on the number of documents to be scanned",
                default_value=False,
                parent_parameter="Please Specify Data Source",
                parent_parameter_val=(ReaderDataSourceOrSink.DocumentDB, ),
            )
    ) -> (
            DataTableOutputPort(
                name="Results dataset",
                friendly_name="Results dataset",
                description="Dataset with downloaded data",
            ),
    ):
        """

        :rtype: object
        """
        input_values = locals()
        return ImportDataModule._run_impl(**input_values),

    @classmethod
    def _run_impl(
            cls,
            source: ReaderDataSourceOrSink,
            input_url: str,
            data_format: WebSourceDataFormat,
            csv_tsv_has_header: bool,
            database_server_name: str,
            database_name: str,
            sql_account_name: str,
            account_password: SecureString,
            trust_server_certificate: bool,
            sql_stream_reader: str,
            auth_type: ReaderAuthenticationType,
            sas_blob_uri: str,
            account_name: str,
            account_key: SecureString,
            account_blob_path: str,
            sas_blob_format: BlobDataFormat,
            account_blob_format: BlobDataFormat,
            delimiter_type: DelimitedTextDelimiterType,
            delimited_text_encoding: DelimitedTextEncodingType,
            excel_format: ExcelFormat,
            excel_name: str,
            account_blob_csv_has_header: bool,
            sas_blob_csv_has_header: bool,
            table_auth_type: ReaderAuthenticationType,
            table_sas: str,
            table_account_name: str,
            table_account_key,
            table_names: str,
            scan_mode: PropertyScan,
            rows_to_scan: int,
            sas_scan_mode: PropertyScan,
            sas_rows_to_scan: int,
            hive_stream_reader: str,
            h_cat_uri: str,
            hadoop_username: str,
            hadoop_password,
            data_location: DataLocation,
            hdfs_uri: str,
            azure_account_name: str,
            azure_storage_key,
            container_name: str,
            url_content: str,
            power_query_url: str,
            document_db_server: str,
            document_db_database_name: str,
            document_db_password,
            document_db_collection: str,
            document_db_query: str,
            document_db_query_params: str,
            infer_schema: bool):

        source_friendly_name = cls._args.source.friendly_name

        if source is ReaderDataSourceOrSink.AzureBlobStorage:
            if auth_type is ReaderAuthenticationType.PublicOrSAS:
                return read_blobs_via_public_sas(
                    sas_blob_uri=sas_blob_uri,
                    sas_blob_format=sas_blob_format,
                    sas_blob_csv_has_header=sas_blob_csv_has_header
                )
            elif auth_type is ReaderAuthenticationType.Account:
                return read_blobs_via_account(
                    account_name=account_name,
                    account_key=account_key.value,
                    account_blob_path=account_blob_path,
                    account_blob_format=account_blob_format,
                    delimiter_type=delimiter_type,
                    delimited_text_encoding=delimited_text_encoding,
                    excel_format=excel_format,
                    excel_name=excel_name,
                    account_blob_csv_has_header=account_blob_csv_has_header
                )
            else:
                raise NotImplementedError(
                    f"Unsupported input '{auth_type}' for parameter '{cls._args.auth_type.name}'")
        elif source is ReaderDataSourceOrSink.AzureTable:
            raise NotImplementedError(f"Unsupported input '{source}' for parameter '{source_friendly_name}'")
        elif source is ReaderDataSourceOrSink.DocumentDB:
            raise NotImplementedError(f"Unsupported input '{source}' for parameter '{source_friendly_name}'")
        elif source is ReaderDataSourceOrSink.HiveQuery:
            raise NotImplementedError(f"Unsupported input '{source}' for parameter '{source_friendly_name}'")
        elif source is ReaderDataSourceOrSink.Http:
            if data_format is WebSourceDataFormat.CSV or data_format is WebSourceDataFormat.TSV:
                return read_csv(
                    input_url=input_url,
                    data_format=data_format,
                    has_header=csv_tsv_has_header)
            elif data_format is WebSourceDataFormat.ARFF:
                return read_arff(input_url=input_url)
            elif data_format is WebSourceDataFormat.SvmLight:
                return read_svmlight(input_url=input_url)
            else:
                raise NotImplementedError(
                    f"Unsupported input '{data_format}' for parameter '{cls._args.data_format.name}'")
        elif source is ReaderDataSourceOrSink.PowerQuery:
            raise NotImplementedError(f"Unsupported input '{source}' for parameter '{source_friendly_name}'")
        elif source is ReaderDataSourceOrSink.SqlAzure:
            return read_from_azure_sql_with_data_flow(
                database_server_name=database_server_name,
                database_name=database_name,
                sql_account_name=sql_account_name,
                account_password=account_password.value,
                trust_server_certificate=trust_server_certificate,
                sql_statement=sql_stream_reader,
            )
        else:
            raise NotImplementedError(f"Unsupported input '{source}' for parameter '{source_friendly_name}'")
