from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
import gcloud.rest.datastore.constants as constants  # pylint: disable=unused-import


def test_importable():
    assert True
