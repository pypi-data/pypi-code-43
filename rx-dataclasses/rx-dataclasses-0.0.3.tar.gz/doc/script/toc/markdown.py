from importlib.util import find_spec
from operator import itemgetter
import sys
import os
import yaml
from pathlib import Path

TOCHEADER = """
### API
"""
TOCITEM = """{indent}* [{itemname}]({itemlink}) """

def cli(args):
    _template = Path(args[0].strip())
    apimodules = [module.strip() for module in args[1:]]

    with open(str(_template)) as template:
        links = []
        for apimodule in apimodules:
            modpath = apimodule.split('.')
            if find_spec(apimodule).origin.endswith('__init__.py'):
                modpath.append('index.md')
            else:
                modpath[-1] = modpath[-1] + '.md'
            links.append({'itemname': apimodule, 'itemlink': str(Path(*modpath)), 'indent': (len(apimodule.split('.')) - 1) * '    '})
        print(template.read())
        print(TOCHEADER)
        for link in sorted(links, key=itemgetter('itemname')):
            print(TOCITEM.format(**link))

if __name__ == '__main__':
    cli(sys.argv[1:])