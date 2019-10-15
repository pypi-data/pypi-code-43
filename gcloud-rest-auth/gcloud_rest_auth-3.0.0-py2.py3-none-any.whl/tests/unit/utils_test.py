from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
import pickle

import gcloud.rest.auth.utils as utils  # pylint: disable=unused-import
import pytest


@pytest.mark.parametrize('str_or_bytes', ['Hello Test',
                                          'UTF-8 Bytes'.encode('utf-8'),
                                          pickle.dumps([])])
def test_encode_decode(str_or_bytes):
    encoded = utils.encode(str_or_bytes)
    expected = str_or_bytes
    if isinstance(expected, str):
        try:
            expected = str_or_bytes.encode('utf-8')
        except UnicodeDecodeError:
            pass
    assert expected == utils.decode(encoded)
