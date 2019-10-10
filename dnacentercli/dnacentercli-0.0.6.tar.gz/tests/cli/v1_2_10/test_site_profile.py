import click
import pytest
from json import loads
from tests.environment import DNA_CENTER_VERSION
from tests.models.schema_validator import json_schema_validate
from dnacentersdk import mydict_data_factory
from tests.config import SITE_PROFILE_DEVICE_IP


pytestmark = pytest.mark.skipif(DNA_CENTER_VERSION != '1.2.10', reason='version does not match')


@pytest.mark.skipif(not all([SITE_PROFILE_DEVICE_IP]) is True,
                    reason="tests.config values required not present")
@pytest.mark.site_profile
def test_get_device_details_by_ip(runner, cli, auth_options):
    result = runner.invoke(cli, [*auth_options, 'site-profile', 'get-device-details-by-ip', '--device_ip', SITE_PROFILE_DEVICE_IP])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_7fbe4b804879baa4_v1_2_10').validate(obj) is None


@pytest.mark.site_profile
def test_provision_nfv(runner, cli, auth_options):
    result = runner.invoke(cli, [*auth_options, 'site-profile', 'provision-nfv'])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_828828f44f28bd0d_v1_2_10').validate(obj) is None
