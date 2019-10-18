from __future__ import annotations

import sys
import argparse
import platform

from .refreezer import refreeze


def main() -> None:
    if platform.system() != 'Windows':
        print(
            "%s requires to be running on Windows" % sys.argv[0],
            file=sys.stderr,
        )
        sys.exit(1)

    parser = argparse.ArgumentParser()
    parser.add_argument('--prefix', default=sys.prefix)
    parser.add_argument('--quiet', '-q', action="store_true")
    parser.add_argument('--no-dry', '-n', action="store_true")

    args = parser.parse_args()

    if not args.no_dry:
        print("running with dry mode. use --no-dry to make effect")
    refreeze(args.prefix, not args.quiet, not args.no_dry)


if __name__ == '__main__':
    main()
