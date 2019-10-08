from enum import Enum
import json
import os
import shutil
import subprocess
import tempfile
import time

import boto3
from botocore.exceptions import ClientError
import click
import jinja2 as j2
import yaml

from halo import Halo
import virtualenv
import zipfile


command_settings = {
    'ignore_unknown_options': True,
}


class Actions(Enum):
    CREATE = 'create'
    REVIEW = 'review'
    DELETE = 'delete'
    UPDATE = 'update'
    MAKE_DIST = 'makedist'
    PUSH_DIST = 'pushdist'

    @classmethod
    def to_list(cls):
        return [x.lower() for x, _ in cls.__members__.items()]


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
SPINNER = Halo(spinner='dots')


def _zipdir(path, zipf):
    for root, dirs, files in os.walk(path):
        for file in files:
            zipf.write(
                os.path.join(root, file),
                os.path.relpath(
                    os.path.join(root, file), os.path.join(path, '.')))


def _upload_file(client, file_name, bucket, object_name=None):
    if object_name is None:
        object_name = file_name

    try:
        response = client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        click.echo(e)
        click.echo(response)
        return False
    return True


def _push_dist(appconf):
    node_conf = appconf['nodeconf']
    dist_zip = node_conf['node'].get('archive', 'dist.zip')

    session = boto3.Session(profile_name='dev')
    s3_client = session.client('s3')

    SPINNER.start('Uploading distribution')
    if not _upload_file(
            s3_client,
            dist_zip,
            node_conf['node']['bucket_name'],
            node_conf['node']['archive']):
        click.echo('Error uploading file')
        SPINNER.fail('Upload failed')
        return False
    SPINNER.succeed('Upload successful')
    os.remove(dist_zip)
    return True


def _make_zip(appconf):
    node_conf = appconf['nodeconf']
    venv_dir = os.path.join(os.getcwd(), '.venv')
    lib_dir = os.path.join(venv_dir, 'lib', 'python3.7', 'site-packages')
    script_file = node_conf.get('script', 'node.py')
    dist_zip = node_conf['node'].get('archive', 'dist.zip')

    SPINNER.start('Creating zip distribution')
    zipf = zipfile.ZipFile(dist_zip, 'w', zipfile.ZIP_DEFLATED)
    _zipdir(lib_dir, zipf)
    zipf.write(script_file)
    zipf.close()
    SPINNER.succeed('Distribution made successfully')


def _clean_temp_files(appconf):
    node_conf = appconf['nodeconf']
    venv_dir = os.path.join(os.getcwd(), '.venv')
    dist_zip = node_conf['node'].get('archive', 'dist.zip')

    SPINNER.start('Removing old files')
    if os.path.isfile(dist_zip):
        os.remove(dist_zip)
    if os.path.isdir(venv_dir):
        shutil.rmtree(venv_dir)
    SPINNER.succeed('Old files removed')


def _create_dist(appconf):
    venv_dir = os.path.join(os.getcwd(), '.venv')
    pip_exec = os.path.join(venv_dir, 'bin', 'pip')

    _clean_temp_files(appconf)

    SPINNER.start('Creating venv')
    virtualenv.create_environment(venv_dir)
    SPINNER.succeed('venv created')

    SPINNER.start('Installing requirements')
    subprocess.check_call([
        pip_exec, 'install', '-r', 'requirements.txt', '-I'],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    SPINNER.succeed('Installation successful')

    _make_zip(appconf)

    return True


def _gen_from_template(appconf, node, rendered_template):
    template = None
    fd, path = tempfile.mkstemp()
    try:
        with os.fdopen(fd, 'w') as tmp:
            tmp.write(rendered_template)
        cp = subprocess.run(
            ['cfndsl', '-b', '-y', node.name, path], text=True,
            check=True, capture_output=True)
        template = cp.stdout
    finally:
        os.remove(path)
    return template


def _review(appconf, node, rendered_template):
    template = _gen_from_template(appconf, node, rendered_template)
    click.echo(json.dumps(json.loads(template), indent=4, sort_keys=True))
    return True


def _stack_name(appconf):
    args = {'StackName': appconf['nodeconf']['stack_name']}
    return args


def _make_create_args(appconf, body):
    args = _stack_name(appconf)
    if body is not None:
        args['TemplateBody'] = body
    if 'create_args' in appconf['nodeconf']:
        args.update(appconf['nodeconf']['create_args'])
    return args


def _create(appconf, node, rendered_template):
    session = boto3.Session(profile_name='dev')
    cfn_client = session.client('cloudformation')
    template = _gen_from_template(appconf, node, rendered_template)
    response = cfn_client.validate_template(TemplateBody=template)
    if response['ResponseMetadata']['HTTPStatusCode'] >= 300:
        click.echo('Template failed')
        return False

    if not _create_dist(appconf) or not _push_dist(appconf):
        return False

    SPINNER.start('Creating stack')
    response = cfn_client.create_stack(**_make_create_args(appconf, template))
    if response['ResponseMetadata']['HTTPStatusCode'] >= 300:
        SPINNER.fail('Create failed')
        return False
    response = cfn_client.describe_stacks(**_stack_name(appconf))
    stack_id = response['Stacks'][0]['StackId']
    arg = {'StackName': stack_id}
    while(response['Stacks'][0]['StackStatus'] == 'CREATE_IN_PROGRESS'):
        time.sleep(5)
        response = cfn_client.describe_stacks(**arg)
    if response['Stacks'][0]['StackStatus'] != 'CREATE_COMPLETE':
        SPINNER.fail('Create failed in process')
        return False
    SPINNER.succeed('Create succeeded')
    return True


def _delete(appconf):
    session = boto3.Session(profile_name='dev')
    cfn_client = session.client('cloudformation')
    SPINNER.start('Deleting stack')
    response = cfn_client.delete_stack(**_stack_name(appconf))
    if response['ResponseMetadata']['HTTPStatusCode'] >= 300:
        SPINNER.fail('Delete failed')
        return False
    response = cfn_client.describe_stacks(**_stack_name(appconf))
    stack_id = response['Stacks'][0]['StackId']
    arg = {'StackName': stack_id}
    while(response['Stacks'][0]['StackStatus'] == 'DELETE_IN_PROGRESS'):
        time.sleep(5)
        response = cfn_client.describe_stacks(**arg)
    if response['Stacks'][0]['StackStatus'] != 'DELETE_COMPLETE':
        SPINNER.fail('Delete failed in process')
        return False
    SPINNER.succeed('Delete succeeded')
    return True


@click.command(context_settings=command_settings)
@click.argument(
    'action', type=click.Choice(Actions.to_list()))
@click.argument('node', type=click.File('rb'))
@click.option(
    '--appyaml', type=click.File('rb'),
    help='configuration for application',
    default=None)
@click.option(
    '--node-type', type=click.Choice(['node']),
    help='node type to fabricate',
    default='node')
@click.option(
    '--templates', type=click.Path('exists=True'),
    default=os.path.join(THIS_DIR, 'templates'),
    help='template directory')
@click.option(
    '--template-file',
    default='cfndsl.rb.j2',
    help='template file')
@click.option(
    '--profile',
    default='',
    help='profile to use')
@click.option(
    '--account-arn',
    default='',
    help='account arn to use')
def main(
        action, node, appyaml, node_type,
        templates, template_file, profile,
        account_arn):
    fd, path = tempfile.mkstemp(suffix='.yaml')
    if node.name.endswith('.py'):
        p = subprocess.run(['python', node.name], capture_output=True)
        y = yaml.load(p.stdout, Loader=yaml.FullLoader)
        with os.fdopen(fd, 'w') as tmp:
            yaml.dump(y, tmp, default_flow_style=False)
    else:
        shutil.copyfile(node.name, path)

    with open(path, 'r') as node_f:
        conf = yaml.load(node_f, Loader=yaml.FullLoader)

        start = time.time()
        appconf = {} if appyaml is None else yaml.load(
            appyaml, Loader=yaml.FullLoader)
        appconf['nodeconf'] = conf
        conf['acctarn'] = account_arn
        env = j2.Environment(
            loader=j2.FileSystemLoader(templates), trim_blocks=False)
        rendered_template = env.get_template(template_file).render(conf)
        action_enum = Actions[action.upper()]
        ret = False
        if action_enum == Actions.CREATE:
            ret = _create(appconf, node_f, rendered_template)
        elif action_enum == Actions.REVIEW:
            ret = _review(appconf, node_f, rendered_template)
        elif action_enum == Actions.DELETE:
            ret = _delete(appconf)
        elif action_enum == Actions.MAKE_DIST:
            ret = _create_dist(appconf)
        elif action_enum == Actions.PUSH_DIST:
            ret = _push_dist(appconf)
        else:
            click.echo('Unimplemented action')
        end = time.time()
        if action_enum != Actions.REVIEW:
            click.echo('Elapsed time: %f seconds' % (end - start))

    if path is not None:
        os.remove(path)

    if not ret:
        click.echo('Process failed')
        exit(1)


if __name__ == '__main__':
    main()
