import click
import pytest
from json import loads, dumps
from tests.environment import DNA_CENTER_VERSION
from tests.models.schema_validator import json_schema_validate
from dnacentersdk import mydict_data_factory
import time
from functools import reduce


pytestmark = pytest.mark.skipif(DNA_CENTER_VERSION != '1.2.10', reason='version does not match')


@pytest.mark.template_programmer
def test_gets_the_templates_available(runner, cli, auth_options):
    result = runner.invoke(cli, [*auth_options, 'template-programmer', 'gets-the-templates-available'])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_01b09a254b9ab259_v1_2_10').validate(obj) is None


@pytest.mark.template_programmer
def test_get_projects(runner, cli, auth_options):
    result = runner.invoke(cli, [*auth_options, 'template-programmer', 'get-projects'])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_109d1b4f4289aecd_v1_2_10').validate(obj) is None


@pytest.mark.template_programmer
def test_get_template_details(runner, cli, auth_options):
    templates_available = runner.invoke(cli, [*auth_options, 'template-programmer', 'gets-the-templates-available'])
    templates_available = mydict_data_factory('', loads(templates_available.output))

    projects = runner.invoke(cli, [*auth_options, 'template-programmer', 'get-projects'])
    projects = mydict_data_factory('', loads(projects.output))

    templateID = None
    if len(projects) > 0 and len(projects[0].templates) > 0:
        templateID = projects[0].templates[0].id
    if len(templates_available) > 0:
        templateID = templateID or templates_available[0].templateId

    result = runner.invoke(cli, [*auth_options, 'template-programmer', 'get-template-details', '--template_id', templateID])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_83a3b9404cb88787_v1_2_10').validate(obj) is None


@pytest.mark.template_programmer
def test_get_template_versions(runner, cli, auth_options):
    templates_available = runner.invoke(cli, [*auth_options, 'template-programmer', 'gets-the-templates-available'])
    templates_available = mydict_data_factory('', loads(templates_available.output))

    projects = runner.invoke(cli, [*auth_options, 'template-programmer', 'get-projects'])
    projects = mydict_data_factory('', loads(projects.output))

    templateID = None
    if len(projects) > 0 and len(projects[0].templates) > 0:
        templateID = projects[0].templates[0].id
    if len(templates_available) > 0:
        templateID = templateID or templates_available[0].templateId

    result = runner.invoke(cli, [*auth_options, 'template-programmer', 'get-template-versions', '--template_id', templateID])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_c8bf6b65414a9bc7_v1_2_10').validate(obj) is None


@pytest.mark.template_programmer
def test_create_project(runner, cli, auth_options):
    result = runner.invoke(cli, [*auth_options, 'template-programmer', 'create-project', '--name', 'test_project'])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_00aec9b1422ab27e_v1_2_10').validate(obj) is None


@pytest.mark.template_programmer
def test_create_template(runner, cli, auth_options):
    projects = runner.invoke(cli, [*auth_options, 'template-programmer', 'get-projects'])
    projects = mydict_data_factory('', loads(projects.output))
    filtered_project = list(filter(lambda x: x.name == 'test_project', projects))

    result = runner.invoke(cli, [*auth_options, 'template-programmer', 'create-template', '--project_id', filtered_project[0].id,
                                 '--composite', False,
                                 '--devicetypes', dumps({"productFamily": "Switches and Hubs"}),
                                 '--name', 'test_template',
                                 '--rollbacktemplatecontent', "",
                                 '--softwaretype', 'IOS-XE',
                                 '--softwarevariant', 'XE',
                                 '--templatecontent', 'show version\n'])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_f6b119ad4d4aaf16_v1_2_10').validate(obj) is None


@pytest.mark.template_programmer
def test_update_template(runner, cli, auth_options):
    projects = runner.invoke(cli, [*auth_options, 'template-programmer', 'get-projects'])
    projects = mydict_data_factory('', loads(projects.output))
    filtered_project = list(filter(lambda x: x.name == 'test_project', projects))

    template = runner.invoke(cli, [*auth_options, 'template-programmer', 'get-template-details', '--template_id', filtered_project[0].templates[0].id])
    template = mydict_data_factory('', loads(template.output))

    result = runner.invoke(cli, [*auth_options, 'template-programmer', 'update-template', '--composite', template.composite,
                                 *reduce(lambda a, b: a + b, [['--containingtemplates', x] for x in template.containingTemplates], []),
                                 *reduce(lambda a, b: a + b, [['--devicetypes', dumps(x)] for x in template.deviceTypes], []),
                                 '--id', template.id, '--name', template.name + '_updated', '--projectid', template.projectId,
                                 '--rollbacktemplatecontent', template.rollbackTemplateContent,
                                 *reduce(lambda a, b: a + b, [['--rollbacktemplateparams', x] for x in template.rollbackTemplateParams], []),
                                 '--softwaretype', template.softwareType,
                                 '--softwarevariant', template.softwareVariant,
                                 '--templatecontent', template.templateContent,
                                 *reduce(lambda a, b: a + b, [['--templateparams', x] for x in template.templateParams], [])])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_7781fa0548a98342_v1_2_10').validate(obj) is None


@pytest.mark.template_programmer
def test_update_project(runner, cli, auth_options):
    projects = runner.invoke(cli, [*auth_options, 'template-programmer', 'get-projects'])
    projects = mydict_data_factory('', loads(projects.output))
    filtered_project = list(filter(lambda x: x.name == 'test_project', projects))

    result = runner.invoke(cli, [*auth_options, 'template-programmer', 'update-project', '--id', filtered_project[0].id,
                                 '--name', filtered_project[0].name + '_updated'])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_9480fa1f47ca9254_v1_2_10').validate(obj) is None


@pytest.mark.template_programmer
def test_version_template(runner, cli, auth_options):
    projects = runner.invoke(cli, [*auth_options, 'template-programmer', 'get-projects'])
    projects = mydict_data_factory('', loads(projects.output))
    filtered_project = list(filter(lambda x: x.name == 'test_project_updated', projects))

    template = runner.invoke(cli, [*auth_options, 'template-programmer', 'get-template-details', '--template_id', filtered_project[0].templates[0].id])
    template = mydict_data_factory('', loads(template.output))

    result = runner.invoke(cli, [*auth_options, 'template-programmer', 'version-template', '--templateid', template.id])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_62b05b2c40a9b216_v1_2_10').validate(obj) is None


@pytest.mark.template_programmer
def test_preview_template(runner, cli, auth_options):
    projects = runner.invoke(cli, [*auth_options, 'template-programmer', 'get-projects'])
    projects = mydict_data_factory('', loads(projects.output))
    filtered_project = list(filter(lambda x: x.name == 'test_project_updated', projects))

    template = runner.invoke(cli, [*auth_options, 'template-programmer', 'get-template-details', '--template_id', filtered_project[0].templates[0].id])
    template = mydict_data_factory('', loads(template.output))

    result = runner.invoke(cli, [*auth_options, 'template-programmer', 'preview-template', '--templateid', template.id])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_f393abe84989bb48_v1_2_10').validate(obj) is None


@pytest.mark.template_programmer
def test_deploy_template(runner, cli, auth_options):
    projects = runner.invoke(cli, [*auth_options, 'template-programmer', 'get-projects'])
    projects = mydict_data_factory('', loads(projects.output))
    filtered_project = list(filter(lambda x: x.name == 'test_project_updated', projects))

    template = runner.invoke(cli, [*auth_options, 'template-programmer', 'get-template-details', '--template_id', filtered_project[0].templates[0].id])
    template = mydict_data_factory('', loads(template.output))

    device_list = runner.invoke(cli, [*auth_options, 'devices', 'get-device-list',
                                      '--family', template.deviceTypes[0].productFamily,
                                      '--software_type', template.softwareType])
    device_list = mydict_data_factory('', loads(device_list.output)).response

    targetInfoList = [['--targetinfo', dumps({'id': t.managementIpAddress, 'type': 'MANAGED_DEVICE_IP', 'params': {}})] for t in device_list]

    result = runner.invoke(cli, [*auth_options, 'template-programmer', 'deploy-template',
                                 '--forcepushtemplate', True, '--iscomposite', template.composite,
                                 '--maintemplateid', template.parentTemplateId,
                                 *reduce(lambda a, b: a + b, targetInfoList),
                                 '--templateid', template.id])
    assert not result.exception
    obj_dt = loads(result.output)
    assert json_schema_validate('jsd_6099da82477b858a_v1_2_10').validate(obj_dt) is None

    time.sleep(10)
    deploymentID = mydict_data_factory('', obj_dt).deploymentId.split(" ")[-1]
    result = runner.invoke(cli, [*auth_options, 'template-programmer', 'get-template-deployment-status', '--deployment_id', deploymentID])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_9c9a785741cbb41f_v1_2_10').validate(obj) is None


@pytest.mark.template_programmer
def test_delete_template(runner, cli, auth_options):
    projects = runner.invoke(cli, [*auth_options, 'template-programmer', 'get-projects'])
    projects = mydict_data_factory('', loads(projects.output))
    filtered_project = list(filter(lambda x: x.name == 'test_project_updated', projects))

    template = runner.invoke(cli, [*auth_options, 'template-programmer', 'get-template-details', '--template_id', filtered_project[0].templates[0].id])
    template = mydict_data_factory('', loads(template.output))

    result = runner.invoke(cli, [*auth_options, 'template-programmer', 'delete-template', '--template_id', template.id])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_a7b42836408a8e74_v1_2_10').validate(obj) is None


@pytest.mark.template_programmer
def test_delete_project(runner, cli, auth_options):
    projects = runner.invoke(cli, [*auth_options, 'template-programmer', 'get-projects'])
    projects = mydict_data_factory('', loads(projects.output))
    filtered_project = list(filter(lambda x: x.name == 'test_project_updated', projects))

    result = runner.invoke(cli, [*auth_options, 'template-programmer', 'delete-project', '--project_id', filtered_project[0].id])
    assert not result.exception
    if result.output.strip():
        obj = loads(result.output)
        assert json_schema_validate('jsd_d0a1abfa435b841d_v1_2_10').validate(obj) is None
