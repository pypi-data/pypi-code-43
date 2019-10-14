#!/usr/bin/env python
"""NStream v0.1.
Usage:
  nstream ship new <name>...
  nstream ship <name> move <x> <y> [--speed=<kn>]
  nstream ship shoot <x> <y>
  nstream mine (set|remove) <x> <y> [--moored|--drifting]
  nstream -h | --help
  nstream --version
Options:
  -h --help     Show this screen.
  --version     Show version.
  --speed=<kn>  Speed in knots [default: 10].
  --moored      Moored (anchored) mine.
  --drifting    Drifting mine.
"""
from docopt import docopt


if __name__ == '__main__':
    arguments = docopt(__doc__, version='NStream v0.1')
    print(arguments)