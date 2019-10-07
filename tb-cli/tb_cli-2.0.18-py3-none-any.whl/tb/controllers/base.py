from cement import Controller
from cement.utils.version import get_version_banner
from ..version import __version__

VERSION_BANNER = """
The team b cli %s
%s
""" % (__version__, get_version_banner())


class Base(Controller):
    class Meta:
        label = 'base'

        # text displayed at the top of --help output
        description = 'The team b cli'

        # text displayed at the bottom of --help output
        epilog = 'Usage: tb command1 --foo bar'

        # controller level arguments. ex: 'tb --version'
        arguments = [
            (['-v', '--version'],
             {'action': 'version',
              'version': VERSION_BANNER})
        ]

    def _default(self):
        """Default action if no sub-command is passed."""

        self.app.args.print_help()
