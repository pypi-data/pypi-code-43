from datetime import datetime
from random import shuffle

from oauth2client.service_account import ServiceAccountCredentials
import github
import github.GithubObject
import gspread
import os
import re
import yaz

from .github import Github
from .log import logger, set_verbose
from .spreadsheet import Worksheet
from .version import __version__


class ZichtRepository:
    def __init__(self, repository: github.Repository.Repository):
        self._repository = repository

    @property
    def is_zicht_repository(self):
        return "zicht" == self._repository.owner.login

    @property
    def identity(self):
        return "{repo.owner.login}/{repo.name}".format(repo=self._repository)

    @property
    def name(self):
        return self._repository.name

    @property
    def last_modified(self):
        return str(self._repository.pushed_at)

    @property
    def _description(self):
        description = str(self._repository.description).strip()
        match = re.match(r"^(?P<type>library|website|utility|obsolete)\s+-\s+(?P<description>.+)$", description, re.IGNORECASE)
        if match:
            return match.group("type").capitalize(), match.group("description")
        return "Other", description

    @property
    def type(self):
        return self._description[0]

    @property
    def description(self):
        return self._description[1]

    @property
    def maintainers(self):
        try:
            readme = self._repository.get_readme().decoded_content.decode("utf-8")
        except (github.UnknownObjectException, github.GithubException):
            readme = ""

        maintainers = []
        it = iter(readme.splitlines())
        for line in it:
            if re.match(r"^#+\s*maintainer", line, re.IGNORECASE):
                for line in it:
                    if re.match(r"^#", line):
                        break
                    match = re.match(r"^[\s*-]*(?P<maintainer>.+?)\s*(?P<mail><.*>)?$", line)
                    if match:
                        maintainers.append(match.group("maintainer"))
                break

        return ", ".join(sorted(maintainers))

    @property
    def errors(self):
        errors = []

        # Everything should have a specified type
        if "Other" == self.type:
            errors.append("unspecified type")

        # Everything must have a description
        if not self.description:
            errors.append("missing description")

        # Libraries and Utilities must have a maintainer
        if self.type in ("Library", "Utility") and not self.maintainers:
            errors.append("missing maintainer")

        return ", ".join(errors)

    def __str__(self):
        return self.identity


class RepositoryListSheet:
    def __init__(self, json_key_file: str, sheet_key: str):
        scope = ['https://spreadsheets.google.com/feeds']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(json_key_file, scope)
        gc = gspread.authorize(credentials)
        self.sheet = gc.open_by_key(sheet_key)
        self.worksheets = [RepositoryListWorksheet(worksheet) for worksheet in self.sheet.worksheets()]

    def update(self, repo):
        for worksheet in self.worksheets:
            worksheet.update(repo)

    def set_updating(self, *args, **kwargs):
        for worksheet in self.worksheets:
            worksheet.set_updating(*args, **kwargs)

    def unset_updating(self, *args, **kwargs):
        for worksheet in self.worksheets:
            worksheet.unset_updating(*args, **kwargs)


class RepositoryListWorksheet(Worksheet):
    def __init__(self, worksheet: gspread.Worksheet):
        self.worksheet = worksheet

    def update(self, repo: ZichtRepository):
        if not repo.is_zicht_repository:
            logger.debug("Skipping %s because the repo is not owned by Zicht (%s)", repo.name, self.worksheet.id)
            return

        update = False
        updated_cells = []

        if repo.type in self.worksheet.title:
            # add or update the repo on this worksheet
            row_header = self.find_or_create_row_header(repo.identity, updated_cells)
            if row_header is None:
                logger.debug("Skipping %s because there is no row available (%s)", repo.name, self.worksheet.id)
                return
            logger.info("Checking %s in column #%s (%s)", repo.name, row_header.col, self.worksheet.id)

            # the column_headers contains the top cell of the column indexed by their name
            # when one of these names corresponds to a valid repo data source, the associated column is updated
            column_headers = {cell.value.lower().replace(' ', '_'): cell for cell in self.get_row(1) if cell.value}
            row = {cell.col: cell for cell in self.get_row(row_header.row)}

            for attr in ['last_modified', 'description', 'maintainers', 'errors']:
                column_header = column_headers.get(attr)
                if column_header:
                    cell = row[column_header.col]
                    value = getattr(repo, attr)
                    if cell.value != value:
                        cell.value = value
                        update = True
                    updated_cells.append(cell)

        else:
            # remove the repo from this worksheet
            row_header = self.find_row_header(repo.identity)
            if row_header is not None:
                for cell in self.get_row(row_header.row, 0):
                    if cell.value:
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


class RepositoryList(yaz.BasePlugin):
    """
    Connect to a google spreadsheet and update it with a summary of github repositories.
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
        """Update the spreadsheet with the summary of a single repository."""
        set_verbose(verbose, debug)

        sheet = RepositoryListSheet(os.path.expanduser(self.json_key_file), self.sheet_key)
        sheet.set_updating()
        try:
            repo = ZichtRepository(self.github.get_user(user).get_repo(name))
            sheet.update(repo)
        finally:
            sheet.unset_updating()

    @yaz.task
    def update_all(self, limit: int = 666, verbose: bool = False, debug: bool = False):
        """Update the spreadsheet with the summary of all repositories."""
        set_verbose(verbose, debug)

        logger.info('Fetching repositories')
        repos = list(self.github.get_user().get_repos()[:limit])
        shuffle(repos)
        logger.info('Fetched %s repositories', len(repos))

        sheet = RepositoryListSheet(os.path.expanduser(self.json_key_file), self.sheet_key)
        sheet.set_updating()
        try:
            for repo in repos:
                repo = ZichtRepository(repo)
                sheet.update(repo)
        finally:
            sheet.unset_updating()
