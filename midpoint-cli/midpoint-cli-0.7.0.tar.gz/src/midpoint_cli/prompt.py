import sys
from cmd import Cmd

from clint.textui import colored

from midpoint_cli.mpclient import MidpointClient
from midpoint_cli.prompt_delete import DeleteClientPrompt
from midpoint_cli.prompt_get import GetClientPrompt
from midpoint_cli.prompt_org import OrgClientPrompt
from midpoint_cli.prompt_put import PutClientPrompt
from midpoint_cli.prompt_resource import ResourceClientPrompt
from midpoint_cli.prompt_script import ScriptClientPrompt
from midpoint_cli.prompt_task import TaskClientPrompt
from midpoint_cli.prompt_user import UserClientPrompt


class MidpointClientPrompt(Cmd,
                           TaskClientPrompt,
                           GetClientPrompt,
                           PutClientPrompt,
                           DeleteClientPrompt,
                           ResourceClientPrompt,
                           UserClientPrompt,
                           OrgClientPrompt,
                           ScriptClientPrompt
                           ):

    def __init__(self, client: MidpointClient):
        Cmd.__init__(self)
        is_a_tty = hasattr(sys.stdin, 'isatty') and sys.stdin.isatty()
        self.client = client
        self.prompt = colored.green('midpoint') + '> ' if is_a_tty else ''
        self.intro = 'Welcome to Midpoint client ! Type ? for a list of commands' \
            if is_a_tty else None

    def can_exit(self):
        return True

    def do_EOF(self, inp):
        print()
        return self.do_exit(inp)

    def do_exit(self, inp):
        return True

    def help_exit(self):
        print('Exit the shell')
