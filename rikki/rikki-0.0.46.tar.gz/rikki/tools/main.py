import sys
from typing import Optional, Sequence
from rikki.template.template import behave_init
from rikki.run import RikkiTestRunner


def rikki(args: Optional[Sequence[str]] = sys.argv[1:]) -> Optional[int]:
    if not args:
        print("Use --help to find possible options")
        return
    if len(args) > 1:
        print("You can't use more than 1 argument. Use --help to find possible options")
        return

    command = args[0]

    if command == "init":
        behave_init()
        return

    if command == "run":
        RikkiTestRunner().run()
        return

    if command == "--help":
        print("init - will init folder structures for behave test environment")
        print("run - will run tests defined in the folder with default config")
        print("--help - show this help")


if __name__ == "__main__":
    rikki(sys.argv[1:])
