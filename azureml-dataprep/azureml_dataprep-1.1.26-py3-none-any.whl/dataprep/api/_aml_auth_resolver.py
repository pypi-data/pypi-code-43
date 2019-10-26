import json
import os
from ._aml_helper import get_workspace_from_run, verify_workspace


def _resolve_auth_from_workspace(request, writer, socket):
    try:
        from azureml.core import Workspace
        from azureml.data.datastore_client import _DatastoreClient
        from azureml._base_sdk_common.service_discovery import get_service_url


        auth_type = request.get('auth_type')
        ws_name = request.get('ws_name')
        subscription = request.get('subscription')
        resource_group = request.get('resource_group')

        if auth_type == 'SP':
            from azureml.core.authentication import ServicePrincipalAuthentication
            extra_args = request.get('extra_args')
            if not extra_args:
                writer.write(json.dumps({'result': 'error', 'error': 'InvalidServicePrincipalCreds'}))
                return
            creds = json.loads(extra_args)
            auth = ServicePrincipalAuthentication(creds['tenantId'], creds['servicePrincipalId'], creds['password'])
            ws = Workspace.get(ws_name, auth=auth, subscription_id=subscription, resource_group=resource_group)
        else:
            if not ws_name or not subscription or not resource_group:
                writer.write(json.dumps({'result': 'error', 'error': 'InvalidWorkspace'}))
                return

            ws = get_workspace_from_run() or \
                Workspace.get(ws_name, subscription_id=subscription, resource_group=resource_group)
            auth = ws._auth

        verify_workspace(ws, subscription, resource_group, ws_name)

        host = os.environ.get('AZUREML_SERVICE_ENDPOINT') or \
            get_service_url(ws._auth, ws.service_context._get_workspace_scope(), ws._workspace_id)

        writer.write(json.dumps({
            'result': 'success',
            'auth': json.dumps(auth.get_authentication_header()),
            'host': host
        }))
    except Exception as e:
        writer.write(json.dumps({'result': 'error', 'error': str(e)}))


def register_datastore_resolver(requests_channel):
    requests_channel.register_handler('resolve_auth_from_workspace', _resolve_auth_from_workspace)
