from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from pkg_resources import get_distribution
__version__ = get_distribution('gcloud-rest-auth').version

from gcloud.rest.auth.iam import IamClient
from gcloud.rest.auth.session import SyncSession
from gcloud.rest.auth.token import Token
from gcloud.rest.auth.utils import decode
from gcloud.rest.auth.utils import encode
from gcloud.rest.auth.build_constants import BUILD_GCLOUD_REST


__all__ = ['__version__', 'IamClient', 'Token', 'decode', 'encode',
           'SyncSession', 'BUILD_GCLOUD_REST']
