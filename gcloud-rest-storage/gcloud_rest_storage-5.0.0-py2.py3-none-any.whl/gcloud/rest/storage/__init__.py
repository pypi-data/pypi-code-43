from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from pkg_resources import get_distribution
__version__ = get_distribution('gcloud-rest-storage').version

from gcloud.rest.storage.blob import Blob
from gcloud.rest.storage.bucket import Bucket
from gcloud.rest.storage.storage import SCOPES
from gcloud.rest.storage.storage import Storage


__all__ = ['__version__', 'Blob', 'Bucket', 'SCOPES', 'Storage']
