import os
import re

from lib.logging import info, warning
from lib.utils import exec, get_repo_name

class Git(object):
    def __init__(self, repo, dir, repo_name, verbose):
        self.dir = dir
        self.repo = repo
        self.repo_name = repo_name
        self.verbose = verbose

        os.environ['PROJECT_NAME'] = repo_name

    def clone(self):
        exec('git clone %s %s' % (self.repo, self.dir), verbose=self.verbose)

    def fetch(self):
        cmd = 'git fetch'
        if self.verbose:
            cmd += ' -v'

        exec(cmd, cwd=self.dir, verbose=self.verbose)

    def pull(self):
        exec('git pull', cwd=self.dir, verbose=self.verbose)