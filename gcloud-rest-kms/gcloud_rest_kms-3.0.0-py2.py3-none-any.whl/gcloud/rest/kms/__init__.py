from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from pkg_resources import get_distribution
__version__ = get_distribution('gcloud-rest-kms').version

from gcloud.rest.kms.kms import KMS
from gcloud.rest.kms.kms import SCOPES
from gcloud.rest.kms.utils import decode
from gcloud.rest.kms.utils import encode


__all__ = ['__version__', 'decode', 'encode', 'KMS', 'SCOPES']
