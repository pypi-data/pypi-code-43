import shlex
from argparse import ArgumentParser, RawTextHelpFormatter

import tabulate

# Org command wrapper parser

org_parser = ArgumentParser(
    formatter_class=RawTextHelpFormatter,
    prog='org',
    description='Manage server organizations.',
    epilog='''
Available commands:
  ls       List all organizations.
  search   Search for an organization.
''')
org_parser.add_argument('command', help='User command to execute.')
org_parser.add_argument('arg', help='Optional command arguments.', nargs='*')

# User search parser

org_search = ArgumentParser(
    formatter_class=RawTextHelpFormatter,
    prog='org search',
    description='Search for an organization.',
)
org_search.add_argument('searchquery', help='A string fragment found in the organization data.', nargs='+')


class OrgClientPrompt:

    def do_org(self, inp):
        try:
            org_args = shlex.split(inp)
            ns = org_parser.parse_args(org_args)

            if ns.command == 'ls':
                orgs = self.client.get_orgs()
                print(tabulate.tabulate(orgs, headers='keys'))
            if ns.command == 'search':
                search_ns = org_search.parse_args(org_args[1:])
                orgs = self.client.search_orgs(search_ns.searchquery)
                print(tabulate.tabulate(orgs, headers='keys'))

        except SystemExit:
            pass

    def help_org(self):
        org_parser.print_help()

    def do_orgs(self, inp):
        self.do_org('ls')

    def help_orgs(self):
        print('List all server organizations. This is a shortcut for "org ls"')
