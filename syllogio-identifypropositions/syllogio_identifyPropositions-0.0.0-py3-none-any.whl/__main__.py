from identifyPropositions import identify
import json
import sys


def main(args=None):
    if args is None:
        args = sys.argv[1:]
    print(json.dumps(identify(args[0]), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
