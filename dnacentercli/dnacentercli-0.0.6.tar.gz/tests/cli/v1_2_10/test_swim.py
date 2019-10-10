import click
import pytest
from json import loads, dumps
from tests.environment import DNA_CENTER_VERSION, DNA_CENTER_BASE_URL
from tests.models.schema_validator import json_schema_validate
from dnacentersdk import mydict_data_factory
from tests.config import LOCAL_SOFTWARE_IMAGE_PATH, LOCAL_SOFTWARE_IMAGE_NAME


pytestmark = pytest.mark.skipif(DNA_CENTER_VERSION != '1.2.10', reason='version does not match')


@pytest.mark.swim
def test_get_software_image_details(runner, cli, auth_options):
    result = runner.invoke(cli, [*auth_options, 'swim', 'get-software-image-details', '--sort_order', 'asc'])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_0c8f7a0b49b9aedd_v1_2_10').validate(obj) is None


@pytest.mark.skipif(not all([LOCAL_SOFTWARE_IMAGE_PATH, LOCAL_SOFTWARE_IMAGE_PATH]) is True,
                    reason="tests.config values required not present")
@pytest.mark.swim
def test_import_local_software_image(runner, cli, auth_options):
    result = runner.invoke(cli, [*auth_options, 'swim', 'import-local-software-image', '--filename', LOCAL_SOFTWARE_IMAGE_NAME, '--file', LOCAL_SOFTWARE_IMAGE_PATH])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_4dbe3bc743a891bc_v1_2_10').validate(obj) is None


@pytest.mark.skipif(not all([DNA_CENTER_BASE_URL]) is True,
                    reason="tests.config values required not present")
@pytest.mark.swim
def test_import_software_image_via_url(runner, cli, auth_options):
    image_details = runner.invoke(cli, [*auth_options, 'swim', 'get-software-image-details', '--sort_order', 'asc'])
    image_details = mydict_data_factory('', loads(image_details.output)).response[0]

    list_of_available_namespaces = runner.invoke(cli, [*auth_options, 'file', 'get-list-of-available-namespaces'])
    list_of_available_namespaces = mydict_data_factory('', loads(list_of_available_namespaces.output))

    files = runner.invoke(cli, [*auth_options, 'file', 'get-list-of-files', '--name_space', list_of_available_namespaces.response[0]])
    files = mydict_data_factory('', loads(files.output)).response[0].downloadPath

    result = runner.invoke(cli, [*auth_options, 'swim', 'import-software-image-via-url',
                                 '--payload', dumps([{
                                     'applicationType': image_details.applicationType,
                                     'vendor': image_details.vendor,
                                     'imageFamily': image_details.family,
                                     'sourceURL': DNA_CENTER_BASE_URL + '/dna/intent/api/v1/' + files
                                 }])])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_bc8aab4746ca883d_v1_2_10').validate(obj) is None


@pytest.mark.swim
def test_trigger_software_image_activation(runner, cli, auth_options):
    device_list = runner.invoke(cli, [*auth_options, 'devices', 'get-device-list'])
    device_list = mydict_data_factory('', loads(device_list.output))

    image_details = runner.invoke(cli, [*auth_options, 'swim', 'get-software-image-details', '--sort_order', 'asc'])
    image_details = mydict_data_factory('', loads(image_details.output)).response[0]

    result = runner.invoke(cli, [*auth_options, 'swim', 'trigger-software-image-activation',
                                 '--payload', dumps([{
                                     'activateLowerImageVersion': True,
                                     'deviceUuid': device_list.response[0].id,
                                     'distributeIfNeeded': True,
                                     'imageUuidList': [image_details.imageUuid],
                                 }])])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_fb9beb664f2aba4c_v1_2_10').validate(obj) is None


@pytest.mark.swim
def test_trigger_software_image_distribution(runner, cli, auth_options):
    device_list = runner.invoke(cli, [*auth_options, 'devices', 'get-device-list'])
    device_list = mydict_data_factory('', loads(device_list.output))

    image_details = runner.invoke(cli, [*auth_options, 'swim', 'get-software-image-details', '--sort_order', 'asc'])
    image_details = mydict_data_factory('', loads(image_details.output)).response[0]

    result = runner.invoke(cli, [*auth_options, 'swim', 'trigger-software-image-distribution',
                                 '--payload', dumps([{
                                     'deviceUuid': device_list.response[0].id,
                                     'imageUuid': image_details.imageUuid
                                 }])])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_8cb6783b4faba1f4_v1_2_10').validate(obj) is None
