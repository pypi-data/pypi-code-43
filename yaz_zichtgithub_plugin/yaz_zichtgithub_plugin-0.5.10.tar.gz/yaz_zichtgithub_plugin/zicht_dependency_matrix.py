from datetime import datetime
from random import shuffle

from oauth2client.service_account import ServiceAccountCredentials
import github
import github.GithubObject
import gspread
import json
import os
import yaz

from .github import Github
from .log import logger, set_verbose
from .spreadsheet import Worksheet
from .version import __version__

__all__ = ["DependencyMatrix"]


class VersionMatrixSheet:
    def __init__(self, json_key_file: str, sheet_key: str):
        scope = ['https://spreadsheets.google.com/feeds']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(json_key_file, scope)
        gc = gspread.authorize(credentials)
        self.sheet = gc.open_by_key(sheet_key)
        self.worksheets = [VersionMatrixWorksheet(worksheet) for worksheet in self.sheet.worksheets()]

    def set_dependencies(self, *args, **kwargs):
        for worksheet in self.worksheets:
            worksheet.set_dependencies(*args, **kwargs)

    def set_updating(self, *args, **kwargs):
        for worksheet in self.worksheets:
            worksheet.set_updating(*args, **kwargs)

    def unset_updating(self, *args, **kwargs):
        for worksheet in self.worksheets:
            worksheet.unset_updating(*args, **kwargs)


class VersionMatrixWorksheet(Worksheet):
    def __init__(self, worksheet: VersionMatrixSheet):
        self.worksheet = worksheet

    def set_dependencies(self, repo, dependencies):
        update = False
        updated_cells = []

        column_header = self.find_or_create_column_header(repo.name, updated_cells)
        if column_header is None:
            logger.debug("Skipping %s because there is no column available (%s)", repo.name, self.worksheet.id)
            return
        logger.info("Checking %s in column #%s (%s)", repo.name, column_header.col, self.worksheet.id)

        version_column = {cell.row: cell for cell in self.get_column(column_header.col)}
        checked_rows = set()

        # check rows that have a dependency
        for dependency, version in dependencies.items():
            row_header = self.find_or_create_row_header(dependency, updated_cells)
            if row_header is None:
                logger.debug("Skipping %s because there is no row available (%s)", dependency, self.worksheet.id)
                continue

            checked_rows.add(row_header.row)

            if row_header.row in version_column:
                cell = version_column[row_header.row]
            else:
                cell = self.get_cell(row_header.row, column_header.col)
                version_column[row_header.row] = cell

            if cell.value != version:
                logger.info("Update dependency %s from \"%s\" to \"%s\" (%s)", dependency, cell.value, version, self.worksheet.id)
                cell.value = version
                update = True
            updated_cells.append(cell)

        if update:
            self.set_cells(updated_cells)

        # clear rows that do not have a dependency
        update = False
        updated_cells = []
        for cell in version_column.values():
            if cell.row not in checked_rows:
                if cell.value != "":
                    cell.value = ""
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


class DependencyMatrix(yaz.BasePlugin):
    """
    Connect to a google spreadsheet and update it with all composer.lock and package-lock.json found in github repositories.
    """

    json_key_file = None
    sheet_key = None

    def __init__(self):
        if not (self.json_key_file and self.sheet_key):
            raise RuntimeError(
                "The json_key_file and sheet_key must be specified, please add a DependencyMatrix plugin override in your user directory")

    @yaz.dependency
    def set_github(self, github: Github):
        self.github = github.get_service()

    @yaz.task
    def version(self, verbose: bool = False, debug: bool = False):
        """Gives the software version."""
        set_verbose(verbose, debug)
        return __version__

    @yaz.task(user__help="The repo user, i.e. \"zicht\"", name__help="The repo name, i.e. \"itertools\"")
    def update_repo(self, user: str, name: str, verbose: bool = False, debug: bool = False):
        """Update the spreadsheet with the dependencies of a single repository."""
        set_verbose(verbose, debug)

        sheet = VersionMatrixSheet(os.path.expanduser(self.json_key_file), self.sheet_key)
        sheet.set_updating()
        try:
            repo = self.github.get_user(user).get_repo(name)
            dependencies = {}
            dependencies.update(self.get_composer_dependencies(repo))
            dependencies.update(self.get_npm_dependencies(repo))
            if dependencies:
                sheet.set_dependencies(repo, dependencies)
        finally:
            sheet.unset_updating()

    @yaz.task
    def update_all(self, limit: int = 666, verbose: bool = False, debug: bool = False):
        """Update the spreadsheet with the dependencies of all repositories."""
        set_verbose(verbose, debug)

        logger.info('Fetching repositories')
        repos = list(self.github.get_user().get_repos()[:limit])
        shuffle(repos)
        logger.info('Fetched %s repositories', len(repos))

        sheet = VersionMatrixSheet(os.path.expanduser(self.json_key_file), self.sheet_key)
        sheet.set_updating()
        try:
            for repo in repos:
                dependencies = {}
                dependencies.update(self.get_composer_dependencies(repo))
                dependencies.update(self.get_npm_dependencies(repo))
                if dependencies:
                    sheet.set_dependencies(repo, dependencies)
        finally:
            sheet.unset_updating()

    def get_composer_dependencies(self, repo, ref=github.GithubObject.NotSet):
        try:
            file = repo.get_file_contents('/composer.lock', ref)
        except github.GithubException:
            return {}
        data = json.loads(file.decoded_content.decode())

        return {"composer {}".format(package['name']): package['version'].strip() for package in data['packages']}

    def get_npm_dependencies(self, repo, ref=github.GithubObject.NotSet):
        try:
            file = repo.get_file_contents('/package-lock.json', ref)
        except github.GithubException:
            try:
                file = repo.get_file_contents('/javascript/package-lock.json', ref)
            except github.GithubException:
                return {}
        data = json.loads(file.decoded_content.decode())

        if "dependencies" not in data:
            return {}

        return {"npm {}".format(name): dependency["version"].strip() for name, dependency in
                data['dependencies'].items()}
