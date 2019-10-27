# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['shinyutils']

package_data = \
{'': ['*'], 'shinyutils': ['data/*']}

install_requires = \
['crayons', 'matplotlib>=3.0.0,<4.0.0', 'seaborn>=0.9.0,<0.10.0']

setup_kwargs = {
    'name': 'shinyutils',
    'version': '2.0.0',
    'description': 'Personal collection of common utilities',
    'long_description': '# shinyutils\nVarious utilities for common tasks. :sparkles: :sparkles: :sparkles:\n\n## Setup\nInstall with `pip`.\n\n```bash\npip install shinyutils\n```\n\n## `matwrap`\nWrapper around `matplotlib` and `seaborn`.\n### Usage\n```python\nfrom shinyutils import MatWrap as mw  # do not import `matplotlib`, `seaborn`\n\nmw.configure()  # this should be called before importing any packages that import matplotlib\n\nfig = mw.plt().figure()\nax = fig.add_subplot(111)  # `ax` can be used normally now\n\n# Use class methods in `MatWrap` to access `matplotlib`/`seaborn` functions.\nmw.mpl()  # returns `matplotlib` module\nmw.plt()  # returns `matplotlib.pyplot` module\nmw.sns()  # returns `seaborn` module\n```\n\n### Configuration\nUse `mw.configure` to configure plots. Arguments (defaults indicated with []) are:\n```python\ncontext: seaborn context ([paper]/poster/talk/notebook)\nstyle: seaborn style (white/whitegrid/dark/darkgrid/[ticks])\nfont: any font available to fontspec (default [Latin Modern Roman])\nlatex_pkgs: additional latex packages to be included before defaults\n**rc_extra: matplotlib rc parameters to override defaults\n```\n\n## `subcls`\nUtility functions for dealing with subclasses.\n### Functions\n* __`get_subclasses(cls)`__: returns a list of all the subclasses of `cls`.\n* __`get_subclass_names(cls)`__: returns a list of names of all subclasses of `cls`.\n* __`get_subclass_from_name(base_cls, cls_name)`__: return the subclass of `base_cls` named `cls_name`.\n* __`build_subclass_object(base_cls, cls_name, kwargs)`__: return an instance of `get_subclass_from_name` initialized using `kwargs`.\n\n## `argp`\nUtilities for argument parsing.\n### `LazyHelpFormatter`\n`HelpFormatter` with sane defaults, and colors (courtesy of `crayons`)! To use, simply pass `formatter_class=LazyHelpFormatter` when creating `ArgumentParser` instances.\n```python\narg_parser = ArgumentParser(formatter_class=LazyHelpFormatter)\nsub_parsers = arg_parser.add_subparsers(dest="cmd")\nsub_parsers.required = True\n# `formatter_class` needs to be set for sub parsers as well.\ncmd1_parser = sub_parsers.add_parser("cmd1", formatter_class=LazyHelpFormatter)\n```\n\n### `comma_separated_ints`\n`ArgumentParser` type representing a comma separated list of ints (example `1,2,3,4`).\n```python    \narg_parser.add_argument("--csi", type=comma_separated_ints)\n```\n\n### `OutputFileType`\n`ArgumentParser` type representing an output file. The file\'s base directory is created if needed. The returned value is a file object.\n\n### `OutputDirectoryType`\n`ArgumentParser` type representing an output directory. The directory is created if it doesn\'t exist.\n\n### `ClassType`\n`ArgumentParser` type representing sub-classes of a given base class. The returned value is a class.\n```python\nclass Base:\n    pass\n\nclass A(Base):\n    pass\n\nclass B(Base):\n    pass\n\narg_parser.add_argument("--cls", type=ClassType(Base), default=A)\n```\n\n### `shiny_arg_parser`\n`ArgumentParser` object with LazyHelpFormatter, and logging argument.\n\n## `logng`\nUtilities for logging.\n### `build_log_argp`\nCreates an argument group with logging arguments.\n```\n>>> arg_parser = ArgumentParser()\n>>> build_log_argp(arg_parser)\n>>> arg_parser.print_help()\nusage: test.py [-h] [--log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}]\n\noptional arguments:\n  -h, --help            show this help message and exit\n  --log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}\n```\n\n### `conf_logging`\nConfigures global logging (and adds colors!) using arguments returned by `ArgumentParser.parse_args`. `log_level` can be over-ridden with the keyword argument. Colors are not enabled if output isn\'t a tty.\n```python\nargs = arg_parser.parse_args()\nconf_logging(args)\nconf_logging(args, log_level="INFO")  # override `log_level`\n```\nBy default, the package configures logging at INFO level.\n',
    'author': 'Jayanth Koushik',
    'author_email': 'jnkoushik@gmail.com',
    'url': 'https://github.com/jayanthkoushik/shinyutils',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
