# This is replaced during release process.
# flake8: noqa
__version_suffix__ = '87'

APP_NAME = "zalando-kubectl"

KUBECTL_VERSION = 'v1.14.7'
KUBECTL_SHA512 = {
    'linux': '6d84db16061dd8d3e3eb49c94d2559d0c7cb4896f0ca3003259c733da4fd2de8de87619cff27249b0f8b29fb56f94e150b2dd2d64186e4195bda46e1e8048092',
    'darwin': '04278365c8b3e75b3515ab8982756b613ff79ac76aaf06cfc684d801f00db7485b8090dae43a468f7deb67fc3adf27f52933c85a5246dd5ccaf0ec43791ea46a'
}

STERN_VERSION = '1.10.0'
STERN_SHA256 = {
    'linux': 'a0335b298f6a7922c35804bffb32a68508077b2f35aaef44d9eb116f36bc7eda',
    'darwin': 'b91dbcfd3bbda69cd7a7abd80a225ce5f6bb9d6255b7db192de84e80e4e547b7'
}

APP_VERSION = KUBECTL_VERSION + "." + __version_suffix__
