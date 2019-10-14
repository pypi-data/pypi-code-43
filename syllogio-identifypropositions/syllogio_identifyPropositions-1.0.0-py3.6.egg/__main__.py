"""Usage: idpr [options] INPUT

Options:
  -h --help                 Show this message
  -m MODEL --model=MODEL    specify a spaCy model. Defaults to "en_core_web_sm".
"""
from . import identify, __version__
from docopt import docopt
import json
import sys


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    cli = docopt(__doc__, argv=args, version="idpr " + __version__)

    opts = {"text": cli["INPUT"]}
    if cli["MODEL"] is not None:
        opts["model_name"] = cli["MODEL"]

    print(json.dumps(identify(**opts), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
