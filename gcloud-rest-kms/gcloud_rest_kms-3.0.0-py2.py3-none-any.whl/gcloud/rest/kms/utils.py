from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
# TODO: this file is copied from gcloud-rest-taskqueue
from future import standard_library
standard_library.install_aliases()
import base64
from typing import Union


def decode(payload     )       :
    """
    https://en.wikipedia.org/wiki/Base64#URL_applications modified Base64
    for URL variants exist, where the + and / characters of standard
    Base64 are respectively replaced by - and _
    """
    variant = payload.replace('-', '+').replace('_', '/')
    return base64.b64decode(variant).decode()


def encode(payload                   )       :
    """
    https://en.wikipedia.org/wiki/Base64#URL_applications modified Base64
    for URL variants exist, where the + and / characters of standard
    Base64 are respectively replaced by - and _
    """
    if not isinstance(payload, bytes):
        payload = payload.encode('utf-8')

    encoded = base64.b64encode(payload)
    return encoded.replace(b'+', b'-').replace(b'/', b'_').decode('utf-8')
