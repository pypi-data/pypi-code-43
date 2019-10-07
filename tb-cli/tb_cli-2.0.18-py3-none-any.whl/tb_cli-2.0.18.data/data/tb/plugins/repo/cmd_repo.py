import os
import sys
from os import path
from typing import Set

import yaml
from cement import Controller, ex

from tb import Repository, TbError
from tb.arguments import repository
from tb.job_execution import parallel_call
from tb import Tb


class RepoController(Controller):
    class Meta:
        label = 'repo'
        help = "commands to manage your teams' git repositories"
        stacked_on = 'base'
        stacked_type = 'nested'
        description = "Commands to help with git repository management functions.  " \
                      "Default command syncs all repositories."

        arguments = repository.arguments

    @repository.validate
    @ex(help="adds the current repository to the organization config.",
        arguments=repository.arguments)
    def add(self):
        app: Tb = self.app

        team_name = app.term.prompt_menu("What team should own this repository?",
                                         options=list(app.config_manager.teams.keys()))

        team_file = path.join(app.config_manager.org_repo_dir, f"{team_name}.yml")
        if not path.isfile(team_file):
            raise TbError(f"Unable to find team configuration file at {team_file}")

        repo_name = os.path.basename(os.getcwd())
        git_url, _, ret = app.captured_cmd(repo_name, "git config --get remote.origin.url")
        if ret:
            raise TbError(f"Unable to determine git url")

        with open(team_file, 'r') as f:
            try:
                data = yaml.load(f)
            except yaml.YAMLError as exc:
                app.term.error(exc)

        data.setdefault("repositories", {})[repo_name] = {
            "team": team_name,
            "url": git_url.strip().decode('utf-8')
        }
        with open(team_file, 'w') as outfile:
            yaml.dump(data, outfile, default_flow_style=False)

        app.term.success(f"Team file {team_file} modified to add the {repo_name} repository")

    @repository.validate
    @ex(help="pulls (with rebase) or clones the repositories to your source directory.",
        arguments=repository.arguments)
    def sync(self):
        app: Tb = self.app
        repos = self._get_unique_repos()
        if not repos:
            app.term.info("Nothing to do, exiting")
            return

        names, outputs = self._sync_repos(app.src_dir, repos)
        app.term.columns(names, outputs, ['Repo', 'Sync Status'], report_format="{:32}{:^7}")

    def _default(self):
        self.sync()

    def _get_unique_repos(self) -> Set[Repository]:
        app: Tb = self.app
        team_repos = {r for r in app.repositories.values() if r.team in app.config_manager.selected_teams}
        if app.config_manager.org_repo.name not in (x.name for x in team_repos):
            team_repos.add(app.config_manager.org_repo)
        return team_repos

    def _gen_call_clone(self, src, repo: Repository, branch=None):
        app: Tb = self.app
        app.term.info("Cloning repository: {}, uri: {}".format(repo.name, repo.url))
        path = os.path.realpath(os.path.join(src, repo.name))
        assert (not os.path.isdir(path))  # checked above
        app.term.action("Clone", path)
        args = ['git', "clone"]
        if branch:
            args.extend(['-b', branch])
        args.extend([repo.url, path])
        return app.cmd_callable(repo.name, *args, cwd=src)

    def _gen_call_sync(self, src: str, repo: Repository):
        app: Tb = self.app
        path = os.path.realpath(os.path.join(src, repo.name))
        app.term.action("Sync", path)
        self._call_update_source_remote(path, repo)
        args = ['git', 'pull', '--prune', '--rebase']
        return app.cmd_callable(repo.name, *args, cwd=path)

    def _call_update_source_remote(self, path, repo: Repository):
        app: Tb = self.app
        source_remote = repo.source_remote or "origin"
        args = ['git', 'config', '--get', f'remote.{source_remote}.url']
        url, _, ret = app.captured_cmd(repo.name, *args, cwd=path, shell=True)
        if ret != 0:
            print(app.term.warn("Command {} failed with code {}".format(" ".join(args), ret)))
            return ret

        url = url.strip().decode('utf-8')
        expected = repo.url
        if url != expected:
            app.term.print(f"Update source remote: <old>{url}</old> -> <new>{expected}</new>")
            args = ['git', 'config', f'remote.{source_remote}.url', expected]
            ret = app.cmd(repo.name, *args, cwd=path)

        sys.stdout.flush()
        return ret

    def _sync_repos(self, src: str, repos: Set[Repository]):
        """Clones all uncloned repositories and does a pull --rebase for others."""
        jobs = []
        for repo in repos:
            path = os.path.realpath(os.path.join(src, repo.name))
            if not os.path.isdir(path):
                jobs.append(self._gen_call_clone(src, repo))
            else:
                jobs.append(self._gen_call_sync(src, repo))

        outputs = parallel_call(jobs)
        return (r.name for r in repos), outputs
