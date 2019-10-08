import json
import os
import subprocess

from lib.bitbucket import Bitbucket
from lib.git import Git
from lib.github import GithubWrapper
from lib.logging import info, warning
from lib.utils import get_repo_name

class Sourcerio(object):
    def __init__(self, args):
        self.api_key = args.api_key
        self.directory = args.directory
        self.errors = []
        self.organization = args.organization
        self.password = args.password
        self.type = args.type
        self.user = args.user
        self.verbose = args.verbose

    def run(self):
        if not os.path.isdir(self.directory):
            warning('creating backup directory: %s' % self.directory)
            os.makedirs(self.directory)

        repos = self.list_repositories()
        self.backup_repos(repos)

    def backup_repos(self, repos):
        info('[%s] backing up repositories' % self.type)

        for repo in repos:
            try:
                repo_name = get_repo_name(repo, self.type)
                path = os.path.join(self.directory, repo_name)

                git = Git(repo, path, repo_name, self.verbose)

                if os.path.isdir(path):
                    git.fetch()
                else:
                    git.clone()
            except subprocess.CalledProcessError:
                self.errors.append(repo_name)

    def list_repositories(self):
        if self.type == 'bitbucket':
            bitbucket = Bitbucket(self.user, self.password, self.organization)
            return bitbucket.list_repositories()

        elif self.type == 'github':
            github = GithubWrapper(self.api_key, self.organization)
            return github.list_repositories()
