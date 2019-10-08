import os
import re
import subprocess

from lib.logging import info, error, warning

def exec(cmd, cwd=None, verbose=True):
    tag = '[%s]' % os.environ['PROJECT_NAME']
    info('%s %s' % (tag, cmd))

    if verbose:
        output = None
    else:
        output = open(os.devnull, 'w')

    if isinstance(cmd, str):
        cmd = cmd.split()

    retry = 0
    max_retries = 3

    while (retry < max_retries):
        try:
            return subprocess.check_call(
                cmd,
                stdout=output,
                stderr=output,
                cwd=cwd
            )
        except subprocess.CalledProcessError as e:
            retry += 1
            warning("last command failed. retries remaining: %s" % (max_retries - retry))

            if retry == max_retries:
                error(e.stderr)
                raise e

def get_repo_name(repo, type):
    if type == 'bitbucket':
        regex = re.compile(r'git@bitbucket.org:devolutions\/(.*).git')
    elif type == 'github':
        regex = re.compile(r'git@github.com:Devolutions\/(.*).git')
    result = regex.search(repo)
    
    return result.group(1)
