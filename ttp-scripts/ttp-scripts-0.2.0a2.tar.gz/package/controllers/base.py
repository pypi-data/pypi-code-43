
from ..core import api
from cement import Controller, ex
from cement.utils.version import get_version_banner
from cement.utils import shell
from getpass import getpass
import requests
from ..core.version import get_version

VERSION_BANNER = """
Manage pipeline versions %s
%s
""" % (get_version(), get_version_banner())


class Base(Controller):
    class Meta:
        label = 'base'

        # text displayed at the top of --help output
        description = 'Manage pipeline versions'

        # text displayed at the bottom of --help output
        epilog = 'Usage: ttp login'

        # controller level arguments. ex: 'ttp --version'
        arguments = [
            ### add a version banner
            ( [ '-v', '--version' ],
              { 'action'  : 'version',
                'version' : VERSION_BANNER } ),
        ]


    def _default(self):
        """Default action if no sub-command is passed."""

        self.app.args.print_help()


    @ex(
        help='Login',
    )
    def login(self):
        """Log into TwinThread"""
        username = shell.Prompt("Username?")

        password = getpass("Password?")
    
        self.app.log.info("Logging in...")

        api.login(username.input, password)

        self.app.log.info("Login succeeded.")
        self.app.log.info("You are now authenticated.")

    @ex(help="Open kubernetes dashboard")
    def dashboard(self):
        self.app.log.info("Open the link below to see kubernetes status.")
        shell.cmd("echo http://localhost:3989/api/v1/namespaces/kube-system/services/kubernetes-dashboard/proxy/#!/overview?namespace=default", capture=False)
        shell.cmd("kubectl proxy -p 3989", capture=False)
