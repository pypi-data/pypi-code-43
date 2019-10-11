from importlib.util import find_spec
import sys
import os
import yaml
from pathlib import Path


def cli(args):
    _template = Path(args[0].strip())
    _mkdocs = Path(args[1].strip())
    apimodules = [module.strip() for module in args[2:]]
    with open(str(_mkdocs), 'w') as mkdocs:
        with open(str(_template)) as template:
            config = yaml.load(template, Loader=yaml.FullLoader)
            api = []
            for apimodule in apimodules:
                modpath = apimodule.split('.')
                if find_spec(apimodule).origin.endswith('__init__.py'):
                    modpath.append('index.md')
                else:
                    modpath[-1] = modpath[-1] + '.md'

                api.append({apimodule: str(Path(*modpath))})
            config['nav'].append({'API': api})
        print(yaml.dump(config))

if __name__ == '__main__':
    cli(sys.argv[1:])