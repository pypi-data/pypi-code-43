# coding=utf-8
from __future__ import print_function
import os
import argparse
import base64
import json
import logging
import requests
import shutil
import tempfile
import subprocess
from collections import OrderedDict
from ibm_apidocs_cli.version import __version__
from lxml import html
from outdated import warn_if_outdated

logger = logging.getLogger(__name__)


def get_argument_parser():
    """
    generate a CLI arguments parser
    Returns:
       argument parser
    """
    parser = argparse.ArgumentParser(description='Generate the apidocs files.')
    # required parameters
    requiredArgs = parser.add_argument_group('Required arguments')
    requiredArgs.add_argument(
        '-i', '--openapi', nargs='+', metavar='input-oas', help='Input OpenAPI specification file path or url', required=True)
    # Optional parameters
    optionalArgs = parser._action_groups.pop()
    parser.add_argument('-b', '--batch', action='store_true', help='Run in batch mode')
    parser.add_argument('-c', '--config', metavar='config-file', help='Name of front matter config file')
    parser.add_argument('--mapfile', metavar='map-file', help='Path to mapping file')
    parser.add_argument('--apidocs', metavar='apidocs-dir', help='Path to apidocs repository containing config files. Default is current directory.')
    parser.add_argument('--templates', metavar='templates-dir', help='Path to directory containing custom front matter templates.')
    parser.add_argument('--output_folder', metavar='output-folder', help='Output folder for generated files (manual mode only)')
    parser.add_argument('--target', metavar='target', help='Parent of target cloud-api-docs directories (batch mode only)')
    parser.add_argument('--frontmatter', metavar='frontmatter-cli', help='Frontmatter repository or local CLI')
    parser.add_argument('--sdk_generator', metavar='sdkgen-jar', help='Path to location of SDK generator JAR file')
    parser.add_argument('--sdkgen_release', metavar='sdkgen-release', help='Release of SDK generator to download')
    parser.add_argument('--push', action='store_true', help='Push updated apidocs repos to GHE after generating')
    parser.add_argument('--keep_sdk', action='store_true', help='Keep generated SDK files')
    parser.add_argument('--keep_temp', action='store_true', help='Keep temp directory')
    parser.add_argument('--no_update', action='store_true', help='Do not update SDK versions in front matter config')
    parser.add_argument('--verbose', action='store_true', help='verbose flag')
    parser.add_argument('--version', action='version',
                        version='%(prog)s {version}'.format(version=__version__))

    parser._action_groups.append(optionalArgs)
    return parser


def process_args(parser):
    """
    Parses the parser
    Returns:
        dict -- dictionary with the arguments and values
    """
    args = parser.parse_args()

    # validate environment
    if 'throw' in args:
        logger.error(args.throw)
        exit(1)

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    return args


def main():
    parser = get_argument_parser()
    args = process_args(parser)

    if args.batch:
        if args.output_folder:
            raise ValueError('--output_folder not valid in batch mode. Use --target to write output to local cloud-api-docs repos.')
        if args.config:
            raise ValueError('--config not valid in batch mode. The config file for each API definition must be specified in map file.')
        if args.apidocs:
            raise ValueError('--apidocs not valid in batch mode. Use --target to specify location of local cloud-api-docs repos, or omit to automatically download based on the service names specified in the map file.')
        if args.templates:
            raise ValueError('--templates not valid in batch mode. The front-matter templates for each API definition must be specified in the map file.')
    else:
        if len(args.openapi) >> 1:
            raise ValueError('Multiple input files not valid in manual mode. Use batch mode to process multiple API definitions.')
        if args.target:
            raise ValueError('--target not valid in manual mode. Use --output_folder to specify location for generated files, or --apidocs to specify location of local cloud-api-docs repo.')
        if args.push:
            raise ValueError('--push not valid in manual mode. Use batch mode to push generated files to GHE.')

    temp_dir = tempfile.mkdtemp()

    get_mapfile = any([not args.config,
                       not (args.sdk_generator or args.sdkgen_release),
                       not args.templates,
                       args.batch])

    # Global values
    if get_mapfile:
        mapping = get_mapping(args.mapfile)
    else:
        mapping = None
    frontmatter_cli = get_frontmatter_cli(args.frontmatter, temp_dir)
    sdk_generator_cli = get_sdk_generator_cli(args.sdk_generator, args.sdkgen_release, mapping, temp_dir)

    for openapi in args.openapi:

        openapi_abs = os.path.abspath(openapi)
        openapi_file = get_basename(openapi)

        if args.batch:

            if not openapi_file in [d['openapi'] for d in mapping['public']+mapping['private']]:
                logger.info('Skipping %s (not found in mapping file).', openapi_file)
                continue
            else:
                logger.info('Processing %s...', openapi_file)

            service_name = next(item for item in mapping['public']+mapping['private'] if item['openapi']==openapi_file)['service']
            logger.info('Service name: %s', service_name)

            apidocs_dir = get_apidocs_dir(service_name=service_name, temp_dir=temp_dir, target=args.target)

            if args.target:
                output_folder_abs = os.path.abspath(os.path.join(args.target, service_name))
            else:
                output_folder_abs = apidocs_dir

        else:

            if args.output_folder:
                output_folder_abs = os.path.abspath(args.output_folder)
            else:
                output_folder_abs = os.getcwd()

            if args.apidocs:
                apidocs_dir = os.path.abspath(args.apidocs)
            else:
                apidocs_dir = os.getcwd()

            service_name = None

        templates_dir = get_frontmatter_templates(frontmatter_cli, args.templates, openapi_file, mapping)

        input_frontmatter_config = get_config_file(args.config, openapi_file, apidocs_dir, mapping)

        output_frontmatter_config = os.path.join(output_folder_abs, os.path.basename(input_frontmatter_config))

        frontmatter_md_file = os.path.join(output_folder_abs, os.path.splitext(openapi_file)[0])+'.md'

        logger.info('frontmatter_cli: %s', frontmatter_cli)
        logger.info('sdk_generator_cli: %s', sdk_generator_cli)

        process_openapi_file(openapi_file=openapi_abs, frontmatter_cli=frontmatter_cli, sdk_generator_cli=sdk_generator_cli,
                             templates_dir=templates_dir, output_folder=output_folder_abs, apidocs_dir=apidocs_dir,
                             service_name=service_name, input_frontmatter_config=input_frontmatter_config,
                             output_frontmatter_config=output_frontmatter_config, no_update=args.no_update,
                             frontmatter_md_file=frontmatter_md_file, keep_sdk=args.keep_sdk, push=args.push)

    if not args.keep_temp:
        logger.info('Removing temporary directory %s', temp_dir)
        shutil.rmtree(temp_dir)

def process_openapi_file(openapi_file=None, frontmatter_cli=None, sdk_generator_cli=None, templates_dir=None, output_folder=None, apidocs_dir=None, service_name=None, input_frontmatter_config=None, output_frontmatter_config=None, no_update=None, frontmatter_md_file=None, keep_sdk=None, push=None):

    supported_languages = get_supported_languages(openapi_file)

    logger.info('Processing openapi_file: %s', openapi_file)
    logger.info('Front-matter config_file: %s', input_frontmatter_config)
    logger.info('Front-matter templates directory: templates_dir: %s', templates_dir)
    logger.info('Supported_languages: %s', supported_languages)

    if not os.path.exists(output_folder):
        logger.info('Creating output directory %s', output_folder)
        os.makedirs(output_folder)

    if not os.path.dirname(openapi_file) == os.path.normpath(output_folder):
        logger.info('Copying %s file to output directory', openapi_file)
        shutil.copyfile(openapi_file, os.path.join(output_folder, get_basename(openapi_file)))

    logger.info('Creating the frontmatter configuration')
    create_frontmatter_config_file(openapi_file=openapi_file, input_config_file=input_frontmatter_config,
                                   supported_languages=supported_languages, output_config_file=output_frontmatter_config,
                                   no_update=no_update)

    logger.info('Calling frontmatter to generate the md file')
    logger.info('With %s', templates_dir)
    create_frontmatter_md_file(frontmatter_cli=frontmatter_cli, openapi_file=openapi_file,
                               frontmatter_config_file=output_frontmatter_config, output_file=frontmatter_md_file,
                               templates_dir=templates_dir)

    logger.info('Creating language specific middle panel')
    create_language_specific_files(sdk_generator_cli=sdk_generator_cli, supported_languages=supported_languages,
                                   openapi_file=openapi_file, apidocs_folder=apidocs_dir, output_folder=output_folder,
                                   keep_sdk=keep_sdk)

    if push:
        logger.info('Pushing updated files from %s to cloud-api-docs/%s', apidocs_dir, service_name)
        push_to_ghe(openapi_file=openapi_file, apidocs_dir=apidocs_dir, service_name=service_name, test=False)


def get_mapping(mapfile=None):
    '''If required, loads the API definition mapping file from the specified location, or from GitHub.'''

    if mapfile:
        with open(mapfile) as f:
            mapping = json.load(f)
        logger.info('Loaded map file from %s', mapfile)
    else:
        github_token = os.environ.get('GITHUB_TOKEN')
        if not github_token:
            raise ValueError('Cannot download map file without GitHub token. Either set GITHUB_TOKEN or specify local map file.')
        mapfile_url = 'https://api.github.ibm.com/repos/Watson/developer-cloud--api-definitions/contents/generate-apidocs.json'
        r = requests.get(mapfile_url,
                         headers={'Authorization': 'token '+github_token})
        r.raise_for_status()

        mapping = json.loads(base64.b64decode(r.json()['content']).decode())

        logger.info('Loaded map file from %s', mapfile_url)

    return mapping


def get_apidocs_dir(service_name=None, temp_dir=None, target=None):
    '''Download cloud-api-docs repo for the service to a temporary directory for batch-mode
       processing.

      Arguments:
      service_name {String} -- Service name, also name of apidocs repo
      temp_dir {String} -- Base temporary directory
      target {String} -- Optional target directory
    '''

    github_token = os.environ.get('GITHUB_TOKEN')
    if not github_token:
        raise ValueError('Cannot download cloud-api-docs repo without GitHub token. Either set GITHUB_TOKEN or use manual mode.')
    if target:
        apidocs_dir = os.path.join(os.path.abspath(target), service_name)
    else:
        apidocs_dir = os.path.join(temp_dir, 'cloud-api-docs', service_name)
    if not os.path.isdir(apidocs_dir):
        logger.info('Cloning cloud-api-docs repo to %s', apidocs_dir)
        subprocess.call(['git',
                         'clone',
                         'https://'+github_token+'@github.ibm.com/cloud-api-docs/'+service_name+'.git',
                         apidocs_dir])
    return apidocs_dir


def get_config_file(config_file=None, openapi_file=None, apidocs_dir=None, mapping=None):
    '''Get config file name either from command-line argument or from mapping file.'''

    if not config_file:
        config_filename = next(item for item in mapping['public']+mapping['private'] if item['openapi']==openapi_file)['config']
        config_file = os.path.join(apidocs_dir, config_filename)
        logger.info('Looked up config file: %s', config_file)

    if os.path.dirname(config_file) == '':
        config_file = os.path.join(apidocs_dir, config_file)

    return config_file

def get_basename(filepath):
    '''Returns the basename of the given filepath without the file extension'''

    if not filepath:
        raise ValueError('openapi file path cannot be null or empty')
    basename = os.path.basename(filepath)
    return basename

def get_frontmatter_cli(frontmatter, temp_dir):
    '''Returns the absolute path to the frontmatter app.js file

    Arguments:
      sdk_generator {String} -- The path to the app.js file or the folder where the app.js file is
      temp_dir {String} -- The path to the temp directory, used to clone the repo if necessary

    Raises:
      ValueError -- if the given path doesn't exist

    Returns:
      String -- The absolute file path to the frontmatter app.js file
    '''

    if not frontmatter:
        github_token = os.environ.get('GITHUB_TOKEN')
        if not github_token:
            raise ValueError('Cannot download front-matter generator without GitHub token. Either set GITHUB_TOKEN or specify front-matter generator location.')
        frontmatter = os.path.join(temp_dir, 'frontmatter')
        logger.info('Cloning front-matter generator to %s', frontmatter)
        subprocess.call(['git',
                         'clone',
                         'https://'+github_token+'@github.ibm.com/cloud-doc-build/frontmatter-generator.git',
                         frontmatter])
        subprocess.call(['npm',
                         'install',
                         '--prefix',
                         frontmatter])

    cli = os.path.join(os.path.abspath(frontmatter), 'app.js')
    logger.info('Using front-matter CLI at %s', cli)

    if not os.path.exists(cli):
        raise ValueError('Front-matter generator not found at %s.' % cli)

    return cli

def get_frontmatter_templates(frontmatter_cli=None, templates=None, openapi_file=None, mapping=None):
    '''Returns the absolute path to the frontmatter templates to use.

    Arguments:
      frontmatter {String} -- The path to the frontmatter generator being used
      custom_templates {String} -- The path to the custom templates, if specified
    '''
    if not templates:
        logger.info('Looking up front-matter templates directory in mapping file.')
        if not openapi_file in [d['openapi'] for d in mapping['public']+mapping['private']]:
            raise ValueError('%s not found in mapping file.' % openapi_file)
        templates = next(item for item in mapping['public']+mapping['private'] if item['openapi'] == openapi_file)['frontmatter']
    if os.path.isabs(templates):
        return templates
    else:
        return os.path.join(os.path.dirname(frontmatter_cli), templates)

def get_sdk_generator_cli(sdk_generator=None, sdkgen_release=None, mapping=None, temp_dir=None):
    '''Returns the absolute path to the SDK generator JAR file. If a local JAR 
    file was not specified, the SDK generator JAR file is loaded from the
    specified sdkgen release. If no sdkgen release was specified, the latest
    maintenance release is determined based on the major release configured in
    the map file.

    Arguments:
      sdk_generator {String} -- The path to the jar file or the folder where the jar file is
      sdkgen_release {String} -- The release of the SDK generator to download
      mapping - Contents of the map file, if loaded
      temp_dir {String} -- The path to the temp directory, used to download the jar file if necessary

    Raises:
      ValueError -- if the given path doesn't exist or no matching release is found

    Returns:
      String -- The absolute file path to the SDK Generator jar file
    '''

    if not sdk_generator:
        github_token = os.environ.get('GITHUB_TOKEN')
        if not github_token:
            raise ValueError('Cannot download SDK generator without GitHub token. Either set GITHUB_TOKEN or specify SDK generator JAR file location.')
        if not sdkgen_release:
            sdkgen_major_release = mapping['sdkgen_major_release']
            sdkgen_url = 'https://api.github.ibm.com/repos/CloudEngineering/openapi-sdkgen/releases'
            r = requests.get(sdkgen_url,
                             headers={'Authorization': 'token '+github_token})
            r.raise_for_status()
            sdkgen_releases_response = json.loads(r.text)
            all_releases = [rel['tag_name'] for rel in sdkgen_releases_response]
            maint_releases = [rel for rel in all_releases if rel.startswith(sdkgen_major_release+'.') and '-rc' not in rel]
            if not maint_releases:
                raise ValueError('No public releases found for sdkgen major release %s' % sdkgen_major_release)
            maint_releases.sort(key=lambda s: list(map(int, s.split('.'))))
            sdkgen_release = maint_releases[-1]
            logger.info('sdkgen major release: %s', sdkgen_major_release)
            logger.info('sdkgen maintenance release: %s', sdkgen_release)

        sdkgen_release_url = 'https://api.github.ibm.com/repos/CloudEngineering/openapi-sdkgen/releases/tags/'+sdkgen_release
        r = requests.get(sdkgen_release_url,
                         headers={'Authorization': 'token '+github_token})
        r.raise_for_status()
        sdkgen_release = json.loads(r.text)
        sdkgen_jar = 'openapi-sdkgen-'+sdkgen_release['tag_name']+'.jar'

        logger.info('Downloading SDK generator JAR file %s', sdkgen_jar)

        r = requests.get(sdkgen_release['assets_url'],
                         headers={'Authorization': 'token '+github_token})
        sdkgen_assets = json.loads(r.text)

        jar_asset = next((i for i in sdkgen_assets if i['name'] == sdkgen_jar), None)

        r = requests.get(jar_asset['url'],
                         headers={'Authorization': 'token '+github_token,
                                  'Accept': 'application/octet-stream'}
                        )
        with open(os.path.join(temp_dir, 'openapi-sdkgen.jar'), 'wb') as f:
            f.write(r.content)

        sdk_generator = temp_dir

    if os.path.isdir(sdk_generator):
        cli = os.path.abspath(os.path.join(sdk_generator, 'openapi-sdkgen.jar'))
    else:
        cli = os.path.abspath(sdk_generator)

    if os.path.isdir(sdk_generator):
        cli = os.path.abspath(os.path.join(sdk_generator, 'openapi-sdkgen.jar'))
    else:
        cli = os.path.abspath(sdk_generator)

    if not os.path.isfile(cli):
        raise ValueError('Could not find SDK generator JAR at %s' % sdk_generator)

    return cli

def get_supported_languages(openapi_file=None):
    '''
    Generates the list of supported languages to be used by the SDK generator.
    The list is derived from the x-sdk-supported-languages in the OAS API definition file

    Arguments:
      openapi_file {String} -- The name of the OAS API definition file

    Raises:
      ValueError -- if a required file cannot be found or parsed

    Returns:
      String -- The array of supported languages
    '''

    with open(openapi_file) as f:
        openapi = json.load(f)

    if 'x-sdk-supported-languages' in openapi['info']:
        supported_languages = openapi['info']['x-sdk-supported-languages']
    else:
        supported_languages = []

    return supported_languages


def get_latest_sdk_version(language):
    '''
    Performs an HTTP GET to retrieve the GitHub release page for the latest
    SDK release for the specified language, and parses the returned HTML to
    find the release number.

    Arguments:
      language {String} -- The name of the SDK language (for example, "java").

    Raises:
      RuntimeError -- If the version number cannot be identified from the page

    Returns:
      String -- The version number (for example, "2.1").
    '''
    url = 'https://github.com/watson-developer-cloud/' + \
        language + '-sdk/releases/latest'
    page = html.fromstring(requests.get(url).content)

    matches = page.xpath(r"//div[@class='release-header'][1]//a[re:match(text(), '^[a-zA-Z\-]*[\d.]+$')]",
                         namespaces={"re": "http://exslt.org/regular-expressions"})

    if matches:
        if matches[0].text[0] == 'v':
            sdk_ver = matches[0].text[1:]
        elif matches[0].text.startswith('java-sdk-'):
            sdk_ver = matches[0].text[9:]
        else:
            sdk_ver = matches[0].text
    else:
        raise RuntimeError(
            'Latest SDK version for %s not found in expected format' % language)

    return sdk_ver


def create_frontmatter_config_file(openapi_file=None, input_config_file=None, supported_languages=None, output_config_file=None, no_update=False):
    '''
    Generates the config file that will be used for front matter generation.
    Any value specified in the input YAML config will be passed through
    as-is. Other values (if required) are derived from the OAS file or
    queried from GitHub.

    Arguments:
      openapi_file {String} -- The name of the OAS API definition file
      config_file {String} -- The name of the input config YAML file
      supported_languages {String} -- The supported languages from the OAS API definition file
      output_file {String} -- The name of the generated front matter config file
      no_update {boolean} -- Uses the input config as-is without updating SDK versions

    Raises:
      ValueError -- if a required file cannot be found or parsed

    '''

    with open(input_config_file) as f:
        input_fm_config = json.load(f, object_pairs_hook=OrderedDict)
    with open(openapi_file) as f:
        openapi = json.load(f)

    output_fm_config = OrderedDict(input_fm_config.items())
    if 'serviceMajorVersion' not in output_fm_config:
        output_fm_config['serviceMajorVersion'] = openapi['info']['version'].split('.')[
            0]

    if not no_update:
        for l in supported_languages:
            output_fm_config[l+'SdkVersion'] = get_latest_sdk_version(l)

    with open(output_config_file, 'w') as f:
        json.dump(output_fm_config, f, indent=2, separators=(',', ': '))


def create_frontmatter_md_file(frontmatter_cli=None, openapi_file=None, frontmatter_config_file=None, output_file=None, templates_dir=None):
    '''
    Generates the Markdown source file (md) file from the front matter config file generated
    in the previous step.  Assumes the frontmatter-generator repository has been downloaded and
    is accessible to enable the call to app.js to execute properly.

    Arguments:
      frontmatter_cli {String} -- The name of the frontmatter app.js file
      openapi_file {String} -- The name of the OAS API definition file
      frontmatter_config_file {String} -- The name of the generated front matter config file
      output_file {String} -- The name of the generated md file

    Raises:
      ValueError -- if a required file cannot be found or parsed
    '''

    logger.info('\n')
    logger.info('frontmatter_cli: %s', frontmatter_cli)
    logger.info('openapi_file: %s', openapi_file)
    logger.info('frontmatter_config_file: %s', frontmatter_config_file)
    logger.info('output_file: %s', output_file)

    fg_command = "node %s -i %s -c %s -t %s -o %s" % (
        frontmatter_cli, openapi_file, frontmatter_config_file, templates_dir, output_file)

    working_directory = os.path.dirname(frontmatter_cli)
    logger.info('frontmatter generator command: %s', fg_command)
    logger.info('frontmatter generator location: %s', working_directory)
    logger.info('custom frontmatter templates location: %s', templates_dir)

    subprocess.call(fg_command, shell=True, cwd=working_directory)


def create_language_specific_files(sdk_generator_cli=None, supported_languages=None, openapi_file=None, apidocs_folder=None, output_folder=None, keep_sdk=False):
    '''
    Generates the middle panel for all supported languages.  Assumes the SDK generator (openapi-sdkgen) release directory has been
    downloaded and is accessible to enable the call to openapi-sdkgen.sh to execute properly.

    Arguments:
      sdk_generator_cli {String} -- The name of the sdk generator shell script
      supported_languages {String} -- The supported languages from the OAS API definition file
      openapi_file {String} -- The name of the OAS API definition file
      output_folder {String} -- The name of the folder where the middle column for each language will be written
      keep_sdk {boolean} -- Whether to keep the generated SDK files for debugging purposes

    Raises:
      ValueError -- if a required file cannot be found or parsed
    '''

    logger.info('\n')
    logger.info('sdk_generator_cli: %s', sdk_generator_cli)
    logger.info('supported_languages: %s', supported_languages)
    logger.info('openapi_file: %s', openapi_file)
    logger.info('apidocs_folder: %s', apidocs_folder)
    logger.info('output_folder: %s', output_folder)

    working_directory = os.path.dirname(sdk_generator_cli)
    logger.info('SDK generator location: %s', working_directory)

    index_file = os.path.join(apidocs_folder, 'apiref-index.json')
    if os.path.isfile(index_file):
        with open(index_file) as f:
            apiref_index = json.load(f)
    else:
        logger.warning('apiref-index.json not found.')
        apiref_index = {}

    for sdk in supported_languages:
        watson_sdk = 'watson-' + sdk
        oas_filename = os.path.basename(openapi_file)
        if oas_filename in apiref_index:
            if sdk in apiref_index[oas_filename]:
                target_filename = apiref_index[oas_filename][sdk]
            else:
                target_filename = sdk + '-apiref.json'
                logger.warning('Language %s not found in apiref-index.json. Using default file name %s.', sdk, target_filename)
        else:
            target_filename = sdk + '-apiref.json'
            logger.warning('%s not found in apiref-index.json. Using default file name %s.', oas_filename, target_filename)
        sdk_temp = os.path.join(output_folder, '_sdktemp')
        sdk_command = "java -jar %s generate -i %s -g %s -o %s --apiref %s" % (
            sdk_generator_cli, openapi_file, watson_sdk, sdk_temp, os.path.join(output_folder, target_filename))
        logger.info('SDK generator command: %s', sdk_command)
        subprocess.call(sdk_command, shell=True, cwd=working_directory)
        if not keep_sdk:
            logger.info('Deleting SDK artifacts directory %s', sdk_temp)
            shutil.rmtree(sdk_temp)

def push_to_ghe(openapi_file=None, apidocs_dir=None, service_name=None, test=None):
    '''Push cloud-api-docs repo for the service to GHE.

       Arguments:
       apidocs_dir {String} -- Path to the location of the local clone of the repo to push.

       service_name {String} -- Name of cloud-api-docs repo for the service.

       test {Boolean} -- Whether to use --dry-run option (used by unit test)
    '''

    github_token = os.environ.get('GITHUB_TOKEN')
    if not github_token:
        raise ValueError('Cannot push cloud-api-docs repo without GitHub token. Either set GITHUB_TOKEN or omit --push argument.')

    subprocess.call(['git',
                     'add',
                     '--all'],
                     cwd=apidocs_dir)
    
    subprocess.call(['git', 'commit', '--all',
                     '--message=ibm-apidocs-cli: build '+os.path.basename(openapi_file)],
                     cwd=apidocs_dir)
    
    subprocess.call(['git',
                     'push',
                     'https://'+github_token+'@github.ibm.com/cloud-api-docs/'+service_name,
                     'master'] +  (['--dry-run'] if test else []),
                     cwd=apidocs_dir)