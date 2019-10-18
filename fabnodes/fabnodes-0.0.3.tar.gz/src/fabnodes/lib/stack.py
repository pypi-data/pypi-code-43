import os
import shutil
import subprocess
import tempfile
import time

import boto3

from halo import Halo
import virtualenv

from fabnodes.lib import filesystem as fs


SPINNER = Halo(spinner='dots')


def _make_zip(appconf):
    node_conf = appconf['nodeconf']
    venv_dir = os.path.join(os.getcwd(), '.venv')
    lib_dir = os.path.join(venv_dir, 'lib', 'python3.7', 'site-packages')
    script_file = node_conf.get('script', 'node.py')
    dist_zip = node_conf['node'].get('archive', 'dist.zip')

    SPINNER.start('Creating zip distribution')
    fs.make_zip(dist_zip, lib_dir, [script_file])
    SPINNER.succeed('Distribution made successfully')
    return True


def _clean_temp_files(appconf):
    node_conf = appconf['nodeconf']
    venv_dir = os.path.join(os.getcwd(), '.venv')
    dist_zip = node_conf['node'].get('archive', 'dist.zip')

    SPINNER.start('Removing old/temp files')
    if os.path.isfile(dist_zip):
        os.remove(dist_zip)
    if os.path.isdir(venv_dir):
        shutil.rmtree(venv_dir)
    SPINNER.succeed('Old/Temp files removed')
    return True


class CFNDSLError(Exception):
    pass


def _gen_from_template(appconf, node, rendered_template):
    template = None
    fd, path = tempfile.mkstemp()
    try:
        with os.fdopen(fd, 'w') as tmp:
            tmp.write(rendered_template)
        cp = subprocess.run(
            ['cfndsl', '-b', '-y', node.name, path], text=True,
            capture_output=True)
        if cp.returncode != 0:
            raise CFNDSLError('Error in cfndsl process: %s' % cp.stderr)
        template = cp.stdout
    finally:
        os.remove(path)
    return template


def _stack_name(appconf):
    args = {'StackName': appconf['nodeconf']['stack_name']}
    return args


def _make_create_args(appconf, body):
    args = _stack_name(appconf)
    if '"Type":"AWS::IAM::' in body:
        args['Capabilities'] = ['CAPABILITY_IAM']
    if body is not None:
        args['TemplateBody'] = body
    if 'create_args' in appconf['nodeconf']:
        args.update(appconf['nodeconf']['create_args'])
    return args


def _validate_template(appconf, node, rendered_template):
    session = boto3.Session(profile_name=appconf['profile'])
    cfn_client = session.client('cloudformation')
    template = _gen_from_template(appconf, node, rendered_template)
    response = cfn_client.validate_template(TemplateBody=template)
    if response['ResponseMetadata']['HTTPStatusCode'] >= 300:
        return False
    return True


def _wait_for_stack_state(appconf, expected_state, goal_state):
    session = boto3.Session(profile_name=appconf['profile'])
    cfn_client = session.client('cloudformation')
    response = cfn_client.describe_stacks(**_stack_name(appconf))
    stack_id = response['Stacks'][0]['StackId']
    arg = {'StackName': stack_id}

    SPINNER.start('Waiting stack state change: %s -> %s' % (
        expected_state, goal_state))
    while(response['Stacks'][0]['StackStatus'] == expected_state):
        time.sleep(5)
        response = cfn_client.describe_stacks(**arg)
    if response['Stacks'][0]['StackStatus'] != goal_state:
        SPINNER.fail('Did not reach goal state: %s' % goal_state)
        return False
    SPINNER.succeed('Reached state: %s' % goal_state)
    return True


def _create_stack(appconf, node, rendered_template):
    session = boto3.Session(profile_name=appconf['profile'])
    cfn_client = session.client('cloudformation')
    template = _gen_from_template(appconf, node, rendered_template)
    SPINNER.start('Creating stack')
    response = cfn_client.create_stack(**_make_create_args(appconf, template))
    if response['ResponseMetadata']['HTTPStatusCode'] >= 300:
        SPINNER.fail('Create failed')
        return False
    SPINNER.succeed('Create call succeeded')
    return True


def _delete_stack(appconf):
    session = boto3.Session(profile_name=appconf['profile'])
    cfn_client = session.client('cloudformation')
    SPINNER.start('Deleting stack')
    response = cfn_client.delete_stack(**_stack_name(appconf))
    if response['ResponseMetadata']['HTTPStatusCode'] >= 300:
        SPINNER.fail('Delete failed')
        return False
    SPINNER.succeed('Delete call succeeded')
    return True


def _create_distribution_environment():
    venv_dir = os.path.join(os.getcwd(), '.venv')

    SPINNER.start('Creating venv')
    virtualenv.create_environment(venv_dir)
    SPINNER.succeed('venv created')
    return True


def _install_requirements():
    venv_dir = os.path.join(os.getcwd(), '.venv')
    pip_exec = os.path.join(venv_dir, 'bin', 'pip')
    SPINNER.start('Installing requirements')
    subprocess.check_call([
        pip_exec, 'install', '-r', 'requirements.txt', '-I'],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    SPINNER.succeed('Installation successful')
    return True


def _upload_dist(appconf):
    node_conf = appconf['nodeconf']
    dist_zip = node_conf['node'].get('archive', 'dist.zip')

    session = boto3.Session(profile_name=appconf['profile'])
    s3_client = session.client('s3')

    SPINNER.start('Uploading distribution')
    if not fs._upload_file(
            s3_client,
            dist_zip,
            node_conf['node']['bucket_name'],
            node_conf['node']['archive']):
        SPINNER.fail('Upload failed')
        return False
    SPINNER.succeed('Upload successful')
    os.remove(dist_zip)
    return True
