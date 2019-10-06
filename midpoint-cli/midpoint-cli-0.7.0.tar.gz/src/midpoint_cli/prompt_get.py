import shlex
from argparse import ArgumentParser, RawTextHelpFormatter
from xml.etree import ElementTree

get_parser = ArgumentParser(
    formatter_class=RawTextHelpFormatter,
    prog='get',
    description='Get a server object.',
    epilog='')
get_parser.add_argument('objectclass', help='Type of the object to fetch (Java Type).')
get_parser.add_argument('oid', help='Object ID.')
get_parser.add_argument('file', help='Save the XML data to this file.', nargs='?')


class GetClientPrompt:
    def do_get(self, inp):
        try:
            get_args = shlex.split(inp)
            ns = get_parser.parse_args(get_args)

            xml_text = self.client.get_xml(ns.objectclass, ns.oid)
            xml_root = ElementTree.fromstring(xml_text)

            status_node = xml_root.find('{http://midpoint.evolveum.com/xml/ns/public/common/common-3}status')

            if status_node is not None and status_node.text == 'fatal_error':
                print(xml_root.find('{http://midpoint.evolveum.com/xml/ns/public/common/common-3}message').text)
            else:
                if ns.file is None:
                    print(xml_text)
                else:
                    with open(ns.file, 'w') as f:
                        f.write(xml_text)

        except AttributeError as e:
            print('Error:', e)
        except SystemExit:
            pass

    def help_get(self):
        get_parser.print_help()
