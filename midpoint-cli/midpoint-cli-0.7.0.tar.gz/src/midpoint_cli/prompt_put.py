import shlex
from argparse import ArgumentParser, RawTextHelpFormatter

put_parser = ArgumentParser(
    formatter_class=RawTextHelpFormatter,
    prog='put',
    description='Create or update a server object.',
    epilog='')
put_parser.add_argument('-p', '--patch', help='Patch the object according to the following patch file.', action='store')
put_parser.add_argument('-w', '--patchwrite', help='Write the result of the patching phase in a file <patchfile>.xml', action='store_true')
put_parser.add_argument('file', help='Load XML data from this file.')


class PutClientPrompt:
    def do_put(self, inp):
        try:
            put_args = shlex.split(inp)
            ns = put_parser.parse_args(put_args)

            o_class, o_id = self.client.put_xml(ns.file, ns.patch, ns.patchwrite)
            print('Object uploaded:', o_class, o_id)

        except SystemExit:
            pass

    def help_put(self):
        put_parser.print_help()
