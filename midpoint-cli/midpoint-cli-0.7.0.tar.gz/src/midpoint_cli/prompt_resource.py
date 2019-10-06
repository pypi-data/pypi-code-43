import shlex
from argparse import ArgumentParser, RawTextHelpFormatter

import tabulate

resource_parser = ArgumentParser(
    formatter_class=RawTextHelpFormatter,
    prog='resource',
    description='Manage resources.',
    epilog='''
Available commands:
  ls     List all server resources.
  test   Test a resource.
''')
resource_parser.add_argument('command', help='Resource command to execute.', nargs=1)
resource_parser.add_argument('arg', help='Optional command arguments.', nargs='*')

# resource RUN parser

resource_test_parser = ArgumentParser(
    formatter_class=RawTextHelpFormatter,
    prog='resource test',
    description='Test a resource status.',
)
resource_test_parser.add_argument('resource', help='resource to be tested.', nargs='+')


class ResourceClientPrompt:

    def do_resource(self, inp):
        try:
            resource_args = shlex.split(inp)
            ns = resource_parser.parse_args(resource_args)

            if ns.command == ['ls']:
                resources = self.client.get_resources()
                print(tabulate.tabulate(resources, headers='keys'))
            if ns.command == ['test']:
                run_ns = resource_test_parser.parse_args(resource_args[1:])
                resources = self.client.get_resources()

                for resource_id in run_ns.resource:
                    print('Testing resource', resource_id, '...')
                    resource_obj = resources.find_object(resource_id)

                    if resource_obj is None:
                        print('Resource reference not found:', resource_id)
                    else:
                        status = self.client.test_resource(resource_obj.get_oid())
                        print('Test status:', status)


        except SystemExit:
            pass

    def help_resource(self):
        resource_parser.print_help()

    def do_resources(self, inp):
        self.do_resource('ls')

    def help_resources(self):
        print('List all server resources. This is a shortcut for "resource ls"')
