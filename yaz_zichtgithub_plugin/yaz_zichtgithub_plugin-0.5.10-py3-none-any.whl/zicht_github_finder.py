import re
import github
import github.GithubObject
import yaz

from .version import __version__
from .github import Github
from .log import logger, set_verbose

__all__ = ["GithubFinder"]


class GithubFinder(yaz.BasePlugin):
    """
    Connect to github and perform searches within specified files.
    """

    @yaz.dependency
    def set_github(self, github: Github):
        self.github = github.get_service()

    @yaz.task
    def version(self, verbose: bool = False, debug: bool = False):
        """Gives the software version."""
        set_verbose(verbose, debug)
        return __version__

    @yaz.task(
        pattern__help="Regular expression to match, i.e. boudewijn",
        filename__help="Filename to search in",
        ignore_case__help="Regular expression flag for re.IGNORECASE, defaults to ignore_case=True",
        multi_line__help="Regular expression flag for re.MULTILINE, defaults to multi_line=False",
        dot_all__help="Regular expression flag for re.DOTALL, defaults to dot_all=False",
    )
    def search(self, pattern: str, filename: str = "/README.md", ignore_case: bool = True, multi_line: bool = False, dot_all: bool = False, verbose: bool = False, debug: bool = False):
        """Search for reg-exp pattern within given file within all repositories"""
        set_verbose(verbose, debug)

        # Determine re flags
        flags = 0
        if ignore_case:
            flags &= re.IGNORECASE
        if multi_line:
            flags &= re.MULTILINE
        if dot_all:
            flags &= re.DOTALL

        exp = re.compile(pattern, flags)

        for repo in self.github.get_user().get_repos():
            try:
                file = repo.get_file_contents(filename)
            except github.GithubException:
                logger.info("%s: no file found", repo.name)
                continue

            content = file.decoded_content.decode()
            if exp.search(content):
                print(repo.name)
            else:
                logger.info("%s: no match found", repo.name)
