import json
import os
import ssl

from urllib.request import Request, urlopen

from azureml.studio.modulehost.attributes import ReleaseState
from azureml.studio.common.error import AlghostRuntimeError
from azureml.studio.common.json_encoder import EnhancedJsonEncoder
from azureml.studio.core.logger import common_logger


class ServerConf:
    """Configuration for different servers"""

    AVAILABLE_NAMES = (
        'int',
        'ppe',
        'ppe_au',
        'eastus',
        'eastus2',
        'westus2',
        'westeurope',
        'northeurope',
        'southcentralus',
        'westcentralus',
        'southeastasia',
        'australiaeast',
        'eastus2euap',
        'canadacentral',
        'uksouth',
        'centralindia',
        'japaneast',
        'eastasia',
        'westus',
        'centralus',
        'northcentralus',
    )

    def __init__(self, name):
        if name not in self.AVAILABLE_NAMES:
            common_logger.warning(f"Unrecognized region '{name}'. Trying anyway.")

        self._name = name

    @property
    def name(self):
        return self._name

    @property
    def url(self):
        if self._name == 'int':
            return 'https://amlv2-test1.azureml-test.net/api'
        elif self._name == 'ppe':
            return 'https://amlv2-test2.azureml-test.net/api'
        elif self._name == 'ppe_au':
            return 'https://amlv2-test3.azureml-test.net/api'
        else:
            return f"https://{self._name}.studioapi.azureml.com/api"

    @property
    def workspace_id(self):
        return '506153734175476c4f62416c57734963'

    @property
    def allowed_release_states(self):
        if self._name in ('int', 'ppe', 'ppe_au'):
            return ReleaseState.Beta, ReleaseState.Release
        else:
            return ReleaseState.Release,


def _init_ssl_context(cert_file=None):
    if not cert_file:
        raise ValueError(f"cert_file must not be empty.")
    if not os.path.isfile(cert_file):
        raise ValueError(f"Cert file {cert_file} not found.")

    context = ssl.create_default_context()
    context.load_cert_chain(cert_file)
    return context


class ModuleRegistry:
    def __init__(self, base_url, workspace_id, cert_file=None):
        self._base_url = base_url
        self._workspace_id = workspace_id
        self._cert_file = cert_file

    @property
    def modules_url(self):
        return f"{self._base_url}/admin/modules?workspaceId={self._workspace_id}"

    @property
    def batch_base_url(self):
        return f"{self._base_url}/admin/workspaces/{self._workspace_id}/modules/batches"

    @property
    def headers(self):
        return {
            'Content-Type': 'application/json'
        }

    @staticmethod
    def _payload_data_of_module(module):
        return {
            'UploadId': 'dummy',
            'Module': module.ux_contract_dict,
        }

    def _payload_data_of_module_list(self, modules):
        return [self._payload_data_of_module(m) for m in modules]

    def _send_request(self, url, data=None, method=None):
        if data is not None:
            data = json.dumps(data, cls=EnhancedJsonEncoder).encode()
        if method is None:
            method = 'GET' if data is None else 'POST'
        req = Request(url, data, self.headers, method=method)

        # need client certificate to communicate with server
        context = _init_ssl_context(cert_file=self._cert_file)

        try:
            with urlopen(req, context=context) as res:
                body = res.read().decode()
                return body
        except BaseException as e:
            raise AlghostRuntimeError(f"Failed while performing {method} {url}") from e

    def list_modules(self):
        ret = self._send_request(self.modules_url)
        return json.loads(ret)

    def get_latest_batch_id(self):
        dct = self.get_batch()
        return dct['Number']

    def get_batch_description(self, batch_id='latest'):
        dct = self.get_batch(batch_id=batch_id)
        return f"Batch id {dct['Number']}, containing {len(dct['AssetIds'])} modules."

    def get_batch(self, batch_id='latest'):
        url = f"{self.batch_base_url}/{batch_id}/details"
        ret = self._send_request(url)
        dct = json.loads(ret)
        return dct

    def add_batch(self, batch_id, modules):
        url = f"{self.batch_base_url}/{batch_id}"
        data = self._payload_data_of_module_list(modules)
        return self._send_request(url, data)

    def activate_batch(self, batch_id, force=False):
        url = f"{self.batch_base_url}/{batch_id}/active?forceDowngrade={force}"
        return self._send_request(url, method='POST')
