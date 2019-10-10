import click
import pytest
from json import loads, dumps
from tests.environment import DNA_CENTER_VERSION
from tests.models.schema_validator import json_schema_validate
from dnacentersdk import mydict_data_factory


pytestmark = pytest.mark.skipif(DNA_CENTER_VERSION != '1.2.10', reason='version does not match')


@pytest.mark.tag
def test_create_tag(runner, cli, auth_options):
    result = runner.invoke(cli, [*auth_options, 'tag', 'create-tag', '--name', 'InterestingTool01'])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_1399891c42a8be64_v1_2_10').validate(obj) is None


@pytest.mark.tag
def test_get_tag(runner, cli, auth_options):
    result = runner.invoke(cli, [*auth_options, 'tag', 'get-tag', '--order', 'des', '--sort_by', 'name'])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_ee9aab01487a8896_v1_2_10').validate(obj) is None


@pytest.mark.tag
def test_get_tag_created(runner, cli, auth_options):
    result = runner.invoke(cli, [*auth_options, 'tag', 'get-tag', '--name', 'InterestingTool01'])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_ee9aab01487a8896_v1_2_10').validate(obj) is None


@pytest.mark.tag
def test_get_tag_by_id(runner, cli, auth_options):
    tags = runner.invoke(cli, [*auth_options, 'tag', 'get-tag', '--order', 'des', '--sort_by', 'name'])
    tags = mydict_data_factory('', loads(tags.output))

    result = runner.invoke(cli, [*auth_options, 'tag', 'get-tag-by-id', '--id', tags.response[0].id])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_c1a359b14c89b573_v1_2_10').validate(obj) is None


@pytest.mark.tag
def test_get_tag_by_id_created(runner, cli, auth_options):
    tag_created = runner.invoke(cli, [*auth_options, 'tag', 'get-tag', '--name', 'InterestingTool01'])
    tag_created = mydict_data_factory('', loads(tag_created.output))

    result = runner.invoke(cli, [*auth_options, 'tag', 'get-tag-by-id', '--id', tag_created.response[0].id])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_c1a359b14c89b573_v1_2_10').validate(obj) is None


@pytest.mark.tag
def test_get_tag_count(runner, cli, auth_options):
    result = runner.invoke(cli, [*auth_options, 'tag', 'get-tag-count'])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_8091a9b84bfba53b_v1_2_10').validate(obj) is None


@pytest.mark.tag
def test_get_tag_resource_types(runner, cli, auth_options):
    result = runner.invoke(cli, [*auth_options, 'tag', 'get-tag-resource-types'])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_4695090d403b8eaa_v1_2_10').validate(obj) is None


@pytest.mark.tag
def test_get_tag_member_count(runner, cli, auth_options):
    tags = runner.invoke(cli, [*auth_options, 'tag', 'get-tag', '--order', 'des', '--sort_by', 'name'])
    tags = mydict_data_factory('', loads(tags.output))

    tag_resource_types = runner.invoke(cli, [*auth_options, 'tag', 'get-tag-resource-types'])
    tag_resource_types = mydict_data_factory('', loads(tag_resource_types.output))

    result = runner.invoke(cli, [*auth_options, 'tag', 'get-tag-member-count', '--id', tags.response[0].id,
                                 '--member_type', tag_resource_types.response[0], '--level', '0'])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_2e9db85840fbb1cf_v1_2_10').validate(obj) is None


@pytest.mark.tag
def test_updates_tag_membership(runner, cli, auth_options):
    tag_created = runner.invoke(cli, [*auth_options, 'tag', 'get-tag', '--name', 'InterestingTool01'])
    tag_created = mydict_data_factory('', loads(tag_created.output)).response[0].id

    device_list = runner.invoke(cli, [*auth_options, 'devices', 'get-device-list'])
    device_list = mydict_data_factory('', loads(device_list.output))
    key = device_list.response[0].id

    result = runner.invoke(cli, [*auth_options, 'tag', 'updates-tag-membership',
                                 '--membertotags', dumps({key: [tag_created]}),
                                 '--membertype', 'networkdevice',
                                 '--active_validation', False])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_45bc7a8344a8bc1e_v1_2_10').validate(obj) is None


@pytest.mark.tag
def test_add_members_to_the_tag(runner, cli, auth_options):
    tag_created = runner.invoke(cli, [*auth_options, 'tag', 'get-tag', '--name', 'InterestingTool01'])
    tag_created = mydict_data_factory('', loads(tag_created.output)).response[0].id

    device_list = runner.invoke(cli, [*auth_options, 'devices', 'get-device-list'])
    device_list = mydict_data_factory('', loads(device_list.output))

    result = runner.invoke(cli, [*auth_options, 'tag', 'add-members-to-the-tag', '--id', tag_created,
                                 '--payload', dumps({"networkdevice": [device_list.response[0].id]})])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_00a2fa6146089317_v1_2_10').validate(obj) is None


@pytest.mark.tag
def test_get_tag_members_by_id(runner, cli, auth_options):
    tag_created = runner.invoke(cli, [*auth_options, 'tag', 'get-tag', '--name', 'InterestingTool01'])
    tag_created = mydict_data_factory('', loads(tag_created.output)).response[0].id

    tag_resource_types = runner.invoke(cli, [*auth_options, 'tag', 'get-tag-resource-types'])
    tag_resource_types = mydict_data_factory('', loads(tag_resource_types.output))

    result = runner.invoke(cli, [*auth_options, 'tag', 'get-tag-members-by-id', '--id', tag_created,
                                 '--member_type', tag_resource_types.response[0], '--level', '0'])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_eab7abe048fb99ad_v1_2_10').validate(obj) is None


@pytest.mark.tag
def test_update_tag(runner, cli, auth_options):
    tag = runner.invoke(cli, [*auth_options, 'tag', 'get-tag', '--name', 'InterestingTool01'])
    tag = mydict_data_factory('', loads(tag.output)).response[0]

    result = runner.invoke(cli, [*auth_options, 'tag', 'update-tag', '--id', tag.id, '--name', '{} Updated'.format(tag.name)])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_4d86a993469a9da9_v1_2_10').validate(obj) is None


# @pytest.mark.tag
def test_remove_tag_member(runner, cli, auth_options):
    tag = runner.invoke(cli, [*auth_options, 'tag', 'get-tag', '--name', 'InterestingTool01'])
    tag = mydict_data_factory('', loads(tag.output)).response[0]

    device = runner.invoke(cli, [*auth_options, 'devices', 'get-device-list'])
    device = mydict_data_factory('', loads(device.output)).response[0]

    result = runner.invoke(cli, [*auth_options, 'tag', 'remove-tag-member', '--id', tag.id, '--member_id', device.id])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_caa3ea704d78b37e_v1_2_10').validate(obj) is None


@pytest.mark.tag
def test_delete_tag(runner, cli, auth_options):
    tag = runner.invoke(cli, [*auth_options, 'tag', 'get-tag', '--name', 'InterestingTool01'])
    tag = mydict_data_factory('', loads(tag.output)).response[0]

    result = runner.invoke(cli, [*auth_options, 'tag', 'delete-tag', '--id', tag.id])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_429c28154bdaa13d_v1_2_10').validate(obj) is None
