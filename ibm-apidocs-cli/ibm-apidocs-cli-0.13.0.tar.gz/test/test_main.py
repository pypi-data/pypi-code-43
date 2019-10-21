# coding=utf-8

import os
import json
import re
import shutil
import subprocess
from ibm_apidocs_cli.main import get_basename, get_mapping, get_apidocs_dir, get_config_file, get_frontmatter_cli, get_frontmatter_templates, get_sdk_generator_cli, get_latest_sdk_version, create_frontmatter_config_file, create_frontmatter_md_file, create_language_specific_files, get_argument_parser, process_args, push_to_ghe


def test_get_basename_from_file():
    assert 'assistant-v1.json' == get_basename(
        '/home/geman/public/assistant-v1.json')
    assert 'assistant-v1.json' == get_basename('/assistant-v1.json')
    assert 'assistant-v1.json' == get_basename('assistant-v1.json')
    try:
        name = get_basename('')
        assert '%s should be None' % name
    except ValueError as identifier:
        pass


def test_get_mapping():
    assert get_mapping(
        './test/resources/mapping/generate-apidocs.json')['name'] == 'api-mapping'
    assert get_mapping(None)['name'] == 'api-mapping'


def test_get_push_apidocs_dir():
    if os.path.isdir('./test/target/personality-insights'):
        shutil.rmtree('./test/target/personality-insights')
    apidocs_dir = get_apidocs_dir(service_name='personality-insights', temp_dir=None, target='./test/target')
    assert os.path.isdir(apidocs_dir)
    with open(apidocs_dir+'/README.md', 'a') as f:
        f.write('Updating existing file')
    open(apidocs_dir+'/__test-new-file', 'a').close()
    push_to_ghe(openapi_file='openapi_file', apidocs_dir=apidocs_dir, service_name='personality-insights', test=True)
    git_diff = subprocess.check_output(['git', 'diff', '--name-only', 'HEAD~1'],
                                       universal_newlines=True,
                                       cwd=apidocs_dir).splitlines()
    assert len(git_diff) == 2
    assert 'README.md' in git_diff and '__test-new-file' in git_diff
    shutil.rmtree(apidocs_dir)


def test_get_config_file():
    assert get_config_file('assistant-v1-config.json',
                           'assistant-v1.json',
                           './test/resources/apidocs',
                           None) == './test/resources/apidocs/assistant-v1-config.json'
    with open('./test/resources/mapping/generate-apidocs.json') as f:
        mapping = json.load(f)
    assert get_config_file(None,
                           'assistant-v1.json',
                           './test/resources/apidocs',
                           mapping) == './test/resources/apidocs/assistant-v1-config.json'


def test_get_frontmatter_cli():
    cli = get_frontmatter_cli('./test/resources/frontmatter/', '')
    assert cli is not None
    assert cli.endswith('/test/resources/frontmatter/app.js')

    cli = get_frontmatter_cli(
        frontmatter=None, temp_dir='./test/target/fm_temp')
    assert cli is not None
    assert cli.endswith('/test/target/fm_temp/frontmatter/app.js')
    assert os.path.isfile('./test/target/fm_temp/frontmatter/app.js')
    shutil.rmtree('./test/target/fm_temp')


def test_get_frontmatter_templates():
    templates_dir = get_frontmatter_templates('./test/resources/frontmatter/app.js',
                                              'templates-dir',
                                              None,
                                              None)
    assert templates_dir == './test/resources/frontmatter/templates-dir'
    with open('./test/resources/mapping/generate-apidocs.json') as f:
        mapping = json.load(f)
    templates_dir = get_frontmatter_templates('./test/resources/frontmatter/app.js',
                                              None,
                                              'assistant-data-v1.json',
                                              mapping)
    assert templates_dir == './test/resources/frontmatter/templates-data'


def test_get_sdk_generator_cli():
    cli = get_sdk_generator_cli(sdk_generator='./test/resources/sdk-generator/run.jar',
                                sdkgen_release=None, mapping=None, temp_dir=None)
    assert cli is not None
    assert cli.endswith('/test/resources/sdk-generator/run.jar')

    with open('./test/resources/mapping/generate-apidocs.json') as f:
        mapping = json.load(f)
    cli = get_sdk_generator_cli(
        sdk_generator=None, sdkgen_release=None, mapping=mapping, temp_dir='./test/target')
    assert cli is not None
    assert cli.endswith('/test/target/openapi-sdkgen.jar')
    assert os.path.isfile('./test/target/openapi-sdkgen.jar')
    os.remove('./test/target/openapi-sdkgen.jar')

    cli = get_sdk_generator_cli(
        sdk_generator=None, sdkgen_release='1.0.0.1', mapping=None, temp_dir='./test/target')
    assert cli is not None
    assert cli.endswith('/test/target/openapi-sdkgen.jar')
    assert os.path.isfile('./test/target/openapi-sdkgen.jar')
    os.remove('./test/target/openapi-sdkgen.jar')


def test_get_latest_sdk_version():
    languages = ['java', 'node', 'python', 'ruby',
                 'go', 'swift', 'dotnet-standard', 'unity']
    for l in languages:
        sdk_ver = get_latest_sdk_version(l)
        assert re.match(r"[\d]+[\d.\.]*[\d]$", sdk_ver)


def test_create_frontmatter_config_file():
    languages = ['java', 'node', 'python', 'ruby', 'go', 'swift']
    create_frontmatter_config_file('./test/resources/apidocs/personality-insights-v3.json',
                                   './test/resources/apidocs/personality-insights-v3-config.json', languages, './test/target/personality-insights-v3-config.json')
    with open('./test/target/personality-insights-v3-config.json') as f:
        test_config = json.load(f)
    expected = ['publicUrls',
                'gatewayUrls',
                'serviceMajorVersion',
                'serviceName',
                'sdkName',
                'javaSdkVersion',
                'pythonSdkVersion',
                'swiftSdkVersion']
    assert set(expected).issubset(test_config.keys())


def test_create_frontmatter_md_file():
    create_frontmatter_md_file('./test/resources/frontmatter/app.js', './test/resources/apidocs/personality-insights-v3.json',
                               './test/target/personality-insights-v3-config.json', './test/target/personality-insights-v3.md')


def test_create_language_specific_files():
    languages = ['java', 'node', 'python', 'ruby', 'go', 'swift']
    create_language_specific_files('./test/resources/sdk-generator/run.jar', languages,
                                   './test/resources/apidocs/personality-insights-v3.json', './test/resources/apidocs/', './test/target', True)
    create_language_specific_files('./test/resources/sdk-generator/run.jar', languages,
                                   './test/resources/apidocs/personality-insights-v3.json', './test/resources/', './test/target', True)


def test_main():
    result = os.system('ibm-apidocs-cli --openapi ./test/resources/apidocs/personality-insights-v3.json \
                                      --apidocs ./test/resources/apidocs \
                                      --config personality-insights-v3-config.json \
                                      --output_folder ./test/target \
                                      --frontmatter ./test/resources/frontmatter \
                                      --sdk_generator ./test/resources/sdk-generator \
                                      --keep_sdk')
    assert result == 0

    result = os.system('ibm-apidocs-cli --batch --openapi ./test/resources/apidocs/*.json \
                                      --frontmatter ./test/resources/frontmatter \
                                      --sdk_generator ./test/resources/sdk-generator')
    assert result == 0
