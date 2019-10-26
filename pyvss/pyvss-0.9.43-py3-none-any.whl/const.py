PACKAGE_NAME = "pyvss"

__version__ = '0.9.43'

API_ENDPOINT_BASE = 'https://cloud-api.eis.utoronto.ca'
VSKEY_STOR_ENDPOINT = 'https://vskey-stor.eis.utoronto.ca'
DEFAULT_TIMEOUT = 60
DEFAULT_DEBUG = False
DATETIME_FMT = '%Y-%m-%d %H:%M'
VALID_VM_USAGE = [
    ('Production', 'Prod'),
    ('Testing', 'Test'),
    ('Development', 'Dev'),
    ('QA', 'QA'),
]
VALID_VM_BUILD_PROCESS = ['clone', 'template', 'image', 'os_install']
