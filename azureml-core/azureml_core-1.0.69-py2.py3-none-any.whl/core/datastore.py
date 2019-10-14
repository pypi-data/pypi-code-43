# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains functionality for managing Datastores in Azure Machine Learning service."""


class Datastore(object):
    """Represents a storage abstraction over an Azure Machine Learning storage account.

    Datastores are attached to workspaces and are used to store connection information to Azure
    storage services so you can refer to them by name and don't need to remember the connection
    information and secret used to connect to the storage services.

    Examples of supported Azure storage services that can be registered as datastores are:

    * Azure Blob Container
    * Azure File Share
    * Azure Data Lake
    * Azure Data Lake Gen2
    * Azure SQL Database
    * Azure PostgreSQL
    * Databricks File System

    Use this class to perform management operations, including register, list, get, and remove datastores.
    Datastores for each service are created with the ``register*`` methods of this class. When using a datastore
    to access data, you must have permission to access that data, which depends on the credentials registered
    with the datastore.

    For more information on datastores and how they can be used in machine learning see the following articles:

    * `Access data in Azure storage
      services <https://docs.microsoft.com/azure/machine-learning/service/how-to-access-data>`_
    * `Train models with Azure Machine Learning using
      estimator <https://docs.microsoft.com/azure/machine-learning/service/how-to-train-ml-models>`_
    * `Create and run machine learning
      pipelines <https://docs.microsoft.com/azure/machine-learning/service/how-to-create-your-first-pipeline>`_

    .. remarks::

        The following example shows how to create a Datastore connected to Azure Blob Container.

        .. code-block:: python

            from msrest.exceptions import HttpOperationError

            blob_datastore_name='MyBlobDatastore'
            account_name=os.getenv("BLOB_ACCOUNTNAME_62", "<my-account-name>") # Storage account name
            container_name=os.getenv("BLOB_CONTAINER_62", "<my-container-name>") # Name of Azure blob container
            account_key=os.getenv("BLOB_ACCOUNT_KEY_62", "<my-account-key>") # Storage account key

            try:
                blob_datastore = Datastore.get(ws, blob_datastore_name)
                print("found blob datastore with name: %s" % blob_datastore_name)
            except HttpOperationError:
                blob_datastore = Datastore.register_azure_blob_container(
                    workspace=ws,
                    datastore_name=blob_datastore_name,
                    account_name=account_name, # Storage account name
                    container_name=container_name, # Name of Azure blob container
                    account_key=account_key) # Storage account key
                print("registered blob datastore with name: %s" % blob_datastore_name)

            blob_data_ref = DataReference(
                datastore=blob_datastore,
                data_reference_name="blob_test_data",
                path_on_datastore="testdata")

        Full sample is available from
        https://github.com/Azure/MachineLearningNotebooks/blob/master/how-to-use-azureml/machine-learning-pipelines/intro-to-pipelines/aml-pipelines-data-transfer.ipynb


    """

    def __new__(cls, workspace, name=None):
        """Get a datastore by name. This call will make a request to the datastore service.

        :param workspace: The workspace.
        :type workspace: azureml.core.Workspace
        :param name: The name of the datastore, defaults to None, which gets the default datastore.
        :type name: str, optional
        :return: The corresponding datastore for that name.
        :rtype: AbstractDatastore
        """
        if name is None:
            return Datastore._client().get_default(workspace)
        return Datastore._client().get(workspace, name)

    def __init__(self, workspace, name=None):
        """Get a datastore by name. This call will make a request to the datastore service.

        :param workspace: The workspace.
        :type workspace: azureml.core.Workspace
        :param name: The name of the datastore, defaults to None, which gets the default datastore.
        :type name: str, optional
        :return: The corresponding datastore for that name.
        :rtype: AbstractDatastore
        """
        self.workspace = workspace
        self.name = name

    def set_as_default(self):
        """Set the default datastore.

        :param datastore_name: The name of the datastore.
        :type datastore_name: str
        """
        Datastore._client().set_default(self.workspace, self.name)

    def unregister(self):
        """Unregisters the datastore. the underlying storage service will not be deleted."""
        Datastore._client().delete(self.workspace, self.name)

    @staticmethod
    def get(workspace, datastore_name):
        """Get a datastore by name. This is same as calling the constructor.

        :param workspace: The workspace.
        :type workspace: azureml.core.Workspace
        :param datastore_name: The name of the datastore, defaults to None, which gets the default datastore.
        :type datastore_name: str, optional
        :return: The corresponding datastore for that name.
        :rtype: azureml.data.azure_storage_datastore.AzureFileDatastore
                or azureml.data.azure_storage_datastore.AzureBlobDatastore
        """
        return Datastore._client().get(workspace, datastore_name)

    @staticmethod
    def get_default(workspace):
        """Get the default datastore for the workspace.

        :param workspace: The workspace.
        :type workspace: azureml.core.Workspace
        :return: The default datastore for the workspace
        :rtype: azureml.data.azure_storage_datastore.AzureFileDatastore
                or azureml.data.azure_storage_datastore.AzureBlobDatastore
        """
        return Datastore._client().get_default(workspace)

    @staticmethod
    def register_azure_blob_container(workspace, datastore_name, container_name, account_name, sas_token=None,
                                      account_key=None, protocol=None, endpoint=None, overwrite=False,
                                      create_if_not_exists=False, skip_validation=False, blob_cache_timeout=None,
                                      grant_workspace_access=False, subscription_id=None, resource_group=None):
        """Register an Azure Blob Container to the datastore.

        You can choose to use SAS Token or Storage Account Key

        :param workspace: The workspace.
        :type workspace: azureml.core.Workspace
        :param datastore_name: The name of the datastore, case insensitive, can only contain alphanumeric characters
            and _.
        :type datastore_name: str
        :param container_name: The name of the azure blob container.
        :type container_name: str
        :param account_name: The storage account name.
        :type account_name: str
        :param sas_token: An account SAS token, defaults to None.
        :type sas_token: str, optional
        :param account_key: A storage account key, defaults to None.
        :type account_key: str, optional
        :param protocol: Protocol to use to connect to the blob container. If None, defaults to https.
        :type protocol: str, optional
        :param endpoint: The endpoint of the blob container. If None, defaults to core.windows.net.
        :type endpoint: str, optional
        :param overwrite: overwrites an existing datastore. If the datastore does not exist,
            it will create one, defaults to False
        :type overwrite: bool, optional
        :param create_if_not_exists: create the file share if it does not exists, defaults to False
        :type create_if_not_exists: bool, optional
        :param skip_validation: skips validation of storage keys, defaults to False
        :type skip_validation: bool, optional
        :param blob_cache_timeout: When this blob is mounted, set the cache timeout to this many seconds.
            If None, defaults to no timeout (i.e. blobs will be cached for the duration of the job when read).
        :type blob_cache_timeout: int, optional
        :param grant_workspace_access: grants Workspace Managed Identities(MSI) access to the user storage account,
            defaults to False. This should be set if the Storage account is in VNET. If set to True, we will use the
            Workspace MSI token to grant access to the user storage account. It may take a while for the
            granted access to reflect.
        :type grant_workspace_access: bool, optional
        :param subscription_id: The subscription id of the storage account, defaults to None.
        :type subscription_id: str, optional
        :param resource_group: The resource group of the storage account, defaults to None.
        :type resource_group: str, optional
        :return: The blob datastore.
        :rtype: azureml.data.azure_storage_datastore.AzureBlobDatastore
        """
        return Datastore._client().register_azure_blob_container(
            workspace=workspace,
            datastore_name=datastore_name,
            container_name=container_name,
            account_name=account_name,
            sas_token=sas_token,
            account_key=account_key,
            protocol=protocol,
            endpoint=endpoint,
            overwrite=overwrite,
            create_if_not_exists=create_if_not_exists,
            skip_validation=skip_validation,
            blob_cache_timeout=blob_cache_timeout,
            grant_workspace_access=grant_workspace_access,
            subscription_id=subscription_id,
            resource_group=resource_group,
        )

    @staticmethod
    def register_azure_file_share(workspace, datastore_name, file_share_name, account_name, sas_token=None,
                                  account_key=None, protocol=None, endpoint=None, overwrite=False,
                                  create_if_not_exists=False, skip_validation=False):
        """Register an Azure File Share to the datastore.

        You can choose to use SAS Token or Storage Account Key

        :param workspace: The workspace this datastore belongs to.
        :type workspace: azureml.core.Workspace
        :param datastore_name: The name of the datastore, case insensitive, can only contain alphanumeric characters
            and _.
        :type datastore_name: str
        :param file_share_name: The name of the azure file container.
        :type file_share_name: str
        :param account_name: The storage account name.
        :type account_name: str
        :param sas_token: An account SAS token, defaults to None.
        :type sas_token: str, optional
        :param account_key: A storage account key, defaults to None.
        :type account_key: str, optional
        :param protocol: The protocol to use to connect to the file share. If None, defaults to https.
        :type protocol: str, optional
        :param endpoint: The endpoint of the file share. If None, defaults to core.windows.net.
        :type endpoint: str, optional
        :param overwrite: Whether to overwrite an existing datastore. If the datastore does not exist,
            it will create one. The default is False.
        :type overwrite: bool, optional
        :param create_if_not_exists: Whether to create the file share if it does not exists. The default is False.
        :type create_if_not_exists: bool, optional
        :param skip_validation: Whether to skip validation of storage keys. The default is False.
        :type skip_validation: bool, optional
        :return: The file datastore.
        :rtype: azureml.data.azure_storage_datastore.AzureFileDatastore
        """
        return Datastore._client().register_azure_file_share(workspace, datastore_name, file_share_name, account_name,
                                                             sas_token, account_key, protocol, endpoint, overwrite,
                                                             create_if_not_exists, skip_validation)

    @staticmethod
    def register_azure_data_lake(workspace, datastore_name, store_name, tenant_id, client_id, client_secret,
                                 resource_url=None, authority_url=None, subscription_id=None, resource_group=None,
                                 overwrite=False):
        """Initialize a new Azure Data Lake Datastore.

        .. remarks::

            .. note::

                Azure Data Lake Datastore supports data transfer and running U-Sql jobs using AML Pipelines.
                It does not provide upload and download through the SDK.

        :param workspace: The workspace this datastore belongs to.
        :type workspace: azureml.core.Workspace
        :param datastore_name: The datastore name.
        :type datastore_name: str
        :param store_name: The ADLS store name.
        :type store_name: str
        :param tenant_id: The Directory ID/Tenant ID of the service principal.
        :type tenant_id: str
        :param client_id: The Client ID/Application ID of the service principal.
        :type client_id: str
        :param client_secret: The secret of the service principal.
        :type client_secret: str
        :param resource_url: The resource URL, which determines what operations will be performed on the Data Lake
            store, if None, defaults to https://datalake.azure.net/ which allows us to perform filesystem operations.
        :type resource_url: str, optional
        :param authority_url: The authority URL used to authenticate the user, defaults to
            https://login.microsoftonline.com.
        :type authority_url: str, optional
        :param subscription_id: The ID of the subscription the ADLS store belongs to.
        :type subscription_id: str, optional
        :param resource_group: The resource group the ADLS store belongs to.
        :type resource_group: str, optional
        :param overwrite: Whether to overwrite an existing datastore. If the datastore does not exist,
            it will create one. The default is False.
        :type overwrite: bool, optional
        :return: Returns the Azure Data Lake Datastore.
        :rtype: azureml.data.azure_data_lake_datastore.AzureDataLakeDatastore
        """
        return Datastore._client().register_azure_data_lake(
            workspace, datastore_name, store_name, tenant_id, client_id, client_secret,
            resource_url, authority_url, subscription_id, resource_group, overwrite)

    @staticmethod
    def register_azure_data_lake_gen2(workspace, datastore_name, filesystem, account_name, tenant_id, client_id,
                                      client_secret, resource_url=None, authority_url=None, protocol=None,
                                      endpoint=None, overwrite=False):
        """Initialize a new Azure Data Lake Gen2 Datastore.

        :param workspace: The workspace this datastore belongs to.
        :type workspace: azureml.core.Workspace
        :param datastore_name: The datastore name.
        :type datastore_name: str
        :param filesystem: The name of the Data Lake Gen2 filesystem.
        :type filesystem: str
        :param account_name: The storage account name.
        :type account_name: str
        :param tenant_id: The Directory ID/Tenant ID of the service principal.
        :type tenant_id: str
        :param client_id: The Client ID/Application ID of the service principal.
        :type client_id: str
        :param client_secret: The secret of the service principal.
        :type client_secret: str
        :param resource_url: The resource URL, which determines what operations will be performed on
            the data lake store, defaults to https://storage.azure.com/ which allows us to perform filesystem
            operations.
        :type resource_url: str, optional
        :param authority_url: The authority URL used to authenticate the user, defaults to
            https://login.microsoftonline.com.
        :type authority_url: str, optional
        :param protocol: Protocol to use to connect to the blob container. If None, defaults to https.
        :type protocol: str, optional
        :param endpoint: The endpoint of the blob container. If None, defaults to core.windows.net.
        :type endpoint: str, optional
        :param overwrite: Whether to overwrite an existing datastore. If the datastore does not exist,
            it will create one. The default is False.
        :type overwrite: bool, optional
        :return: Returns the Azure Data Lake Gen2 Datastore.
        :rtype: azureml.data.azure_data_lake_datastore.AzureDataLakeGen2Datastore

        """
        return Datastore._client()._register_azure_data_lake_gen2(
            workspace, datastore_name, filesystem, account_name, tenant_id, client_id, protocol, endpoint,
            client_secret, resource_url, authority_url, overwrite)

    @staticmethod
    def register_azure_sql_database(workspace, datastore_name, server_name, database_name, tenant_id, client_id,
                                    client_secret, resource_url=None, authority_url=None, endpoint=None,
                                    overwrite=False):
        """Initialize a new Azure SQL database Datastore.

        :param workspace: The workspace this datastore belongs to.
        :type workspace: azureml.core.Workspace
        :param datastore_name: The datastore name.
        :type datastore_name: str
        :param server_name: The SQL server name.
        :type server_name: str
        :param database_name: The SQL database name.
        :type database_name: str
        :param tenant_id: The Directory ID/Tenant ID of the service principal.
        :type tenant_id: str
        :param client_id: The Client ID/Application ID of the service principal.
        :type client_id: str
        :param client_secret: The secret of the service principal.
        :type client_secret: str
        :param resource_url: The resource URL, which determines what operations will be performed on
            the SQL database store, if None, defaults to https://database.windows.net/.
        :type resource_url: str, optional
        :param authority_url: The authority URL used to authenticate the user, defaults to
            https://login.microsoftonline.com.
        :type authority_url: str, optional
        :param endpoint: The endpoint of the SQL server. If None, defaults to database.windows.net.
        :type endpoint: str, optional
        :param overwrite: Whether to overwrite an existing datastore. If the datastore does not exist,
            it will create one. The default is False.
        :type overwrite: bool, optional
        :return: Returns the SQL database Datastore.
        :rtype: azureml.data.azure_sql_database_datastore.AzureSqlDatabaseDatastore
        """
        return Datastore._client().register_azure_sql_database(
            workspace, datastore_name, server_name, database_name, tenant_id, client_id, client_secret,
            resource_url, authority_url, endpoint, overwrite)

    @ staticmethod
    def register_azure_postgre_sql(workspace, datastore_name, server_name, database_name, user_id, user_password,
                                   port_number=None, endpoint=None,
                                   overwrite=False):
        """Initialize a new Azure PostgreSQL Datastore.

        :param workspace: The workspace this datastore belongs to.
        :type workspace: azureml.core.Workspace
        :param datastore_name: The datastore name.
        :type datastore_name: str
        :param server_name: The PostgreSQL server name.
        :type server_name: str
        :param database_name: The PostgreSQL database name.
        :type database_name: str
        :param user_id: The User ID of the PostgreSQL server.
        :type user_id: str
        :param user_password: The User Password of the PostgreSQL server.
        :type user_password: str
        :param port_number: The Port Number of the PostgreSQL server
        :type port_number: str
        :param endpoint: The endpoint of the PostgreSQL server. If None, defaults to postgres.database.azure.com.
        :type endpoint: str, optional
        :param overwrite: Whether to overwrite an existing datastore. If the datastore does not exist,
            it will create one. The default is False.
        :type overwrite: bool, optional
        :return: Returns the PostgreSQL database Datastore.
        :rtype: azureml.data.azure_postgre_sql_datastore.AzurePostgreSqlDatastore
        """
        return Datastore._client().register_azure_postgre_sql(
            workspace, datastore_name, server_name, database_name, user_id, user_password,
            port_number, endpoint, overwrite)

    @ staticmethod
    def register_azure_my_sql(workspace, datastore_name, server_name, database_name, user_id, user_password,
                              port_number=None, endpoint=None,
                              overwrite=False):
        """Initialize a new Azure MySQL Datastore.

        :param workspace: The workspace this datastore belongs to.
        :type workspace: azureml.core.Workspace
        :param datastore_name: The datastore name.
        :type datastore_name: str
        :param server_name: The MySQL server name.
        :type server_name: str
        :param database_name: The MySQL database name.
        :type database_name: str
        :param user_id: The User ID of the MySQL server.
        :type user_id: str
        :param user_password: The user password of the MySQL server.
        :type user_password: str
        :param port_number: The port number of the MySQL server.
        :type port_number: str
        :param endpoint: The endpoint of the MySQL server. If None, defaults to mysql.database.azure.com.
        :type endpoint: str, optional
        :param overwrite: Whether to overwrite an existing datastore. If the datastore does not exist,
            it will create one. The default is False.
        :type overwrite: bool, optional
        :return: Returns the MySQL database Datastore.
        :rtype: azureml.data.azure_my_sql_datastore.AzureMySqlDatastore
        """
        return Datastore._client().register_azure_my_sql(
            workspace, datastore_name, server_name, database_name, user_id, user_password,
            port_number, endpoint, overwrite)

    @staticmethod
    def register_dbfs(workspace, datastore_name):
        """Initialize a new Databricks File System (DBFS) datastore.

        :param workspace: The workspace this datastore belongs to.
        :type workspace: azureml.core.Workspace
        :param datastore_name: The datastore name.
        :type datastore_name: str
        """
        return Datastore._client().register_dbfs(workspace, datastore_name)

    @staticmethod
    def _client():
        """Get a client.

        :return: Returns the client
        :rtype: DatastoreClient
        """
        from azureml.data.datastore_client import _DatastoreClient
        return _DatastoreClient
