import os
import sys
import time
import json
import gitlab
import urllib
import subprocess

from loguru import logger
from datetime import datetime, timedelta


class Config:
    DEFAULTS = {
        'token': None,
        'log_level': False
    }

    def __init__(self, *args, **kwargs):
        cnf = Config.DEFAULTS
        base = os.environ['HOME']
        if not base:
            base = '/tmp'
        try:
            with open(os.path.join(base, '.gitgud.json'), 'r') as f:
                cnf = json.load(f)
        except Exception as e:
            pass
        self.base = base
        self.cnf = cnf

    def __getitem__(self, key):
        return self.cnf[key]

    def __setitem__(self, key, value):
        self.cnf[key] = value
        with open(os.path.join(self.base, '.gitgud.json'), 'w') as f:
            json.dump(self.cnf, f)


def get_config_singleton():
    conf = Config()

    def __inner__(*args, **kwargs):
        return conf
    return __inner__


global get_config
get_config = get_config_singleton()


class LazyGl():
    def __init__(self, token):
        self.gl = None
        self.token = token
        self.project_name = os.popen(
            "git remote get-url origin | cut -d ':' -f2 | sed \"s/\\.git//\"").read().strip()
        self.project_url = urllib.parse.quote(self.project_name, safe='')

    def __call__(self):
        if self.gl is None:
            self.gl = gitlab.Gitlab(
                'https://gitlab.com', private_token=self.token)
            self.gl.auth()
        return self.gl


def prompt_for_token():
    print('Personal access token not found.')
    print('You can create one here : https://gitlab.com/profile/personal_access_tokens')
    print(' scope: api')
    print('')
    print('Token:')
    print('> ', end='')
    sys.stdout.flush()
    token = sys.stdin.readline().strip("\n")
    return token


def validate_gitlab_auth(token):
    gl = gitlab.Gitlab('https://gitlab.com', private_token=token)
    return gl.auth()


def git(command: str, quiet=False):
    conf = get_config()
    logger.debug('+ git {}', command)
    sp = None
    try:
        sp = subprocess.run(
            "git {}".format(command).split(),
            capture_output=True,
            check=True
        )
    except Exception:
        if not quiet:
            logger.opt(exception=True).debug('git execution failed.')
        raise
    else:
        if not quiet:
            logger.debug('git output: {}', sp.stdout)
        return sp


def get_merge_request(gl, source, dest=None):
    project = gl().projects.get(gl.project_url)
    lf = filter(
        lambda x: x.source_branch == '{}'.format(source),
        project.mergerequests.list()
    )
    if dest is not None:
        lf = filter(
            lambda x: x.target_branch == '{}'.format(dest),
            lf
        )
    mr = list(lf)
    if not len(mr):
        logger.error('Could not find Gitlab merge request')
        logger.error(' for branch "{}" (dest={}), exiting.'.format(
            source, dest
        ))
        return None
    mr = mr[0]
    return mr


def is_clean_git():
    res = git('status -s')
    for short in bytes('MADRCU', 'ascii'):
        if short in res.stdout:
            return False
    return True


def ensure_clean_git():
    if not is_clean_git():
        logger.error('Git state need to be clean for this operation')
        sys.exit(1)


def wait_for_pipeline(project, pipeline_id, timeout=3600):
    details = project.pipelines.get(pipeline_id)
    logger.info('Waiting for pipeline {}', details.web_url)
    limit = datetime.now() + timedelta(seconds=timeout)
    while datetime.now() < limit:
        details = project.pipelines.get(pipeline_id)
        if details.status in ['created', 'pending', 'running']:
            logger.debug('Pipeline status: {}', details.status)
            time.sleep(5)
        else:
            return details


def wait_for_mr_pipeline(project, mr, timeout=3600):
    pipelines = mr.pipelines()
    if not len(pipelines):
        logger.debug(
            'No pipeline have yet run for this merge request. Skipping wait')
        return None
    p = pipelines[0]
    return wait_for_pipeline(project, p['id'])


def ensure_mr_pipeline_succeeded(project, mr):
    last_pipeline = wait_for_mr_pipeline(project, mr)
    if last_pipeline is not None:
        if last_pipeline.status == 'failed':
            logger.error(
                'The last build failed for {}. Exiting.', last_pipeline)
            sys.exit(1)
        elif last_pipeline.status in ['canceled', 'skipped']:
            logger.warning('Last pipeline for merge request did not ran')
        return last_pipeline
    return None
