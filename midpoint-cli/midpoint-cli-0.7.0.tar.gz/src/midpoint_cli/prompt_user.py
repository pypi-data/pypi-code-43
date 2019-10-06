import shlex
from argparse import ArgumentParser, RawTextHelpFormatter

import tabulate

# User command wrapper parser

user_parser = ArgumentParser(
    formatter_class=RawTextHelpFormatter,
    prog='user',
    description='Manage server users.',
    epilog='''
Available commands:
  ls       List all users.
  search   Search for a user.
''')
user_parser.add_argument('command', help='User command to execute.')
user_parser.add_argument('arg', help='Optional command arguments.', nargs='*')

# User search parser

user_search_parser = ArgumentParser(
    formatter_class=RawTextHelpFormatter,
    prog='user search',
    description='Search for a user.',
)
user_search_parser.add_argument('searchquery', help='A string fragment found in the user data.', nargs='+')


class UserClientPrompt:

    def do_user(self, inp):
        try:
            user_args = shlex.split(inp)
            ns = user_parser.parse_args(user_args)

            if ns.command == 'ls':
                users = self.client.get_users()
                print(tabulate.tabulate(users, headers='keys'))
            if ns.command == 'search':
                search_ns = user_search_parser.parse_args(user_args[1:])
                users = self.client.search_users(search_ns.searchquery)
                print(tabulate.tabulate(users, headers='keys'))

        except SystemExit:
            pass

    def help_user(self):
        user_parser.print_help()

    def do_users(self, inp):
        self.do_user('ls')

    def help_users(self):
        print('List all server users. This is a shortcut for "user ls"')
