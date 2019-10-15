import pytest

from seeq.base import gconfig
from seeq import spy

from . import test_common


@pytest.mark.system
def test_bad_login():
    with pytest.raises(RuntimeError):
        spy.login('mark.derbecker@seeq.com', 'DataLab!', url='https://bogus')

    # Remove overrides that resulted from spy.login() with bogus URL
    gconfig.override_global_property('seeq_server_hostname', '')
    gconfig.override_global_property('seeq_server_port', '')
    gconfig.override_global_property('seeq_secure_port', '')

    try:
        spy.login('mark.derbecker@seeq.com', 'DataLab!', auth_provider='bogus')
        assert False, 'Exception was not raised with bogus auth_provider'
    except RuntimeError:
        pass


@pytest.mark.system
def test_good_login():
    test_common.login()


@pytest.mark.system
def test_credentials_file_with_username():
    with pytest.raises(RuntimeError):
        spy.login('mark.derbecker@seeq.com', 'DataLab!', credentials_file='credentials.key')
