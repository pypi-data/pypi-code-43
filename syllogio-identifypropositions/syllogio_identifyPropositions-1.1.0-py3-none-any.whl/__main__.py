"""Usage: idpr [options] INPUT

Options:
  -m <model> --model <model>    Specify a spaCy model. Defaults to "en_core_web_sm".
  -V --version                  Print version and exit.
  -h --help                     Show this message.
"""
from identifyPropositions import identify, __version__
from docopt import docopt
import json
import sys


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    cli = docopt(__doc__, argv=args, version="idpr " + __version__)

    opts = {"text": cli["INPUT"]}
    if cli["--model"] is not None:
        opts["model_name"] = cli["--model"]

    print(json.dumps(identify(**opts), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
