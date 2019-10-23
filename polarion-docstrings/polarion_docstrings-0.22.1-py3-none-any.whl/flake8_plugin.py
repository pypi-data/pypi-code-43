"""Check Polarion docstrings using flake8."""

from pkg_resources import get_distribution
from polarion_tools_common import configuration

from polarion_docstrings import checker


def get_version():
    """Return plugin version."""
    try:
        return get_distribution(__package__).version
    # pylint: disable=broad-except
    except Exception:
        # package is not installed
        return "0.0"


def set_compiled_lists(config):
    """Save compiled regular expressions for whitelist and blacklist into config."""
    if not config:
        return
    config["_compiled_whitelist"], config[
        "_compiled_blacklist"
    ] = checker.DocstringsChecker.get_compiled_lists(config)


class PolarionDocstringsPlugin:
    """The flake8 entry point."""

    name = "polarion_checks"
    version = get_version()
    config = None

    def __init__(self, tree, filename):
        self.tree = tree
        self.filename = filename
        self.set_config(filename)

    @classmethod
    def set_config(cls, filename):
        """Set plugin configuration.

        We set it once as a class attribute so the setup doesn't need to be done
        repeatedly for each checked file.
        """
        if cls.config is None:
            cls.config = configuration.get_config(project_path=filename) or {}
            set_compiled_lists(cls.config)

    def run(self):
        """Run checks."""
        return checker.DocstringsChecker(
            self.tree, self.filename, self.config, PolarionDocstringsPlugin
        ).get_errors()
