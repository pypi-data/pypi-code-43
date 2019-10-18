"""Deploy references from source control."""

from dataclasses import dataclass
import logging
import multiprocessing
import os
import shutil
import subprocess
import tempfile
import textwrap
from typing import Callable, ContextManager, List, NoReturn, Optional, Sequence

import click
import git  # type: ignore
import pkg_resources

LOGGER = logging.getLogger(__name__)

###############################################################################

__version__ = pkg_resources.get_distribution(__name__).version


class VerdocError(Exception):
    """Exceptions emitted from this module inherit from this error."""


class BuildContextError(VerdocError):
    """Exceptions emitted from the build context inherit from this error."""


class ReferenceNotFoundError(BuildContextError):
    """A refname is not recognized by the build context."""


class ReferenceAlreadyBuiltError(BuildContextError):
    """A refname has already been built by the build context."""


class BuilderError(VerdocError):
    """Exceptions emitted from the builder inherit from this error."""


class UnbuildableBuildJobError(BuilderError):
    """A build job is not buildable."""


class FailedBuildJobError(BuilderError):
    """A build job failed."""


@dataclass
class BuildJob:
    """Bundle data needed to build."""

    name: str
    source_dir: str
    dest_dir: str

    def log_path(self) -> str:
        """Return the path to the build log."""
        return os.path.join(self.dest_dir, 'build.log')


@dataclass
class BuildSpec:
    """Bundle data needed to make a build job."""

    repo_path: str
    refname: str
    dest_dir: str


@dataclass
class BuildManager:
    """Build references from ``repo_path`` into ``dest_dir``."""

    repo_path: str
    build_context: Callable[[BuildSpec], ContextManager[BuildJob]]
    builder: Callable[[BuildJob], None]
    dest_dir: str

    def build(self, refnames: Sequence[str]) -> int:
        """Build ``refnames`` and return an exit status."""
        with multiprocessing.Pool() as pool:
            return sum(pool.imap_unordered(self.build_target, set(refnames)))

    def build_protocol(self, build_spec: BuildSpec) -> None:
        """Build ``build_spec``."""
        # https://github.com/python/mypy/issues/5485
        with self.build_context(build_spec) as build_job:  # type: ignore
            LOGGER.debug(
                '[%s] %s: %s',
                build_spec.refname,
                self.__class__.__name__,
                build_job,
            )
            # https://github.com/python/mypy/issues/5485
            self.builder(build_job)  # type: ignore

    def build_target(self, refname: str) -> int:
        """Build ``refname`` and return an exit status."""
        try:
            LOGGER.info('[%s] started', refname)
            self.build_protocol(
                build_spec=BuildSpec(
                    repo_path=self.repo_path,
                    refname=refname,
                    dest_dir=os.path.join(self.dest_dir, refname),
                ),
            )
        except ReferenceNotFoundError as exc:
            LOGGER.error('[%s] cancelled, %s', refname, exc)
            return 1
        except ReferenceAlreadyBuiltError as exc:
            LOGGER.warning('[%s] skipped, %s', refname, exc)
            return 0
        except UnbuildableBuildJobError as exc:
            LOGGER.error('[%s] aborted, %s', refname, exc)
            return 1
        except FailedBuildJobError as exc:
            LOGGER.error('[%s] failed, %s', refname, exc)
            return 1
        else:
            LOGGER.info('[%s] succeeded', refname)
            return 0


###############################################################################


@dataclass
class GitBuildContext:
    """Build Git references."""

    def __init__(self, build_spec: BuildSpec):
        """Look up ``build_spec.refname`` in ``build_spec.repo_path``."""
        self._dest_dir = build_spec.dest_dir
        self._source_dir: Optional[str] = None

        LOGGER.debug(
            "[%s] %s: Looking up '%s' reference in '%s'...",
            build_spec.refname,
            self.__class__.__name__,
            build_spec.refname,
            build_spec.repo_path,
        )
        repo = git.Repo(build_spec.repo_path)
        try:
            self._ref = repo.refs[build_spec.refname]
        except IndexError as exc:
            raise ReferenceNotFoundError(str(exc)) from exc

    def __enter__(self) -> BuildJob:
        """Create a build job using a temporary clone."""
        if self.already_built_commit() == str(self._ref.commit):
            raise ReferenceAlreadyBuiltError(
                f"'{self._ref.commit}' already built in '{self._dest_dir}'",
            )

        assert self._source_dir is None
        self._source_dir = tempfile.mkdtemp()

        LOGGER.debug(
            "[%s] %s: Checking out '%s' into '%s'...",
            self._ref.name,
            self.__class__.__name__,
            self._ref.commit,
            self._source_dir,
        )
        clone = self._ref.repo.clone(self._source_dir, no_checkout=True)
        clone.git.checkout(self._ref.commit)

        return BuildJob(
            name=self._ref.name,
            source_dir=self._source_dir,
            dest_dir=self._dest_dir,
        )

    def __exit__(self, exc_type, exc, traceback_) -> bool:
        """Clean up the temporary clone."""
        if not exc:
            self.write_commit()

        LOGGER.debug(
            "[%s] %s: Cleaning up '%s'...",
            self._ref.name,
            self.__class__.__name__,
            self._source_dir,
        )
        assert self._source_dir is not None
        shutil.rmtree(self._source_dir, ignore_errors=True)
        self._source_dir = None

        return False

    def already_built_commit(self) -> Optional[str]:
        """Read ``self.commit_file_path()``."""
        commit_file_path = self.commit_file_path()
        LOGGER.debug(
            "[%s] %s: Reading '%s'...",
            self._ref.name,
            self.__class__.__name__,
            commit_file_path,
        )
        try:
            with open(commit_file_path) as commit_file:
                return commit_file.read()
        except (FileExistsError, FileNotFoundError, NotADirectoryError):
            return None

    def commit_file_path(self) -> str:
        """Get the path to a file that contains the already-built commit."""
        return os.path.join(self._dest_dir, '.commit')

    def write_commit(self) -> None:
        """Write ``self.commit_file_path()``."""
        commit_file_path = self.commit_file_path()
        LOGGER.debug(
            "[%s] %s: Writing '%s' to '%s'...",
            self._ref.name,
            self.__class__.__name__,
            self._ref.commit,
            commit_file_path,
        )
        with open(self.commit_file_path(), 'w') as commit_file:
            commit_file.write(str(self._ref.commit))


@dataclass
class ToxBuilder:
    """Use tox to build."""

    env: str = 'verdoc'

    def __call__(self, build_job: BuildJob) -> None:
        """Run ``tox -e '{self.env}' -- '{build_job.dest_dir}'``."""
        self.check_build(build_job)
        LOGGER.debug(
            "[%s] %s: Building '%s' into '%s'...",
            build_job.name,
            self.__class__.__name__,
            build_job.source_dir,
            build_job.dest_dir,
        )
        shutil.rmtree(build_job.dest_dir, ignore_errors=True)
        try:
            try:
                os.makedirs(build_job.dest_dir)
            except FileExistsError as exc:
                LOGGER.debug("[%s] tox: %s", build_job.name, exc)
            build_log_path = build_job.log_path()
            with open(build_log_path, 'w') as build_log:
                LOGGER.debug(
                    "[%s] %s: Logging to '%s'...",
                    build_job.name,
                    self.__class__.__name__,
                    build_log_path,
                )
                subprocess.run(
                    self._tox(
                        configfile=build_job.source_dir,
                        posargs=[build_job.dest_dir],
                    ),
                    check=True,
                    stderr=subprocess.STDOUT,
                    stdout=build_log,
                )
        except (NotADirectoryError, subprocess.CalledProcessError) as exc:
            raise FailedBuildJobError(str(exc)) from exc

    def _tox(
            self,
            configfile: Optional[str] = None,
            posargs: Optional[List] = None,
    ) -> List[str]:
        """Return a tox command that can be passed to ``subprocess.run``."""
        tox = ['tox', '-e', self.env]
        if configfile:
            tox.extend(['-c', configfile])
        if posargs:
            tox.extend(['--'] + posargs)
        return tox

    def check_build(self, build_job: BuildJob) -> None:
        """Raise UnbuildableBuildJobError if ``build_job`` is not buildable."""
        LOGGER.debug(
            "[%s] %s: Checking for a '%s' env in '%s'...",
            build_job.name,
            self.__class__.__name__,
            self.env,
            build_job.source_dir,
        )
        try:
            subprocess.run(
                self._tox(configfile=build_job.source_dir) + ['--showconfig'],
                capture_output=True,
                check=True,
                text=True,
            )
        except subprocess.CalledProcessError as exc:
            raise UnbuildableBuildJobError(
                # https://github.com/tox-dev/tox/issues/1434
                exc.stderr.strip() or exc.stdout.strip(),
            ) from exc


###############################################################################


# https://github.com/python/typeshed/pull/3385
DEST_OPTION = click.option(  # type: ignore
    '--dest',
    help='Specify the path to build in.',
    nargs=1,
    type=click.Path(),
    default=os.getcwd(),
    show_default='current working directory',
)
VERSION_OPTION = click.version_option(__version__)


@click.command()
@click.option(
    '--build-opt',
    help='Pass keyword arguments to the builder (e.g. foo=bar).',
    nargs=1,
    multiple=True,
)
@DEST_OPTION
@click.option(
    '--log-level',
    help='Specify how verbose output should be.',
    nargs=1,
    type=click.Choice(
        ['debug', 'info', 'warning', 'error', 'critical'],
        case_sensitive=False,
    ),
    default='info',
    show_default=True,
)
# https://github.com/python/typeshed/pull/3385
@click.option(  # type: ignore
    '--repo',
    help='Specify the repository to look for references in.',
    nargs=1,
    type=click.Path(exists=True),
    default=os.getcwd(),
    show_default='current working directory',
)  # pylint: disable=too-many-arguments
@VERSION_OPTION
@click.argument('refnames', nargs=-1)
@click.pass_context
def cli(
        ctx: click.Context,
        build_opt: Sequence[str],
        dest: str,
        log_level: str,
        repo: str,
        refnames: Sequence[str],
) -> NoReturn:
    """Get ``REFNAMES`` from ``--repo`` and build them into ``--dest``."""
    logging.basicConfig(level=logging.getLevelName(log_level.upper()))
    builder_kwargs = {
        key: value
        for opt in build_opt
        for key, _, value in [opt.partition('=')]
    }
    try:
        builder = ToxBuilder(**builder_kwargs)
    except TypeError as exc:
        LOGGER.error('Builder creation failed (%s).', exc)
        ctx.exit(1)
    ctx.exit(
        BuildManager(
            repo_path=repo,
            build_context=GitBuildContext,
            builder=builder,
            dest_dir=dest,
        ).build(
            refnames=refnames,
        ),
    )


def redirect_web(path: str, url: str) -> None:
    """Create an HTML file at ``path`` that redirects to ``url``."""
    LOGGER.info("Redirecting '%s' to '%s'...", path, url)
    with open(path, 'w') as html_file:
        html_file.write(
            textwrap.dedent(f'''\
                <!DOCTYPE HTML>
                <html lang="en">
                <head>
                    <meta http-equiv="refresh" content="0; url={url}">
                    <title>Redirecting...</title>
                    <script>window.location = "{url}"</script>
                </head>
                <body>
                <a href="{url}">{url}</a>
                </body>
                </html>
            '''),
        )


@click.command()
@DEST_OPTION
@VERSION_OPTION
@click.argument('url', nargs=1)
@click.pass_context
def cli_index(ctx: click.Context, dest: str, url: str) -> NoReturn:
    """Create an index.html file in ``--dest`` that redirects to ``URL``."""
    try:
        redirect_web(path=os.path.join(dest, 'index.html'), url=url)
    except OSError as exc:
        LOGGER.error(exc)
        ctx.exit(1)
    ctx.exit(0)
