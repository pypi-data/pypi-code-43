from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from pkg_resources import get_distribution
__version__ = get_distribution('gcloud-rest-taskqueue').version

from gcloud.rest.taskqueue.queue import PushQueue
from gcloud.rest.taskqueue.queue import SCOPES
from gcloud.rest.taskqueue.utils import decode
from gcloud.rest.taskqueue.utils import encode


__all__ = ['__version__', 'decode', 'encode', 'PushQueue', 'SCOPES']
