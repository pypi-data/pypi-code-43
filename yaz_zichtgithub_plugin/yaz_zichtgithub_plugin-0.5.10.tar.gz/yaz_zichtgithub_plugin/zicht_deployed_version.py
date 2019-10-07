import os
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
import github
import github.GithubObject
import gspread
import re
import tabulate
import yaz

from .github import Github
from .log import logger, set_verbose
from .spreadsheet import Worksheet
from .version import __version__

__all__ = ["DeployedVersion"]


class Deploy:
    def __init__(self, repo, tag, sha, flavor, environment, description):
        self.repo = repo
        self.tag = tag
        self.sha = sha
        self.flavor = flavor
        self.environment = environment
        self.description = description

    @property
    def table_row(self):
        return [self.repo, self.tag, self.flavor, self.environment, self.description, self.sha]

    def __str__(self):
        return "{self.repo} {self.tag} {self.description}".format(self=self)


class DeployedVersionSheet:
    def __init__(self, json_key_file: str, sheet_key: str):
        scope = ['https://spreadsheets.google.com/feeds']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(json_key_file, scope)
        gc = gspread.authorize(credentials)
        self.sheet = gc.open_by_key(sheet_key)
        self.worksheets = [DeployedVersionWorksheet(worksheet) for worksheet in self.sheet.worksheets()]

    def update(self, deploys):
        for worksheet in self.worksheets:
            worksheet.update(deploys)

    def set_updating(self, *args, **kwargs):
        for worksheet in self.worksheets:
            worksheet.set_updating(*args, **kwargs)

    def unset_updating(self, *args, **kwargs):
        for worksheet in self.worksheets:
            worksheet.unset_updating(*args, **kwargs)


class DeployedVersionWorksheet(Worksheet):
    def __init__(self, worksheet: gspread.Worksheet):
        self.worksheet = worksheet

    def update(self, deploys):
        update = False
        updated_cells = []

        for deploy in deploys:
            for row_header in [self.find_row_header(deploy.repo), self.find_row_header("{}:{}".format(deploy.repo, deploy.flavor))]:
                if row_header:
                    col_header = self.find_column_header(deploy.environment)
                    if col_header:
                        cell = self.get_cell(row_header.row, col_header.col)
                        if cell.value != deploy.description:
                            cell.value = deploy.description
                            update = True
                        updated_cells.append(cell)

                    col_header = self.find_column_header("{}:sha".format(deploy.environment))
                    if col_header:
                        cell = self.get_cell(row_header.row, col_header.col)
                        if cell.value != deploy.sha:
                            cell.value = deploy.sha
                            update = True
                        updated_cells.append(cell)

        if update:
            self.set_cells(updated_cells)

    def set_updating(self, message: str = "UPDATING"):
        cell = self.get_cell(1, 1)
        cell.value = message.format(now=datetime.now())
        self.set_cells([cell])

    def unset_updating(self, message: str = "{now}"):
        cell = self.get_cell(1, 1)
        cell.value = message.format(now=datetime.now())
        self.set_cells([cell])


class DeployedVersion(yaz.BasePlugin):
    """
    Synchronize deployment tags from github to google sheets.
    """

    json_key_file = None
    sheet_key = None

    @yaz.dependency
    def set_github(self, github: Github):
        self.github = github.get_service()

    @yaz.task
    def version(self, verbose: bool = False, debug: bool = False):
        """Gives the software version."""
        set_verbose(verbose, debug)
        return __version__

    @yaz.task(user__help="The repo user, i.e. \"zicht\"", name__help="The repo name, i.e. \"donner.nl\"")
    def show_repo(self, user: str, name: str, verbose: bool = False, debug: bool = False):
        """Display the deployment tags of a single repository."""
        set_verbose(verbose, debug)

        headers = ['repository', 'tag', 'flavor', 'environment', 'nice description', 'sha hash']
        table = [deploy.table_row for deploy in self.__get_deploys(self.github.get_user(user).get_repo(name))]
        table.sort()
        return tabulate.tabulate(table, headers=headers)

    @yaz.task
    def show_all(self, limit: int = 666, verbose: bool = False, debug: bool = False):
        """Display the deployment tags of all repositories."""
        set_verbose(verbose, debug)

        headers = ['repository', 'tag', 'flavor', 'environment', 'nice description', 'sha hash']
        repos = list(self.github.get_user().get_repos()[:limit])
        for repo in repos:
            table = [deploy.table_row for deploy in self.__get_deploys(repo)]
            if table:
                table.sort()
                print(tabulate.tabulate(table, headers=headers))
                print()

    @yaz.task(user__help="The repo user, i.e. \"zicht\"", name__help="The repo name, i.e. \"concertgebouw.nl\"")
    def update_repo(self, user: str, name: str, verbose: bool = False, debug: bool = False):
        """Update the spreadsheet with the deployment tags of a single repository."""
        set_verbose(verbose, debug)

        sheet = DeployedVersionSheet(os.path.expanduser(self.json_key_file), self.sheet_key)
        sheet.set_updating()
        try:
            deploys = self.__get_deploys(self.github.get_user(user).get_repo(name))
            if deploys:
                sheet.update(deploys)
        finally:
            sheet.unset_updating()

    @yaz.task
    def update_all(self, limit: int = 666, verbose: bool = False, debug: bool = False):
        """Update the spreadsheet with the deployment tags of all repositories."""
        set_verbose(verbose, debug)

        sheet = DeployedVersionSheet(os.path.expanduser(self.json_key_file), self.sheet_key)
        sheet.set_updating()
        try:
            repos = list(self.github.get_user().get_repos()[:limit])
            for repo in repos:
                deploys = self.__get_deploys(repo)
                if deploys:
                    sheet.update(deploys)
        finally:
            sheet.unset_updating()

    def __get_deploys(self, repo):
        deploys = []
        tags = {}
        for tag in repo.get_tags():
            tags.setdefault(tag.commit.sha, []).append(tag)
        for tag_list in tags.values():
            for tag in tag_list:
                flavor, environment, description = self.__match_deployment_tag(tag, tags)
                if environment:
                    deploys.append(Deploy(repo.name, tag.name, tag.commit.sha, flavor, environment, description))
        return deploys

    def __match_deployment_tag(self, tag: github.Tag.Tag, tags: dict):
        """Returns (flavor, environment, nice-description) tuple."""
        match = re.match('(?:(?P<flavor>.+)_)?(?P<environment>.*)-env', tag.name)
        if match is None:
            return None, None, None
        else:
            return match.group('flavor'), match.group('environment'), self.__get_nice_description(tag.commit, tags)

    def __get_nice_description(self, commit, tags):
        """Returns a string in the format 'semver' or 'semver-distance-sha' for the given commit."""
        distance = 0
        node = commit

        while node:
            versions = [tag for tag in tags.get(node.sha, []) if re.match('[0-9]+([.][0-9]+)*(-[a-zA-Z]+)?', tag.name)]
            if versions:
                if distance == 0:
                    return versions[0].name
                else:
                    return '{version}-{distance}-{sha}'.format(version=versions[0].name, distance=distance, sha=commit.sha[0:8])

            if len(node.parents) == 0:
                break

            node = node.parents[0]
            distance += 1

        return '0.0.0-{distance}-{sha}'.format(distance=distance, sha=commit.sha[0:8])

    def __iter_parents(self, commit):
        """Iterate over first parent recursively sorted by commit date"""
