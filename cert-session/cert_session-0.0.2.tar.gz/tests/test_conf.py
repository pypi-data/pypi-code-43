'''Unit tests'''

import os


def test_conf_cert_path(cert_path):
    assert os.path.exists(cert_path)
