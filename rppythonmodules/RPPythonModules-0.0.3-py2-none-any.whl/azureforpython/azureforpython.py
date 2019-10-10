
import os
from azure.mgmt.compute import ComputeManagementClient
import azure.mgmt.resource
import automationassets
from azure.cli.core import get_default_cli
from azure.common.credentials import ServicePrincipalCredentials
from azure.keyvault import KeyVaultClient

def get_automation_runas_credential(runas_connection):
    from OpenSSL import crypto
    import binascii
    from msrestazure import azure_active_directory
    import adal

    # Get the Azure Automation RunAs service principal certificate
    cert = automationassets.get_automation_certificate("AzureRunAsCertificate")
    pks12_cert = crypto.load_pkcs12(cert)
    pem_pkey = crypto.dump_privatekey(crypto.FILETYPE_PEM,pks12_cert.get_privatekey())
    
    # Get run as connection information for the Azure Automation service principal
    application_id = runas_connection["ApplicationId"]
    thumbprint = runas_connection["CertificateThumbprint"]
    tenant_id = runas_connection["TenantId"]

    # Authenticate with service principal certificate
    resource ='https://vault.azure.net'
    authority_url = ("https://login.microsoftonline.com/"+tenant_id)
    context = adal.AuthenticationContext(authority_url)
    return azure_active_directory.AdalAuthentication(
    lambda: context.acquire_token_with_client_certificate(
            resource,
            application_id,
            pem_pkey,
            thumbprint)
    )

def connect_azure():
    # Authenticate to Azure using the Azure Automation RunAs service principal
    try:
        runas_connection = automationassets.get_automation_connection("AzureRunAsConnection")
        credentials = get_automation_runas_credential(runas_connection)
        return credentials
    except:
        # FOR LOCAL TESTING ONLY! ALWAYS REMOVE THE TENANT ID, CLIENT, AND KEY BEFORE MERGING TO REPO.
               
        # Tenant ID for your Azure subscription. Grab in LastPass under Shared-SRE-Support folder called SREAzureAutomation Credentials
        TENANT_ID = ''

        # Your service principal App ID. Grab in LastPass under Shared-SRE-Support folder called SREAzureAutomation Credentials
        CLIENT = ''

        # Your service principal password. Grab in LastPass under Shared-SRE-Support folder called SREAzureAutomation Credentials
        KEY = ''

        credentials = ServicePrincipalCredentials(
            client_id = CLIENT,
            secret = KEY,
            tenant = TENANT_ID
        )
        return credentials